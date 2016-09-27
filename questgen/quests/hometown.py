# coding: utf-8
import random

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import requirements
from questgen import actions


class Hometown(QuestBetween2):
    TYPE = 'hometown'
    TAGS = ('can_start', )

    @classmethod
    def get_hometown(cls, selector):
        return selector._kb[selector.preferences_hometown().place]

    @classmethod
    def find_receiver(cls, selector, initiator):
        return None

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):

        hometown = cls.get_hometown(selector)

        return cls.construct(nesting=nesting,
                             selector=selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=None,
                             receiver_position=selector.new_place(candidates=(hometown.uid, )))


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Начало: посетить родной города',
                            require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        arriving = facts.State(uid=ns+'arriving',
                               description='Прибытие в город',
                               require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        action_choices = [facts.State(uid=ns+'drunk_song', description='спеть пьяную песню', actions=[actions.Message(type='drunk_song'),
                                                                                                       actions.DoNothing(type='drunk_song')]),
                          facts.State(uid=ns+'stagger_streets', description='пошататься по улицам', actions=[actions.Message(type='stagger_streets'),
                                                                                                              actions.DoNothing(type='stagger_streets')]),
                          facts.State(uid=ns+'chatting', description='пообщаться с друзьями', actions=[actions.Message(type='chatting'),
                                                                                                        actions.DoNothing(type='chatting')]),
                          facts.State(uid=ns+'search_old_friends', description='искать старого друга', actions=[actions.Message(type='search_old_friends'),
                                                                                                                 actions.DoNothing(type='search_old_friends')]),
                          facts.State(uid=ns+'remember_names', description='вспоминать имена друзей', actions=[actions.Message(type='remember_names'),
                                                                                                                actions.DoNothing(type='remember_names')])]

        home_actions = random.sample(action_choices, 3)

        finish = facts.Finish(uid=ns+'finish',
                              start=start.uid,
                              results={ receiver_position.uid: RESULTS.SUCCESSED},
                              nesting=nesting,
                              description='завершить посещение города',
                              actions=[actions.GiveReward(object=hero.uid, type='finish')])

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=arriving.uid),

                 arriving,

                 facts.Jump(state_from=arriving.uid, state_to=home_actions[0].uid),
                 facts.Jump(state_from=home_actions[0].uid, state_to=home_actions[1].uid),
                 facts.Jump(state_from=home_actions[1].uid, state_to=home_actions[2].uid),
                 facts.Jump(state_from=home_actions[2].uid, state_to=finish.uid),

                 finish
               ]

        line.extend(home_actions)
        line.extend(participants)

        return line
