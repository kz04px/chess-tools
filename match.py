import subprocess


class EngineMatch:
    def __init__(self):
        self.engines = []

    def parse(self, params):
        pass

    def run(self, verbose=False):
        params = "C:\\Program Files (x86)\\cutechess\\cutechess-cli.exe"

        # Add engines
        params += " -engine name=wyldchess proto=uci cmd=\"engines\\wyldchess.exe\""
        params += " -engine name=tscp proto=xboard cmd=\"engines\\tscp181.exe\""
        params += " -engine name=Cinnamon-2 proto=uci cmd=\"engines\\cinnamon_2.0_x64-INTEL.exe\""

        # Other
        params += " -each tc=1+0.01s -games 10 -concurrency 3 -recover -ratinginterval 5 -tournament gauntlet"

        p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        last_score = ""
        rank = ""
        while p.poll() is None:
            l = p.stdout.readline().decode("utf-8") 
            l = l.rstrip("\r\n")

            
            if l[0:14] == "ELO difference":
                print(last_score)
                print(l)
            elif l[0:9] == "Score of ":
                last_score = l
            elif l[0:4] == "Rank":
                verbose = True
            elif l[0:1] == " " and verbose == True:
                pass
            else:
                if verbose:
                    print("")
                verbose = False
            
            # if l[0:24] == "Warning: Illegal PV move":
                # continue
            # elif l[0:14] == "ELO difference":
                # print(last_score)
                # print(l)
            # elif l[0:4] == "Rank":
                # verbose = True
            # elif l[0:14] == "Finished match":
                # verbose = False
            # elif l[0:9] == "Score of ":
                # last_score = l
            # elif l[0:13] == "Started game ":
                # verbose = False

            if verbose:
                print(l)
        #print(last_score)

    def add_engine(self, name, protocol, path):
        if protocol not in ["uci", "xboard"]:
            return
        self.engines.append("-engine name=\"{}\" proto={} cmd=\"{}\"".format(name, protocol, path))
