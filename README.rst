########
Questgen
########

Library for automatic quest generation. Allows creation of nested, nonlinear quests with events and various constraints (e.g., "the outcome of the quest for this character must only be positive") based on a world description given as predicates.

It also supports visualization of the generated quests. Example visualization: svg_

.. _svg: http://tiendil.org/static/trash/collect_debt.svg

Quest constructors are located in: ``./questgen/quests/``

The generator was developed for use in (now stopped) the text MMOZPG game The-Tale_, repository_

.. _The-Tale: http://the-tale.org

.. _repository: https://github.com/the-tale

Visualizations of all "basic" quest templates are stored in ``./questgen/svgs/``.

Details of the library's functionality can be found in the article on habrahabr_.

.. _habrahabr: http://habrahabr.ru/post/201680/

**************************
Legend for the Visualizer
**************************

The quest graph is displayed without modifications (e.g., all event variants are shown).

* gray nodes — start and end points of the quest;
* purple nodes — decision points;
* green nodes — regular story points;
* red nodes — conditional transitions;
* cyan outlines — subquests;
* darker backgrounds in nodes indicate conditions that must be met to transition to that story point;
* lighter backgrounds indicate actions that must be performed immediately upon entering that story point.
* yellow outlines — events;

************
Installation
************

::

   pip install questgen

**************
How it Works
**************

World states are described using predicates, e.g.:

.. code:: python

   LocatedIn(object='hero', place='place_1')

and stored in a knowledge base (KB).

Quests are described as directed connected graphs with one initial node and several terminal nodes (also stored in the KB).

* Each node has a list of requirements that must be satisfied before transitioning into it (e.g., the hero must be at a specific location);
* Each node has a list of actions to perform upon entry;
* Each edge has two lists of actions:
  * actions performed when starting to traverse the edge;
  * actions performed when finishing traversal (upon satisfying all requirements of the new node);
* Several types of nodes exist:
  * Initial — one per quest; the starting point;
  * Terminal — multiple per quest; determines quest outcomes (for connecting with other quests);
  * Regular — a narrative node; can have multiple incoming edges and exactly one outgoing edge;
  * Decision — can have multiple outgoing edges, selectable until one of the following nodes is reached.

Multiple nodes can be combined into an "event," which expands upon quest generation completion by removing all but one node. This allows for random events.

General generation procedure:

#. Create world description;
#. Create quest;
#. Process the quest (see example usage below);
#. Validate correctness;
#. Handle the quest in-game (the game should implement the code that executes while traversing the graph).

**Note:** Quest generation might fail occasionally (raising a ``questgen.exceptions.RollBackError``). This does not indicate a critical issue; it simply means the quest graph generated was unsuitable. Generation should be retried. A larger world description typically ensures faster and more successful quest generations by reducing collisions.

*******
Example
*******

See ``./helpers/example.py``

*************
Visualization
*************

Visualizer: ``./helpers/visualizer.py`` generates quest template images in ``./questgen/svgs/``.

Uses ``graphviz`` via the ``pygraph`` library.

*If generated images are incorrect (misaligned), install a newer version of graphviz.*

