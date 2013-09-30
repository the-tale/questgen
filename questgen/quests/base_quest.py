# coding: utf-8

class ROLES(object):
    INITIATOR = 'initiator'
    INITIATOR_POSITION = 'initiator_position'
    RECEIVER = 'receiver'
    RECEIVER_POSITION = 'receiver_position'


class BaseQuest(object):
    TYPE = None
    TAGS = ()


class QuestBetween2(BaseQuest):

    @classmethod
    def construct_from_nothing(cls, knowledge_base, selector):
        return cls.construct_from_place(knowledge_base, selector, selector.new_place())

    @classmethod
    def construct_from_place(cls, knowledge_base, selector, start_place):
        return cls.construct_between_2(knowledge_base,
                                       selector,
                                       initiator=selector.person_from(places=(start_place, )),
                                       receiver=selector.new_person())

    @classmethod
    def construct_from_person(cls, knowledge_base, selector, initiator):
        return cls.construct_between_2(knowledge_base, selector, initiator, receiver=selector.new_person())

    @classmethod
    def construct_between_2(cls, knowledge_base, selector, initiator, receiver):
        return cls.construct( knowledge_base,
                              selector,
                              initiator=initiator,
                              initiator_position=selector.place_for(objects=(initiator,)),
                              receiver=receiver,
                              receiver_position=selector.place_for(objects=(receiver,)))

    @classmethod
    def construct(cls, knowledge_base, selector, initiator, initiator_position, receiver, receiver_position):
        raise NotImplementedError
