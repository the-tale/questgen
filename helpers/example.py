# coding: utf-8

from questgen.knowledge_base import KnowledgeBase # "knowledge base" about the world and the quest
from questgen import facts # all facts
from questgen.selectors import Selector # helper class for finding the necessary facts
from questgen import restrictions # restrictions that must be met in a valid quest
from questgen import transformators # transformations that can be made to the knowledge base
from questgen import machine # mechanism for iterating through the quest
from questgen import logic

# import quests
from questgen.quests.quests_base import QuestsBase
from questgen.quests.spying import Spying
from questgen.quests.hunt import Hunt
from questgen.quests.hometown import Hometown
from questgen.quests.search_smith import SearchSmith
from questgen.quests.delivery import Delivery
from questgen.quests.caravan import Caravan
from questgen.quests.collect_debt import CollectDebt
from questgen.quests.help_friend import HelpFriend
from questgen.quests.interfere_enemy import InterfereEnemy
from questgen.quests.help import Help

from questgen.relations import PROFESSION

# list of restrictions for world facts
WORLD_RESTRICTIONS = [restrictions.SingleLocationForObject(),
                      restrictions.ReferencesIntegrity()]

# list of restrictions for the quest graph
QUEST_RESTRICTIONS =  [restrictions.SingleStartStateWithNoEnters(), # only one starting vertex for the quest
                       restrictions.FinishStateExists(), # there are finishing vertices
                       restrictions.AllStatesHasJumps(), # there are transitions from all states
                       restrictions.ConnectedStateJumpGraph(), # the graph is connected
                       restrictions.NoCirclesInStateJumpGraph(), # the graph has no cycles
                       restrictions.MultipleJumpsFromNormalState(), # each normal vertex has only one outgoing edge
                       restrictions.ChoicesConsistency(), # check the integrity of the choices
                       restrictions.QuestionsConsistency(), # check the integrity of the conditional nodes
                       restrictions.FinishResultsConsistency() # check that results are specified for each participant for each quest ending
                       ]


# create a quest
# this function can throw a questgen.exceptions.RollBackError exception and this is its normal behavior
# the exception means that the quest could not be created and the attempt should be repeated
def create_quest():

    # form a list of quests for generation
    qb = QuestsBase()
    qb += [Spying, Hunt, Hometown, SearchSmith, Delivery, Caravan, CollectDebt, HelpFriend, InterfereEnemy, Help]

    kb = KnowledgeBase()

    # describe the world
    kb += [ facts.Hero(uid='hero'), # our hero

            facts.Place(uid='place_1', terrains=(1,)), # there is a place with identifier place_1 and landscape types 1,
            facts.Place(uid='place_2', terrains=(0,)),
            facts.Place(uid='place_3', terrains=(0,)),
            facts.Place(uid='place_4', terrains=(1,)),
            facts.Place(uid='place_5', terrains=(2,)),
            facts.Place(uid='place_6', terrains=(1,)),
            facts.Place(uid='place_7', terrains=(2,)),
            facts.Place(uid='place_8', terrains=(2,)),
            facts.Place(uid='place_9', terrains=(1,)),
            facts.Place(uid='place_10', terrains=(2,)),

            facts.Person(uid='person_1', profession=PROFESSION.NONE), # there is a character with identifier person_1 and no profession
            facts.Person(uid='person_2', profession=PROFESSION.BLACKSMITH),
            facts.Person(uid='person_3', profession=PROFESSION.ROGUE),
            facts.Person(uid='person_4', profession=PROFESSION.NONE),
            facts.Person(uid='person_5', profession=PROFESSION.NONE),
            facts.Person(uid='person_6', profession=PROFESSION.NONE),
            facts.Person(uid='person_7', profession=PROFESSION.NONE),
            facts.Person(uid='person_8', profession=PROFESSION.NONE),
            facts.Person(uid='person_9', profession=PROFESSION.NONE),
            facts.Person(uid='person_10', profession=PROFESSION.NONE),

            facts.LocatedIn(object='person_1', place='place_1'), # character person_1 is located in place_1
            facts.LocatedIn(object='person_2', place='place_2'),
            facts.LocatedIn(object='person_3', place='place_3'),
            facts.LocatedIn(object='person_4', place='place_4'),
            facts.LocatedIn(object='person_5', place='place_5'),
            facts.LocatedIn(object='person_6', place='place_6'),
            facts.LocatedIn(object='person_7', place='place_7'),
            facts.LocatedIn(object='person_8', place='place_8'),
            facts.LocatedIn(object='person_9', place='place_9'),
            facts.LocatedIn(object='person_10', place='place_10'),

            facts.LocatedIn(object='hero', place='place_1'), # the hero is located in place_1

            facts.Mob(uid='mob_1', terrains=(0,)), # there is a monster inhabiting territories with identifier 0 (for the hunting quest)
            facts.PreferenceMob(object='hero', mob='mob_1'), # the hero likes to hunt the monster mob_1
            facts.PreferenceHometown(object='hero', place='place_2'), # the hero considers place_2 to be his hometown
            facts.PreferenceFriend(object='hero', person='person_4'), # the hero is friends with person_4
            facts.PreferenceEnemy(object='hero', person='person_5'), # the hero is enemies with person_5

            # specify that upgrading equipment costs 777 coins (for the SearchSmith quest)
            # facts.HasMoney(object='hero', money=888), # if this fact is uncommented, the hero will buy equipment in this quest instead of doing the blacksmith's quest
            facts.UpgradeEquipmentCost(money=777),

            facts.OnlyGoodBranches(object='place_2'), # do not harm place_2
            facts.OnlyGoodBranches(object='person_4'), # do not harm person_4
            facts.OnlyBadBranches(object='person_5') ] # do not help person_5


    kb.validate_consistency(WORLD_RESTRICTIONS) # check world restrictions

    selector = Selector(kb, qb)

    # create the quest (get a list of facts)
    quests_facts = selector.create_quest_from_place(nesting=0,
                                                    initiator_position=kb['place_1'],
                                                    tags=('can_start', ))

    kb += quests_facts

    transformators.activate_events(kb) # activate events (leave one of several graph vertices, delete the rest)
    transformators.remove_restricted_states(kb) # remove states that cannot be transitioned to (e.g., those that harm those who should not be harmed)
    transformators.remove_broken_states(kb) # clean up the quest graph from damage caused by previous actions
    transformators.determine_default_choices(kb) # determine default choices at forks

    kb.validate_consistency(WORLD_RESTRICTIONS) # check the world again
    kb.validate_consistency(QUEST_RESTRICTIONS) # check the quest graph (in case it is completely destroyed)

    return kb


