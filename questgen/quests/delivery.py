# coding: utf-8
import random

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import requirements
from questgen import actions
from questgen import relations
from questgen import exceptions


class Delivery(QuestBetween2):
    TYPE = 'delivery'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def find_receiver(cls, selector, initiator):
        return selector.new_person(restrict_social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.CONCURRENT),),
                                   social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.PARTNER),))

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        antagonist_marker = None

        try:
            antagonist = selector.new_person(first_initiator=False,
                                             professions=[relations.PROFESSION.ROGUE],
                                             restrict_social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.PARTNER),
                                                                          (receiver.uid, relations.SOCIAL_RELATIONS.PARTNER)),
                                             social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.CONCURRENT),
                                                                 (receiver.uid, relations.SOCIAL_RELATIONS.CONCURRENT)))
            antagonist_marker = facts.ProfessionMarker(person=antagonist.uid, profession=antagonist.profession)
        except exceptions.NoFactSelectedError:
            antagonist = selector.new_person(restrict_social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.PARTNER),
                                                                          (receiver.uid, relations.SOCIAL_RELATIONS.PARTNER)),
                                             social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.CONCURRENT),
                                                                 (receiver.uid, relations.SOCIAL_RELATIONS.CONCURRENT)))

        antagonist_position = selector.place_for(objects=(antagonist.uid,))

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Start: delivery',
                            require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        facts.QuestParticipant(start=start.uid, participant=antagonist.uid, role=ROLES.ANTAGONIST) ]

        delivery_choice = facts.Choice(uid=ns+'delivery_choice',
                                 description='Decision: deliver or steal')


        finish_delivery = facts.Finish(uid=ns+'finish_delivery',
                                       start=start.uid,
                                       results={ initiator.uid: RESULTS.SUCCESSED,
                                                 receiver.uid: RESULTS.SUCCESSED,
                                                 antagonist.uid: RESULTS.NEUTRAL},
                                       nesting=nesting,
                                       description='Deliver the package to the recipient',
                                       require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                       actions=[actions.GiveReward(object=hero.uid, type='finish_delivery')])

        finish_fake_delivery = facts.Finish(uid=ns+'finish_fake_delivery',
                                            start=start.uid,
                                            results={ initiator.uid: RESULTS.FAILED,
                                                      receiver.uid: RESULTS.FAILED,
                                                      antagonist.uid: RESULTS.NEUTRAL},
                                            nesting=nesting,
                                            description='Forge the letter',
                                            require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                            actions=[actions.GiveReward(object=hero.uid, type='finish_fake_delivery', scale=2.0)])

        fake_delivery_dummy_state = facts.FakeFinish(uid=ns+'dummy_state',
                                                     start=start.uid,
                                                     results={ initiator.uid: RESULTS.NEUTRAL,
                                                               receiver.uid: RESULTS.NEUTRAL,
                                                               antagonist.uid: RESULTS.NEUTRAL},
                                                     nesting=nesting,
                                                     description='dummy, so you can control the appearance of the letter forgery')

        finish_steal = facts.Finish(uid=ns+'finish_steal',
                                    start=start.uid,
                                    results={ initiator.uid: RESULTS.FAILED,
                                              receiver.uid: RESULTS.FAILED,
                                              antagonist.uid: RESULTS.SUCCESSED},
                                    nesting=nesting,
                                    description='Deliver the package to the fence',
                                    require=[requirements.LocatedIn(object=hero.uid, place=antagonist_position.uid)],
                                    actions=[actions.GiveReward(object=hero.uid, type='finish_steal', scale=1.5)])

        delivery_stealed = facts.State(uid=ns+'delivery_stealed',
                                       description='letter stolen',
                                       require=[requirements.LocatedOnRoad(object=hero.uid,
                                                                           place_from=initiator_position.uid,
                                                                           place_to=receiver_position.uid,
                                                                           percents=random.uniform(0.6, 0.9))],
                                       actions=[actions.Message(type='delivery_stealed'),
                                                actions.MoveNear(object=hero.uid)])

        fight_for_stealed = facts.Question(uid=ns+'fight_for_stealed',
                                           description='Fight the thief',
                                           actions=[actions.Message(type='fight_thief'),
                                                    actions.Fight(mercenary=True)],
                                           condition=[requirements.IsAlive(object=hero.uid)])


        finish_fight_for_stealed__hero_died = facts.Finish(uid=ns+'finish_fight_for_stealed__hero_died',
                                                          start=start.uid,
                                                          results={ initiator.uid: RESULTS.NEUTRAL,
                                                                    receiver.uid: RESULTS.NEUTRAL,
                                                                    antagonist.uid: RESULTS.NEUTRAL},
                                                                    nesting=nesting,
                                                          description='The hero failed to retrieve the stolen letter',
                                                          actions=[actions.Message(type='finish_fight_for_stealed__hero_died')])


        finish_fight_for_stealed__delivery = facts.Finish(uid=ns+'finish_fight_for_stealed__delivery',
                                                          start=start.uid,
                                                          results={ initiator.uid: RESULTS.SUCCESSED,
                                                                    receiver.uid: RESULTS.SUCCESSED,
                                                                    antagonist.uid: RESULTS.NEUTRAL},
                                                          nesting=nesting,
                                                          description='Deliver the package to the recipient',
                                                          require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                                          actions=[actions.GiveReward(object=hero.uid, type='finish_delivery')])


        line = [ start,
                 delivery_choice,
                 delivery_stealed,
                 fight_for_stealed,
                 finish_delivery,
                 finish_steal,
                 finish_fake_delivery,
                 fake_delivery_dummy_state,
                 finish_fight_for_stealed__hero_died,
                 finish_fight_for_stealed__delivery,

                 facts.Jump(state_from=start.uid, state_to=delivery_choice.uid),

                 facts.Jump(state_from=delivery_stealed.uid, state_to=fight_for_stealed.uid),

                 facts.Option(state_from=delivery_choice.uid, state_to=delivery_stealed.uid, type='delivery',
                              markers=[relations.OPTION_MARKERS.HONORABLE], start_actions=[actions.Message(type='start_delivery'),]),
                 facts.Option(state_from=delivery_choice.uid, state_to=finish_delivery.uid, type='delivery',
                              markers=[relations.OPTION_MARKERS.HONORABLE], start_actions=[actions.Message(type='start_delivery'),]),
                 facts.Option(state_from=delivery_choice.uid, state_to=finish_steal.uid, type='steal',
                              markers=[relations.OPTION_MARKERS.DISHONORABLE], start_actions=[actions.Message(type='start_steal'),]),
                 facts.Option(state_from=delivery_choice.uid, state_to=finish_fake_delivery.uid, type='fake',
                              markers=[relations.OPTION_MARKERS.DISHONORABLE], start_actions=[actions.Message(type='start_fake'),]),
                 facts.Option(state_from=delivery_choice.uid, state_to=fake_delivery_dummy_state.uid,
                              markers=[], type='dummy_lie'),

                 facts.Answer(state_from=fight_for_stealed.uid, state_to=finish_fight_for_stealed__delivery.uid,
                              condition=True, start_actions=[actions.Message(type='delivery_returned')]),
                 facts.Answer(state_from=fight_for_stealed.uid, state_to=finish_fight_for_stealed__hero_died.uid, condition=False),

                 facts.Event(uid=ns+'delivery_variants', description='Delivery options', members=(delivery_stealed.uid, finish_delivery.uid)),
                 facts.Event(uid=ns+'lie_variants', description='Deception options', members=(fake_delivery_dummy_state.uid, finish_fake_delivery.uid))
                ]

        line.extend(participants)

        if antagonist_marker:
            line.append(antagonist_marker)

        return line
