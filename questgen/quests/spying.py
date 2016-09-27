# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import requirements
from questgen import actions
from questgen import relations


class Spying(QuestBetween2):
    TYPE = 'spying'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def find_receiver(cls, selector, initiator):
        return selector.new_person(restrict_social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.PARTNER),),
                                   social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.CONCURRENT),))


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                      type=cls.TYPE,
                      nesting=nesting,
                      description='Начало: задание на шпионаж',
                      require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid),
                               requirements.LocatedIn(object=receiver.uid, place=receiver_position.uid)],
                      actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        start_spying = facts.Choice(uid=ns+'start_spying',
                              description='Прибытие в город цели',
                              require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                              actions=[actions.Message(type='arrived_to_target')])


        spying_middle = facts.Choice(uid=ns+'spying_middle',
                               description='Шпионаж',
                               actions=[actions.MoveNear(object=hero.uid, place=receiver_position.uid)])

        continue_spying = facts.State(uid=ns+'continue_spying',
                                      description='Продолжить шпионаж')

        success_spying = facts.State(uid=ns+'success_spying',
                                description='шпионим без происшествий',
                                require=[requirements.LocatedNear(object=hero.uid, place=receiver_position.uid)],
                                actions=[actions.Message(type='success_spying'),
                                         actions.MoveNear(object=hero.uid, place=receiver_position.uid)])

        witness = facts.State(uid=ns+'witness',
                              description='героя заметил один из работников цели',
                              require=[requirements.LocatedNear(object=hero.uid, place=receiver_position.uid)],
                              actions=[actions.Message(type='witness'),
                                       actions.MoveNear(object=hero.uid, place=receiver_position.uid)  ])

        witness_fight = facts.Question(uid=ns+'witness_fight',
                                       description='удалось ли победить свидетеля?',
                                       condition=[requirements.IsAlive(object=hero.uid)],
                                       actions=[actions.Message(type='witness_fight'),
                                                actions.Fight(mercenary=True)])

        open_up = facts.State(uid=ns+'open_up',
                        description='Раскрыться',
                        require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                        actions=[actions.Message(type='open_up')])


        report_data = facts.Finish(uid=ns+'report_data',
                                   start=start.uid,
                                   results={initiator.uid: RESULTS.SUCCESSED,
                                            receiver.uid: RESULTS.FAILED},
                                   nesting=nesting,
                                   description='Сообщить сообранную информацию',
                                   require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                   actions=[actions.GiveReward(object=hero.uid, type='report_data')])

        finish_spying_choice = facts.Choice(uid=ns+'finish_spying_choice',
                                            description='Варианты выбора завершения шпионажа')

        blackmail_finish = facts.Finish(uid=ns+'blackmail_finish',
                                        start=start.uid,
                                        results={initiator.uid: RESULTS.NEUTRAL,
                                                 receiver.uid: RESULTS.FAILED},
                                        nesting=nesting,
                                        description='Шантажировать самостоятельно',
                                        require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                        actions=[actions.GiveReward(object=hero.uid, type='blackmail_finish', scale=1.25)])

        witness_failed = facts.Finish(uid=ns+'witness_failed',
                                      start=start.uid,
                                      results={initiator.uid: RESULTS.NEUTRAL,
                                               receiver.uid: RESULTS.NEUTRAL},
                                      nesting=nesting,
                                      description='свидетель смог скрыться',
                                      actions=[actions.Message(type='witness_failed') ])

        open_up_finish = facts.Finish(uid=ns+'open_up_finish',
                                      start=start.uid,
                                      results={initiator.uid: RESULTS.FAILED,
                                               receiver.uid: RESULTS.SUCCESSED},
                                      nesting=nesting,
                                      description='Завершить задание и остатсья в городе цели',
                                      require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                      actions=[actions.GiveReward(object=hero.uid, type='open_up_finish')])

        open_up_lying = facts.Finish(uid=ns+'open_up_lying',
                                     start=start.uid,
                                     results={initiator.uid: RESULTS.FAILED,
                                              receiver.uid: RESULTS.SUCCESSED},
                                     nesting=nesting,
                                     description='Вернуться к заказчику и сообщить ложную информацию',
                                     require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                     actions=[actions.GiveReward(object=hero.uid, type='open_up_lying', scale=1.5)])

        start_spying__spying_middle = facts.Option(state_from=start_spying.uid, state_to=spying_middle.uid, type='spy',
                                                   markers=[relations.OPTION_MARKERS.HONORABLE], start_actions=[actions.Message(type='start_spying'),])
        start_spying__spying_middle__blackmail = facts.Option(state_from=start_spying.uid,
                                                              state_to=spying_middle.uid,
                                                              type='blackmail',
                                                              markers=[relations.OPTION_MARKERS.DISHONORABLE],
                                                              start_actions=[actions.Message(type='start_spying'),])
        start_spying__open_up = facts.Option(state_from=start_spying.uid, state_to=open_up.uid, type='open_up',
                                             markers=[relations.OPTION_MARKERS.DISHONORABLE], start_actions=[actions.Message(type='start_open_up'),])

        spying_middle__continue_spying = facts.Option(state_from=spying_middle.uid, state_to=continue_spying.uid, type='spy',
                                                      markers=[relations.OPTION_MARKERS.HONORABLE])
        spying_middle__continue_spying__blackmail = facts.Option(state_from=spying_middle.uid, state_to=continue_spying.uid, type='blackmail',
                                                                 markers=[relations.OPTION_MARKERS.DISHONORABLE])
        spying_middle__open_up = facts.Option(state_from=spying_middle.uid, state_to=open_up.uid, type='open_up',
                                              markers=[relations.OPTION_MARKERS.DISHONORABLE], start_actions=[actions.Message(type='start_open_up'),])

        finish_spying__report_data = facts.Option(state_from=finish_spying_choice.uid,
                                                  state_to=report_data.uid,
                                                  type='spy',
                                                  markers=[relations.OPTION_MARKERS.HONORABLE],
                                                  start_actions=[actions.Message(type='go_report_data')])
        finish_spying__blackmail = facts.Option(state_from=finish_spying_choice.uid,
                                                state_to=blackmail_finish.uid,
                                                type='blackmail',
                                                markers=[relations.OPTION_MARKERS.DISHONORABLE],
                                                start_actions=[actions.Message(type='go_blackmail')])


        line = [ start,
                  start_spying,
                  spying_middle,
                  success_spying,
                  continue_spying,
                  open_up,
                  report_data,
                  open_up_finish,
                  open_up_lying,
                  witness,
                  witness_fight,
                  witness_failed,
                  finish_spying_choice,
                  blackmail_finish,

                  facts.Jump(state_from=start.uid, state_to=start_spying.uid),

                  facts.Jump(state_from=continue_spying.uid, state_to=success_spying.uid),
                  facts.Jump(state_from=continue_spying.uid, state_to=witness.uid),

                  start_spying__spying_middle,
                  start_spying__spying_middle__blackmail,
                  start_spying__open_up,

                  spying_middle__continue_spying,
                  spying_middle__continue_spying__blackmail,
                  spying_middle__open_up,

                  finish_spying__report_data,
                  finish_spying__blackmail,

                  facts.Jump(state_from=success_spying.uid, state_to=finish_spying_choice.uid),

                  facts.Jump(state_from=witness.uid, state_to=witness_fight.uid),

                  facts.Jump(state_from=open_up.uid, state_to=open_up_finish.uid),
                  facts.Jump(state_from=open_up.uid, state_to=open_up_lying.uid, start_actions=[actions.Message(type='move_to_report_lie'),]),

                  facts.OptionsLink(options=(start_spying__spying_middle.uid,
                                             spying_middle__continue_spying.uid,
                                             finish_spying__report_data.uid)),
                  facts.OptionsLink(options=(start_spying__spying_middle__blackmail.uid,
                                             spying_middle__continue_spying__blackmail.uid,
                                             finish_spying__blackmail.uid)),

                  facts.Answer(state_from=witness_fight.uid, state_to=finish_spying_choice.uid, condition=True),
                  facts.Answer(state_from=witness_fight.uid, state_to=witness_failed.uid, condition=False),

                  facts.Event(uid=ns+'open_up_variants', description='Варианты окончания раскрытия', members=(open_up_finish.uid, open_up_lying.uid)),
                  facts.Event(uid=ns+'spying_variants', description='Варианты событий при шпионаже', members=(success_spying.uid, witness.uid)),
                ]

        line.extend(participants)

        return line
