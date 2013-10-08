# coding: utf-8
import random

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts


class Hometown(QuestBetween2):
    TYPE = 'hometown'
    TAGS = ('can_start', )

    @classmethod
    def get_hometown(cls, selector):
        return selector._kb[selector.preferences_hometown().place]

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
                            description=u'Начало: посетить родной города',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        arriving = facts.State(uid=ns+'arriving',
                               description=u'Прибытие в город',
                               require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        action_choices = [facts.State(uid=ns+'drunk_song', description=u'спеть пьяную песню', actions=[facts.Message(type='drunk_song'),
                                                                                                       facts.DoNothing(type='drunk_song')]),
                          facts.State(uid=ns+'stagger_streets', description=u'пошататься по улицам', actions=[facts.Message(type='stagger_streets'),
                                                                                                              facts.DoNothing(type='stagger_streets')]),
                          facts.State(uid=ns+'chatting', description=u'пообщаться с друзьями', actions=[facts.Message(type='chatting'),
                                                                                                        facts.DoNothing(type='chatting')]),
                          facts.State(uid=ns+'search_old_friends', description=u'искать старого друга', actions=[facts.Message(type='search_old_friends'),
                                                                                                                 facts.DoNothing(type='search_old_friends')]),
                          facts.State(uid=ns+'remember_names', description=u'вспоминать имена друзей', actions=[facts.Message(type='remember_names'),
                                                                                                                facts.DoNothing(type='remember_names')])]

        actions = random.sample(action_choices, 3)

        finish = facts.Finish(uid=ns+'finish',
                              result=RESULTS.SUCCESSED,
                              nesting=nesting,
                              description=u'завершить посещение города',
                              actions=[facts.GiveReward(object=hero.uid, type='finish'),
                                       facts.GivePower(object=receiver_position.uid, power=1)])

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=arriving.uid),

                 arriving,

                 facts.Jump(state_from=arriving.uid, state_to=actions[0].uid),
                 facts.Jump(state_from=actions[0].uid, state_to=actions[1].uid),
                 facts.Jump(state_from=actions[1].uid, state_to=actions[2].uid),
                 facts.Jump(state_from=actions[2].uid, state_to=finish.uid),

                 finish
               ]

        line.extend(actions)
        line.extend(participants)

        return line
