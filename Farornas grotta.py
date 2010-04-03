#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("data/source/")

from main import *

def main():
	game = CaveOfDanger()

	game.run()
	game.input_thread.join()

	if game.networkThread.isAlive():
		main.networkThread.join()


if __name__ == "__main__":
	main()
