# coding:utf-8

import gv

from questgen import facts
from questgen import requirements
from questgen import actions
from questgen import exceptions
from questgen import relations


def link_colors_generator():
    color_elements = ['55', 'aa', 'ff']

    for r in color_elements:
        for g in color_elements:
            for b in color_elements:
                yield '#%s%s%s' % (r, g, b)


link_colors = link_colors_generator()

class HEAD_COLORS(object):
    START = '#eeeeee'
    STATE = '#ddffdd'
    FINISH = '#eeeeee'
    CHOICE = '#ddddff'
    QUESTION = '#ffdddd'

    START_REQUIREMENTS = '#dddddd'
    STATE_REQUIREMENTS = '#cceecc'
    FINISH_REQUIREMENTS = '#dddddd'
    CHOICE_REQUIREMENTS = '#ccccee'
    QUESTION_REQUIREMENTS = '#eecccc'

    START_ACTIONS = '#ffffff'
    STATE_ACTIONS = '#eeffee'
    FINISH_ACTIONS = '#ffffff'
    CHOICE_ACTIONS = '#eeeeff'
    QUESTION_ACTIONS = '#ffeeee'

    EVENT_SUBGRAPH = '#ffffdd'
    EVENT = '#eeeecc'

    SUBQUEST_SUBGRAPH = '#%02xffff'

    # LINK = '#ffaaaa'

    JUMP = '#ffffff'
    JUMP_ACTIONS_START = '#eeeeee'
    JUMP_ACTIONS_END = '#dddddd'
    JUMP_MARKER = '#aadddd'

class TEXT_COLORS:
    NORMAL = '#000000'
    PROFESSION = '#aa55aa'


class SubGraph(object):

    def __init__(self, uid, color, members):
        self.uid = 'cluster_%s' % uid
        self.color = color
        self.members = set(members)
        self.children = set()
        self.parents = set()

    def find_children(self, subgraphs):
        for graph in subgraphs:
            if graph.members - self.members:
                continue
            if graph is self:
                continue
            self.children.add(graph)
            graph.parents.add(self)

    def find_real_children(self):
        real_children = set()

        for child in self.children:
            if not any(child in check_child.children for check_child in self.children):
                real_children.add(child)

        self.children = real_children

    @classmethod
    def draw_hierarchy(cls, graphs, graph, nodes):

        for subgraph in graphs:
            if subgraph.parents:
                continue
            subgraph.draw(graph, nodes, nesting=0)

    def draw(self, graph, nodes, nesting):
        subgraph = gv.graph(graph, self.uid)
        gv.setv(subgraph, 'label', self.uid)
        # gv.setv(subgraph, 'rank', 'same')
        gv.setv(subgraph, 'shape', 'box')
        gv.setv(subgraph, 'bgcolor', self.color % (150+nesting*25) if '%' in self.color else self.color)

        for node_uid in self.members:
            if node_uid in nodes:
                gv.node(subgraph, node_uid)

        for child in self.children:
            child.draw(subgraph, nodes, nesting=nesting+1)


