# coding: utf-8


from questgen.quests.base_quest import QuestBetween2, RESULTS, ROLES
from questgen import facts


class Simple(QuestBetween2):
    TYPE = 'simple'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def find_receiver(cls, selector, initiator):
        return selector.new_person()


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Начало: самый простой квест')

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=initiator_position.uid, role=ROLES.INITIATOR_POSITION),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        finish_successed = facts.Finish(uid=ns+'finish_successed',
                                        start=start.uid,
                                        results={initiator.uid: RESULTS.SUCCESSED,
                                                 initiator_position.uid: RESULTS.SUCCESSED,
                                                 receiver.uid: RESULTS.SUCCESSED,
                                                 receiver_position.uid: RESULTS.SUCCESSED},
                                        nesting=nesting,
                                        description='завершить задание удачно')

        finish_failed = facts.Finish(uid=ns+'finish_failed',
                                     start=start.uid,
                                     results={initiator.uid: RESULTS.FAILED,
                                              initiator_position.uid: RESULTS.FAILED,
                                              receiver.uid: RESULTS.FAILED,
                                              receiver_position.uid: RESULTS.FAILED},
                                     nesting=nesting,
                                     description='завершить задание плохо')

        event = facts.Event(uid=ns+'event', members=(finish_successed.uid, finish_failed.uid))

        line = [ start,
                 finish_successed,
                 finish_failed,
                 event,
                 facts.Jump(state_from=start.uid, state_to=finish_successed.uid),
                 facts.Jump(state_from=start.uid, state_to=finish_failed.uid) ]

        line.extend(participants)

        return line
