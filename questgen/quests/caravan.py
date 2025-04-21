# coding: utf-8

import random

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import requirements
from questgen import actions
from questgen import relations


class Caravan(QuestBetween2):
    TYPE = 'caravan'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def find_receiver(cls, selector, initiator):
        return selector.new_person(restrict_social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.CONCURRENT),),
                                   social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.PARTNER),))

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        black_market = selector.new_place()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Start: caravan',
                            require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        facts.QuestParticipant(start=start.uid, participant=black_market.uid, role=ROLES.ANTAGONIST_POSITION)]

        path_percents_1 = random.uniform(0.1, 0.3)
        path_percents_2 = random.uniform(0.4, 0.6)
        path_percents_3 = random.uniform(0.7, 0.9)

        first_moving = facts.State(uid=ns+'first_moving',
                                    description='moving with the caravan',
                                    require=[requirements.LocatedOnRoad(object=hero.uid, place_from=initiator_position.uid, place_to=receiver_position.uid, percents=path_percents_1)])

        caravan_choice = facts.Choice(uid=ns+'caravan_choice',
                                      description='Decision: protect or rob')

        first_defence = facts.Choice(uid=ns+'first_defence',
                                     description='first defense',
                                     require=[requirements.LocatedOnRoad(object=hero.uid,
                                                                         place_from=initiator_position.uid, place_to=receiver_position.uid, percents=path_percents_2)],
                                     actions=[actions.Message(type='defence')])

        first_defence_continue = facts.Question(uid=ns+'first_defence_continue',
                                                description='was the caravan successfully defended?',
                                                condition=[requirements.IsAlive(object=hero.uid)],
                                                actions=[actions.Fight()])

        second_moving = facts.State(uid=ns+'second_moving',
                                    description='moving with the caravan',
                                    require=[requirements.LocatedOnRoad(object=hero.uid, place_from=initiator_position.uid, place_to=receiver_position.uid, percents=path_percents_3)])

        second_defence = facts.Question(uid=ns+'second_defence',
                                        description='second defense',
                                        condition=(requirements.IsAlive(object=hero.uid),),
                                        actions=(actions.Message(type='defence'),
                                                 actions.Fight(), ))

        finish_defence = facts.Finish(uid=ns+'finish_defence',
                                      start=start.uid,
                                      results={ initiator.uid: RESULTS.SUCCESSED,
                                                receiver.uid: RESULTS.SUCCESSED,
                                                black_market.uid: RESULTS.NEUTRAL },
                                      nesting=nesting,
                                      description='The caravan arrives at the destination',
                                      require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                      actions=[actions.GiveReward(object=hero.uid, type='finish_defence')])

        move_to_attack = facts.State(uid=ns+'move_to_attack',
                                     description='leading the caravan into an ambush',
                                     require=[requirements.LocatedOnRoad(object=hero.uid,
                                                                         place_from=initiator_position.uid, place_to=receiver_position.uid, percents=path_percents_2)])

        attack = facts.Question(uid=ns+'attack',
                                description='attack',
                                condition=(requirements.IsAlive(object=hero.uid),),
                                actions=(actions.Message(type='attack'),
                                         actions.Fight(mercenary=True), ))

        run = facts.State(uid=ns+'run',
                          description='fleeing the scene of the crime',
                          actions=(actions.MoveNear(object=hero.uid),))

        fight = facts.Question(uid=ns+'fight',
                               description='defending the loot',
                               condition=(requirements.IsAlive(object=hero.uid),),
                               actions=(actions.Message(type='fight'),
                                        actions.Fight(mercenary=True), ))

        hide = facts.State(uid=ns+'hide',
                           description='hiding',
                           actions=(actions.Message(type='hide'),
                                    actions.MoveNear(object=hero.uid)))

        finish_attack = facts.Finish(uid=ns+'finish_attack',
                                     start=start.uid,
                                     results={ initiator.uid: RESULTS.FAILED,
                                               receiver.uid: RESULTS.FAILED,
                                               black_market.uid: RESULTS.SUCCESSED },
                                     nesting=nesting,
                                     description='Sell the goods on the black market',
                                     require=[requirements.LocatedIn(object=hero.uid, place=black_market.uid)],
                                     actions=[actions.GiveReward(object=hero.uid, type='finish_attack', scale=1.5)])

        finish_defence_failed = facts.Finish(uid=ns+'finish_defence_failed',
                                             start=start.uid,
                                             results={ initiator.uid: RESULTS.NEUTRAL,
                                                       receiver.uid: RESULTS.NEUTRAL,
                                                       black_market.uid: RESULTS.NEUTRAL },
                                             nesting=nesting,
                                             description='The hero failed to defend the caravan',
                                             actions=[actions.Message(type='finish_defence_failed')])

        finish_attack_failed = facts.Finish(uid=ns+'finish_attack_failed',
                                            start=start.uid,
                                            results={ initiator.uid: RESULTS.NEUTRAL,
                                                      receiver.uid: RESULTS.NEUTRAL,
                                                      black_market.uid: RESULTS.NEUTRAL },
                                            nesting=nesting,
                                            description='The hero failed to rob the caravan',
                                            actions=[actions.Message(type='finish_attack_failed')])

        caravan_choice__first_defence = facts.Option(state_from=caravan_choice.uid, state_to=first_defence.uid, type='jump_defence',
                                                     markers=[relations.OPTION_MARKERS.HONORABLE], start_actions=[actions.Message(type='choose_defence'),])
        caravan_choice__move_to_attack = facts.Option(state_from=caravan_choice.uid, state_to=move_to_attack.uid, type='jump_attack',
                                                     markers=[relations.OPTION_MARKERS.DISHONORABLE], start_actions=[actions.Message(type='choose_attack'),])

        first_defence__first_defence_continue = facts.Option(state_from=first_defence.uid, state_to=first_defence_continue.uid, type='jump_defence',
                                                             markers=[relations.OPTION_MARKERS.HONORABLE], )
        first_defence__move_to_attack = facts.Option(state_from=first_defence.uid, state_to=move_to_attack.uid, type='jump_attack',
                                                     markers=[relations.OPTION_MARKERS.DISHONORABLE], start_actions=[actions.Message(type='choose_attack'),])

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=first_moving.uid, start_actions=(actions.Message(type='first_moving'), )),

                 first_moving,

                 facts.Jump(state_from=first_moving.uid, state_to=caravan_choice.uid),

                 caravan_choice,

                 caravan_choice__first_defence,
                 caravan_choice__move_to_attack,

                 first_defence,

                 first_defence__first_defence_continue,
                 first_defence__move_to_attack,

                 first_defence_continue,

                 facts.Answer(state_from=first_defence_continue.uid, state_to=second_moving.uid, condition=True),
                 facts.Answer(state_from=first_defence_continue.uid, state_to=finish_defence_failed.uid, condition=False),

                 second_moving,

                 facts.Jump(state_from=second_moving.uid, state_to=second_defence.uid),

                 second_defence,

                 facts.Answer(state_from=second_defence.uid, state_to=finish_defence.uid, condition=True),
                 facts.Answer(state_from=second_defence.uid, state_to=finish_defence_failed.uid, condition=False),

                 finish_defence,

                 move_to_attack,

                 facts.Jump(state_from=move_to_attack.uid, state_to=attack.uid),

                 attack,

                 facts.Answer(state_from=attack.uid, state_to=run.uid, condition=True, start_actions=(actions.Message(type='start_run'),)),
                 facts.Answer(state_from=attack.uid, state_to=finish_attack_failed.uid, condition=False),

                 run,

                 facts.Jump(state_from=run.uid, state_to=fight.uid),

                 fight,

                 facts.Answer(state_from=fight.uid, state_to=hide.uid, condition=True, start_actions=(actions.Message(type='start_hide'),)),
                 facts.Answer(state_from=fight.uid, state_to=finish_attack_failed.uid, condition=False),

                 hide,

                 facts.Jump(state_from=hide.uid, state_to=finish_attack.uid),

                 finish_attack,

                 facts.OptionsLink(options=(caravan_choice__first_defence.uid, first_defence__first_defence_continue.uid)),

                 finish_defence_failed,
                 finish_attack_failed
                ]

        line.extend(participants)

        return line
