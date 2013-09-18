# coding: utf-8

from questgen.knowledge_base import KnowledgeBase
from questgen import facts
from questgen.graph_drawer import Drawer
from questgen.selectors import Selector
from questgen import restrictions

from questgen.quests.spying import Spying


kb = KnowledgeBase()

kb += [ facts.Hero(uid='hero'),

        facts.Place(uid='place_customer', terrains=()),
        facts.Place(uid='place_target', terrains=()),

        facts.Person(uid='customer', profession=0),
        facts.Person(uid='target', profession=0),

        facts.LocatedIn(object='customer', place='place_customer'),
        facts.LocatedIn(object='target', place='place_target')]

kb += Spying.construct_from_nothing(kb, Selector(kb))


kb.validate_consistency([restrictions.SingleStartState(),
                         restrictions.NoJumpsFromFinish(),
                         restrictions.SingleLocationForObject(),
                         restrictions.ReferencesIntegrity(),
                         restrictions.ConnectedStateJumpGraph(),
                         restrictions.NoCirclesInStateJumpGraph()])

drawer = Drawer(knowledge_base=kb)
drawer.draw('./test_draw.svg')
