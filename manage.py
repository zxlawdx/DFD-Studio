#!/usr/bin/env python3
"""CLI oficial do Vela (mesmo padrão do startproject)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vela.cli.commands import CommandRunner

if __name__ == '__main__':
    CommandRunner().execute(sys.argv[1:])
