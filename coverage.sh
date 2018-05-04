#! /bin/bash

. ./venv/bin/activate

coverage run -m unittest discover -s /Users/billhails/PycharmProjects/PyScheme/pyscheme/tests -t /Users/billhails/PycharmProjects/PyScheme/pyscheme/tests
coverage html
