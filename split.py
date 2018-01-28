import chess
import subprocess
import time


#  Results for startpos
#  Depth          Nodes
#  1                 20
#  2                400
#  3              8,902
#  4            197,281
#  5          4,865,609
#  6        119,060,324
#  7      3,195,901,860


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


if __name__ == "__main__":
    enginePath = "engines/baislicka"
    depth = 1

    p = Engine(enginePath)
    p.send("uci\n")
    p.send("isready\n")

    board = chess.Board()

    #board.push(chess.Move.from_uci("d2d3"))
    #board.push(chess.Move.from_uci("b7b5"))
    #board.push(chess.Move.from_uci("e1d2"))
    #board.push(chess.Move.from_uci("b5b4"))

    print(board)

    print("Depth: {}".format(depth))
    total = 0
    for idx, move in enumerate(board.legal_moves):
        nboard = chess.Board(board.fen())
        nboard.push(move)

        p.send("position fen {}\n".format(nboard.fen()))
        p.send(("perft {}\n").format(depth))
        nodes = p.get("nodes")
        total = total + int(nodes)
        print("{}:  {}  {}".format(idx+1, move, nodes))
    print("Total: {}".format(total))