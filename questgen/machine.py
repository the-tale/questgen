# coding: utf-8
import random

from questgen.facts import Pointer, Start, Finish, Jump

from questgen import exceptions


class Machine(object):

    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    @property
    def pointer(self):
        if Pointer.UID not in self.knowledge_base:
            self.knowledge_base += Pointer()
        return self.knowledge_base[Pointer.UID]

    @property
    def is_processed(self): # TODO: tests
        return self.pointer.state in self.knowledge_base and isinstance(self.knowledge_base[self.pointer.state], Finish)

    @property
    def next_state(self):
        if self.pointer.jump is None:
            if self.pointer.state is None:
                return self.knowledge_base.filter(Start).next()
            else:
                return None

        return self.knowledge_base[self.knowledge_base[self.pointer.jump].state_to]

    def step(self):

        if self.next_state is None:
            raise exceptions.NoJumpsFromLastStateError(state=self.pointer.state)
        new_pointer = self.pointer.change(state=self.next_state.uid, jump=None)

        if not isinstance(self.next_state, Finish):
            new_pointer = new_pointer.change(jump=self.get_next_jump(self.next_state).uid)

        self.knowledge_base -= self.pointer
        self.knowledge_base += new_pointer

    def can_do_step(self):
        return self.next_state is not None and all(requirement.check(self.knowledge_base) for requirement in self.next_state.require)

    def step_until_can(self):
        while self.can_do_step():
            self.step()

    def get_next_jump(self, state):
        jumps = self.get_available_jumps(state)
        if not jumps:
            raise exceptions.NoJumpsAvailableError(state=state)
        return random.choice(jumps)

    def get_available_jumps(self, state):
        return [jump
                for jump in self.knowledge_base.filter(Jump)
                if jump.state_from == state.uid]
