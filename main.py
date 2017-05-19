import argparse
import perft as p
import match as m
import tactics as t


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automated chess engine testing')
    parser.add_argument('--version', action='version', version='Engine tester v1')
    parser.add_argument("-perft", action='store_true', help="run perft tests")
    parser.add_argument("-match", action='store_true', help="run match")
    parser.add_argument("-tactics", action='store_true', help="run tactics")
    args = parser.parse_args()

    if args.perft:
        perft = p.PerftSuite()
        perft.load("suites\\perft\\hartmann.epd")
        perft.depth = 3
        perft.start("engines\\wyldchess.exe")
        perft.results()
    elif args.match:
        match = m.EngineMatch()
        match.add_engine("wyldchess", "uci", "engines\\wyldchess.exe")
        match.add_engine("TSCP", "xboard", "engines\\tscp181.exe")
        match.add_engine("Cinnamon-2", "uci", "engines\\cinnamon_2.0_x64-INTEL.exe")
        match.start()
    elif args.tactics:
        pass
