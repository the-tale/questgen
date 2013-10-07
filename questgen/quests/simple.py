# coding: utf-8


from questgen.quests.base_quest import QuestBetween2, RESULTS
from questgen import facts


class Simple(QuestBetween2):
    TYPE = 'simple'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def construct(cls, selector, initiator, initiator_position, receiver, receiver_position):

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            is_entry=selector.is_first_quest,
                            description=u'Начало: самый простой квест')

        finish_successed = facts.Finish(uid=ns+'finish_successed',
                                        result=RESULTS.SUCCESSED,
                                        description=u'завершить задание удачно')

        finish_failed = facts.Finish(uid=ns+'finish_failed',
                                     result=RESULTS.FAILED,
                                     description=u'завершить задание плохо')

        event = facts.Event(uid=ns+'event', members=(finish_successed.uid, finish_failed.uid))

        line = [ start,
                 finish_successed,
                 finish_failed,
                 event,
                 facts.Jump(state_from=start.uid, state_to=finish_successed.uid),
                 facts.Jump(state_from=start.uid, state_to=finish_failed.uid) ]

        return line
