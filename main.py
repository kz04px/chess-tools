import argparse
import perft as p
import match as m
import tactics as t


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automated chess engine testing')
    parser.add_argument('--version', action='version', version='Engine tester v1')
    parser.add_argument('-perft', nargs='*')
    parser.add_argument('-match', action='store_true')
    parser.add_argument('-tactics', nargs='*')
    parser.add_argument('-verbose', action='store_true')

    args, unknown = parser.parse_known_args()
    args = vars(args)

    if args["perft"]:
        perft = p.PerftSuite()
        perft.parse(args["perft"])
        perft.run(verbose=args["verbose"])

    if args["match"]:
        match = m.EngineMatch()
        match.parse(' '.join(unknown))
        match.run(verbose=args["verbose"])

    if args["tactics"]:
        tactics = t.TacticsSuite()
        tactics.parse(args["tactics"])
        tactics.run(verbose=args["verbose"])
