# PyScheme

A small lambda-language interpreter written in Python

I have a few ideas I'd like to pull in from my abortive F-natural project,
specifically:

- [x] incorporate `amb` with keywords `then` and `back`, i.e. `define x = 5 then 6`
and `if (x == 0) { back }`.
- [x] strong implicit type checking.
- [x] first-class environments.
- [x] built-in linked lists with `@` (cons) and `@@` (append) operators.
- [ ] strings are linked lists of char.
- [x] Three-valued logic system.
- [x] Partial and over-complete function application.

Syntax is very much in the javascript style, and I'm currently parsing with a hand-written recursive descent parser,
which isn'a ideal.

## First Impressions

To get a feel for the language, read through the integration tests in `pyscheme/tests/integration`

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

You'll additionally need to install `coverage`. To install `coverage` go to the root of the distro and do
```
$ source ./venv/bin/activate
$ pip install coverage
```

## Test Coverage

Once those packages are installed, to see test coverage just run the `coverage.sh` script (OSX/Unix), then open
`htmlcov/index.html` in your browser. For other plarforms you can look at `coverage.sh` and see what it does (it's
only a couple of lines of code.) If anyone wants to provide a
 `coverage.bat` or similar for other platforms please
submit a PR.
