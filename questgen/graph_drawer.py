# coding:utf-8
from collections import defaultdict

import gv

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

class HEAD_COLORS(object):
    START = '#eeeeee'
    STATE = '#ddffdd'
    FINISH = '#eeeeee'

    START_REQUIREMENTS = '#dddddd'
    STATE_REQUIREMENTS = '#cceecc'
    FINISH_REQUIREMENTS = '#dddddd'


class Drawer(object):

    def __init__(self, knowledge_base):
        self.kb = knowledge_base


    def draw(self, path):

        graph = gv.strictdigraph('quest')

        gv.setv(graph, 'rankdir', 'LR')
        gv.setv(graph, 'splines', 'ortho')

        tags = defaultdict(set)

        nodes = {}

        for state in self.kb.filter(State):
            node = gv.node(graph, state.uid)
            gv.setv(node, 'shape', 'plaintext')
            gv.setv(node, 'label', self.create_label_for(state).encode('utf-8'))
            gv.setv(node, 'fontsize', '10')

            nodes[state.uid] = node

            for tag in state.tags:
                tags[tag].add(state.uid)

        for jump in self.kb.filter(Jump):
            edge = gv.edge(nodes[jump.state_from], nodes[jump.state_to])
            gv.setv(edge, 'tailport', jump.state_from)
            gv.setv(edge, 'headport', jump.state_to)

            # for tag in jump.tags:
            #     tags[tag].add(jump.state_to)

        for tag, elements in tags.items():
            subgraph = gv.graph(graph, 'cluster_' + tag)
            for node_uid in elements:
                gv.node(subgraph, node_uid)

            gv.setv(subgraph, 'label', tag)
            gv.setv(subgraph, 'rank', 'same')
            gv.setv(subgraph, 'shape', 'box')
            gv.setv(subgraph, 'bgcolor', '#ffffdd')

        gv.layout(graph, 'dot');
        # gv.render(graph, 'dot')
        gv.render(graph, path[path.rfind('.')+1:], path)


    def create_label_for(self, state):
        if isinstance(state, Start):
            return self.create_label_for_start(state)
        if isinstance(state, Finish):
            return self.create_label_for_finish(state)
        if isinstance(state, State):
            return self.create_label_for_state(state)
        return None

    def create_label_for_start(self, start):
        return self.create_label_for_state(start, bgcolor=HEAD_COLORS.START, requirements_bgcolor=HEAD_COLORS.START_REQUIREMENTS)

    def create_label_for_finish(self, finish):
        return self.create_label_for_state(finish, bgcolor=HEAD_COLORS.FINISH, requirements_bgcolor=HEAD_COLORS.FINISH_REQUIREMENTS)

    def create_label_for_state(self, state, bgcolor=HEAD_COLORS.STATE, requirements_bgcolor=HEAD_COLORS.STATE_REQUIREMENTS):

        requirements = []

        for requirement in state.require:
            if isinstance(requirement, LocatedIn):
                requirements.append(self.create_tr_for_located_in(requirement, bgcolor=requirements_bgcolor))

        return table(tr(td(i(state.uid))),
                     tr(td(b(state.label))),
                     tr(td(state.description, colspan=2)),
                     *requirements,
                     bgcolor=bgcolor,
                     port=state.uid)

    def create_tr_for_located_in(self, requirement, bgcolor):
        return tr(td(u'%s <b>находится в </b> %s' % (requirement.object, requirement.place), bgcolor=bgcolor))


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
