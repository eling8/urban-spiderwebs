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

def dijkstrasDistance(graph, nodesMap, node, limit=None):
	queue = Queue.PriorityQueue()
	seen = set()
	minDistances = {}

	queue.put((0, node))

	count = 0

	while not queue.empty():
		priority, n = queue.get()

		if n in seen:
			continue
		seen.add(n)
		count += 1
		if limit is not None:
			if count >= limit:
				break

		minDistances[n] = priority
		currNode = graph.GetNI(n)

		for index in range(currNode.GetDeg()):
			neighbor = currNode.GetNbrNId(index)

			if neighbor in seen:
				continue

			cost = getEdgeLength(n, neighbor, nodesMap)
			queue.put((cost + priority, neighbor))

	return minDistances

# adapted from https://networkx.github.io/documentation/development/_modules/networkx/algorithms/centrality/closeness.html
def closenessCentrality(graph, nodesMap, normalized=True):
	closeness_centrality = {}
	for node in graph.Nodes():
		n = node.GetId()
		sp = dijkstrasDistance(graph, nodesMap, n)
		totsp = sum(sp.values())

		if totsp > 0.0 and graph.GetNodes() > 1:
			closeness_centrality[n] = (len(sp) - 1.0) / totsp
			if normalized:
				s = (len(sp)-1.0) / (graph.GetNodes() - 1)
				closeness_centrality[n] *= s
		else:
			closeness_centrality[n] = 0.0

	return closeness_centrality

def approxCloseness(graph, nodesMap):
	allDistances = {}
	sampled = set()

	# take N / K samples
	for _ in xrange(graph.GetNodes() / K):
		# pick new random node
		n = graph.GetRndNId()
		while n in sampled:
			n = graph.GetRndNId()
		sampled.add(n)

		sp = dijkstrasDistance(graph, nodesMap, n)

		allDistances[n] = list(sp.values())
		# for each node, store distance from node n to that node in map
		for nid in sp:
			if not nid in allDistances:
				allDistances[nid] = []
			allDistances[nid].append(sp[nid])

	# inverse of the average distance to other nodes
	results = {}
	for nid in allDistances:
		total = sum(allDistances[nid])
		results[nid] = len(allDistances[nid]) / float(total)

	return results

def urbanness(graph, nodesMap, normalized=True):
	results = {}
	for node in graph.Nodes():
		nid = node.GetId()

		sp = dijkstrasDistance(graph, nodesMap, nid, limit=500)
		totsp = 0
		count = 0
		for value in sp:
			if sp[value] > 0.005:
				totsp += sp[value]
				count += 1
		if count == 0:
			continue

		results[nid] = count / float(totsp)

	return results

