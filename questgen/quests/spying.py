# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import requirements
from questgen import actions


class Spying(QuestBetween2):
    TYPE = 'spying'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                      type=cls.TYPE,
                      nesting=nesting,
                      description=u'Начало: задание на шпионаж',
                      require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid),
                               requirements.LocatedIn(object=receiver.uid, place=receiver_position.uid)],
                      actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        start_spying = facts.Choice(uid=ns+'start_spying',
                              description=u'Прибытие в город цели',
                              require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                              actions=[actions.Message(type='arrived_to_target')])


        spying_middle = facts.Choice(uid=ns+'spying_middle',
                               description=u'Шпионаж',
                               actions=[actions.MoveNear(object=hero.uid, place=receiver_position.uid)])

        continue_spying = facts.State(uid=ns+'continue_spying',
                                description=u'Продолжить шпионаж',
                                require=[requirements.LocatedNear(object=hero.uid, place=receiver_position.uid)],
                                actions=[actions.MoveNear(object=hero.uid, place=receiver_position.uid),
                                         actions.Message(type='continue_spying')])

        open_up = facts.State(uid=ns+'open_up',
                        description=u'Раскрыться',
                        require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                        actions=[actions.Message(type='open_up')])


        report_data = facts.Finish(uid=ns+'report_data',
                                   start=start.uid,
                                   results={initiator.uid: RESULTS.SUCCESSED,
                                            receiver.uid: RESULTS.FAILED},
                                   nesting=nesting,
                                   description=u'Сообщить сообранную информацию',
                                   require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                   actions=[actions.GiveReward(object=hero.uid, type='report_data'),
                                            actions.GivePower(object=initiator.uid, power=1),
                                            actions.GivePower(object=receiver.uid, power=-1)])

        open_up_finish = facts.Finish(uid=ns+'open_up_finish',
                                      start=start.uid,
                                      results={initiator.uid: RESULTS.FAILED,
                                               receiver.uid: RESULTS.SUCCESSED},
                                      nesting=nesting,
                                      description=u'Завершить задание и остатсья в городе цели',
                                      require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                      actions=[actions.GiveReward(object=hero.uid, type='open_up_finish'),
                                               actions.GivePower(object=initiator.uid, power=-1),
                                               actions.GivePower(object=receiver.uid, power=1)])

        open_up_lying = facts.Finish(uid=ns+'open_up_lying',
                                     start=start.uid,
                                     results={initiator.uid: RESULTS.FAILED,
                                              receiver.uid: RESULTS.SUCCESSED},
                                     nesting=nesting,
                                     description=u'Вернуться к заказчику и сообщить ложную информацию',
                                     require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                     actions=[actions.GiveReward(object=hero.uid, type='open_up_lying', scale=1.5),
                                              actions.GivePower(object=initiator.uid, power=-1.5),
                                              actions.GivePower(object=receiver.uid, power=1.5)])

        start_spying__spying_middle = facts.Option(state_from=start_spying.uid, state_to=spying_middle.uid, type='spy', start_actions=[actions.Message(type='start_spying'),])
        start_spying__open_up = facts.Option(state_from=start_spying.uid, state_to=open_up.uid, type='open_up', start_actions=[actions.Message(type='start_open_up'),])

        spying_middle__continue_spying = facts.Option(state_from=spying_middle.uid, state_to=continue_spying.uid, type='spy')
        spying_middle__open_up = facts.Option(state_from=spying_middle.uid, state_to=open_up.uid, type='open_up', start_actions=[actions.Message(type='start_open_up'),])


        line = [ start,
                  start_spying,
                  spying_middle,
                  continue_spying,
                  open_up,
                  report_data,
                  open_up_finish,
                  open_up_lying,

                  facts.Jump(state_from=start.uid, state_to=start_spying.uid),

                  start_spying__spying_middle,
                  start_spying__open_up,

                  spying_middle__continue_spying,
                  spying_middle__open_up,

                  facts.Jump(state_from=continue_spying.uid, state_to=report_data.uid, start_actions=[actions.Message(type='move_to_report_data'),]),

                  facts.Jump(state_from=open_up.uid, state_to=open_up_finish.uid),
                  facts.Jump(state_from=open_up.uid, state_to=open_up_lying.uid, start_actions=[actions.Message(type='move_to_report_lie'),]),

                  facts.OptionsLink(options=(start_spying__spying_middle.uid, spying_middle__continue_spying.uid)),

                  facts.Event(uid=ns+'open_up_variants', description=u'Варианты окончания раскрытия', members=(open_up_finish.uid, open_up_lying.uid))
                ]

        line.extend(participants)

        return line
