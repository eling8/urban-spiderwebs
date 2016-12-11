import snap
import random
import Queue
import heapq
import osmParser

C = 5
K = 100
N = 1000
NUM_SAMPLES = N / K

def getEdgeLength(node1, node2, nodesMap):
	lat1, lon1 = nodesMap[node1]
	lat2, lon2 = nodesMap[node2]

	return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5

def getDeltas(graph, node, nodesMap):
	shortestPath = {} # map from (node1, node2) to shortest path length between the two nodes
	numShortestPaths = {}
	nodesList = {} # map from nodeId to list of BFS traversal

	s = node

	queue = Queue.Queue()
	queue.put((None, s, 0))
	shortestPath[(s, s)] = 0

	nodesList[s] = []

	parents = {}
	children = {}

	while not queue.empty():
		prev, v, length = queue.get()

		# Add to the ordering in which we do BFS
		nodesList[s].append(v)

		# Add previous node to v's parent set
		if v not in parents:
			parents[v] = set()
		if prev is not None:
			parents[v].add(prev)

		# Set up children set
		if v not in children:
			children[v] = set()

		# Add all unvisited or equal length shortest path neighboring nodes to queue
		currNode = graph.GetNI(v)
		for index in range(currNode.GetDeg()):
			neighbor = currNode.GetNbrNId(index)
			edgeLength = getEdgeLength(v, neighbor, nodesMap)
			if (s, neighbor) not in shortestPath or shortestPath[(s, neighbor)] == length + edgeLength:
				queue.put((v, neighbor, length + edgeLength))
				shortestPath[(s, neighbor)] = length + edgeLength
				children[v].add(neighbor)

	# populate numShortestPaths
	for v in nodesList[s]:
		if v == s:
			numShortestPaths[(s, v)] = 1
		else:
			total = sum([numShortestPaths[s, neighbor] for neighbor in parents[v]])
			numShortestPaths[(s, v)] = total
			
	# calculate dependencies
	dependency = {}
	for w in reversed(nodesList[s]):
		setV = {} # map from valid v to o_sv
		for parent in parents[w]:
			if shortestPath[(s, w)] > shortestPath[(s, parent)]:
				setV[parent] = numShortestPaths[(s, parent)] / float(numShortestPaths[(s, w)])
			if shortestPath[(s, w)] == shortestPath[(s, parent)]:
				dependency[tuple(sorted((parent, w)))] = 0

		for v in setV:
			dependency[tuple(sorted((v, w)))] = setV[v] # set to o_sv / o_sw

		if len(children[w]) != 0: # not a leaf
			total = 1
			for x in children[w]:
				total += dependency[tuple(sorted((x, w)))]

			for v in setV:
				dependency[tuple(sorted((v, w)))] *= total

	return dependency

def algorithm2(graph, nodesMap):
	allDependencies = {}
	numK = {}
	shortestPath = {} # map from (node1, node2) to shortest path length between the two nodes
	numShortestPaths = {}
	nodesList = {} # map from nodeId to list of BFS traversal

	for edge in graph.Edges():
		start = edge.GetSrcNId()
		end = edge.GetDstNId()

		tup = tuple(sorted((start, end)))
		allDependencies[tup] = 0
		numK[tup] = 0

	for _ in xrange(graph.GetNodes() / K):
		s = graph.GetRndNId()

		dependency = getDeltas(graph, s, nodesMap)

		for edge in dependency:
			if allDependencies[edge] < C * N:
				allDependencies[edge] += dependency[edge]
				numK[edge] += 1

		canBreak = True
		for edge in allDependencies:
			if allDependencies[edge] < C * N:
				canBreak = False
				break
			if numK[edge] < NUM_SAMPLES:
				canBreak = False
				break
		if canBreak: break

	removed = set()
	for edge in allDependencies:
		if numK[edge] == 0:
			removed.add(edge)
		else:
			allDependencies[edge] = allDependencies[edge] * N / float(numK[edge])

	for edge in removed:
		del allDependencies[edge]

	return allDependencies

def analyzeCity(city):
	graph, nodesMap = osmParser.simpleLoadFromFile(city)
	return algorithm2(graph, nodesMap), nodesMap
