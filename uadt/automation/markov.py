from numpy.random import choice


class Node(object):
    """
    A node in a markov chain.
    """

    def __init__(self, name):
        self.name = name
        self.transitions = []

    def add_transition(self, transition):
        self.transitions.append(transition)

        total_weight = float(sum([t.weight for t in self.transitions]))

        for transition in self.transitions:
            transition.probability = transition.weight / total_weight

    def random_move(self):
        """
        Takes a random step from this node, picking from outgoing transitions.
        """

        transition_probabilities = [t.probability for t in self.transitions]
        return choice(self.transitions, 1, p=transition_probabilities)[0]


class Transition(object):
    """
    Represents a transition in the chain.
    """

    def __init__(self, source, destination, name, weight):
        self.source = source
        self.destination = destination
        self.name = name
        self.weight = weight
        self.probability = 1.0


class MarkovChain(object):
    """
    Represents a first order markov chain.
    """

    def __init__(self, transition_list, initial, final):

        # Collect all nodes
        node_names = set()

        for info in transition_list:
            node_names.add(info['start_node'])
            node_names.add(info['end_node'])

        # Create a node object for each node name
        self.nodes = {}
        for name in node_names:
            self.nodes[name] = Node(name)

        # Create transition objects and assign them to nodes
        # from which they originate
        for info in transition_list:
            transition = Transition(
                self.nodes[info['start_node']],
                self.nodes[info['end_node']],
                info['name'],
                info['weight']
            )

            self.nodes[info['start_node']].add_transition(transition)

        # Mark the initial and final nodes
        self.initial = self.nodes[initial]
        self.final = self.nodes[final]

        self.current = self.initial

    def random_walk(self, length):
        """
        Performs a random walk on states of the markov chain. Once the length
        of the walk is exceeded, we take the shortest path to the final node.
        """

        for step_number in range(length):
            transition = self.current.random_move()
            yield transition.name
            self.current = transition.destination

        # Make sure we end up in the finish state
        for transition in self.get_shortest_path(self.current, self.final):
            yield transition.name
            self.current = transition.destination

    def get_shortest_path(self, start, end):
        """
        Searches for the shortest path from 'start' to the 'end'. Using
        Breath-first search algorithm is sufficient here since the distance
        metric is the number of steps required (every edge has equal weight).
        """

        shortest_path = None
        to_visit = []
        visited = set()

        # We start at the 'start', having walked an empty path
        to_visit.append((start, []))

        while to_visit:
            node, path = to_visit.pop(0)

            # If we got to the end, let's stop searching
            if node == end:
                shortest_path = path
                break

            # Else schedule all non-visited neighbours for a visit
            to_visit.extend(
                (t.destination, [t] + path)
                for t in node.transitions
                if t.destination not in visited
            )

            # Mark all neighbours as visited (so that some other vertex does
            # not plan to go through too)
            visited.update(set([t.destination for t in node.transitions]))

        if shortest_path is None:
            raise ValueError("Path between {0} and {1} was not found"
                             .format(start, end))

        # Otherwise we have the shortest path, let's read it out
        yield from shortest_path
