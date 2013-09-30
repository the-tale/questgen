# coding: utf-8
import random

from questgen.quests.base_quest import QuestBetween2, ROLES
from questgen.facts import ( Start,
                             State,
                             Jump,
                             Finish,
                             Event,
                             Place,
                             Person,
                             LocatedIn,
                             LocatedNear,
                             Choice,
                             Option,
                             Message,
                             GivePower,
                             Fight,
                             OptionsLink,
                             QuestParticipant)


class Hunt(QuestBetween2):
    TYPE = 'hunt'
    TAGS = ('can_start', )
    HUNT_LOOPS = (2, 4)

    @classmethod
    def get_mob(cls, knowledge_base, selector):
        return knowledge_base[knowledge_base[selector.preferences_mob()].mob]

    @classmethod
    def construct_from_place(cls, knowledge_base, selector, start_place):

        mob = cls.get_mob(knowledge_base, selector)

        return cls.construct(knowledge_base,
                             selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=None,
                             receiver_position=selector.new_place(terrains=mob.terrains))


    @classmethod
    def construct(cls, knowledge_base, selector, initiator, initiator_position, receiver, receiver_position):

        mob = cls.get_mob(knowledge_base, selector)

        hero_uid = selector.heroes()[0]

        ns = knowledge_base.get_next_ns()

        start = Start(uid=ns+'start',
                      type=cls.TYPE,
                      description=u'Начало: задание на охоту',
                      require=[LocatedIn(object=hero_uid, place=initiator_position)],
                      actions=[Message(id='intro')])

        participants = [QuestParticipant(start=start.uid, participant=receiver_position, role=ROLES.RECEIVER_POSITION) ]

        start_hunting = State(uid=ns+'start_hunting',
                              description=u'Прибытие в город охоты',
                              require=[LocatedIn(object=hero_uid, place=receiver_position)],
                              actions=[LocatedNear(object=hero_uid, place=receiver_position)])

        hunt_loop = []

        for i in xrange(random.randint(*cls.HUNT_LOOPS)):

            hunt = State(uid=ns+'hunt_%d' % i,
                         description=u'Охота',
                         require=[LocatedNear(object=hero_uid, place=receiver_position)],
                         actions=[LocatedNear(object=hero_uid, place=receiver_position)])

            fight = State(uid=ns+'fight_%d' % i,
                          description=u'Сражение с жертвой',
                          actions=[Message(id='fight'),
                                   Fight(uid='fight_%d' % i, mob=mob.uid)])

            if hunt_loop:
                hunt_loop.append(Jump(state_from=hunt_loop[-1].uid, state_to=hunt.uid, start_actions=[Message(id='start_track'),]))

            hunt_loop.extend([hunt,
                              Jump(state_from=hunt.uid, state_to=fight.uid),
                              fight])

        sell_prey = Finish(uid=ns+'sell_prey',
                           type='sell_prey',
                           description=u'Продать добычу',
                           require=[LocatedIn(object=hero_uid, place=receiver_position)],
                           actions=[Message(id='sell_prey'),
                                    GivePower(object=receiver_position, power=1)])

        facts = [ start,
                  start_hunting,
                  sell_prey,

                  Jump(state_from=start.uid, state_to=start_hunting.uid, start_actions=[Message(id='move_to_hunt'),]),
                  Jump(state_from=start_hunting.uid, state_to=hunt_loop[0].uid, start_actions=[Message(id='start_track'),]),
                  Jump(state_from=hunt_loop[-1].uid, state_to=sell_prey.uid, start_actions=[Message(id='return_with_prey'),]),
                ]

        facts.extend(hunt_loop)
        facts.extend(participants)

        return facts
