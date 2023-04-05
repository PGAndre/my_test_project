#!/bin/sh -e

isort cli.py
isort app/
isort tests/

black cli.py
black app/
black tests/