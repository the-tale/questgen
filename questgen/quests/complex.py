# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts


class Complex(QuestBetween2):
    TYPE = 'complex'
    TAGS = ('can_start', )

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
                            description=u'Начало: «сложное» задание',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        arriving = facts.Choice(uid=ns+'arriving',
                                description=u'Заплатить пошлину при прибытии в город или махнуть через стену',
                                require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        tax = facts.Question(uid=ns+'tax',
                             description=u'Хватит ли у героя денег на пошлину',
                             condition=(facts.HasMoney(object=hero.uid, money=100500),),
                             actions=[facts.Message(type='tax_officer_conversation')])

        finish_not_paid = facts.Finish(uid=ns+'finish_not_paid',
                                       start=start.uid,
                                       results={ receiver_position.uid: RESULTS.FAILED},
                                       nesting=nesting,
                                       description=u'завершить задание',
                                       actions=[facts.GiveReward(object=hero.uid, type='finish'),
                                                facts.GivePower(object=receiver_position.uid, power=-1)])

        finish_paid = facts.Finish(uid=ns+'finish_paid',
                                   start=start.uid,
                                   results={ receiver_position.uid: RESULTS.SUCCESSED},
                                   nesting=nesting,
                                   description=u'завершить задание',
                                   actions=[facts.GiveReward(object=hero.uid, type='finish'),
                                            facts.GivePower(object=receiver_position.uid, power=1)])

        line = [ start,
                 arriving,
                 tax,
                 finish_not_paid,
                 finish_paid,

                 facts.Jump(state_from=start.uid, state_to=arriving.uid),
                 facts.Option(state_from=arriving.uid, state_to=finish_not_paid.uid, type='not_paid'),
                 facts.Option(state_from=arriving.uid, state_to=tax.uid, type='pay_tax'),
                 facts.Answer(state_from=tax.uid, state_to=finish_paid.uid, condition=True),
                 facts.Answer(state_from=tax.uid, state_to=finish_not_paid.uid, condition=False) ]

        line.extend(participants)

        return line
