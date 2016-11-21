if __name__ == "__main__":
	from imposm.parser import OSMParser

import xml.etree.ElementTree as ET


import snap
import json
import pickle
import os

DATA_PATH = "../data/"

# create snap graph from parsed nodes and ways
def createGraph(nodes, edges):
	G = snap.TUNGraph.New()
	renumbered = {}
	idToOsmid = {}
	counter = 0

	for osmid in edges:
		refs = edges[osmid]

		for i in range(0, len(refs) - 1):
			start = refs[i]
			end = refs[i+1]

			# not all edges in a way are in nodes in the graph if at the boundary
			if start not in nodes or end not in nodes:
				continue

			# if way is a road, add nodes if they haven't been added before
			if start not in renumbered:
				renumbered[start] = counter
				idToOsmid[counter] = start
				G.AddNode(counter)
				counter += 1
			if end not in renumbered:
				renumbered[end] = counter
				idToOsmid[counter] = end
				G.AddNode(counter)
				counter += 1

			G.AddEdge(renumbered[start], renumbered[end])

	return G, idToOsmid

def parseToGraph(file_name):
	tree = ET.parse(file_name)
	root = tree.getroot()

	nodes = {}
	edges = {}
	minCoord = ()
	maxCoord = ()

	for child in root:
		if child.tag == "node":
			lat = child.attrib['lat']
			lon = child.attrib['lon']
			id = child.attrib['id']

			nodes[id] = (lat, lon)

		elif child.tag == "way":
			types = [tag.attrib['k'] for tag in child.findall('tag')]
			id = child.attrib['id']

			if 'highway' in types:
				wayNodes = []
				for node in child.findall('nd'):
					nodeId = node.attrib['ref']
					wayNodes.append(nodeId)

				edges[id] = wayNodes

		elif child.tag == "bounds":
			minCoord = (child.attrib['minlat'], child.attrib['minlon'])
			maxCoord = (child.attrib['maxlat'], child.attrib['maxlon'])


	G, idToOsmid = createGraph(nodes, edges)

	return G, idToOsmid, nodes

def saveToFile(G, idToOsmid, nodes, name):
	out = snap.TFOut(DATA_PATH + name + ".graph") # graph saved as _.graph
	G.Save(out)
	out.Flush()

	idOut = open(DATA_PATH + name + ".id", 'w')
	pickle.dump(idToOsmid, idOut, 1)

	nodesOut = open(DATA_PATH + name + ".coords", 'w')
	pickle.dump(nodes, nodesOut, 1)

def loadFromFile(name):
	G = snap.TUNGraph.Load(snap.TFIn(DATA_PATH + name + ".graph"))

	idIn = open(DATA_PATH + name + ".id", 'r')
	idToOsmid = pickle.load(idIn)

	coords = open(DATA_PATH + name + ".coords", 'r')
	coordsMap = pickle.load(coords)

	return G, idToOsmid, coordsMap # variation for simple OSM saving.

"""
.graph: snap graph
.nodes: nodes information (dict from osmid to Node)
.edges: edges information (dict from osmid to Way)
.id: node id to osmid dictionary
.coords: osmid to coordinate tuple dictionary
"""

def saveAllOSM():
	dir = "../../openstreetmap-data"
	for folder in os.listdir(dir):
		if os.path.isfile(folder): continue
		for file in os.listdir(dir + "/" + folder):
			if file == '.DS_Store': continue

			name = file.split('.')[0]
			graphPath = os.path.abspath(DATA_PATH + name + ".graph")

			if os.path.isfile(graphPath):
				print "Skipping", name
				continue

			print "Starting", name

			fullpath = os.path.abspath(dir + "/" + folder + "/" + file)
			
			G, idToOsmid, nodes = parseToGraph(fullpath)
			
			saveToFile(G, idToOsmid, nodes, name)

			print "Finished", name

if __name__ == "__main__":
	saveAllOSM()

# fileName = 'stanford'

# G, idToOsmid, o = parseToGraph(fileName + '.osm')
# saveToFile(G, idToOsmid, o, fileName)

# G, idToOsmid, o = loadFromFile(fileName)

# print G.GetNodes()
# nodeToBetweenness = snap.TIntFltH()
# edgeToBetweenness = snap.TIntPrFltH()
# betweenness = snap.GetBetweennessCentr(G, nodeToBetweenness, edgeToBetweenness)

# maxCentrality = 0
# maxNode = None
# for node in nodeToBetweenness:
# 	print o.nodes[idToOsmid[node]].tags()
# 	print "Centrality:", nodeToBetweenness[node]
# 	if nodeToBetweenness[node] > maxCentrality:
# 		maxCentrality = nodeToBetweenness[node]
# 		maxNode = node

# print maxCentrality
# print o.nodes[idToOsmid[maxNode]].osmid(), o.nodes[idToOsmid[maxNode]].tags(), o.nodes[idToOsmid[maxNode]].coords()
