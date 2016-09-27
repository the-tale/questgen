# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import requirements
from questgen import actions


class Simplest(QuestBetween2):
    TYPE = 'simplest'
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
                             receiver_position=selector.new_place())


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Начало: простейшее задание',
                            require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        arriving = facts.State(uid=ns+'arriving',
                               description='Прибытие в другой город',
                               require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        facts.State(uid=ns+'any_action',
                    description='выполнить какое-то действие',
                    actions=[actions.Message(type='do smth')])

        finish = facts.Finish(uid=ns+'finish',
                              start=start.uid,
                              results={ receiver_position.uid: RESULTS.SUCCESSED},
                              nesting=nesting,
                              description='завершить задание',
                              actions=[actions.GiveReward(object=hero.uid, type='finish')])

        line = [ start,
                 facts.Jump(state_from=start.uid, state_to=arriving.uid),
                 arriving,
                 facts.Jump(state_from=arriving.uid, state_to=finish.uid),
                 finish  ]

        line.extend(participants)

        return line
