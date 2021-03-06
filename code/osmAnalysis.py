import snap
import osmParser
import math
import pickle
import os

ANALYSIS_PATH = "../analysis"
METADATA_PATH = "metadata"
# DATA_PATH := <defined in osmParser>

class osmNode(object):
    """
    UNUSED at the moment
    Simple af, just to group info together.
    """
    def __init__(self, nid, osmid=None, lat=None, long_=None):
        self.nid = nid
        self.osmid = osmid
        self.latitude = lat
        self.longitude = long_

class osmAnalyzer(object):

    def __init__(self, graph_name, autoprocess=True):

        self._city_name = graph_name

        # self._graph := a snap graph representing the street data
        # self._nid_to_osmid := a map of snap node id to osmid
        # self._osmid_to_coords := a map of osmid to (lat, long) geographical coordinates
        self.initialize_map_data(graph_name)

        if not autoprocess:
            return # Do not continue on to the processing. No idea when I would use this, but whatever.

        # Index-building
        # --------------
        # self._degree_distribution := map of degree value to count of nodes w/ that degree in self._graph
        # print "calculating degree"
        self.form_degree_distribution()
        # print 'degree dist:'
        # print self._degree_distribution
        
        # self._closeness_index := dict from self._graph node ids to closeness centrality
        # print "calculating closeness"
        self.form_closeness_centrality_index()

        self._most_close_nid = self.lowest_closeness_centrality_node()
        # print "closenessest node:"
        # print self._osmid_to_coords[self._nid_to_osmid[self._most_close_nid]]
        
        # self._node_between_index := dict from self._graph node ids to betweenness centrality
        # self._edge_between_index := dict from self._graph edges (as pairs of node ids)
        #                                 to betweenness centrality
        # print "calculating betweenness"
        self.form_betweenness_centrality_index()

        # self._urbanness_index := dict from self._graph node ids to urbanness
        # print "calculating urbanness"
        self.form_urbanness_index()

        # Specific statistics operations
        # ------------------------------
        # 3 centralities. Get coordinates with _nid_to_osmid and _osmid_to_coords.
        self._most_between_nid = self.highest_betweenness_centrality_node()
        self._most_between_eid = self.highest_betweenness_centrality_edge()

        # print "most between node:"
        # print self._osmid_to_coords[self._nid_to_osmid[self._most_between_nid]]

        self._most_close_nid = self.lowest_closeness_centrality_node()

        # self._city_area := the area of the city as a float. crude box approximation.
        # self._km2_per_node := <see below>
        self._km2_per_node = self.calculate_citywide_area_per_node()
        
        # downtown
        self._most_urban_nid = self.calculate_downtown_center()

    def initialize_map_data(self, name):
        graph, id_osmid_map, coord_data = osmParser.loadFromFile(name)
        self._graph = graph
        self._nid_to_osmid = id_osmid_map
        self._osmid_to_coords = coord_data

        # TECH DEBT: _osmid_to_coords is wrong, has coordinates of osmids that are not mapped to an
        #    actual node in the snap graph. Removing those below.
        # valid_osmids = self._nid_to_osmid.values()
        # all_osmids = self._osmid_to_coords.keys()
        # for osmid in all_osmids:
        #     if osmid not in valid_osmids:
        #         self._osmid_to_coords.pop(osmid, None)

    def _rehydrate_snap_graph(self):
        """
        IMPORTANT: run this after restoring from a pickle.
        After restoring this osmAnalyzer from a pickled state, it doesn't have its snap graph because
            the snap graph object doesn't work with the pickle API; I chopped off self._graph before
            pickling.
        This restores the snap graph from the data/ folder.
        """
        self._graph = snap.TUNGraph.Load(snap.TFIn(DATA_PATH + self._city_name + ".graph"))

    def summarize(self):
        """
        Prints some shit.
        """
        print "City name:", self._city_name
        print 'degree dist:'
        print self._degree_distribution
        print "km2 per node:"
        print self._km2_per_node
        print "city area:"
        print self._city_area
        print "most between node:"
        print self._osmid_to_coords[self._nid_to_osmid[self._most_between_nid]]
        print "closenessest node:"
        print self._osmid_to_coords[self._nid_to_osmid[self._most_close_nid]]
        print "urbanest node:"
        print self._osmid_to_coords[self._nid_to_osmid[self._most_urban_nid]]

    # ================
    # Graph Properties
    # ================
    
    def form_degree_distribution(self, normalized=False):
        """
        sets self._degree_distribution as a dict of degrees to count of nodes with that degree.
        :return: the histogram dict described above.
        """
        data = snap.TIntPrV()
        snap.GetDegCnt(self._graph, data)

        histogram = {}
        for item in data:
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
        snap.GetBetweennessCentr(self._graph, node_data, edge_data, 1.0)

        node_index = {}
        for nid in node_data:
            node_index[nid] = node_data[nid]

        edge_index = {}
        for edge_tuple in edge_data:
            edge = (edge_tuple.GetVal1(), edge_tuple.GetVal2())
            edge_index[edge] = edge_data[edge_tuple]

        self._node_between_index = node_index
        self._edge_between_index = edge_index

    def lowest_closeness_centrality_node(self, auto_tiebreak=True):
        """
        closeness of an edge/node := average distance to any node in the graph.
        :return: the node(s) with lowest closeness centrality.
        """
        best = []

        lowest_value = min(self._closeness_index.values())
        for nid in self._closeness_index:
            if self._closeness_index[nid] == lowest_value:
                if auto_tiebreak:
                    return nid
                else:
                    best.append(nid)

        assert(len(best) != 0) # It should never be empty; must exist a key with the lowest value.
        return best

    def highest_betweenness_centrality_node(self, auto_tiebreak=True):
        """
        :return: the node id of the node with the highest betweenness centrality.
        """
        return self._highest_betweenness_centrality(auto_tiebreak, self._node_between_index)

    def highest_betweenness_centrality_edge(self, auto_tiebreak=True):
        """
        :return: the edge (as a (nid1, nid2) pair) with the highest betweenness centrality.
        """
        return self._highest_betweenness_centrality(auto_tiebreak, self._edge_between_index)

    def _highest_betweenness_centrality(self, auto_tiebreak, target_dict):
        """ Helper function for the above two.
        """
        # Try to always use the auto_tiebreak feature. I haven't prepared this class for multiple bests.
        best = []

        highest_value = max(target_dict.values())
        for id_ in target_dict:
            if target_dict[id_] == highest_value:
                if auto_tiebreak:
                    return id_
                else:
                    best.append(id_)

        assert(len(best) != 0) # It should never be empty; must exist a key with the highest value.
        return best


    # ======================
    # Longitude and Latitude
    # ======================

    def calculate_citywide_area_per_node(self):
        """
        The area (sq kilometers) of our osm data bounding box along latitude and longitude
            axes (representing crude city bounds), divided by the number of nodes
            (e.g. intersections) in the city.
        :return: a float, with units km^2/node.
        """
        coordinates = self._osmid_to_coords.values()
        latitudes = [coord[0] for coord in coordinates]
        longitudes = [coord[1] for coord in coordinates]
        lat_max = max(latitudes)
        lat_min = min(latitudes)
        long_max = max(longitudes)
        long_min = min(longitudes)
        R = 6371.0

        # http://mathforum.org/library/drmath/view/63767.html
        # A = (pi/180)R^2 |sin(lat1)-sin(lat2)| |lon1-lon2|
        self._city_area = math.pi/180.0 * (R ** 2) * abs(math.sin(lat_max) - math.sin(lat_min)) * abs(long_max - long_min)
        return self._city_area / len(coordinates)

    @staticmethod
    def _distance(lat1, long1, lat2, long2):
        """ L2 norm, i.e. euclidean norm, without the sqrt.
            Because this distance is only relevant in the context of comparing urbanness within 1 city,
            I won't worry too much about actual physical accuracy.
        """
        return (lat1-lat2) ** 2 + (long1-long2) ** 2

    def _get_urbanness(self, nid, n):
        """
        Helper for calculating the urbanness of one single osm node.
        :return: urbanness(node) := 1 / (average distance to closest n nodes)
        """
        osmid = self._nid_to_osmid[nid]
        n_lat, n_lon = self._osmid_to_coords[osmid]

        coordinates = self._osmid_to_coords.values()
        distances = []
        for lat, lon in coordinates:
            distances.append(self._distance(lat, lon, n_lat, n_lon))
        
        # Can optimze this with heapq library and partial sorting.
        distances = sorted(distances)[:n]
        urbanness = 1.0 * len(distances) / sum(distances)
        return urbanness

    def form_urbanness_index(self, n=100):
        """
        NOTE: I invented this measure.
        In calculations, I make the assumption that within a single city, the curvature of the earth is trivial.
        Distance is therefore approximated by the L2 norm between two geographical coordinates.

        The urbanness of a node is a measure of how close that node is to its nearby nodes.
        urbanness(node) := 1 / (average distance to closest n nodes)
        """
        index = {}
        for node in self._graph.Nodes():
            nid = node.GetId()
            index[nid] = self._get_urbanness(nid, n)

        self._urbanness_index = index


    def calculate_downtown_center(self):
        """
        Uses self._urbanness_index. Get the most "urban" location in the city.
        :return: a node id.
        """
        best_nid = None
        best_val = 0
        for nid in self._urbanness_index:
            if self._urbanness_index[nid] > best_val:
                best_val = self._urbanness_index[nid]
                best_nid = nid
        return best_nid

    # Use all this and make Tableau maps??


