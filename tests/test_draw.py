# coding: utf-8

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import ( Start,
                             State,
                             Jump,
                             Finish,
                             Event,
                             Place,
                             Person,
                             LocatedIn,
                             Choice,
                             Option)
from questgen.graph_drawer import Drawer
from questgen.selectors import Selector
from questgen.restrictions import (SingleStartState,
                                   NoJumpsFromFinish,
                                   SingleLocationForObject,
                                   ReferencesIntegrity,
                                   ConnectedStateJumpGraph,
                                   NoCirclesInStateJumpGraph)

from questgen.quests.spying import Spying


kb = KnowledgeBase()

kb += [SingleStartState(),
       NoJumpsFromFinish(),
       SingleLocationForObject(),
       ReferencesIntegrity(),
       ConnectedStateJumpGraph(),
       NoCirclesInStateJumpGraph()]

kb += [ Place(uid='place_customer', terrains=()),
        Place(uid='place_target', terrains=()),

        Person(uid='customer', profession=0),
        Person(uid='target', profession=0),

        LocatedIn(object='customer', place='place_customer'),
        LocatedIn(object='target', place='place_target')]

kb += Spying.construct_from_nothing(Selector(kb))


kb.validate_consistency()

drawer = Drawer(knowledge_base=kb)
drawer.draw('./test_draw.svg')
