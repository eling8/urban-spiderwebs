from dualGraph import DualGraph
import random
from queue import PriorityQueue
from collections import defaultdict

class DualGraphCar(object):

    def __init__(self, dual_graph):

        self.roadmap = dual_graph
        self.H_WEIGHT = 1000000

        # self._start_nid
        # self._stop_nid
        # self._itinerary
        self._setup_trip()

        self.position = self._start_nid   # The current street.
        self.progress = 0                 # How far down the current street. moves on when reaches the street weight.


    @staticmethod
    def heuristic(n1, n2):
        return self.H_WEIGHT * self.roadmap._distance(self.roadmap.street_coordinates[n1],
                                                      self.roadmap.street_coordinates[n2])  # 1 million coeff is adjustable

    @staticmethod
    def _get_travelled_path(previous, end_nid):
        """
        reconstruct the path our A* search took to get from self._start_nid to self._stop_nid.
        """
        path = [end_nid]

        current = end_nid
        while current in previous:
            path.append(previous[current])
            current = previous[current]

        return path.reverse()

    def _shortest_path(self):
        """
        Return a sequence of nodes that leads from src to dest.
        :return: a list of nids
        run A* search.
        """
        previous_of = {}
        costs = defaultdict(lambda: float("inf"))

        in_line = set()
        waiting_line = PriorityQueue()
        evaluated = set()

        # A tuple (priority, node, distance so far
        waiting.put((0, self._start_nid))
        in_line.add(self._start_nid)
        costs[self._start_nid] = 0.0

        while not waiting_line.empty():
            curr_node = waiting_line.get()[1]
            in_line.remove(curr_node)
            evaluated.add(curr_node)

            # if this is our destination, end. May not be *the* shortest path, but it is a good estimate and it
            # saves us from having to traverse the whole graph. A strong heuristic helps make this estimate better.
            if curr_node == self._stop_nid:
                return self._get_travelled_path(previous_of, self._stop_nid)

            current_cost = costs[curr_node] + self.roadmap.street_weights[curr_node]

            deg = curr_node.GetOutDeg()
            for i in xrange(deg):
                nbr = curr_node.GetOutNId(i)

                if nbr in in_line or nbr in evaluated: continue

                if current_cost < costs[nbr]:
                    costs[nbr] = current_cost
                    previous_of[nbr] = curr_node

                new_priority = 0 if nbr == self._stop_nid else costs[nbr] + self.heuristic(nbr, self._stop_nid)
                waiting_line.put((new_priority, nbr))
                in_line.add(nbr)

        # No path was found
        return [None]

    def _setup_trip(self):
        """
        Select 2 nodes.
        """
        selections = []
        parameter = self.roadmap.GetNodes()

        # Uniformly at random select two nodes. Mathematical hack.
        for node in self.roadmap.Nodes():
            if random.random() < 1.0 / parameter:
                selections.append(node.GetId())
            if len(selections) > 1:
                break
            parameter -= 1

        self._start_nid = selections[0]
        self._stop_nid = selections[1]

        self._itinerary = self._shortest_path()



    def tick(self):
        """
        With some probability a function of the # of cars on that street, this car increments self.progress.
        """
