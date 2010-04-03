#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("data/source/")

from main import *

def main():
	print """\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\naoo\n\naaaaaaaaa
	aaaaaaaaaaa        aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
	aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  """
	game = CaveOfDanger()

	game.run()
	game.input_thread.join()

	if game.networkThread.isAlive():
		game.networkThread.join()


if __name__ == "__main__":
	main()
