# coding: utf-8
import random

from collections import Iterable

from questgen import exceptions
from questgen.quests.base_quest import BaseQuest



class QuestsBase(object):

    def __init__(self):
        self._quests = {}

    def quests(self): return self._quests.itervalues()

    def __iadd__(self, quest, expected_quest=False):
        if isinstance(quest, Iterable) and not expected_quest:
            map(lambda element: self.__iadd__(element, expected_quest=True), quest)
        elif issubclass(quest, BaseQuest):
            if quest.TYPE in self._quests:
                raise exceptions.DuplicatedQuestError(quest=quest)
            self._quests[quest.TYPE] = quest
        else:
            raise exceptions.WrongQuestTypeError(quest=quest)

        return self

    def _available_quests(self, excluded=None, allowed=None, tags=None):

        quests = self._quests.itervalues()

        if excluded is not None:
            quests = (quest for quest in quests if quest.TYPE not in excluded)

        if allowed is not None:
            quests = (quest for quest in quests if quest.TYPE in allowed)


        if tags is not None:
            for tag in tags:
                quests = (quest for quest in quests if tag in quest.TAGS)

        return quests

    def _quests_by_method(self, method_name, **kwargs):
        return (quest for quest in self._available_quests(**kwargs)
                if hasattr(quest, method_name))

    def _quests__from_place(self, **kwargs):
        return self._quests_by_method(method_name='construct_from_place', **kwargs)

    def _quests__from_person(self, **kwargs):
        return self._quests_by_method(method_name='construct_from_person', **kwargs)

    def create_quest_from_place(self, selector, start_place, excluded=None, allowed=None, tags=None):
        choices = list(self._quests__from_place(excluded=excluded, allowed=allowed, tags=tags))

        if not choices:
            raise exceptions.NoQuestChoicesRollBackError()

        quest_class = random.choice(choices)

        return quest_class.construct_from_place(selector=selector, start_place=start_place)

    def create_quest_from_person(self, selector, initiator, excluded=None, allowed=None, tags=None):
        choices = list(self._quests__from_person(excluded=excluded, allowed=allowed, tags=tags))

        if not choices:
            raise exceptions.NoQuestChoicesRollBackError()

        quest_class = random.choice(choices)

        return quest_class.construct_from_person(selector, initiator=initiator)
