# coding: utf-8


from questgen.quests.base_quest import QuestBetween2, ROLES
from questgen import facts
from questgen.relations import PROFESSION


class SearchSmith(QuestBetween2):
    TYPE = 'search_smith'
    TAGS = ('can_start', )

    @classmethod
    def get_hometown(cls, knowledge_base, selector):
        return knowledge_base[knowledge_base[selector.preferences_hometown()].place]

    @classmethod
    def construct_from_place(cls, knowledge_base, selector, start_place):

        receiver = selector.new_person(professions=(PROFESSION.BLACKSMITH,))
        receiver_position = selector.place_for(objects=(receiver,))

        return cls.construct(knowledge_base,
                             selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=receiver,
                             receiver_position=receiver_position)


    @classmethod
    def construct(cls, knowledge_base, selector, initiator, initiator_position, receiver, receiver_position):

        hero_uid = selector.heroes()[0]

        ns = knowledge_base.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            description=u'Начало: посещение кузнеца',
                            require=[facts.LocatedIn(object=hero_uid, place=initiator_position)],
                            actions=[facts.Message(id='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver, role=ROLES.RECEIVER) ]

        arriving = facts.State(uid=ns+'arriving',
                               description=u'Прибытие в город',
                               require=[facts.LocatedIn(object=hero_uid, place=receiver_position)])

        upgrade = facts.State(uid=ns+'upgrade',
                               description=u'Обновление экипировки',
                               actions=[facts.UpgradeEquipment()])

        finish = facts.Finish(uid=ns+'finish',
                              type='finish',
                              description=u'завершить задание',
                              actions=[facts.Message(id='finish'),
                                       facts.GivePower(object=receiver_position, power=1)])

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
