import chess
import chess.uci
import time


class TacticsSuite():
    def __init__(self):
        self.epd = []

    def load(self, path):
        self.positions = []
        file = open(path, 'r')
        for line in file:
            if(len(line) < 3 or line[0] == '#'):
                continue

            line = line.rstrip('\n')
            words = line.split(';')

            # Try filter out non-fen strings
            if(words[0].count('/') != 7):
                continue

            # Test FEN
            try:
                board = chess.Board()
                board = board.set_epd(words[0])
            except ValueError:
                print("Invalid FEN: {}".format(words[0]))
                continue

            self.epd.append(line)
        self.suite_path = path

    def start(self, engine_path, timeper=10, verbose=False):
        engine = chess.uci.popen_engine(engine_path)
        engine.uci()
        engine.isready()
        asd = chess.Board()
        self.wrong = 0

        t0 = time.time()
        for line in self.epd:
            board = asd.set_epd(line)

            engine.position(asd)
            command = engine.go(movetime=timeper, async_callback=True)
            bestmove, ponder = command.result()

            if(bestmove != board['bm'][0]):
                self.wrong += 1
                if(verbose):
                    print("Expected {} got {}".format(bestmove, board['bm'][0]))
        t1 = time.time()

        engine.stop()
        engine.quit()

        # Save results
        self.engine_path = engine_path
        self.total = len(self.epd)
        self.right = self.total-self.wrong
        self.time_used = t1 - t0
        self.timeper = timeper

    def results(self):
        print("Engine: {}".format(self.engine_path))
        print("Suite: {}".format(self.suite_path))
        print("Pass: {}/{} ({:.1f}%)".format(self.right, self.total, 100*self.right/self.total))
        print("Fail: {}/{} ({:.1f}%)".format(self.wrong, self.total, 100*self.wrong/self.total))
        print("Time: {:.2f}s".format(self.time_used))
        print("Movetime: {}ms".format(self.timeper))
