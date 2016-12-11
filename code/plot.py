import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import snap
import pickle
from matplotlib import collections as mc
import heapq
import time
import sys
import osmParser
import weightedBetween
import os

DATA_PATH = "../data/"
BOUNDARIES_PATH = "../city-boundaries.txt"

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
def plotTopK(name, values, coords, k=100, useNodeBetween=True, symbol='o'):
	topK = heapq.nlargest(k, values, key=values.get)

	x = []
	y = []
	for _ in xrange(4):
		x.append([])
		y.append([])

	index = 0
	for node in topK:
		latlon = 0
		if useNodeBetween:
			latlon = coords[node]
		else:
			lat = (coords[node[0]][0] + coords[node[1]][0]) / float(2)
			lon = (coords[node[0]][1] + coords[node[1]][1]) / float(2)
			latlon = (lat, lon)

		x[index / (k / 4)].append(latlon[0])
		y[index / (k / 4)].append(latlon[1])

		index += 1

	figure = plt.figure()

	plotCity(name)

	plt.plot(y[3], x[3], 'b' + symbol)
	plt.plot(y[2], x[2], 'g' + symbol)
	plt.plot(y[1], x[1], 'y' + symbol)
	plt.plot(y[0], x[0], 'r' + symbol)

	figure.savefig(name, dpi=400)

	plt.close(figure)

def test(name):
	if os.path.isfile(DATA_PATH + name + ".between"):
		print "Skipping", name
		return

	start = time.time()

	G, coords = osmParser.simpleLoadFromFile(name)

	print "Calculating betweenness", name

	nodeToBetweenness = snap.TIntFltH()
	edgeToBetweenness = snap.TIntPrFltH()
	snap.GetBetweennessCentr(G, nodeToBetweenness, edgeToBetweenness, 0.25)

	betweenness = {}
	for node in nodeToBetweenness:
		betweenness[node] = nodeToBetweenness[node]

	betweenOut = open(DATA_PATH + name + ".between", 'w')
	pickle.dump(betweenness, betweenOut, 1)

	plotTopK(name, betweenness, coords)

	end = time.time()
	print "took", end - start, "seconds"

def weighted_between_test(name):
	if os.path.isfile(DATA_PATH + name + ".wbetween"):
		print "Skipping", name
		return

	start = time.time()

	print "Calculating betweenness", name

	betweenness, coords = weightedBetween.analyzeCity(name)

	betweenOut = open(DATA_PATH + name + ".wbetween", 'w')
	pickle.dump(betweenness, betweenOut, 1)

	plotTopK(name, betweenness, coords, useNodeBetween=False)

	end = time.time()
	print "took", end - start, "seconds"

############################################
####### OWEN code starts here ##############
############################################

def basically_the_same_test_but_for_closeness(name):
	if os.path.isfile(DATA_PATH + name + ".closeness"):
		print "Skipping", name
		return

	start = time.time()

	G, coords = osmParser.simpleLoadFromFile(name)

	print "Calculating closeness", name

	##
	nodeToCloseness = {}
	for node in G.Nodes():
		nodeToCloseness[node.GetId()] = snap.GetClosenessCentr(G, node.GetId())
	##

	closeOut = open(DATA_PATH + name + ".closeness", 'w')
	pickle.dump(nodeToCloseness, closeOut, 1)

	# plotTopK(name, betweenness, coords)

	end = time.time()
	print "took", end - start, "seconds"

############################################
####### END Owen code ######################
############################################

def plotCloseness(name):
	G, coords = osmParser.simpleLoadFromFile(name)

	closeIn = open(DATA_PATH + name + ".closeness", 'r')
	closeness = pickle.load(closeIn)

	plotTopK(name, closeness, coords, k=400, symbol='.')

# uses:
# between/wbetween/closeness/plot
# between/wbetween/closeness/plot city_name
if __name__ == "__main__":
	if len(sys.argv) == 2:
		arg1 = sys.argv[1]
		if arg1 in ["between", "wbetween", "closeness", "plot"]: # save betweenness on all cities
			file = open(BOUNDARIES_PATH, 'r')
			for line in file:
				name = line.split(",")[0]
				print "Starting", name
				if arg1 == "between":
					test(name)
				elif arg1 == "wbetween":
					weighted_between_test(name)
				elif arg1 == "closeness":
					basically_the_same_test_but_for_closeness(name)
				elif arg1 == "plot":
					figure = plt.figure()
					plotCity(name)
					figure.savefig(name, dpi=400)
				print "Finished", name
	elif len(sys.argv) == 3: # between/wbetween/closeness/plot city_name
		arg1 = sys.argv[1]
		name = sys.argv[2]
		if arg1 == "between":
			test(name)
		elif arg1 == "wbetween":
			weighted_between_test(name)
		elif arg1 == "closeness":
			basically_the_same_test_but_for_closeness(name)
		elif arg1 == "plot":
			figure = plt.figure()
			plotCity(name)
			figure.savefig(name, dpi=400)

