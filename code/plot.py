import numpy as np
import matplotlib.pyplot as plt
import snap
import pickle
from matplotlib import collections as mc
import heapq
import time
import sys
import osmParser

DATA_PATH = "../data/"

def plotCity(name):
	G, coordsMap = osmParser.simpleLoadFromFile(name)

	x = []
	y = []

	for edge in G.Edges():
		start = edge.GetSrcNId()
		end = edge.GetDstNId()

		coords1 = coordsMap[start]
		coords2 = coordsMap[end]

		x.append(coords1[0])
		x.append(coords2[0])
		x.append(None)
		y.append(coords1[1])
		y.append(coords2[1])
		y.append(None)

	plt.plot(y, x, 'k', linewidth=0.5)
	plt.xlabel("longitude")
	plt.ylabel("latitude")
	plt.axis('image')

"""
k is number of notes to plot; must be divisible by 4.
"""
def plotTopK(name, values, coords, k=100):
	topK = heapq.nlargest(k, values, key=values.get)

	x = []
	y = []
	for _ in xrange(4):
		x.append([])
		y.append([])

	index = 0
	for node in topK:
		latlon = coords[node]

		x[index / (k / 4)].append(latlon[0])
		y[index / (k / 4)].append(latlon[1])

		index += 1

	figure = plt.figure()

	plotCity(name)

	plt.plot(y[3], x[3], 'bo')
	plt.plot(y[2], x[2], 'go')
	plt.plot(y[1], x[1], 'yo')
	plt.plot(y[0], x[0], 'ro')

	figure.savefig(name, dpi=400)

def test(name):
	start = time.time()

	G, coords = osmParser.simpleLoadFromFile(name)

	print "Calculating betweenness"

	nodeToBetweenness = snap.TIntFltH()
	edgeToBetweenness = snap.TIntPrFltH()
	snap.GetBetweennessCentr(G, nodeToBetweenness, edgeToBetweenness, 0.1)

	betweenness = {}
	for node in nodeToBetweenness:
		betweenness[node] = nodeToBetweenness[node]

	plotTopK(name, betweenness, coords)

	end = time.time()
	print end - start

# test("helinski")


# Takes one argument with the 
if __name__ == "__main__":
	if len(sys.argv) == 2: # arguments, run only specified
		name = sys.argv[1]
		figure = plt.figure()
		plotCity(name)
		figure.savefig(name, dpi=400)
	elif len(sys.argv) == 3: # city_name test
		if sys.argv[2] != "test": print "Running test"
		test(sys.argv[1])
	else:# no arguments
		print "Please give the name of the city as an argument"



