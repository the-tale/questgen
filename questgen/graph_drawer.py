# coding:utf-8
from collections import defaultdict

import gv

from questgen import facts


class HEAD_COLORS(object):
    START = '#eeeeee'
    STATE = '#ddffdd'
    FINISH = '#eeeeee'
    CHOICE = '#ddddff'

    START_REQUIREMENTS = '#dddddd'
    STATE_REQUIREMENTS = '#cceecc'
    FINISH_REQUIREMENTS = '#dddddd'
    CHOICE_REQUIREMENTS = '#ccccee'

    START_ACTIONS = '#ffffff'
    STATE_ACTIONS = '#eeffee'
    FINISH_ACTIONS = '#ffffff'
    CHOICE_ACTIONS = '#eeeeff'

    SUBGRAPH = '#ffffdd'
    EVENT = '#eeeecc'

    LINK = '#ffaaaa'


class Drawer(object):

    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.graph = gv.strictdigraph('quest')
        self.tags = defaultdict(set)
        self.nodes = {}

        self.linked_edges = set()

    def add_node(self, fact):
        node = gv.node(self.graph, fact.uid)
        gv.setv(node, 'shape', 'plaintext')
        gv.setv(node, 'label', self.create_label_for(fact).encode('utf-8'))
        gv.setv(node, 'fontsize', '10')

        self.nodes[fact.uid] = node

        for tag in fact.tags:
            self.tags[tag].add(fact.uid)

        return node

    def _add_linked_edge(self, jump):
        node = gv.node(self.graph, jump.uid)
        gv.setv(node, 'shape', 'point')
        gv.setv(node, 'label', '')

        edge_1 = gv.edge(self.nodes[jump.state_from], node)
        edge_2 = gv.edge(node, self.nodes[jump.state_to])
        gv.setv(edge_1, 'dir', 'none')
        gv.setv(edge_2, 'headport', jump.state_to)
        gv.setv(edge_1, 'tailport', jump.state_from)

        if isinstance(jump, facts.Option):
            gv.setv(edge_1, 'style', 'dotted')
            gv.setv(edge_2, 'style', 'dotted')

    def _add_edge(self, jump):
        edge = gv.edge(self.nodes[jump.state_from], self.nodes[jump.state_to])
        gv.setv(edge, 'headport', jump.state_to)
        gv.setv(edge, 'tailport', jump.state_from)

        if isinstance(jump, facts.Option):
            gv.setv(edge, 'style', 'dotted')

    def add_edge(self, jump):
        if jump.uid in self.linked_edges:
            self._add_linked_edge(jump)
        else:
            self._add_edge(jump)

    def add_link(self, link):
        node = gv.node(self.graph, link.uid)
        gv.setv(node, 'shape', 'circle')
        gv.setv(node, 'label', 'link')
        gv.setv(node, 'fontsize', '10')
        gv.setv(node, 'style', 'filled')
        gv.setv(node, 'fillcolor', HEAD_COLORS.LINK)
        gv.setv(node, 'fixedsize', 'true')
        gv.setv(node, 'width', '0.33')

        for option_uid in link.options:
            self.linked_edges.add(option_uid)
            edge = gv.edge(node, option_uid)
            gv.setv(edge, 'dir', 'none')
            gv.setv(edge, 'color', HEAD_COLORS.LINK)
            gv.setv(edge, 'minlen', '0')

    def draw(self, path):

        gv.setv(self.graph, 'rankdir', 'LR')
        gv.setv(self.graph, 'splines', 'ortho')
        # gv.setv(self.graph, 'concentrate', 'true') # merge edges

        for state in self.kb.filter(facts.State):
            self.add_node(state)

        for event in self.kb.filter(facts.Event):
            self.add_node(event)

        for link in self.kb.filter(facts.OptionsLink):
            self.add_link(link)

        for jump in self.kb.filter(facts.Jump):
            self.add_edge(jump)

        for tag, elements in self.tags.items():
            subgraph_uid = 'cluster_' + tag

            subgraph = gv.graph(self.graph, subgraph_uid)

            self.nodes[subgraph_uid] = subgraph

            for node_uid in elements:
                gv.node(subgraph, node_uid)

            gv.setv(subgraph, 'label', tag)
            gv.setv(subgraph, 'rank', 'same')
            gv.setv(subgraph, 'shape', 'box')
            gv.setv(subgraph, 'bgcolor', HEAD_COLORS.SUBGRAPH)

            for event in self.kb.filter(facts.Event):
                if event.uid == tag:
                    gv.node(subgraph, event.uid)

        gv.layout(self.graph, 'dot');
        # gv.render(graph, 'dot')
        gv.render(self.graph, path[path.rfind('.')+1:], path)


    def create_label_for(self, fact):
        if isinstance(fact, facts.Start):
            return self.create_label_for_start(fact)
        if isinstance(fact, facts.Finish):
            return self.create_label_for_finish(fact)
        if isinstance(fact, facts.Choice):
            return self.create_label_for_choice(fact)
        if isinstance(fact, facts.State):
            return self.create_label_for_state(fact)
        if isinstance(fact, facts.Event):
            return self.create_label_for_event(fact)
        return None

    def create_label_for_start(self, start):
        return self.create_label_for_state(start,
                                           bgcolor=HEAD_COLORS.START,
                                           requirements_bgcolor=HEAD_COLORS.START_REQUIREMENTS,
                                           actions_bgcolor=HEAD_COLORS.START_ACTIONS)

    def create_label_for_finish(self, finish):
        return self.create_label_for_state(finish,
                                           bgcolor=HEAD_COLORS.FINISH,
                                           requirements_bgcolor=HEAD_COLORS.FINISH_REQUIREMENTS,
                                           actions_bgcolor=HEAD_COLORS.FINISH_ACTIONS)

    def create_label_for_choice(self, finish):
        return self.create_label_for_state(finish,
                                           bgcolor=HEAD_COLORS.CHOICE,
                                           requirements_bgcolor=HEAD_COLORS.CHOICE_REQUIREMENTS,
                                           actions_bgcolor=HEAD_COLORS.CHOICE_ACTIONS)

    def create_label_for_state(self,
                               state,
                               bgcolor=HEAD_COLORS.STATE,
                               requirements_bgcolor=HEAD_COLORS.STATE_REQUIREMENTS,
                               actions_bgcolor=HEAD_COLORS.STATE_ACTIONS):

        trs = []

        for requirement in state.require:
            if isinstance(requirement, facts.LocatedIn):
                trs.append(self.create_tr_for_located_in(requirement, bgcolor=requirements_bgcolor))
            elif isinstance(requirement, facts.LocatedNear):
                trs.append(self.create_tr_for_located_near(requirement, bgcolor=requirements_bgcolor))

        for action in state.actions:
            if isinstance(action, facts.Message):
                trs.append(self.create_tr_for_message(action, bgcolor=actions_bgcolor))
            elif isinstance(action, facts.GivePower):
                trs.append(self.create_tr_for_give_power(action, bgcolor=actions_bgcolor))
            elif isinstance(action, facts.LocatedNear):
                trs.append(self.create_tr_for_located_near(action, bgcolor=actions_bgcolor))

        return table(tr(td(i(state.uid))),
                     tr(td(b(state.label))),
                     tr(td(state.description, colspan=2)),
                     *trs,
                     bgcolor=bgcolor,
                     port=state.uid)

    def create_label_for_event(self, event):
        return table(tr(td(i(event.uid))),
                     tr(td(b(event.label))),
                     tr(td(event.description, colspan=2)),
                     bgcolor=HEAD_COLORS.EVENT,
                     port=event.uid)

    def create_tr_for_located_in(self, requirement, bgcolor):
        return tr(td(u'%s <b>находится в</b>&nbsp;%s' % (requirement.object, requirement.place), bgcolor=bgcolor))

    def create_tr_for_located_near(self, requirement, bgcolor):
        return tr(td(u'%s <b>находится около</b>&nbsp;%s' % (requirement.object, requirement.place), bgcolor=bgcolor))

    def create_tr_for_message(self, message, bgcolor):
        return tr(td(u'<b>сообщение:</b>&nbsp;%s' % message.id, bgcolor=bgcolor))

    def create_tr_for_give_power(self, give_power, bgcolor):
        return tr(td(u'<b>увеличть влияние</b>&nbsp; %s <b>на</b> %.2f' % (give_power.person, give_power.power), bgcolor=bgcolor))


