import chess
import subprocess
import time
import argparse
import queue
import threading
import os

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

q = queue.Queue()
lock = threading.Lock()
correct = 0
incorrect = 0

def read_epd(path):
    with open(path) as f:
        for line in f:
            try:
                board, results = chess.Board().from_epd(line)

                nodes = []
                for key, val in results.items():
                    if not key.startswith("D"):
                        continue
                    nodes.append(val)

                q.put((board.fen(), nodes))
            except:
                pass

def worker(path, depth, verbose):
    global correct
    global incorrect

    with Engine(path) as e:
        e.send("uci\n")
        e.send("isready\n")

        while not q.empty():
            fen, nodes = q.get()

            if verbose:
                print(F"Working: {fen}")

            e.send("ucinewgame\n")
            e.send(F"position fen {fen}\n")

            right = True

            for d in range(depth):
                # Break if the position doesn't have enough
                # results for the depth specified
                if d >= len(nodes):
                    if verbose:
                        print(F"WARNING: depth {d+1} not found for {fen}")
                    break

                # Ask the engine to run perft
                e.send((F"perft {d+1}\n"))
                n = int(e.get("nodes"))

                if n != nodes[d]:
                    if verbose:
                        print(F"ERROR: depth {d+1} expected {nodes[d]} got {n} for {fen}")
                    right = False
                    break

            with lock:
                if right:
                    correct += 1
                else:
                    incorrect += 1

def main():
    parser = argparse.ArgumentParser(description='UCI chess engine perft')
    parser.add_argument("-engine", type=str, help="path to the engine")
    parser.add_argument("-suite", type=str, help="path to the test suite")
    parser.add_argument("-depth", type=int, default=1, help="perft depth")
    parser.add_argument("-threads", type=int, default=1, help="threads to use")
    parser.add_argument("-verbose", help="print extra details", action='store_true')
    args = parser.parse_args()

    if not os.path.isfile(args.engine):
        print("Engine file not found")
        return

    if not os.path.isfile(args.suite):
        print("Suite file not found")
        return

    args.depth = max(args.depth, 1)
    args.threads = max(args.threads, 1)

    # Load positions from .epd
    read_epd(args.suite)

    # Create worker threads
    threads = []
    for i in range(args.threads):
        t = threading.Thread(target=worker, args=(args.engine, args.depth, args.verbose))
        threads.append(t)

    # Details
    print(F"{q.qsize()} positions loaded")

    # Start timing
    t0 = time.time()

    # Start working
    for t in threads:
        t.start()

    # Wait
    for t in threads:
        t.join()

    # Stop timing
    t1 = time.time()

    # Results
    total = correct+incorrect
    print(F"Time:      {t1-t0:.2f}s")
    print(F"Depth:     {args.depth}")
    print(F"Threads:   {args.threads}")
    print(F"Correct:   {correct} ({100*correct/total:.1f}%)")
    print(F"Incorrect: {incorrect} ({100*incorrect/total:.1f}%)")
    print(F"Total:     {total}")

if __name__ == "__main__":
    main()
