from dualGraph import DualGraph
import random
from Queue import PriorityQueue
from collections import defaultdict


class DualGraphCar(object):
    def __init__(self, name, parent_simulator):

        self.simulator = parent_simulator
        self.roadmap = parent_simulator.city_roads
        self.name = name
        self.completed_trips = 0
        self.H_WEIGHT = 1000000

        # self._start_nid, for shortest path finding
        # self._stop_nid,  for shortest path finding
        # self._itinerary
        self._setup_trip()
        self.simulator.car_counts[self._start_nid] = self.simulator.car_counts[self._start_nid] + 1

        self.itinerary_tracking_index = 0  # The index of the starting, current street.
        self.progress = 0.0  # How far down the current street. moves on when exceeds the street weight.


    @property
    def position(self):
        return self.roadmap.street_coordinates[self._itinerary[self.itinerary_tracking_index]]

    def _heuristic(self, n1, n2):
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

        path.reverse()
        return path

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
        waiting_line.put((0, self._start_nid))
        in_line.add(self._start_nid)
        costs[self._start_nid] = 0.0

        while not waiting_line.empty():
            curr_node = waiting_line.get(block=False)[1]  # second element, the node ID, not the priority
            in_line.remove(curr_node)
            evaluated.add(curr_node)

            # if this is our destination, end. May not be *the* shortest path, but it is a good estimate and it
            # saves us from having to traverse the whole graph. A strong heuristic helps make this estimate better.
            if curr_node == self._stop_nid:
                return self._get_travelled_path(previous_of, self._stop_nid)

            current_cost = costs[curr_node] + self.roadmap.street_weights[curr_node]

            curr_ni = self.roadmap.graph.GetNI(curr_node)
            deg = curr_ni.GetOutDeg()
            for i in xrange(deg):
                nbr = curr_ni.GetOutNId(i)

                if nbr in in_line or nbr in evaluated: continue

                if current_cost < costs[nbr]:
                    costs[nbr] = current_cost
                    previous_of[nbr] = curr_node

                new_priority = 0 if nbr == self._stop_nid else costs[nbr] + self._heuristic(nbr, self._stop_nid)
                waiting_line.put((new_priority, nbr))
                in_line.add(nbr)

        # No path was found. SHOULD NOT REACH HERE, all cities are connected.
        return [None]

    def _setup_trip(self):
        """
        Select 2 nodes.
        """
        # Uniformly at random select TWO nodes from possible endpoints.
        self._start_nid = random.choice(self.simulator.possible_endpoints)
        self._stop_nid = self._start_nid
        while self._start_nid == self._stop_nid:
            self._stop_nid = random.choice(self.simulator.possible_endpoints)

        self._itinerary = self._shortest_path()

    def tick(self):
        """
        With some probability a function of the # of cars on that street, this car increments self.progress.
        """
        current_street = self._itinerary[self.itinerary_tracking_index]

        # increment is our speed. We set it to traffic * (|street weight| / [choice 8-12]) units per time step initially.
        # BASE and TOP speeds are min and max caps in trafficSimulator.
        increment = 1.0 / (8 + 4*random.random()) \
                        * self.simulator.traffic_coefficient(current_street) \
                        * self.roadmap.street_weights[current_street]
        if increment < self.simulator.BASE_SPEED: increment = self.simulator.BASE_SPEED
        if increment > self.simulator.TOP_SPEED: increment = self.simulator.TOP_SPEED

        self.progress += increment

        # Move on to the next street in the itinerary.
        if self.progress >= self.roadmap.street_weights[current_street]:

            self.itinerary_tracking_index += 1
            self.progress = 0.0

            # yay, done with this itinerary! reincarnate the car.
            if self.itinerary_tracking_index == len(self._itinerary) - 1:
                self.completed_trips += 1
                self._setup_trip()
                self.itinerary_tracking_index = 0

            # Update self.car_counts in the parent simulator
            self.simulator.car_counts[current_street] = self.simulator.car_counts[
                                                            current_street] - 1  # i.e. the street we exited
            if self.simulator.car_counts[current_street] == 0:
                del self.simulator.car_counts[current_street]

            next_street = self._itinerary[self.itinerary_tracking_index]
            self.simulator.car_counts[next_street] = self.simulator.car_counts[next_street] + 1
