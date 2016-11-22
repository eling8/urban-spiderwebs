import snap


class DualGraph(object):
    """
    A dual representation of a road network. All streets are nodes, and all intersections are represented by edges
     between every pair of nodes that meet at that intersection.
    This will be used in traffic simulation.
    """


    def __init__(self, snap_graph):

        # For getting a new node id to set an edge to.
        self.NID_GENERATOR = 0

        # This will track edge weights, the transition probabilities between two nodes.
        self.weights = {}

        # Keep track of which edges in the snap_graph are which nodes in the dual graph.
        self._names = {}

        # An instance of PUNGraph from snap.
        self.graph = self._create_dual_representation(snap_graph)


    def _get_nid(self):
        """
        :return: the next integer we havent used for nids.
        """
        self.NID_GENERATOR += 1
        return self.NID_GENERATOR


    @staticmethod
    def _norm_edge(n1, n2):
        """
        :param n1: first node id
        :param n2: second node id
        :return: ordered edge (a, b) with b >= a
        """
        return (n1, n2) if n2 > n1 else (n2, n1)


    def _create_all_pairwise_edges(self, dual_nodes, graph):
        length = len(dual_nodes)
        prob = 1.0 / (length-1) # in the absence of transition probabilities, assume uniform

        for i in xrange(length):
            for j in xrange(i+1, length):
                n1 = dual_nodes[i]
                n2 = dual_nodes[j]
                e1 = n1 if n1 < n2 else n2
                e2 = n1+n2 - e1

                graph.AddEdge(e1, e2)
                self.weights[(e1, e2)] = prob



    def _create_dual_representation(self, snap_graph):
        """
        Takes in a traditional SNAP graph of a road network, and creates an instance of DualGraph that is the dual
         representation of that same road network.
        self._weights is also modified to have all the edge weights during this function.

        :param snap_graph: a undirected snap graph.
        :return: another undirected snap graph, transformed to dual.
        """
        graph = snap.TUNGraph.New()

        for edge in snap_graph.Edges():
            nid = self._get_nid()
            edge = self._norm_edge(edge.GetSrcNId(), edge.GetDstNId())
            self._names[edge] = nid
            graph.AddNode(nid)

        for intersection in snap_graph.Nodes():
            dual_nodes = []
            deg = intersection.GetOutDeg()

            if deg < 2: continue

            for i in xrange(deg):
                edge = self._norm_edge(intersection.GetId(), intersection.GetOutNId(i))
                dual_nodes.append(self._names[edge])

            self._create_all_pairwise_edges(dual_nodes, graph)

        return graph


if __name__ == "__main__":
    graph = snap.TUNGraph.New()

    graph.AddNode(10)
    graph.AddNode(11)
    graph.AddNode(12)
    graph.AddNode(13)
    graph.AddNode(14)
    graph.AddNode(141)
    graph.AddNode(142)
    graph.AddNode(1421)

    graph.AddEdge(10, 11)
    graph.AddEdge(10, 12)
    graph.AddEdge(10, 13)
    graph.AddEdge(10, 14)
    graph.AddEdge(14, 141)
    graph.AddEdge(14, 142)
    graph.AddEdge(142, 1421)

    dual_graph = DualGraph(graph)
    new_graph = dual_graph.graph

    print "nodes:"
    for node in new_graph.Nodes():
        print node.GetId()
    print "edges:"
    for edge in new_graph.Edges():
        print "(%s, %s)" % (edge.GetSrcNId(), edge.GetDstNId())

    print dual_graph._names
    print dual_graph.weights




