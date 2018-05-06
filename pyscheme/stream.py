# PyScheme lambda language written in Python
#
# Various input streams that can be plugged ito the lexer to provide input.
#
# Copyright (C) 2018  Bill Hails
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class Stream:
    def read(self):
        pass


class FileStream(Stream):
    def __init__(self, file_name):
        self.file = open(file_name, "r")

    def read(self):
        return self.file.readline()


class StringStream(Stream):
    def __init__(self, string):
        self.string = string

    def read(self):
        string = self.string
        self.string = ''
        return string


class ConsoleStream(Stream):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def read(self):
        return input(self.prompt)