class Drawer(object):

    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.graph = gv.strictdigraph('quest')
        self.nodes = {}
        self.subgraphs = {}

        self.linked_edges = set()

    def add_node(self, fact):
        node = gv.node(self.graph, fact.uid)
        gv.setv(node, 'shape', 'plaintext')
        gv.setv(node, 'label', self.create_label_for(fact))
        gv.setv(node, 'fontsize', '10')

        self.nodes[fact.uid] = node

        return node

    def _add_edge(self, jump):
        node = gv.node(self.graph, jump.uid)

        gv.setv(node, 'shape', 'plaintext')
        gv.setv(node, 'label', self.create_label_for(jump))
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

        if isinstance(jump, facts.Answer):
            pass

    def _add_empty_edge(self, jump):
        edge = gv.edge(self.nodes[jump.state_from], self.nodes[jump.state_to])
        gv.setv(edge, 'headport', jump.state_to)
        gv.setv(edge, 'tailport', jump.state_from)
        gv.setv(edge, 'weight', '20')
        gv.setv(edge, 'minlen', '1')


    def add_edge(self, jump):
        if hasattr(jump, 'type') or hasattr(jump, 'condition') or jump.start_actions or jump.end_actions:
            self._add_edge(jump)
        else:
            self._add_empty_edge(jump)

    def add_link(self, link):

        color = next(link_colors)

        for option_uid in link.options:
            option = self.nodes[option_uid]
            gv.setv(option, 'style', 'filled')
            gv.setv(option, 'color', color)

        # node = gv.node(self.graph, link.uid)
        # gv.setv(node, 'shape', 'circle')
        # gv.setv(node, 'label', 'link')
        # gv.setv(node, 'fontsize', '10')
        # gv.setv(node, 'style', 'filled')
        # gv.setv(node, 'fillcolor', HEAD_COLORS.LINK)
        # gv.setv(node, 'fixedsize', 'true')
        # gv.setv(node, 'width', '0.33')

        # self.nodes[link.uid] = node

        # for option_uid in link.options:
        #     self.linked_edges.add(option_uid)
        #     edge = gv.edge(node, option_uid)
        #     gv.setv(edge, 'dir', 'none')
        #     gv.setv(edge, 'color', HEAD_COLORS.LINK)
        #     gv.setv(edge, 'minlen', '1')
        #     gv.setv(edge, 'headport', option_uid)
        #     gv.setv(edge, 'weight', '10')

    def draw(self, path):

        for state in self.kb.filter(facts.State):
            self.add_node(state)

        for jump in self.kb.filter(facts.Jump):
            self.add_edge(jump)

        for link in self.kb.filter(facts.OptionsLink):
            self.add_link(link)

        ######################
        # draw subgraph
        ######################

        subgraphs = []

        for event in self.kb.filter(facts.Event):
            subgraphs.append(SubGraph(uid=event.uid, color=HEAD_COLORS.EVENT_SUBGRAPH, members=event.members))

        for subquest in self.kb.filter(facts.SubQuest):
            subgraphs.append(SubGraph(uid=subquest.uid, color=HEAD_COLORS.SUBQUEST_SUBGRAPH, members=subquest.members))

        for subgraph in subgraphs:
            subgraph.find_children(subgraphs)

        for subgraph in subgraphs:
            subgraph.find_real_children()

        SubGraph.draw_hierarchy(subgraphs, self.graph, self.nodes)

        gv.layout(self.graph, 'dot');
        # gv.render(self.graph, 'dot')
        gv.render(self.graph, path[path.rfind('.')+1:], path)


    def create_label_for(self, fact):
        if isinstance(fact, facts.Start):
            return self.create_label_for_start(fact)
        if isinstance(fact, facts.Finish):
            return self.create_label_for_finish(fact)
        if isinstance(fact, facts.Choice):
            return self.create_label_for_choice(fact)
        if isinstance(fact, facts.Question):
            return self.create_label_for_question(fact)
        if isinstance(fact, facts.State):
            return self.create_label_for_state(fact)
        if isinstance(fact, facts.Event):
            return self.create_label_for_event(fact)
        if isinstance(fact, facts.Jump):
            return self.create_label_for_jump(fact)

        raise exceptions.CanNotCreateLabelForFactError(fact=fact)

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

    def create_label_for_choice(self, choice):
        return self.create_label_for_state(choice,
                                           bgcolor=HEAD_COLORS.CHOICE,
                                           requirements_bgcolor=HEAD_COLORS.CHOICE_REQUIREMENTS,
                                           actions_bgcolor=HEAD_COLORS.CHOICE_ACTIONS)

    def create_label_for_question(self, question):
        return self.create_label_for_state(question,
                                           bgcolor=HEAD_COLORS.QUESTION,
                                           requirements_bgcolor=HEAD_COLORS.QUESTION_REQUIREMENTS,
                                           actions_bgcolor=HEAD_COLORS.QUESTION_ACTIONS)

    def create_label_for_state(self,
                               state,
                               bgcolor=HEAD_COLORS.STATE,
                               requirements_bgcolor=HEAD_COLORS.STATE_REQUIREMENTS,
                               actions_bgcolor=HEAD_COLORS.STATE_ACTIONS):

        trs = []

        head_colspan = 1

        head = [td(i(state.uid))]

        if hasattr(state, 'type'):
            head.append(td(b(state.type), align='center'))
            head_colspan += 1

        requirement_colspan = 0

        for requirement in state.require:
            requirement_colspan = 2
            trs.append(tr(td(self.create_label_for_requirement(requirement), bgcolor=requirements_bgcolor, colspan=requirement_colspan)))

        actions_colspan = 0

        for action in state.actions:
            actions_colspan = 2
            trs.append(tr(td(self.create_label_for_action(action), bgcolor=actions_bgcolor, colspan=actions_colspan)))

        condition_colspan = 0
        if hasattr(state, 'condition'):
            condition_colspan = 2
            trs.append(tr(td('<b>conditions:</b>', bgcolor=bgcolor, colspan=condition_colspan)))
            for condition in state.condition:
                trs.append(tr(td('<b>if </b>'), td(self.create_label_for_requirement(condition), bgcolor=bgcolor)))

        results_colspan = 0

        if hasattr(state, 'results'):
            results_colspan = 2
            trs.append(tr(td('<b>results:</b>', bgcolor=bgcolor, colspan=results_colspan)))
            results_order = sorted(state.results.keys())
            for object_uid in results_order:
                trs.append(tr(td('<b>%s</b>' % object_uid), td(state.results[object_uid])))

        return table(tr(*head),
                     tr(td(state.description, colspan=max(head_colspan, requirement_colspan, actions_colspan, results_colspan))),
                     *trs,
                     bgcolor=bgcolor,
                     port=state.uid)

    def create_label_for_requirement(self, requirement):
        if isinstance(requirement, requirements.LocatedIn):
            return self.create_label_for_located_in(requirement)
        elif isinstance(requirement, requirements.LocatedNear):
            return self.create_label_for_located_near(requirement)
        elif isinstance(requirement, requirements.HasMoney):
            return self.create_label_for_has_money(requirement)
        elif isinstance(requirement, requirements.IsAlive):
            return self.create_label_for_is_alive(requirement)
        elif isinstance(requirement, requirements.LocatedOnRoad):
            return self.create_label_for_located_on_road(requirement)

        raise exceptions.CanNotCreateLabelForRequirementError(requirement=requirement)

    def create_label_for_action(self, action):
        if isinstance(action, actions.Message):
            return self.create_action_label_for_message(action)
        elif isinstance(action, actions.GiveReward):
            return self.create_action_label_for_give_reward(action)
        elif isinstance(action, actions.MoveNear):
            return self.create_action_label_for_move_near(action)
        elif isinstance(action, actions.Fight):
            return self.create_action_label_for_fight(action)
        elif isinstance(action, actions.DoNothing):
            return self.create_action_label_for_donothing(action)
        elif isinstance(action, actions.UpgradeEquipment):
            return self.create_action_label_for_upgrade_equipment(action)

        raise exceptions.CanNotCreateLabelForActionError(action=action)

    def create_label_for_event(self, event):
        return table(tr(td(i(event.uid))),
                     tr(td(event.description, colspan=2)),
                     bgcolor=HEAD_COLORS.EVENT,
                     port=event.uid)

    def create_label_for_jump(self, jump):
        trs = []

        if hasattr(jump, 'type'):
            trs.append(tr(td(jump.type, bgcolor=HEAD_COLORS.JUMP)))

        if hasattr(jump, 'condition'):
            trs.append(tr(td('TRUE' if jump.condition else 'FALSE', bgcolor=HEAD_COLORS.JUMP)))

        if hasattr(jump, 'markers') and jump.markers:
            strings = {relations.OPTION_MARKERS.HONORABLE: '[honor]',
                       relations.OPTION_MARKERS.DISHONORABLE: '[dishonor]',
                       relations.OPTION_MARKERS.AGGRESSIVE: '[aggression]',
                       relations.OPTION_MARKERS.UNAGGRESSIVE: '[peacefulness]'}

            for marker in jump.markers:
                trs.append(tr(td(strings[marker], bgcolor=HEAD_COLORS.JUMP_MARKER)))

        for action in jump.start_actions:
            trs.append(tr(td(self.create_label_for_action(action), bgcolor=HEAD_COLORS.JUMP_ACTIONS_START)))

        for action in jump.end_actions:
            trs.append(tr(td(self.create_label_for_action(action), bgcolor=HEAD_COLORS.JUMP_ACTIONS_END)))

        return table(*trs, port=jump.uid, border=0)

    def create_label_for_located_in(self, requirement):
        return '%s <b>is located in</b>&nbsp;%s' % (requirement.object, requirement.place)

    def create_label_for_located_near(self, requirement):
        return '%s <b>is located near</b>&nbsp;%s' % (requirement.object, requirement.place)

    def create_label_for_located_on_road(self, requirement):
        return ('%s <b>has passed</b>&nbsp;%d%%<b> of the road from</b>&nbsp;%s <b>to</b>&nbsp;%s' %
                (requirement.object, int(requirement.percents*100), requirement.place_from, requirement.place_to))

    def create_label_for_has_money(self, requirement):
        return '%s <b>has </b>&nbsp;%s <b>coins</b>' % (requirement.object, requirement.money)

    def create_label_for_is_alive(self, requirement):
        return '%s <b>is alive</b>' % (requirement.object)


    def create_action_label_for_move_near(self, requirement):
        if requirement.terrains:
            return '<b>send </b> %s<b>to wander near</b>&nbsp;%s<br/> among the terrains %s' % (requirement.object, requirement.place, requirement.terrains)
        elif requirement.place is None:
            return '<b>send </b> %s<b>to wander around</b><br/>' % requirement.object
        else:
            return '<b>send </b> %s<b>to wander near</b>&nbsp;%s<br/>' % (requirement.object, requirement.place)

    def create_action_label_for_message(self, message):
        return '<b>message:</b>&nbsp;%s' % message.type

    def create_action_label_for_give_reward(self, give_reward):
        return '<b>give reward to </b>&nbsp; %s <b>of type </b> %s <b>in the amount of</b> %.2f' % (give_reward.object, give_reward.type, give_reward.scale)

    def create_action_label_for_fight(self, fight):
        if fight.mob:
            return '<b>fight with</b>&nbsp; %s' % fight.mob

        if fight.mercenary is not None:
            if fight.mercenary:
                return '<b>fight with a mercenary</b>'
            else:
                return '<b>fight with someone other than a mercenary</b>'

        return '<b>fight with someone</b>'

    def create_action_label_for_donothing(self, donothing):
        return '<b>do nothing </b>&nbsp; %s' % donothing.type

    def create_action_label_for_upgrade_equipment(self, upgrade):
        if upgrade.cost is not None:
            return '<b>upgrade equipment for </b>&nbsp;%d <b>coins</b>' % upgrade.cost
        return '<b>upgrade equipment for free</b>'


def b(data): return '<b>%s</b>' % data
def i(data): return '<i>%s</i>' % data

def table(*trs, **kwargs):
    bgcolor = kwargs.get('bgcolor')
    port = kwargs.get('port')
    border = kwargs.get('border', 1)
    return '''<
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
    return '<tr BGCOLOR="#00ff00">%s</tr>' % ''.join(tds)

def td(body, port=None, **kwargs):
    bgcolor = kwargs.get('bgcolor')
    colspan = kwargs.get('colspan', 1)
    align = kwargs.get('align', 'left')
    border = kwargs.get('border', 0)
    return '''<td
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
