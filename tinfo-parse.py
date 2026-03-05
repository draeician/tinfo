#!/usr/bin/env python3
import sys
import os

# Add the 'src' directory to the path so it can find the 'tinfo' package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tinfo.cli import main

if __name__ == "__main__":
    sys.exit(main())
