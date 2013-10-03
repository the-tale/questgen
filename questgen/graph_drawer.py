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

    JUMP = '#ffffff'
    JUMP_ACTIONS_START = '#eeeeee'
    JUMP_ACTIONS_END = '#dddddd'


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

    def _add_edge(self, jump):
        node = gv.node(self.graph, jump.uid)

        gv.setv(node, 'shape', 'plaintext')
        gv.setv(node, 'label', self.create_label_for(jump).encode('utf-8'))
        gv.setv(node, 'fontsize', '10')

        self.nodes[jump.uid] = node

        edge_1 = gv.edge(self.nodes[jump.state_from], node)
        edge_2 = gv.edge(node, self.nodes[jump.state_to])

        gv.setv(edge_1, 'dir', 'none')
        gv.setv(edge_1, 'tailport', jump.state_from)
        gv.setv(edge_1, 'headport', jump.uid)
        gv.setv(edge_1, 'weight', '40')
        gv.setv(edge_1, 'minlen', '1')

        gv.setv(edge_2, 'tailport', jump.uid)
        gv.setv(edge_2, 'headport', jump.state_to)
        gv.setv(edge_2, 'weight', '40')
        gv.setv(edge_2, 'minlen', '1')

        if isinstance(jump, facts.Option):
            gv.setv(edge_1, 'style', 'dotted')
            gv.setv(edge_2, 'style', 'dotted')

    def _add_empty_edge(self, jump):
        edge = gv.edge(self.nodes[jump.state_from], self.nodes[jump.state_to])
        gv.setv(edge, 'headport', jump.state_to)
        gv.setv(edge, 'tailport', jump.state_from)
        gv.setv(edge, 'weight', '20')
        gv.setv(edge, 'minlen', '1')


    def add_edge(self, jump):
        if hasattr(jump, 'type') or jump.start_actions or jump.end_actions:
            self._add_edge(jump)
        else:
            self._add_empty_edge(jump)

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
            gv.setv(edge, 'minlen', '1')
            gv.setv(edge, 'headport', option_uid)
            gv.setv(edge, 'weight', '10')

    def draw(self, path):

        gv.setv(self.graph, 'rankdir', 'LR')
        gv.setv(self.graph, 'splines', 'ortho')
        # gv.setv(self.graph, 'concentrate', 'true') # merge edges

        for state in self.kb.filter(facts.State):
            self.add_node(state)

        for event in self.kb.filter(facts.Event):
            self.add_node(event)

        for jump in self.kb.filter(facts.Jump):
            self.add_edge(jump)

        for link in self.kb.filter(facts.OptionsLink):
            self.add_link(link)

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
        if isinstance(fact, facts.Jump):
            return self.create_label_for_jump(fact)
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
                trs.append(tr(td(self.create_label_for_located_in(requirement), bgcolor=requirements_bgcolor, colspan=2)))
            elif isinstance(requirement, facts.LocatedNear):
                trs.append(tr(td(self.create_label_for_located_near(requirement), bgcolor=requirements_bgcolor, colspan=2)))

        for action in state.actions:
            trs.append(tr(td(self.create_label_for_action(action), bgcolor=actions_bgcolor, colspan=2)))

        if hasattr(state, 'type'):
            head = tr(td(i(state.uid)), td(b(state.type), align='right'))
        else:
            head = tr(td(i(state.uid)))

        return table(head,
                     tr(td(state.description, colspan=2)),
                     *trs,
                     bgcolor=bgcolor,
                     port=state.uid)

    def create_label_for_action(self, action):
        if isinstance(action, facts.Message):
            return self.create_action_label_for_message(action)
        elif isinstance(action, facts.GivePower):
            return self.create_action_label_for_give_power(action)
        elif isinstance(action, facts.LocatedNear):
            return self.create_action_label_for_located_near(action)
        elif isinstance(action, facts.Fight):
            return self.create_action_label_for_fight(action)
        elif isinstance(action, facts.DoNothing):
            return self.create_action_label_for_donothing(action)

    def create_label_for_event(self, event):
        return table(tr(td(i(event.uid))),
                     tr(td(event.description, colspan=2)),
                     bgcolor=HEAD_COLORS.EVENT,
                     port=event.uid)

    def create_label_for_jump(self, jump):
        trs = []

        if hasattr(jump, 'type'):
            trs.append(tr(td(jump.type, bgcolor=HEAD_COLORS.JUMP)))

        for action in jump.start_actions:
            trs.append(tr(td(self.create_label_for_action(action), bgcolor=HEAD_COLORS.JUMP_ACTIONS_START)))

        for action in jump.end_actions:
            trs.append(tr(td(self.create_label_for_action(action), bgcolor=HEAD_COLORS.JUMP_ACTIONS_END)))

        return table(*trs, port=jump.uid, border=0)

    def create_label_for_located_in(self, requirement):
        return u'%s <b>находится в</b>&nbsp;%s' % (requirement.object, requirement.place)

    def create_label_for_located_near(self, requirement):
        return u'%s <b>находится около</b>&nbsp;%s' % (requirement.object, requirement.place)

    # def create_label_for_message(self, message):
    #     return u'<b>сообщение:</b>&nbsp;%s' % message.id

    # def create_label_for_give_power(self, give_power):
    #     return u'<b>увеличивает влияние</b>&nbsp; %s <b>на</b> %.2f' % (give_power.person, give_power.power)

    # def create_label_for_fight(self, fight):
    #     return u'<b>сражается с</b>&nbsp; %s' % fight.mob


    def create_action_label_for_located_near(self, requirement):
        if requirement.terrains:
            return u'<b>отправить </b> %s<b>бродить около</b>&nbsp;%s<br/> среди ландшафтов %s' % (requirement.object, requirement.place, requirement.terrains)
        else:
            return u'<b>отправить </b> %s<b>бродить около</b>&nbsp;%s<br/>' % (requirement.object, requirement.place)

    def create_action_label_for_message(self, message):
        return u'<b>сообщение:</b>&nbsp;%s' % message.id

    def create_action_label_for_give_power(self, give_power):
        return u'<b>увеличить влияние </b>&nbsp; %s <b>на </b> %.2f' % (give_power.object, give_power.power)

    def create_action_label_for_fight(self, fight):
        return u'<b>сразиться с</b>&nbsp; %s' % fight.mob

    def create_action_label_for_donothing(self, donothing):
        return u'<b>заняться </b>&nbsp; %s' % donothing.type


def b(data): return u'<b>%s</b>' % data
def i(data): return u'<i>%s</i>' % data

def table(*trs, **kwargs):
    bgcolor = kwargs.get('bgcolor')
    port = kwargs.get('port')
    border = kwargs.get('border', 1)
    return u'''<
    <table cellpadding="1"
           cellspacing="0"
           border="%(border)d"
           %(bgcolor)s
           %(port)s
           cellborder="1">%(body)s</table>
    >''' % {'body': ''.join(trs),
            'border': border,
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
