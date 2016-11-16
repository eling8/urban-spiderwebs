import snap
import osmParser
from osmParser import ParseOSM

class osmAnalyzer(object):

    def __init__(self, graph_name):

        self._graph = graph_name # DO MORE PROCESSING
        # self._degree_distribution
        self.form_degree_distribution()
        # self._closeness_index
        self.form_closeness_centrality_index()
        # self._betweenness_index
        self.form_betweenness_centrality_index()
        # self._urbanness_index
        self.form_urbanness_index()

    def form_degree_distribution(self):
        """
        sets self._degree_distribution as a dict of degrees to count of nodes with that degree.
        :return: the histogram dict described above.
        """
        data = snap.TIntPrV()
        snap.GetDegCnt(self._graph, data)

        histogram = {}
        for item in DegToCntV:
            histogram[item.GetVal1()] = item.GetVal2()

        self._degree_distribution = histogram

    def form_closeness_centrality_index(self):
        pass

    def form_betweenness_centrality_index(self):
        pass

    def highest_closeness_centrality_node(self):
        pass

    def highest_betweenness_centrality_node(self):
        pass

    # Longitude and Latitude
    # ======================

    def calculate_area_per_node(self):
        """
        The area (sq kilometers) of our osm data bounding box (representing crude city bounds),
        divided by the number of nodes (e.g. intersections) in the city.
        :return: a float, with units km^2/node. Stores this in the class.
        """
        pass

    def form_urbanness_index(self, n=25):
        """
        The urbanness of a node is a measure of how close that node is to its nearby nodes.
        urbanness(node) := 1 / (average distance to closest n nodes)
        :return: None
        """
        pass

    def calculate_downtown_center(self):
        """
        Uses self._urbanness_index. Get the most "urban" location in the city.
        :return: (long, lat) tuple. both are floats.
        """
        pass

    # Use all this and make Tableau maps!