def rehydrate(city_name):
    """
    restore a osmAnalyzer object from the .stats file of a given city.
    """
    oa_pickle_file = open(os.path.join(ANALYSIS_PATH, city_name + ".stats"), 'r')
    oa = pickle.load(oa_pickle_file)


if __name__ == "__main__":
    cities = []
    """
  , "berlin_germany"
  , "bogota_colombia"
  , "buenos-aires_argentina"
  , "cairo_egypt" # DONE
  , "cape-town_south-africa"
  , "doha_qatar"
  , "istanbul_turkey"
  , "jakarta_indonesia"
  , "jerusalem_israel"
  , "london_england"
  , "los-angeles_california"
  , "mexico-city_mexico" # DONE
  , "nairobi_kenya"
  , "new-york_new-york"
  , "rio-de-janeiro_brazil"
  , "rome_italy"
  , "saint-petersburg_russia"
  , "san-francisco_california"
  , "santiago_chile"
  , "sao-paulo_brazil"
  , "seoul_south-korea"
  , "shanghai_china"
  , "sydney_australia"
  , "tokyo_japan"
  , "vancouver_canada"
  """

    exists = os.listdir(ANALYSIS_PATH)

    for city in cities:

        print "Starting", city

        # if city + ".stats" in exists:
        #     print "skipped", city
        #     continue

        oa = osmAnalyzer(city)
        oa.summarize()
        # Remove the snap graph to prepare for pickling.
        oa._graph = None

        city_path = os.path.join(ANALYSIS_PATH, city + ".stats")

        analysis_out = open(city_path, 'w')
        pickle.dump(oa, analysis_out, 1)

        print "Done with", city


