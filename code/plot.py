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
import math

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CURR_DIR, "../data/")
BOUNDARIES_PATH = os.path.join(CURR_DIR, "../city-boundaries.txt")

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
k is number of nodes to plot
"""
def plotTopK(name, values, coords, color, numDivisions=10, k=500, useNodeBetween=True, symbol='.'):
	topK = heapq.nlargest(k, values, key=values.get)

	x = []
	y = []
	for _ in xrange(numDivisions):
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

		x[index / (k / numDivisions)].append(latlon[0])
		y[index / (k / numDivisions)].append(latlon[1])

		index += 1

	figure = plt.figure()

	plotCity(name)

	offset = 3

	colors = np.r_[np.linspace(0.1, 1, numDivisions + offset), np.linspace(0.1, 1, numDivisions + offset)] 
	mymap = plt.get_cmap(color)
	mycolors = mymap(colors)

	for i in range(numDivisions):
		line = plt.plot(y[numDivisions-i-1], x[numDivisions-i-1], symbol)
		plt.setp(line, color=mycolors[i + offset])

	figure.savefig(name, dpi=600)

	plt.close(figure)

def betweenness_test(name):
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

	plotTopK(name, betweenness, coords, "GnBu")

	end = time.time()
	print "took", end - start, "seconds"

def weighted_between_test(name):
	if os.path.isfile(DATA_PATH + name + ".wbetween"):
		print "Skipping", name
		return

	start = time.time()

	print "Calculating weighted betweenness", name

	betweenness, coords = weightedBetween.analyzeCity(name)

	betweenOut = open(DATA_PATH + name + ".wbetween", 'w')
	pickle.dump(betweenness, betweenOut, 1)

	plotTopK(name, betweenness, coords, "OrRd", useNodeBetween=False)

	end = time.time()
	print "took", end - start, "seconds"

def closeness_test(name):
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

	plotTopK(name, nodeToCloseness, coords, "YlGnBu")

	end = time.time()
	print "took", end - start, "seconds"

def weighted_closeness_test(name):
	if os.path.isfile(DATA_PATH + name + ".wcloseness"):
		print "Skipping", name
		return

	start = time.time()

	G, coords = osmParser.simpleLoadFromFile(name)

	print "Calculating weighted closeness", name

	nodeToCloseness = weightedBetween.closenessCentrality(G, coords)

	closeOut = open(DATA_PATH + name + ".wcloseness", 'w')
	pickle.dump(nodeToCloseness, closeOut, 1)

	plotTopK(name, nodeToCloseness, coords, "GnBu")

	end = time.time()
	print "took", end - start, "seconds"

def urbanness_test(name):
	if os.path.isfile(DATA_PATH + name + ".urban"):
		print "Skipping", name
		return

	start = time.time()

	G, coords = osmParser.simpleLoadFromFile(name)

	print "Calculating urbanness", name

	urbanness = weightedBetween.urbanness(G, coords)

	urbanOut = open(DATA_PATH + name + ".urban", 'w')
	pickle.dump(urbanness, urbanOut, 1)

	plotTopK(name, urbanness, coords, "BuPu")

	end = time.time()
	print "took", end - start, "seconds"

def approx_closeness_test(name):
	if os.path.isfile(DATA_PATH + name + ".acloseness"):
		print "Skipping", name
		return

	start = time.time()

	G, coords = osmParser.simpleLoadFromFile(name)

	print "Calculating approx closeness", name

	closeness = weightedBetween.approxCloseness(G, coords)

	closeOut = open(DATA_PATH + name + ".acloseness", 'w')
	pickle.dump(closeness, closeOut, 1)

	plotTopK(name, closeness, coords, "PuBu")

	end = time.time()
	print "took", end - start, "seconds"

def plotTSD(name):
	infoIn = open(DATA_PATH + name + ".tsd", 'r')
	data = pickle.load(infoIn)

	maximum = max(data.values())
	maxLog = int(math.log(maximum))
	numDivisions = 12
	minVal = maximum / numDivisions # minimum coords[data] that passes filter

	x = []
	y = []
	for _ in xrange(numDivisions):
		x.append([])
		y.append([])

	for coords in data:
		value = (numDivisions * data[coords]) / maximum
		if value == 0: # filter out bottom 1/numDivision of data
			continue

		value = (numDivisions * int(math.log(data[coords] - minVal))) / maxLog

		x[numDivisions - (value % numDivisions) - 1].append(coords[0])
		y[numDivisions - (value % numDivisions) - 1].append(coords[1])

	figure = plt.figure()
	plotCity(name)
	
	offset = 3
	npColors = np.r_[np.linspace(0.1, 1, numDivisions + offset), np.linspace(0.1, 1, numDivisions + offset)] 
	mymap = plt.get_cmap("YlOrRd")
	mycolors = mymap(npColors)

	for i in range(numDivisions):
		line = plt.plot(y[numDivisions - i - 1], x[numDivisions - i - 1], '.')
		plt.setp(line, color=mycolors[i + offset])

	figure.savefig(name, dpi=600)
	plt.close(figure)

def plotStat(name, stat):
	if not os.path.isfile(DATA_PATH + name + "." + stat):
		print "Skipping", name
		return

	if stat == "tsd":
		print "Plotting TSD for", name
		plotTSD(name)
		return

	G, coords = osmParser.simpleLoadFromFile(name)

	infoIn = open(DATA_PATH + name + "." + stat, 'r')
	data = pickle.load(infoIn)

	color = ""
	if stat == "between":
		color = "RdPu"
	elif stat == "wbetween":
		color = "OrRd"
	elif stat == "closeness":
		color = "YlGnBu"
	elif stat == "wcloseness":
		color = "GnBu"
	elif stat == "acloseness":
		color = "PuBu"
	elif stat == "urbanness":
		color = "BuPu"
	else:
		print "Invalid stat name, exiting"
		return

	if stat == "wbetween":
		plotTopK(name, data, coords, color, useNodeBetween=False)
	else:
		plotTopK(name, data, coords, color)

plotTSD("tokyo_japan")

# uses:
# between/wbetween/closeness/plot
# between/wbetween/closeness/plot city_name
if __name__ == "__main__":
	if len(sys.argv) == 2:
		arg1 = sys.argv[1]
		if arg1 in ["between", "wbetween", "closeness", "wcloseness", "acloseness", "urban"]: # save betweenness on all cities
			file = open(BOUNDARIES_PATH, 'r')
			for line in file:
				name = line.split(",")[0]
				print "Starting", name
				if arg1 == "between":
					betweenness_test(name)
				elif arg1 == "wbetween":
					weighted_between_test(name)
				elif arg1 == "closeness":
					closeness_test(name)
				elif arg1 == "wcloseness":
					weighted_closeness_test(name)
				elif arg1 == "acloseness":
					approx_closeness_test(name)
				elif arg1 == "urban":
					urbanness_test(name)
				else:
					print arg1, "invalid"
				print "Finished", name
		elif arg1[:4] == "plot":
			file = open(BOUNDARIES_PATH, 'r')
			for line in file:
				name = line.split(",")[0]
				print "Plotting", name

				if arg1 == "plot":
					figure = plt.figure()
					plotCity(name)
					figure.savefig(name, dpi=400)
				else:
					plotStat(name, arg1[4:])
				print "Finished", name
	elif len(sys.argv) == 3: # between/wbetween/closeness/plot city_name
		arg1 = sys.argv[1]
		name = sys.argv[2]
		if arg1[:4] == "plot":
			if arg1 == "plot":
				figure = plt.figure()
				plotCity(name)
				figure.savefig(name, dpi=400)
			else:
				plotStat(name, arg1[4:])
		elif arg1 == "between":
			betweenness_test(name)
		elif arg1 == "wbetween":
			weighted_between_test(name)
		elif arg1 == "closeness":
			closeness_test(name)
		elif arg1 == "wcloseness":
			weighted_closeness_test(name)
		elif arg1 == "acloseness":
			approx_closeness_test(name)
		elif arg1 == "urban":
			urbanness_test(name)

