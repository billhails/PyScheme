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