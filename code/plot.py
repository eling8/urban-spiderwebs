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
import between
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
def plotTopK(name, values, coords, k=100, useNodeBetween=True):
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

	plt.plot(y[3], x[3], 'bo')
	plt.plot(y[2], x[2], 'go')
	plt.plot(y[1], x[1], 'yo')
	plt.plot(y[0], x[0], 'ro')

	figure.savefig(name, dpi=400)

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

	betweenness, coords = between.analyzeCity(name)

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


# Takes one argument with the 
if __name__ == "__main__":
	if len(sys.argv) == 2:
		if sys.argv[1] == "test": # save betweenness on all cities
			file = open(BOUNDARIES_PATH, 'r')
			for line in file:
				name = line.split(",")[0]
				print "Starting", name
				# THE FOLLOWING LINE HAS BEEN CHANGED TO MY OWN FUNCTION -Owen
				# test(name)
				# basically_the_same_test_but_for_closeness(name)
				weighted_between_test(name)
				print "Finished", name
		else: # plot only specified city
			name = sys.argv[1]
			figure = plt.figure()
			plotCity(name)
			figure.savefig(name, dpi=400)
	elif len(sys.argv) == 3: # city_name test
		if sys.argv[2] != "test": print "Running test"
		# test(sys.argv[1])
		weighted_between_test(sys.argv[1])
	else: # no arguments, plot all cities
		file = open(BOUNDARIES_PATH, 'r')
		for line in file:
			name = line.split(",")[0]
			print "Starting", name
			figure = plt.figure()
			plotCity(name)
			figure.savefig(name, dpi=400)
			print "Finished", name
		# print "Please give the name of the city as an argument"



