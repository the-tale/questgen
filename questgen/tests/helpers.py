# coding: utf-8


class FakeInterpreter(object):

    def __init__(self, **kwargs):
        self.results = kwargs


    def __getattr__(self, name):
        if callable(self.results[name]):
            return self.results[name]
        return lambda *argv, **kwargs: self.results[name]
