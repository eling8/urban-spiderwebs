if __name__ == "__main__":
	from imposm.parser import OSMParser

import xml.etree.ElementTree as ET


import snap
import json
import pickle
import os
import random
import sys

DATA_PATH = "../data/"
PRUNE_RESIDENTIAL = 0.2

# create snap graph from parsed nodes and ways
def createGraph(nodes, edges):
	G = snap.TUNGraph.New()
	renumbered = {}
	idToOsmid = {}
	counter = 0

	for osmid in edges:
		refs = edges[osmid]

		for i in xrange(0, len(refs) - 1):
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

	G = snap.GetMxWcc(G)

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

			# if lat > minCoord[0] and lat < maxCoord[0] and lon > minCoord[1] and lon < maxCoord[1]:
			# 	nodes[id] = (lat, lon)

		elif child.tag == "way":
			tags = [tag for tag in child.findall('tag')]
			id = child.attrib['id']

			shouldTag = False
			for tag in tags:
				if tag.attrib['k'] == 'highway':
					if tag.attrib['v'] in ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified']:
						shouldTag = True
					# elif tag.attrib['v'] == 'residential':
					# 	shouldTag = random.uniform(0, 1) <= PRUNE_RESIDENTIAL

			if not shouldTag:
				continue

			wayNodes = []
			for node in child.findall('nd'):
				nodeId = node.attrib['ref']
				wayNodes.append(nodeId)

			edges[id] = wayNodes

		elif child.tag == "bounds":
			minCoord = (child.attrib['minlat'], child.attrib['minlon'])
			maxCoord = (child.attrib['maxlat'], child.attrib['maxlon'])

		elif child.tag == "relation":
			break

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


def saveOneOSM(file, path):
	if file == '.DS_Store': return

	name = file.split('.')[0]
	graphPath = os.path.abspath(DATA_PATH + name + ".graph")

	print name
	return

	if os.path.isfile(graphPath):
		print "Skipping", name
		return

	print "Starting", name

	fullpath = os.path.abspath(path)
	
	G, idToOsmid, nodes = parseToGraph(fullpath)
	
	saveToFile(G, idToOsmid, nodes, name)

	print "Finished", name

"""
.graph: snap graph
.id: node id to osmid dictionary
.coords: osmid to coordinate tuple dictionary
"""

def saveAllOSM(dir):
	for folder in os.listdir(dir):
		if os.path.isfile(folder): continue
		for file in os.listdir(dir + "/" + folder):
			saveOneOSM(file, dir + "/" + folder + "/" + file)

def saveOneRegion(dir):
	for file in os.listdir(dir):
		saveOneOSM(file, dir + "/" + file)

# Takes one argument with the 
if __name__ == "__main__":
	dir = "../../openstreetmap-data"
	if len(sys.argv) > 1: # arguments, run only specified
		dir += "/" + sys.argv[1]
		if os.path.isfile(dir): # run only one city
			saveOneOSM(dir.split("/")[-1].split(".")[0], dir)
		else: # run all specified region
			saveOneRegion(dir)
	else: # no arguments, run all
		saveAllOSM(dir)
