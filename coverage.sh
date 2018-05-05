#! /bin/bash

. ./venv/bin/activate

coverage run -m unittest discover -s pyscheme/tests -t pyscheme/tests
coverage html
