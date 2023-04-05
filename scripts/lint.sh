#!/bin/sh -e

#mypy cli.py app/

flake8 cli.py
flake8 app/

black cli.py --check
black app/ --check