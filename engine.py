import chess
import chess.uci
import threading
import time


class MyEngine(chess.uci.Engine):
    def __init__(self, *args, **kwargs):
        super(MyEngine, self).__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.results = []
        self.perft_search = False

    def send_line(self, line):
        super(MyEngine, self).send_line(line)
        #print("send > {}".format(line))

    def on_line_received(self, buf):
        super(MyEngine, self).on_line_received(buf)
        #print("recv < {}".format(buf))

        words = buf.split(' ')

        if self.perft_search:
            if words[0] == "info":
                depth = 0
                nodes = 0
                for i, subword in enumerate(words):
                    if subword == "depth":
                        depth = words[i+1]
                    elif subword == "nodes": 
                        nodes = words[i+1]

                if int(depth) > 0 and int(nodes) > 0:
                    self.results.append([depth, nodes])
            elif words[0] == "nodes":
                self.lock.release()

    # The engine has to support the perft command
    def perft(self, depth=3):
        self.lock.acquire()
        self.results = []

        self.perft_search = True
        result = self.send_line("perft {}".format(depth))

        self.lock.acquire()
        self.lock.release()
        self.perft_search = False
        return self.results
