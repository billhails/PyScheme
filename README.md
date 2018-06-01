# PyScheme

A small lambda-language interpreter written in Python

Syntax is very much in the javascript/C/Java style, and I'm currently parsing with a hand-written recursive descent parser,
which isn't ideal.

## First Impressions

To get a feel for the language, first check out the [wiki](https://github.com/billhails/PyScheme/wiki), then
read through the integration tests in [`pyscheme/tests/integration`](https://github.com/billhails/PyScheme/tree/master/pyscheme/tests/integration)

## Cloning

I'm new to Python so if anyone has any better way of doing this please comment.

In order to get this running on my laptop after pushing to GitHub from my home computer I did the following:

1. Use PyCharm to create a new project called PyScheme.
1. go to your pycharm projects root directory:
   * `cd ~/PycharmProjects`
1. clone this repository to a temporary location alongside (not in) the PyScheme project:
   * `git clone git@github.com:billhails/PyScheme.git pyscheme-tmp`
1. Copy everything from that temp location into the PyScheme directory (note the trailing slashes):
   * `cp -R pyscheme-tmp/ PyScheme/`
1. delete the unneeded temporary clone:
   * `rm -rf pyscheme-tmp`
1. check that it worked:
   * `cd PyScheme`
   * `git status`

If, like me, you're using PyCharm CE, You'll additionally need to install `coverage`. To install `coverage`
go to the root of the distro and do
```
$ source ./venv/bin/activate
$ pip install coverage
```

## Test Coverage

Once those packages are installed, to see test coverage just run the `coverage.sh` script (OSX/Unix), then open
`htmlcov/index.html` in your browser. For other plarforms you can look at `coverage.sh` and see what it does (it's
only a couple of lines of code.) If anyone wants to provide a `coverage.bat` or similar for other platforms please
submit a PR.

I believe that the PyCharm Professional edition has built-in coverage support.
