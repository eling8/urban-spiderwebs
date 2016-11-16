from imposm.parser import OSMParser
import snap

class Node:
	def __init__(self, osmid, tags, coords):
		self._osmid = osmid
		self._tags = tags
		self._coords = (coords[1], coords[0])

	# OSM id, int
	def osmid(self):
		return self._osmid

	# tags, dict
	def tags(self):
		return self._tags

	# coordinates, (latitude, longitude)
	def coords(self):
		return self._coords

class Way:
	def __init__(self, osmid, tags, refs):
		self._osmid = osmid
		self._tags = tags
		self._refs = refs

	def osmid(self):
		return self._osmid

	def tags(self):
		return self._tags

	def refs(self):
		return self._refs

# simple class that handles the parsed OSM data.
class ParseOSM(object):
	nodes = {} # format: osmid : (osmid, {tags}, (long, lat))
	ways = {} # format: osmid : (osmid, {tags}, [references])

	def waysCallback(self, w):
		for tup in w:
			self.ways[tup[0]] = Way(tup[0], tup[1], tup[2])

	def nodesCallback(self, n):
		for tup in n:
			self.nodes[tup[0]] = Node(tup[0], tup[1], tup[2])

class GraphParser():
	# create snap graph from parsed nodes and ways
	def createGraph(self, osm):
		G = snap.TUNGraph.New()
		renumbered = {}
		counter = 0

		for osmid in osm.nodes:
			# renumber nodes to avoid int overflow
			renumbered[osmid] = counter
			G.AddNode(counter)
			counter += 1
			

		for osmid in osm.ways:
			refs = osm.ways[osmid].refs()
			for i in range(0, len(refs) - 1):
				start = refs[i]
				end = refs[i+1]

				# not all edges in a way are in nodes in the graph if at the boundary
				if start not in renumbered or end not in renumbered:
					continue
				G.AddEdge(renumbered[start], renumbered[end])

		idToOsmid = {}
		for osmid in renumbered:
			idToOsmid[renumbered[osmid]] = osmid

		return G, idToOsmid

def parseToGraph(file_name, concurrency=4):
	# instantiate counter and parser and start parsing
	o = ParseOSM()
	p = OSMParser(concurrency=concurrency, ways_callback=o.waysCallback, nodes_callback=o.nodesCallback)
	p.parse(file_name)

	G, idToOsmid = GraphParser().createGraph(o)
	return G, idToOsmid, o # graph, idToOsmid, ParseOSM object


G, idToOsmid, o = parseToGraph('stanford.osm')

print G.GetNodes()
nodeToBetweenness = snap.TIntFltH()
edgeToBetweenness = snap.TIntPrFltH()
betweenness = snap.GetBetweennessCentr(G, nodeToBetweenness, edgeToBetweenness)

maxCentrality = 0
maxNode = None
for node in nodeToBetweenness:
	print o.nodes[idToOsmid[node]].tags()
	print "Centrality:", nodeToBetweenness[node]
	if nodeToBetweenness[node] > maxCentrality:
		maxCentrality = nodeToBetweenness[node]
		maxNode = node

print maxCentrality
print o.nodes[idToOsmid[maxNode]].tags(), o.nodes[idToOsmid[maxNode]].coords()