# quest interpreter
class Interpreter(object):

    def __init__(self, kb):
        self.kb = kb
        # create a mechanism for iterating through the graph and pass callbacks to it
        self.machine = machine.Machine(knowledge_base=kb, interpreter=self)

        # to emulate changes in the state of the world
        # when it is necessary to satisfy some requirement, simply place it in this set
        # clear it after each successful progression through the plot
        self.satisfied_requirements = set()

    # do the quest
    def process(self):
        while self.machine.do_step():
            print('---- next step ----')

    ###########################
    # CALLBACKS
    ###########################

    # when entering a new vertex
    def on_state__before_actions(self, state):
        print('on state: %s' % state.uid)

        self.satisfied_requirements = set()

        if isinstance(state, facts.Start):
            print('    starting quest "%s"' % state.type)


    def on_state__after_actions(self, state):
        if isinstance(state, facts.Finish):
            print('    finishing quest with results "%s"' % state.results)


    # when transitioning to a new edge
    def on_jump_start__before_actions(self, jump):
        print('on jump start: %s' % jump.uid)
        print('    find %d actions' % len(jump.start_actions))

    def on_jump_start__after_actions(self, jump):
        print('    actions done')

    # when leaving an edge
    def on_jump_end__before_actions(self, jump):
        print('on jump end: %s' % jump.uid)
        print('    find %d actions' % len(jump.end_actions))

    def on_jump_end__after_actions(self, jump):
        print('    actions done')

    # action processing
    def do_message(self, action): print('    action %s' % action)

    def do_give_power(self, action): print('    action %s' % action)

    def do_give_reward(self, action): print('    action %s' % action)

    def do_fight(self, action): print('    action %s' % action)

    def do_do_nothing(self, action): print('    action %s' % action)

    def do_upgrade_equipment(self, action): print('    action %s' % action)

    def do_move_near(self, action): print('    action %s' % action)

    def do_move_in(self, action): print('    action %s' % action)

    def _check_requirement(self, requirement):
        print('    checking %s' % requirement)
        return requirement in self.satisfied_requirements

    def _satisfy_requirement(self, requirement):
        print('    satisfy %s' % requirement)
        self.satisfied_requirements.add(requirement)

    # check requirements
    def check_located_in(self, requirement): return self._check_requirement(requirement)

    def check_located_near(self, requirement): return self._check_requirement(requirement)

    def check_located_on_road(self, requirement): return self._check_requirement(requirement)

    def check_has_money(self, requirement): return self._check_requirement(requirement)

    def check_is_alive(self, requirement): return self._check_requirement(requirement)


    # satisfy requirements
    def satisfy_located_in(self, requirement): self._satisfy_requirement(requirement)

    def satisfy_located_near(self, requirement): self._satisfy_requirement(requirement)

    def satisfy_located_on_road(self, requirement): self._satisfy_requirement(requirement)

    def satisfy_has_money(self, requirement): self._satisfy_requirement(requirement)

    def satisfy_is_alive(self, requirement): self._satisfy_requirement(requirement)


if __name__ == '__main__':
    kb = create_quest()
    interpreter = Interpreter(kb=kb)

    # check that all necessary methods are implemented in the interpreter
    for method_name in logic.get_required_interpreter_methods():
        if not hasattr(interpreter, method_name):
            error = 'the interpreter does not implement the method: %s' % method_name
            print(error)
            raise Exception(error)

    interpreter.process()
