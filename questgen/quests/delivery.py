# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts


class Delivery(QuestBetween2):
    TYPE = 'delivery'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        antagonist = selector.new_person(first_initiator=False)
        antagonist_position = selector.place_for(objects=(antagonist.uid,))

        start = facts.Start(uid=ns+'start',
                      type=cls.TYPE,
                      nesting=nesting,
                      description=u'Начало: доставка',
                      require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                      actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        facts.QuestParticipant(start=start.uid, participant=antagonist.uid, role=ROLES.ANTAGONIST) ]

        delivery_choice = facts.Choice(uid=ns+'delivery_choice',
                                 description=u'Решение: доставить или украсть')


        finish_delivery = facts.Finish(uid=ns+'finish_delivery',
                                       start=start.uid,
                                       results={ initiator.uid: RESULTS.SUCCESSED,
                                                 receiver.uid: RESULTS.SUCCESSED,
                                                 antagonist.uid: RESULTS.NEUTRAL},
                                       nesting=nesting,
                                       description=u'Доставить посылку получателю',
                                       require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                       actions=[facts.GiveReward(object=hero.uid, type='finish_delivery'),
                                                facts.GivePower(object=initiator.uid, power=1),
                                                facts.GivePower(object=receiver.uid, power=1)])

        finish_steal = facts.Finish(uid=ns+'finish_steal',
                                    start=start.uid,
                                    results={ initiator.uid: RESULTS.FAILED,
                                              receiver.uid: RESULTS.FAILED,
                                              antagonist.uid: RESULTS.SUCCESSED},
                                    nesting=nesting,
                                    description=u'Доставить посылку скупщику',
                                    require=[facts.LocatedIn(object=hero.uid, place=antagonist_position.uid)],
                                    actions=[facts.GiveReward(object=hero.uid, type='finish_steal', scale=1.5),
                                             facts.GivePower(object=initiator.uid, power=-1),
                                             facts.GivePower(object=receiver.uid, power=-1),
                                             facts.GivePower(object=antagonist.uid, power=1)])

        line = [ start,
                  delivery_choice,
                  finish_delivery,
                  finish_steal,

                  facts.Jump(state_from=start.uid, state_to=delivery_choice.uid),

                  facts.Option(state_from=delivery_choice.uid, state_to=finish_delivery.uid, type='delivery', start_actions=[facts.Message(type='start_delivery'),]),
                  facts.Option(state_from=delivery_choice.uid, state_to=finish_steal.uid, type='steal', start_actions=[facts.Message(type='start_steal'),])
                ]

        line.extend(participants)

        return line
