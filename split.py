import chess
import subprocess
import time
import argparse
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

def main():
    parser = argparse.ArgumentParser(description='UCI chess engine perft')
    parser.add_argument("-engine", type=str, required=True, help="path to the engine")
    parser.add_argument(
        "-fen",
        type=str,
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        help="fen string to test"
    )
    parser.add_argument("-depth", type=int, default=1, help="perft depth")
    args = parser.parse_args()

    if not os.path.isfile(args.engine):
        print("Engine file not found")
        return

    args.depth = max(args.depth, 1)

    # Check the provided fen string
    try:
        board = chess.Board(args.fen)
    except:
        print(F"Illegal fen {args.fen}")
        return

    # Start the engine
    e = Engine(args.engine)
    e.send("uci\n")
    e.send("isready\n")

    total = 0
    for idx, move in enumerate(board.legal_moves):
        # Reset the engine
        e.send("ucinewgame\n")

        # Reset the position
        nboard = chess.Board(args.fen)

        # Apply the next move
        nboard.push(move)

        print(F"{idx+1}:  {move}", end="")

        # Perft
        if args.depth > 1:
            e.send("position fen {}\n".format(nboard.fen()))
            e.send(("perft {}\n").format(args.depth-1))
            nodes = int(e.get("nodes"))
            total += nodes

            # Results
            print(F"  {nodes}", end="")
        else:
            total += 1

        print("")

    print(F"Total: {total}")

if __name__ == "__main__":
    main()
