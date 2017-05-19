A small python program to help automate chess engine testing

Matches:
  Uses the cutechess CLI to run engine matches and provide elo calculations

Tactics:
  Uses Python-Chess to read standard .epd files

Perft:
  There is no standard command in the UCI protocol for perft
  This program relies on a custom 'perft' command to work
  Engine writers will specifically have to add this command

Perft command:
  Usage: perft <depth>
  Reply: info depth <depth> nodes <nodes>
         nodes <nodes>

Perft example:
  > uci
  < id name Engine
  < uciok
  > isready
  < readyok
  > position startpos
  > perft 3
  < info depth 1 time 0 nodes 20
  < info depth 2 time 0 nodes 400
  < info depth 3 time 0 nodes 8902
  < nodes 8902
  > quit

Requires:
  - Python 3
  - Python-Chess https://pypi.python.org/pypi/python-chess
  - cutechess https://github.com/cutechess/cutechess
