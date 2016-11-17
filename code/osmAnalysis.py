import snap
import osmParser


class osmAnalyzer(object):

    def __init__(self, graph_name):
        
        # self._graph
        # self._id_to_osmid
        # self._osm
        self.initialize_map_data(graph_name)

        # self._degree_distribution 
        self.form_degree_distribution()
        
        # self._closeness_index := dict from self._graph node ids to closeness centrality
        self.form_closeness_centrality_index()
        
        # self._node_between_index := dict from self._graph node ids to betweenness centrality
        # self._edge_between_index := dict from self._graph edges (as pairs of node ids)
        #                                 to betweenness centrality
        self.form_betweenness_centrality_index()
        
        # self._urbanness_index := dict from self._graph node ids to urbanness
        self.form_urbanness_index()

    def initialize_map_data(name):
        graph, id_osmid_map, osm_data = osmParser.loadFromFile(name)
        self._graph = graph
        self._id_to_osmid = id_osmid_map
        self._osm = osm_data

    def form_degree_distribution(self, normalized=False):
        """
        sets self._degree_distribution as a dict of degrees to count of nodes with that degree.
        :return: the histogram dict described above.
        """
        data = snap.TIntPrV()
        snap.GetDegCnt(self._graph, data)

        histogram = {}
        for item in DegToCntV:
            histogram[item.GetVal1()] = item.GetVal2()

        if normalized:
            total = sum(histogram.values())
            for deg in histogram:
                histogram[deg] = 1.0 * shistogram[deg] / total

        self._degree_distribution = histogram


    def form_closeness_centrality_index(self):
        index = {}
        for node in self._graph.Nodes():
            nid = node.GetId()
            index[nid] = snap.GetClosenessCentr(self._graph, nid)
        
        self._closeness_index = index

    def form_betweenness_centrality_index(self):
        """
        Makes a really good map of what edges are travelled the most! 11/15 224 lecture.
        Can color edges based on their betweenness centrality later, for a cool vizualization of
        city centers and traffic approximation.

        Betweenness of an edge/node := # of shortest paths that go through that edge/node
        """
        node_data = snap.TIntFltH()
        edge_data = snap.TIntPrFltH()
        snap.GetBetweennessCentr(self._graph, node_data, edge_data, NodeFrac=1.0)

        node_index = {}
        for nid in node_data:
            node_index[nid] = node_data[nid]

        edge_index = {}
        for edge_tuple in edge_data:
            edge = (edge_tuple.GetVal1(), edge_tuple.GetVal2())
            edge_index[edge] = edge_data[edge_tuple]

        self._node_between_index = node_index
        self._edge_between_index = edge_index

    def highest_closeness_centrality_node(self):
        """
        closeness of an edge/node := average distance to any node in the graph
        """
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
        NOTE: I invented this measure.

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



