import numpy as np
import matplotlib.pyplot as plt
import snap
import pickle
from matplotlib import collections as mc
# import pylab as pl

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

		print coords1, coords2

		x.append(coords1[0])
		x.append(coords2[0])
		x.append(None)
		y.append(coords1[1])
		y.append(coords2[1])
		y.append(None)

	plt.plot(y, x, 'k')
	plt.show()

# plotCity("accra_ghana")
plotCity("stanford")
