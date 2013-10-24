# coding: utf-8


from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen.relations import PROFESSION


class SearchSmith(QuestBetween2):
    TYPE = 'search_smith'
    TAGS = ('can_start', )

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):

        receiver = selector.new_person(first_initiator=False, professions=(PROFESSION.BLACKSMITH,))
        receiver_position = selector.place_for(objects=(receiver.uid,))

        return cls.construct(nesting=nesting,
                             selector=selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=receiver,
                             receiver_position=receiver_position)


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description=u'Начало: посещение кузнеца',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        arriving = facts.State(uid=ns+'arriving',
                               description=u'Прибытие в город',
                               require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        upgrade = facts.State(uid=ns+'upgrade',
                               description=u'Обновление экипировки',
                               actions=[facts.UpgradeEquipment()])

        finish = facts.Finish(uid=ns+'finish',
                              result=RESULTS.SUCCESSED,
                              nesting=nesting,
                              description=u'завершить задание',
                              actions=[facts.GivePower(object=receiver.uid, power=1)])

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=arriving.uid),

                 arriving,

                 facts.Jump(state_from=arriving.uid, state_to=upgrade.uid),

                 upgrade,

                 facts.Jump(state_from=upgrade.uid, state_to=finish.uid),

                 finish
               ]

        line.extend(participants)

        return line
