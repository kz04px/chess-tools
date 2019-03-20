import chess
import chess.uci
import time
import argparse
import queue
import threading
import os

q = queue.Queue()
lock = threading.Lock()
correct = 0
incorrect = 0

def read_epd(path):
    with open(path) as f:
        for line in f:
            try:
                board, results = chess.Board().from_epd(line)

                if not board.is_valid():
                    continue

                if board.is_game_over():
                    continue

                # Get best move
                if "bm" in results.keys():
                    move = results["bm"][0]
                else:
                    continue

                # Check move legality
                if move not in board.legal_moves:
                    continue

                q.put((board, move))
            except:
                pass

def worker(path, movetime, verbose):
    global correct
    global incorrect

    try:
        e = chess.uci.popen_engine(path)
        e.uci()
        e.isready()

        while not q.empty():
            board, answer = q.get()

            e.ucinewgame()
            e.position(board)
            bestmove, _ = e.go(movetime=movetime)

            with lock:
                if bestmove == answer:
                    correct += 1
                else:
                    incorrect += 1

        e.quit()
    except:
        pass

def run(path, num_threads, movetime, verbose):
    global correct
    global incorrect

    correct = 0
    incorrect = 0

    # Create worker threads
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(path, movetime, verbose))
        threads.append(t)

    # Start working
    for t in threads:
        t.start()

    # Wait
    for t in threads:
        t.join()

    return correct, incorrect

def main():
    parser = argparse.ArgumentParser(description='UCI chess engine perft')
    parser.add_argument("-engine", type=str, required=True, help="path to the engine")
    parser.add_argument("-suite", type=str, required=True, help="path to the test suite")
    parser.add_argument("-movetime", type=int, default=100, help="search movetime")
    parser.add_argument("-threads", type=int, default=1, help="threads to use")
    parser.add_argument("-verbose", help="print extra details", action='store_true')
    args = parser.parse_args()

    if not os.path.isfile(args.engine):
        print("Engine file not found")
        return

    # Load positions from .epd
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
        return
    tests = sorted(tests)

    args.movetime = max(args.movetime, 1)
    args.threads  = max(args.threads, 1)

    # Stats
    total_correct = 0
    total_incorrect = 0
    total_time = 0

    try:
        for test in tests:
            read_epd(test)

            # Start timing
            t0 = time.time()

            correct, incorrect = run(args.engine, args.threads, args.movetime, args.verbose)

            # Stop timing
            t1 = time.time()

            head, tail = os.path.split(test)

            total = correct + incorrect
            print(F"{correct}/{total}  {100*correct/total:.1f}%  {tail}")

            total_correct += correct
            total_incorrect += incorrect
            total_time += t1 - t0
    except:
        pass
    print("")

    total_tests = total_correct+total_incorrect
    if total_tests == 0:
        print("No tests were completed")
        return

    # Results
    print(F"Time:      {total_time:.2f}s")
    print(F"Movetime:  {args.movetime}ms")
    print(F"Threads:   {args.threads}")
    print(F"Correct:   {total_correct} ({100*total_correct/total_tests:.1f}%)")
    print(F"Incorrect: {total_incorrect} ({100*total_incorrect/total_tests:.1f}%)")
    print(F"Total:     {total_tests}")

if __name__ == "__main__":
    main()
