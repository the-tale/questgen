# coding: utf-8
import random

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import requirements
from questgen import actions
from questgen import relations


class Pilgrimage(QuestBetween2):
    TYPE = 'pilgrimage'
    TAGS = ('can_start', )

    @classmethod
    def find_receiver(cls, selector, initiator):
        return None

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):

        return cls.construct(nesting=nesting,
                             selector=selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=None,
                             receiver_position=selector.new_place(types=[relations.PLACE_TYPE.HOLY_CITY]))


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Начало: посетить святой город',
                            require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        arriving = facts.State(uid=ns+'arriving',
                               description='Прибытие в город',
                               require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        action_choices = [facts.State(uid=ns+'speak_with_guru', description='поговорить с гуру', actions=[actions.Message(type='speak_with_guru'),
                                                                                                           actions.DoNothing(type='speak_with_guru')]),
                          facts.State(uid=ns+'stagger_holy_streets', description='пошататься по улицам', actions=[actions.Message(type='stagger_holy_streets'),
                                                                                                                   actions.DoNothing(type='stagger_holy_streets')])]

        holy_actions = random.sample(action_choices, 1)

        finish = facts.Finish(uid=ns+'finish',
                              start=start.uid,
                              results={ receiver_position.uid: RESULTS.SUCCESSED},
                              nesting=nesting,
                              description='завершить посещение города',
                              actions=[actions.GiveReward(object=hero.uid, type='finish')])

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=arriving.uid),

                 arriving,

                 facts.Jump(state_from=arriving.uid, state_to=holy_actions[0].uid),
                 facts.Jump(state_from=holy_actions[0].uid, state_to=finish.uid),

                 finish
               ]

        line.extend(holy_actions)
        line.extend(participants)

        return line
