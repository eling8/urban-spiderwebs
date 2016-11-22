import numpy as np
import matplotlib.pyplot as plt
import snap
import pickle
from matplotlib import collections as mc
import heapq
import time

DATA_PATH = "../data/"

def loadFromFile(name):
	G = snap.TUNGraph.Load(snap.TFIn(DATA_PATH + name + ".graph"))

	idIn = open(DATA_PATH + name + ".id", 'r')
	idToOsmid = pickle.load(idIn)

	coords = open(DATA_PATH + name + ".coords", 'r')
	coordsMap = pickle.load(coords)

	return G, idToOsmid, coordsMap

def plotCity(name):
	G, idToOsmid, coordsMap = loadFromFile(name)

	x = []
	y = []

	for edge in G.Edges():
		start = edge.GetSrcNId()
		end = edge.GetDstNId()

		coords1 = coordsMap[idToOsmid[start]]
		coords2 = coordsMap[idToOsmid[end]]

		x.append(coords1[0])
		x.append(coords2[0])
		x.append(None)
		y.append(coords1[1])
		y.append(coords2[1])
		y.append(None)

	plt.plot(y, x, 'k', linewidth=0.5)

"""
k is number of notes to plot; must be divisible by 4.
"""
def plotTopK(name, values, coords, idToOsmid, k=100):
	topK = heapq.nlargest(k, values, key=values.get)

	x = []
	y = []
	for _ in xrange(4):
		x.append([])
		y.append([])

	index = 0
	for node in topK:
		latlon = coords[idToOsmid[node]]

		x[index / (k / 4)].append(latlon[0])
		y[index / (k / 4)].append(latlon[1])

		index += 1

	figure = plt.figure()

	plotCity(name)

	plt.plot(y[3], x[3], 'bo')
	plt.plot(y[2], x[2], 'go')
	plt.plot(y[1], x[1], 'yo')
	plt.plot(y[0], x[0], 'ro')

	plt.xlabel("Longitude")
	plt.ylabel("Latitude")

	figure.savefig(name, dpi=400)

def test(name):
	start = time.time()

	G, idToOsmid, coords = loadFromFile(name)

	print "Calculating betweenness"

	nodeToBetweenness = snap.TIntFltH()
	edgeToBetweenness = snap.TIntPrFltH()
	snap.GetBetweennessCentr(G, nodeToBetweenness, edgeToBetweenness, 0.1)

	betweenness = {}
	for node in nodeToBetweenness:
		betweenness[node] = nodeToBetweenness[node]

	plotTopK(name, betweenness, coords, idToOsmid)

	end = time.time()
	print end - start

test("shanghai_china")

# figure = plt.figure()
# plotCity("shanghai_china")
# figure.savefig("shanghai", dpi=400)
