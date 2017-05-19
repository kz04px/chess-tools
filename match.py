import subprocess


class EngineMatch:
    def __init__(self):
        self.engines = []

    def add_engine(self, name, protocol, path):
        self.engines.append("-engine name=\"{}\" proto={} cmd=\"{}\"".format(name, protocol, path))

    def start(self):
        self.path_cutechess = "C:\\Program Files (x86)\\cutechess\\cutechess-cli.exe"
        self.tc = "1+0.01s"
        self.games = "5"
        self.concurrency = "3"

        params = self.path_cutechess
        for engine in self.engines:
            params += " " + engine
        params += " " + "-each tc={} -games {} -concurrency {} -tournament gauntlet".format(self.tc, self.games, self.concurrency)

        p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        while p.poll() is None:
            l = p.stdout.readline().decode("utf-8") 
            l = l.rstrip("\r\n")

            if l[0:24] == "Warning: Illegal PV move":
              continue

            print(l)
