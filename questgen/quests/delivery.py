# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen.facts import ( Start,
                             State,
                             Jump,
                             Finish,
                             Event,
                             Place,
                             Person,
                             LocatedIn,
                             MoveNear,
                             Choice,
                             Option,
                             Message,
                             GivePower,
                             OptionsLink,
                             QuestParticipant)


class Delivery(QuestBetween2):
    TYPE = 'delivery'
    TAGS = ('can_start', 'can_continue')

    # normal - normal quest
    # special - special quest
    # can_start - can be first quest in tree
    # can_continue - can be not first quest in tree

    @classmethod
    def construct(cls, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        antagonist = selector.new_person()
        antagonist_position = selector.place_for(objects=(antagonist.uid,))

        start = Start(uid=ns+'start',
                      type=cls.TYPE,
                      is_entry=selector.is_first_quest,
                      description=u'Начало: доставка',
                      require=[LocatedIn(object=hero.uid, place=initiator_position.uid)],
                      actions=[Message(type='intro')])

        participants = [QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        QuestParticipant(start=start.uid, participant=antagonist.uid, role=ROLES.ANTAGONIST) ]

        delivery_choice = Choice(uid=ns+'delivery_choice',
                                 description=u'Решение: доставить или украсть')


        finish_delivery = Finish(uid=ns+'finish_delivery',
                                 type='finish_delivery',
                                 result=RESULTS.SUCCESSED,
                                 description=u'Доставить посылку получателю',
                                 require=[LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                 actions=[Message(type='finish_delivery'),
                                          GivePower(object=initiator.uid, power=1),
                                          GivePower(object=receiver.uid, power=1)])

        finish_steal = Finish(uid=ns+'finish_steal',
                                 type='finish_steal',
                                 result=RESULTS.FAILED,
                                 description=u'Доставить посылку скупщику',
                                 require=[LocatedIn(object=hero.uid, place=antagonist_position.uid)],
                                 actions=[Message(type='finish_delivery'),
                                          GivePower(object=initiator.uid, power=-1),
                                          GivePower(object=receiver.uid, power=-1),
                                          GivePower(object=antagonist.uid, power=1)])

        facts = [ start,
                  delivery_choice,
                  finish_delivery,
                  finish_steal,

                  Jump(state_from=start.uid, state_to=delivery_choice.uid),

                  Option(state_from=delivery_choice.uid, state_to=finish_delivery.uid, type='delivery', start_actions=[Message(type='start_delivery'),]),
                  Option(state_from=delivery_choice.uid, state_to=finish_steal.uid, type='steal', start_actions=[Message(type='start_steal'),])
                ]

        facts.extend(participants)

        return facts
