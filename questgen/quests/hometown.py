# coding: utf-8
import random

from questgen.quests.base_quest import QuestBetween2, ROLES
from questgen import facts


class Hometown(QuestBetween2):
    TYPE = 'hometown'
    TAGS = ('can_start', )

    @classmethod
    def get_hometown(cls, knowledge_base, selector):
        return knowledge_base[knowledge_base[selector.preferences_hometown()].place]

    @classmethod
    def construct_from_place(cls, knowledge_base, selector, start_place):

        hometown = cls.get_hometown(knowledge_base, selector)

        return cls.construct(knowledge_base,
                             selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=None,
                             receiver_position=selector.new_place(candidates=(hometown.uid, )))


    @classmethod
    def construct(cls, knowledge_base, selector, initiator, initiator_position, receiver, receiver_position):

        hero_uid = selector.heroes()[0]

        ns = knowledge_base.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            description=u'Начало: посетить родной города',
                            require=[facts.LocatedIn(object=hero_uid, place=initiator_position)],
                            actions=[facts.Message(id='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver_position, role=ROLES.RECEIVER_POSITION) ]

        arriving = facts.State(uid=ns+'arriving',
                               description=u'Прибытие в город',
                               require=[facts.LocatedIn(object=hero_uid, place=receiver_position)])

        action_choices = [facts.State(uid=ns+'drunk_song', description=u'спеть пьяную песню', actions=[facts.Message(id='drunk_song'),
                                                                                                       facts.DoNothing(type='drunk_song')]),
                          facts.State(uid=ns+'stagger_streets', description=u'пошататься по улицам', actions=[facts.Message(id='stagger_streets'),
                                                                                                              facts.DoNothing(type='stagger_streets')]),
                          facts.State(uid=ns+'chatting', description=u'пообщаться с друзьями', actions=[facts.Message(id='chatting'),
                                                                                                        facts.DoNothing(type='chatting')]),
                          facts.State(uid=ns+'search_old_friends', description=u'искать старого друга', actions=[facts.Message(id='search_old_friends'),
                                                                                                                 facts.DoNothing(type='search_old_friends')]),
                          facts.State(uid=ns+'remember_names', description=u'вспоминать имена друзей', actions=[facts.Message(id='remember_names'),
                                                                                                                facts.DoNothing(type='remember_names')])]

        actions = random.sample(action_choices, 3)

        finish = facts.Finish(uid=ns+'finish',
                              type='finish',
                              description=u'завершить посещение города',
                              actions=[facts.Message(id='finish'),
                                       facts.GivePower(object=receiver_position, power=1)])

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
