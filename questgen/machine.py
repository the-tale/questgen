# coding: utf-8
import random

from questgen.facts import Pointer, Start, Finish, Jump

from questgen import exceptions


class Machine(object):

    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def get_pointer(self):
        if Pointer.UID not in self.knowledge_base:
            self.knowledge_base += Pointer()
        return self.knowledge_base[Pointer.UID]

    def step(self):
        pointer = self.get_pointer()

        if pointer.jump is not None:
            next_state = self.knowledge_base[self.knowledge_base[pointer.jump].state_to]
        else:
            next_state = self.knowledge_base.filter(Start).next()

        new_pointer = pointer.change(state=next_state.uid, jump=None)

        if not isinstance(next_state, Finish):
            new_pointer = new_pointer.change(jump=self.get_next_jump(next_state).uid)

        self.knowledge_base -= pointer
        self.knowledge_base += new_pointer

    def can_do_step(self):
        pointer = self.get_pointer()

        if pointer.jump is None:
            next_state = self.knowledge_base.filter(Start).next()
        else:
            next_state = self.knowledge_base[self.knowledge_base[pointer.jump].state_to]

        return all(requirement.check(self.knowledge_base)
                  for requirement in next_state.require)

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