def b(data): return u'<b>%s</b>' % data
def i(data): return u'<i>%s</i>' % data

def table(*trs, **kwargs):
    bgcolor = kwargs.get('bgcolor')
    port = kwargs.get('port')
    return u'''<
    <table cellpadding="1"
           cellspacing="0"
           border="1"
           %(bgcolor)s
           %(port)s
           cellborder="1">%(body)s</table>
    >''' % {'body': ''.join(trs),
            'port': 'port="%s"' % port if port else '',
            'bgcolor': 'BGCOLOR="%s"' % bgcolor if bgcolor is not None else ''}

def tr(*tds):
    return u'<tr BGCOLOR="#00ff00">%s</tr>' % ''.join(tds)

def td(body, port=None, **kwargs):
    bgcolor = kwargs.get('bgcolor')
    colspan = kwargs.get('colspan', 1)
    align = kwargs.get('align', 'left')
    border = kwargs.get('border', 0)
    return u'''<td
                 %(port)s
                 COLSPAN="%(colspan)d"
                 border="%(border)d"
                 align="%(align)s"
                 %(bgcolor)s>%(body)s</td>''' % {'body': body,
                                                 'colspan': colspan,
                                                 'align': align,
                                                 'border': border,
                                                 'port': 'port="%s"' % port if port else '',
                                                 'bgcolor': 'BGCOLOR="%s"' % bgcolor if bgcolor is not None else '' }
