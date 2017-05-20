
class Node(object):
    """
    A node in a markov chain.
    """

    def __init__(self, name):
        self.name = node['name']
        self.transitions = []

    def add_transition(self, transition):
        self.transitions.append(transition)

        total_weight = float(sum([t.weight for t in self.transitions]))

        for transition in self.transitions:
            transition.probability = transition.weight / total_weight


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

    def __init__(self, transition_list):

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
