import chess
import subprocess
import time
import argparse
import queue
import threading


class Engine:
    def __init__(self, path):
        self.p = subprocess.Popen(path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

    def send(self, message):
        self.p.stdin.write(message.encode('utf-8'))
        self.p.stdin.flush()

    def recv(self):
        return self.p.stdout.readline().decode('utf-8')

    def get(self, word):
        while self.p.poll() is None:
            l = self.recv()
            l = l.rstrip('\n')

            parts = l.split(' ')
            if len(parts) > 1  and parts[0] == word:
                return parts[1]
            elif len(parts) == 1:
                try:
                    return int(parts[1])
                except:
                    pass
        return None

    def running(self):
        return self.p.poll() == None


class Manager:
    def __init__(self):
        self.q = queue.Queue()
        self.lock = threading.Lock()

    def go(self, enginePath, depth=4, numThreads=1):
        if self.q.qsize() < 1:
            print("ERROR: no positions loaded")
            return

        if numThreads < 1:
            print("ERROR: number of threads must be >= 1")
            return

        self.total = 0
        self.incorrect = 0

        start = time.time()
        threads = []
        for i in range(numThreads):
            t = threading.Thread(target=self.worker, args=([enginePath, depth]))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        end = time.time()

        if self.total == 0:
            print("No positions analysed")
            return

        print("Depth: {}".format(depth))
        print("Engine: {}".format(enginePath))
        print("")
        print("Correct: {}".format(self.total - self.incorrect))
        print("Incorrect: {}".format(self.incorrect))
        print("Total: {}".format(self.total))
        print("Accuracy: {:.2f}%".format(100.0*(self.total - self.incorrect)/self.total))
        print("Threads: {}".format(numThreads))
        print("Time: {:.2f}s".format(end - start))

    def load(self, path):
        self.q.queue.clear()
        try:
            with open(path, "r") as f:
                for line in f:
                    try:
                        board, results = chess.Board().from_epd(line)
                        self.q.put(line)
                    except:
                        pass
        except Exception as e:
            print(e)
            return False
        return True

    def worker(self, enginePath, depth):
        try:
            p = Engine(enginePath)
        except Exception as e:
            print(e)
            return

        p.send("uci\n")
        p.send("isready\n")

        while self.q.empty() == False:
            line = self.q.get()

            try:
                board, results = chess.Board().from_epd(line)
            except Exception as e:
                print("ERROR: {}".format(e))
                continue

            self.lock.acquire()
            self.total += 1
            self.lock.release()
            fen = board.fen()

            if p.running() == False:
                print("ERROR: engine stopped running")
                break

            p.send("position fen {}\n".format(fen))

            for d in range(1, depth+1):
                depthString = "D" + str(d)

                if depthString in results:
                    p.send(("perft {}\n").format(d))

                    nodes = p.get("nodes")

                    if nodes != str(results[depthString]):
                        self.lock.acquire()
                        if verbose:
                            print("Depth {}  got {}  expected {}  position {}".format(d, nodes, results[depthString], fen))
                        self.incorrect += 1
                        self.lock.release()
                        break
                else:
                    self.lock.acquire()
                    if verbose:
                        print("WARNING: depth {} missing from position {}".format(d, fen))
                    self.lock.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UCI chess engine perft')
    parser.add_argument("-engine", type=str, help="path to the engine")
    parser.add_argument("-suite", type=str, help="path to the test suite")
    parser.add_argument("-depth", type=int, help="perft depth")
    parser.add_argument("-threads", type=int, help="threads to use")
    args = parser.parse_args()

    if args.depth < 1:
        print("ERROR: depth must be >= 1")
        exit(1)

    if args.depth > 7:
        print("WARNING: that's a lot of depth")

    if args.threads < 1:
        print("ERROR: threads must be >= 1")
        exit(2)

    if args.threads > 4:
        print("WARNING: that's a lot of threads")

    perft = Manager()
    perft.load(args.suite)
    perft.go(args.engine, args.depth, args.threads)