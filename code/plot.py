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
k is number of nodes to plot
"""
def plotTopK(name, values, coords, color, numDivisions=10, k=400, useNodeBetween=True, symbol='.'):
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

def plotStat(name, stat):
	if name == "london_england": return
	if name == "sao-paulo_brazil": return 
	G, coords = osmParser.simpleLoadFromFile(name)

	infoIn = open(DATA_PATH + name + "." + stat, 'r')
	data = pickle.load(infoIn)

	color = ""
	if stat == "between":
		# color = "GnBu"
		color = "RdPu"
	elif stat == "wbetween":
		color = "OrRd"
	elif stat == "closeness":
		color = "YlGnBu"
	else:
		print "Invalid stat name, exiting"
		return

	plotTopK(name, data, coords, color, k=400, symbol='.')

# uses:
# between/wbetween/closeness/plot
# between/wbetween/closeness/plot city_name
if __name__ == "__main__":
	if len(sys.argv) == 2:
		arg1 = sys.argv[1]
		if arg1 in ["between", "wbetween", "closeness", "plot", "plotbetween"]: # save betweenness on all cities
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
				elif arg1 == "plot":
					figure = plt.figure()
					plotCity(name)
					figure.savefig(name, dpi=400)
				elif arg1 == "plotbetween":
					plotStat(name, "between")
				print "Finished", name
	elif len(sys.argv) == 3: # between/wbetween/closeness/plot city_name
		arg1 = sys.argv[1]
		name = sys.argv[2]
		if arg1 == "between":
			betweenness_test(name)
		elif arg1 == "wbetween":
			weighted_between_test(name)
		elif arg1 == "closeness":
			closeness_test(name)
		elif arg1 == "plot":
			figure = plt.figure()
			plotCity(name)
			figure.savefig(name, dpi=400)

