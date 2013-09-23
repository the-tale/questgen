# coding: utf-8
import random

from questgen import facts
from questgen import exceptions


class Machine(object):

    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    @property
    def pointer(self):
        if facts.Pointer.UID not in self.knowledge_base:
            self.knowledge_base += facts.Pointer()
        return self.knowledge_base[facts.Pointer.UID]

    @property
    def is_processed(self): # TODO: tests
        return self.pointer.state in self.knowledge_base and isinstance(self.knowledge_base[self.pointer.state], facts.Finish)

    @property
    def current_state(self):
        if self.pointer.state is None:
            return None
        return self.knowledge_base[self.pointer.state]

    def get_start_state(self):
        return self.knowledge_base.filter(facts.Start).next()

    @property
    def next_state(self):
        if self.pointer.jump is None:
            if self.pointer.state is None:
                return self.get_start_state()
            else:
                return None

        return self.knowledge_base[self.knowledge_base[self.pointer.jump].state_to]

    def step(self):
        if self.next_state is None:
            raise exceptions.NoJumpsFromLastStateError(state=self.pointer.state)
        new_pointer = self.pointer.change(state=self.next_state.uid, jump=None)

        if not isinstance(self.next_state, facts.Finish):
            new_pointer = new_pointer.change(jump=self.get_next_jump(self.next_state).uid)

        self.knowledge_base -= self.pointer
        self.knowledge_base += new_pointer

    def can_do_step(self):
        return self.next_state is not None and all(requirement.check(self.knowledge_base) for requirement in self.next_state.require)

    def step_until_can(self):
        while self.can_do_step():
            self.step()

    def sync_pointer(self):
        if self.pointer.state is None:
            return

        new_pointer = self.pointer.change(jump=self.get_next_jump(self.knowledge_base[self.pointer.state]).uid)

        self.knowledge_base -= self.pointer
        self.knowledge_base += new_pointer

    def get_next_jump(self, state, single=True):
        jumps = self.get_available_jumps(state)
        if not jumps:
            raise exceptions.NoJumpsAvailableError(state=state)
        if single and len(jumps) > 1:
            raise exceptions.MoreThenOneJumpsAvailableError(state=state)
        return random.choice(jumps)

    def get_available_jumps(self, state):
        if isinstance(state, facts.Choice):
            defaults = [default for default in self.knowledge_base.filter(facts.ChoicePath) if default.choice == state.uid]
            return [self.knowledge_base[default.option] for default in defaults]

        return [jump
                for jump in self.knowledge_base.filter(facts.Jump)
                if jump.state_from == state.uid]

    def get_nearest_choice(self):
        current_state = self.current_state

        if current_state is None:
            current_state = self.get_start_state()

        while not isinstance(current_state, facts.Finish):

            if isinstance(current_state, facts.Choice):
                options = [option for option in self.knowledge_base.filter(facts.Option) if option.state_from == current_state.uid]
                defaults = [default for default in self.knowledge_base.filter(facts.ChoicePath) if default.choice == current_state.uid]
                return (current_state, options, defaults)

            current_state = self.knowledge_base[self.get_next_jump(current_state, single=True).state_to]

        return (None, None, None)
