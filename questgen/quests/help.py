# coding: utf-8
from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import logic
from questgen import requirements
from questgen import actions
from questgen import relations


class Help(QuestBetween2):
    TYPE = 'help'
    TAGS = ('can_start', 'has_subquests', 'can_continue')

    @classmethod
    def find_receiver(cls, selector, initiator):
        return selector.new_person(restrict_social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.CONCURRENT),),
                                   social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.PARTNER),))

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Начало: помочь знакомому',
                            require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid),
                                     requirements.LocatedIn(object=receiver.uid, place=receiver_position.uid)],
                            actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        finish_successed = facts.Finish(uid=ns+'finish_successed',
                                        start=start.uid,
                                        results={ initiator.uid: RESULTS.SUCCESSED,
                                                  receiver.uid: RESULTS.SUCCESSED},
                                        nesting=nesting,
                                        description='помощь оказана',
                                        require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                        actions=[actions.GiveReward(object=hero.uid, type='finish_successed')])

        finish_failed = facts.Finish(uid=ns+'finish_failed',
                                     start=start.uid,
                                     results={ initiator.uid: RESULTS.FAILED,
                                               receiver.uid: RESULTS.FAILED},
                                     nesting=nesting,
                                     description='не удалось помочь',
                                     actions=[actions.GiveReward(object=hero.uid, type='finish_failed')])

        help_quest = selector.create_quest_from_person(nesting=nesting+1, initiator=receiver, tags=('can_continue',))
        help_extra = []

        for help_fact in logic.filter_subquest(help_quest, nesting):
            if isinstance(help_fact, facts.Start):
                help_extra.append(facts.Jump(state_from=start.uid, state_to=help_fact.uid, start_actions=[actions.Message(type='before_help')]))
            elif isinstance(help_fact, facts.Finish):
                if help_fact.results[receiver.uid] == RESULTS.SUCCESSED:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=finish_successed.uid, start_actions=[actions.Message(type='after_successed_help')]))
                else:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=finish_failed.uid))

        subquest = facts.SubQuest(uid=ns+'help_subquest', members=logic.get_subquest_members(help_quest))

        line = [ start,
                 finish_successed,
                 finish_failed,
                 subquest ]

        line.extend(participants)
        line.extend(help_quest)
        line.extend(help_extra)

        return line
