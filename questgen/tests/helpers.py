import collections.abc


class FakeInterpreter(object):

    def __init__(self, **kwargs):
        self.results = kwargs


    def __getattr__(self, name):
        if isinstance(self.results[name], collections.abc.Callable):
            return self.results[name]
        return lambda *argv, **kwargs: self.results[name]

    def on_state__before_actions(self, state): pass
    def on_state__after_actions(self, state): pass
    def on_jump_start__before_actions(self, jump): pass
    def on_jump_start__after_actions(self, jump): pass
    def on_jump_end__before_actions(self, jump): pass
    def on_jump_end__after_actions(self, jump): pass
