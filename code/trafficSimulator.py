from dualGraph import DualGraph
from Car import DualGraphCar
import osmParser
from collections import defaultdict
from collections import Counter
import math
import pickle

class TrafficSimulator(object):

    def __init__(self, dual_graph, num_cars):
        self.BASE_SPEED = 5.0
        self.TOP_SPEED = 15.0


        # A dictionary of car counts for every street
        self.car_counts = defaultdict(lambda: 0.0)

        # self.city_roads
        # self.possible_endpoints
        self.initialize(dual_graph, num_cars)

        self.cumulative_car_data = Counter()
        self.traffic_video_data = []


    def initialize(self, graph, cars):
        """
        :param graph: dual graph to initialize to.
        :param cars: # cars
        :return: None
        """
        self.city_roads = graph

        max_length = sorted(self.city_roads.street_weights.values())[len(self.city_roads.street_weights) / 2]
        self.possible_endpoints = [node.GetId() for node in self.city_roads.graph.Nodes()
                                   if self.city_roads.street_weights[node.GetId()] < max_length]

        self.setup_simulation(cars)

    def traffic_coefficient(self, street_nid):
        """
        An arbitrary function to simulate traffic slowing down cars.
        Currently an exponentially decreasing model.
        :param street_nid: the street we want a coeff for.
        :return: floating-point number
        """
        count = self.car_counts[street_nid]
        # float(count)-1 should never be less than 0; only streets with a car on them call this function.
        return math.pow(0.25, (float(count)-1) / self.city_roads.street_weights[street_nid])

    def setup_simulation(self, N):
        """
        Initialize the simulation.
        :param N: # of cars
        :return: None
        """
        self.cars = []
        for i in xrange(N):
            if i % 1000 == 0:
                print "created cars", i
            c = DualGraphCar("car_" + str(i), self)
            self.cars.append(c)
            # print [self.city_roads.street_coordinates[i] for i in c._itinerary]

    def run_simulation(self, max_ticks, frame_rate, type='data'):
        """
        Runs the simulation for max_ticks time steps, taking a picture every frame_rate steps.
        :param max_ticks: some #
        :param frame_rate: some #
        :return: None
        """
        for i in xrange(max_ticks):
            if i % 1000 == 0:
                print "generation", i
            self.tick()
            if i % frame_rate == 0:
                if type == 'data':
                    self.add_snapshot()
                elif type == 'video':
                    self.traffic_video_data.append(self.take_snapshot())


    def tick(self):
        for car in self.cars:
            car.tick()
            #roadweight = self.city_roads.street_weights[car._itinerary[car.itinerary_tracking_index]]
            #print car.name, "has travelled", car.progress, "out of", roadweight, "on street %s / %s"
            # % (car.itinerary_tracking_index, len(car._itinerary))


    def add_snapshot(self):
        """
        Taking a picture of the current car distribution.
        :return: a counter of how many cars are on each street coordinate
        """
        for car in self.cars:
            self.cumulative_car_data[car.position] += 1
        # used for debugging:
        #return car_data

    def take_snapshot(self):
        """
        Same thing as above but returns 1 snapshot instead of adding snapshot to cumulative data.
        """
        picture = Counter()
        for car in self.cars:
            picture[car.position] += 1
        return picture


if __name__ == "__main__":

    TYPE = 'video'


    #cities = open("../citynames_1.txt", 'r').read().strip().split('\n')
    cities = ["san-francisco_california"]

    for city in cities:
        print "starting the city of", city
        dg = DualGraph(city)
        tsim = TrafficSimulator(dg, num_cars=3500)
        tsim.run_simulation(10000, 20, type=TYPE) # 25 fps, 40 seconds of gif

        print "pickling", city

        if TYPE == 'data':
            output = open("../data/" + city + '.tsd', 'w')
            pickle.dump(tsim.cumulative_car_data, output, 1)

        elif TYPE == 'video':
            output = open("../data/" + city + '.tvd', 'w')
            pickle.dump(tsim.traffic_video_data, output, 1)

            print "done"


