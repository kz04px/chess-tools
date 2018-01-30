import chess
import chess.uci
import time
import argparse
import queue
import threading
import os


class Manager:
    def __init__(self):
        self.q = queue.Queue()
        self.lock = threading.Lock()

    def go(self, enginePath, movetime=100, numThreads=1, verbose=False):
        if self.q.qsize() < 1:
            print("ERROR: no positions loaded")
            return

        if numThreads < 1:
            print("ERROR: number of threads must be >= 1")
            return

        self.total = 0
        self.incorrect = 0

        threads = []
        for i in range(numThreads):
            t = threading.Thread(target=self.worker, args=([enginePath, movetime, verbose]))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if self.total == 0:
            print("No positions analysed")
            return

        print("{}/{}  {:.2f}%  {}".format(self.total - self.incorrect, self.total, 100.0*(self.total - self.incorrect)/self.total, self.path))
        return self.total - self.incorrect, self.total

    def load(self, path):
        self.q.queue.clear()
        self.path = path
        try:
            with open(path, "r") as f:
                for line in f:
                    try:
                        asd = chess.Board().set_epd(line)
                        if "bm" in asd:
                            self.q.put(line)
                    except:
                        pass
        except Exception as e:
            print(e)
            return False
        return True

    def worker(self, enginePath, timeper, verbose):
        engine = chess.uci.popen_engine(enginePath)
        engine.uci()
        engine.isready()

        board = chess.Board()

        while self.q.empty() == False:
            line = self.q.get()

            asd = board.set_epd(line)

            self.lock.acquire()
            self.total += 1
            self.lock.release()

            engine.position(board)

            command = engine.go(movetime=timeper, async_callback=True)
            bestmove, ponder = command.result()

            if bestmove != asd["bm"][0]:
                self.lock.acquire()
                if verbose:
                    print("Got {}  expected {}  position {}".format(bestmove, asd["bm"][0], board.fen()))
                self.incorrect += 1
                self.lock.release()

        engine.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UCI chess engine tactics')
    parser.add_argument("-engine", type=str, help="path to the engine")
    parser.add_argument("-suite", type=str, help="path to the test suite")
    parser.add_argument("-movetime", type=int, help="search movetime")
    parser.add_argument("-threads", type=int, help="threads to use")
    parser.add_argument("-verbose", help="print extra details", action='store_true')
    args = parser.parse_args()

    if args.movetime < 1:
        print("ERROR: movetime must be >= 1")
        exit(1)

    if args.movetime > 10000:
        print("WARNING: that's a lot of movetime")

    if args.threads < 1:
        print("ERROR: threads must be >= 1")
        exit(2)

    if args.threads > 4:
        print("WARNING: that's a lot of threads")

    if os.path.isfile(args.engine) == False:
        print("Cannot find engine specified")
        exit(3)

    tests = []

    if os.path.isdir(args.suite):
        for root, dirs, files in os.walk(args.suite):
            for file in files:
                if file.endswith(".epd"):
                    tests.append(os.path.join(root, file))
    elif os.path.isfile(args.suite):
        tests.append(args.suite)
    else:
        print("No valid positions found at the path specified")
        exit(4)

    tests = sorted(tests)
    correct = 0
    total = 0

    print("Settings")
    print("Engine: {}".format(args.engine))
    print("Movetime: {}ms".format(args.movetime))
    print("Threads: {}".format(args.threads))
    print("")

    start = time.time()
    tactics = Manager()
    print("Tests")
    for test in tests:
        tactics.load(test)
        c, t = tactics.go(args.engine, args.movetime, args.threads, args.verbose)
        correct = correct + c
        total = total + t
    end = time.time()
    print("")

    print("Totals")
    print("Time: {:.2f}s".format(end - start))
    print("Correct: {}".format(correct))
    print("Total: {}".format(total))
    print("Accuracy: {:.2f}%".format(100.0*correct/total))