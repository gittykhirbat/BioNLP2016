import sys
import re
import networkx as nx
import numpy as np
import numpy.linalg as linalg

#from corenlp analysed out file, get me a python object for querying its field.





#convert passage level annotations in SeeDev data to sentence level datapoints
class clsEntity:
	def __init__ (self, entityId, entityDescription, entityType, start, end, sentenceId, documentId):
		self.entityId = entityId
		self.entityDescription = entityDescription
		self.entityType = entityType
		self.start  = start
		self.end = end
		self.documentId = documentId
		self.sentenceId = sentenceId
		self.token_span = None #the tokens in the sentence corresponding to this entity 

	def get_display(self):
		return "@".join( str(i) for i in  [self.entityId , self.entityDescription, self.entityType, self.start, self.end, self.sentenceId, self.documentId])
	###
	def getTokenSpan(self):
		if self.token_span is None :
			self.token_span = get_doc_obj(self, self).getTokenSpan(self.start, self.end)
		return self.token_span
	###
	@staticmethod 
	def createEntityFromString(line):
		try :
			entityId , entityDescription, entityType, start, end, sentenceId, documentId  = line.split("@")
		except:
			print >>sys.stderr, "prob in createEntityFromString ", line
			sys.exit(-1)
		return clsEntity( entityId , entityDescription, entityType, int(start), int(end), int(sentenceId), documentId  )


###########################################
##globals
LINEAR_EDGE_WEIGHT = 0.9 # http://www.aclweb.org/anthology/W08-0601
DEP_EDGE_WEIGHT =  0.3
SHORTEST_PATH_EDGE_WEIGHT = 0.9



### wrapper around the stanford corenlp parse of a sentence
class coreNLP:
	def __init__ (self):
		### what to store
		self.parseTree= [] # as paranthesized string of sentence 1,...sentence n
		self.dependencyGraph= [] # as list of edges 
		#self.spanToSentenceMap= {}
		self.rawText= [] #sentences, as if sentence-tokenized
		self.tokens = []
		self.lemmas= []
 		self.postags= [] #list of lists -- inner list per sentence

		self.sentenceBoundaries= [] #offsets at which sentence boundaries occur
		self.documentId = ''
		self.dg_with_all_shortest_paths = {} 
		self.fullgraph_for_entity_pair= {}

	def parse(self, fname):
		print >>sys.stderr, "coreNLP parsing ", fname
		if len(self.documentId) > 0 :
			print >>sys.stderr, "multiple parse calls on nlp obj ?"
			sys.exit(-1)			
	
		self.documentId = fname 
		fdata = open(fname).read()
		sentNo= 0 
		sentenceBoundary = 0
		self.tokens = []
		self.tokboundaries = []
		self.lemmas= []
 		self.postags= [] #list of lists -- inner list per sentence

		for sent in re.split( "Sentence #\d+ \(\d+ tokens\):",fdata):
			if not sent or len(sent)<=0  : continue # how do we even get empty lines ??

			rawText = sent[ : sent.find("[Text=")].strip()  #right upto the [Text.. we have the raw sentence text
			self.rawText.append( rawText )

			#next comes the tokens and their spans and pos tags..just take the least CharacterOffsetBegin--that will be the sentence starting offset
			tokens=[]
			postags=[]
			lemmas= []
			tokboundaries= []
			sentenceBoundary = 0
			for tokinfo in re.findall("\[Text=(.*) CharacterOffsetBegin=(\d+) CharacterOffsetEnd=(\d+) PartOfSpeech=(.*) Lemma=(.*) NamedEntityTag=.*\]" ,sent) :
				(toktext, tokstart, tokend, tokpos, toklemma) = tokinfo 
				if sentenceBoundary ==0 :
					sentenceBoundary = int(tokstart) #the first token's start offset, is the sentenceBoundary too

				tokens.append(toktext)
				postags.append(tokpos)
				lemmas.append(toklemma)
				tokboundaries.append( int(tokend) )
			####


			self.tokens.append( tokens )
			self.postags.append( postags )
			self.lemmas.append( lemmas )
			self.tokboundaries.append( tokboundaries )
			self.sentenceBoundaries.append(  sentenceBoundary )


			#now get the parse information
			m=re.search( "(\(ROOT.*\n\n)root\(" ,sent, re.DOTALL)
			if not m :
				print >>sys.stderr, "failed to extract parse info for sentence no ", sentNo
				sys.exit(-1)
			else:
				pt = m.group(1)
				self.parseTree.append(  re.sub( "\s+", " ", pt ) ) 

			#get the dependency graph info
			m= re.search( "(\nroot\(.*\))"  ,sent, re.DOTALL)
			if not m :
				print >>sys.stderr, "failed to get dependency graph for sentence no ", sentNo
				sys.exit(-1)
			else:
				pt = m.group(1)
				self.dependencyGraph.append(  re.sub( "\s+", " ", pt ) ) 


			sentNo += 1
		######
		#print >>sys.stderr, "sentence boundaries", self.sentenceBoundaries

	def getTokenSpan(self, start, end ):
		#find tokens corresponding to this character offset-span
		#first get the sentence
		sentId = self.getSentenceId(start, end)
		n=  len( self.tokens[sentId] )
		tokspan=[]
		#pcn - review and change- todo
		#for i in range(n):
		#	if self.tokboundaries[sentId][i] >= start and self.tokboundaries[sentId][i] <= end  :
		#		tokspan.append( i )

		for i in range(n):
			curb =  self.tokboundaries[sentId][i]
			if curb < start :
				continue 
			if curb >= start :
				tokspan.append( i )
			if curb > end :
				break  
		##
		return tokspan 	 

	def getSentenceId(self,start, end):
		#entity annotations seem to be erroneous. 
		#pick the sentence which contains most of the entity 
		sentenceIds =[]
		currSb = 0
		for sentNo in range(1, len(self.sentenceBoundaries)) :
			prevSb = currSb 
			currSb =  self.sentenceBoundaries[ sentNo ]
			if prevSb <= start < currSb  :
				sentenceIds.append(sentNo -1)
			if prevSb <= end <  currSb :
				sentenceIds.append(sentNo -1) 
				break
		#print "sentenceIds are ", sentenceIds

		if len(sentenceIds) ==0 : #range is outside the last sentence boundary -- which means it is in the last sentence
			#sentenceIds= [ len(self.rawText) -1 ]	
			return  len(self.rawText) -1 
		elif len(sentenceIds) ==1 :
			return sentenceIds[0]
		elif len(sentenceIds) == 2 :
			return sentenceIds[1] 
		else:
			print >>sys.stderr, "problem in sentence boundary detection for ", start, end, self.sentenceBoundaries, self.documentId, sentenceIds
			sys.exit(-1)
	###
	def getLemmas(self, sentenceId): #returns lemmas and their tokenboundaries
		retval= []
		for i in range(len(self.lemmas[sentenceId])):
			retval.append(  (self.lemmas[sentenceId][i], self.tokboundaries[sentenceId][i]) )
		return retval

	def get_display(self, i ): #i is sentenceId 
		return  self.rawText[i] \
			 + "\n\t" + ",".join(self.postags[i])  \
		 	+ "\t", self.parseTree[i]  \
		 	+ "\t", self.dependencyGraph[i]  \
			+ "\n-------------------------------------------------------------------\n"

	def get_labelled_linearsequence(self, e1, e2) :
		global LINEAR_EDGE_WEIGHT,  DEP_EDGE_WEIGHT, SHORTEST_PATH_EDGE_WEIGHT 
		if e1.sentenceId != e2.sentenceId :
			print >>sys.stderr, " problem .. we assume both entities are within a sentence "
			sys.exit(-1)

		tokens = self.tokens[e1.sentenceId]
		tokboundaries = self.tokboundaries[e1.sentenceId]
		postags= self.postags[e1.sentenceId]
		n = len(tokens)  #vertices are numbers to 0.. n-1 , i.e vertex i denotes i'th token
        	
		#the vertex set - name it as l0 .. to ln-1 . 
		vertices= [  "l"+str(i) for i in range(n) ]
		#and edges (in chain fashion) 
		edges= [ (vertices[i], vertices[i+1], LINEAR_EDGE_WEIGHT)  for i in range(n-1) ]  #a edge is a triple(start,end,weight) 
		
		#first get all labels -- it is token text and pos tags, decorated with _M, _A, _B for middle begin and after
		labels= {} #map of vertex to a list of labels
		for i in range(n):  labels[ vertices[i] ] = [] #create empty set - initialization

		#now create the actual labels - token spans described as 0.. p1... p2....p3..p4 --   (p1,p2) =e1 and (p3,p4) = e2
		tokspan1=  e1.getTokenSpan() #self.getTokenSpan( e1.start, e1.end)
		tokspan2=  e2.getTokenSpan() #self.getTokenSpan( e2.start, e2.end)
		try :
			p1, p2 = min(tokspan1), max(tokspan1)
			p3, p4 = min(tokspan2), max(tokspan2)
		except :
			print >>sys.stderr, "prob token spans for ", tokspan1, tokspan2, e1.get_display(), e2.get_display()
			sys.exit(-1)

		#print "sequence labeling  as "  , p1, p2 , p3, p4
		for i in range(n):
			if i < p1:
				labels[ vertices[i] ].append( tokens[i] +"_B" ) #before 
				labels[ vertices[i] ].append( postags[i] +"_B" ) #before 
			elif i > p4 :
				labels[ vertices[i] ].append( tokens[i] +"_A" ) #after
				labels[ vertices[i] ].append( tokens[i] +"_A" ) #after 
			elif i > p2  and i < p3 :  #it is in middle
				labels[ vertices[i] ].append( tokens[i] +"_M" ) #middle 
				labels[ vertices[i] ].append( tokens[i] +"_M" ) #middle 
			else:  #must be part of e1 or e2 -- todo CHECK if there is a need to distinguish ARG1-ARG2
				labels[ vertices[i] ].append( "ENTITY") 
				labels[ vertices[i] ].append( postags[i]  ) 
		### labels are done 				
		return vertices, edges, labels 

	###
	def get_dependency_graph_with_all_shortestpaths(self, sentenceId):
		global LINEAR_EDGE_WEIGHT,  DEP_EDGE_WEIGHT, SHORTEST_PATH_EDGE_WEIGHT 
		if sentenceId in self.dg_with_all_shortest_paths :  		
			return  self.dg_with_all_shortest_paths[sentenceId] #G , depedges, nx.shortest_path(G)

		G = nx.Graph() #undirected,
		n = len( self.tokens[sentenceId] )
		depedges= [] #dependency edges -directed ones from the dependency parse directly
		#vertices are numbers to 0.. n-1 , i.e vertex i denotes i'th token
		for i in range(n): 
			G.add_node(i)
		#edges coming from dependency graph 
		#print "dependency graph string is ", self.dependencyGraph[ e1.sentenceId ]
		degree_of_rootnode= 0
		for dependency in re.findall( "([a-z:]+)\(.*?-(\d+), .*?-(\d+)\)"   ,  self.dependencyGraph[sentenceId]) :
			(deptype,src, end) = dependency
			src, end = int(src)-1, int(end)-1 #stanford dependency graph labels nodes from 1 to n, so convert it back to 0 to n-1
			if src == -1 : 
				degree_of_rootnode += 1
				continue # ignore the root nodes
			if end == -1 :
				print >>sys.stderr, "problem in get_dependency_graph_with_all_shortestpaths ", self.documentId , sentenceId
				sys.exit(-1)
			G.add_edge( src, end, label = deptype )
			depedges.append( (src,end,deptype) ) 
		###
		if degree_of_rootnode != 1 :
			print >>sys.stderr, "root node degree issue", self.documentId, sentenceId
			sys.exit(-1)

		#print "Graph over text ", self.rawText[ e1.sentenceId ] 
		#print "vertices: \t",  G.nodes()
		#print "edges: \t",  G.edges()
		self.dg_with_all_shortest_paths[ sentenceId ] =  (G, depedges, nx.shortest_path(G) ) 
		return self.dg_with_all_shortest_paths[sentenceId] #G , depedges,  nx.shortest_path(G)

	###############

	def get_dependency_graph_with_shortest_path(self, e1, e2):
		global LINEAR_EDGE_WEIGHT,  DEP_EDGE_WEIGHT, SHORTEST_PATH_EDGE_WEIGHT 
		if e1.sentenceId != e2.sentenceId :
			print >>sys.stderr, " problem .. we assume both entities are within a sentence "
			sys.exit(-1)

		tokens = self.tokens[e1.sentenceId]
		postags= self.postags[e1.sentenceId]
	

		#pick the shortest path from amongst the shortest paths between src and dst nodes
		src_nodes = e1.getTokenSpan()#self.getTokenSpan(e1.start, e1.end)
		dst_nodes = e2.getTokenSpan()#self.getTokenSpan(e2.start, e2.end)

		#print "for entites ", e1.get_display() , e2.get_display(), " at idxes ", src_nodes, dst_nodes  
		G, depedges, all_paths = self.get_dependency_graph_with_all_shortestpaths(e1.sentenceId)  

		shortest_path = []
		for src in src_nodes :
			for dst in dst_nodes :
				try:
					if len(shortest_path)==0 : shortest_path =  all_paths[src][dst] 
					elif len(shortest_path) > len( all_paths[src][dst] ) : shortest_path  = all_paths[src][dst]
				except:
#					print "no path between ", src, dst
#					print "Graph over text ", self.rawText[ e1.sentenceId ] 
#					print "for entites ", e1.get_display() , e2.get_display(), " at idxes ", src_nodes, dst_nodes  
#					print "vertices: \t",  G.nodes()
#					print "edges: \t",  G.edges()
#					print "raw dependency string ", self.dependencyGraph[e1.sentenceId]
#					sys.exit(-1)
					continue

		### shortest path is ready

		#print "shortest path:\t",  shortest_path
		#print "shortest path(as tokens):\t",  [tokens[i] for i in shortest_path]
		
		return G, depedges, shortest_path

	###########
	def get_labelled_dependency_graph(self, e1, e2) :
		global LINEAR_EDGE_WEIGHT,  DEP_EDGE_WEIGHT, SHORTEST_PATH_EDGE_WEIGHT 
		if e1.sentenceId != e2.sentenceId :
			print >>sys.stderr, " problem .. we assume both entities are within a sentence "
			sys.exit(-1)

		tokens = self.tokens[e1.sentenceId]
		postags= self.postags[e1.sentenceId]
		n = len(tokens)  #vertices are numbers to 0.. n-1 , i.e vertex i denotes i'th token
       
		undirectedGraph, depedges, shortest_path = self.get_dependency_graph_with_shortest_path(e1,e2)

		#now create new directed weighted graph as described in all path graph kernel
		#nodes carry labels and edges carry weights
		depGraph = nx.DiGraph()
		for i in range(n) : #vertices -its nodes are from token sequence directly 0-n
			if len(shortest_path)>0 :#shortest path exists 
				if  i==shortest_path[0] :  #must be arg1 
					nodelabel= [ "ARG1_IP" , postags[i]+"_IP" ] 
				elif i == shortest_path[-1] : #must be arg2
					nodelabel= [ "ARG2_IP" , postags[i]+"_IP" ]
				elif i in shortest_path : #node lies on shortest dependency path
					nodelabel= [  tokens[i]+"_IP" , postags[i]+"_IP" ] 
				else : #is out side the shortest path - default action
					nodelabel = [ tokens[i], postags[i] ]
			else: #default action again
				nodelabel = [ tokens[i], postags[i] ]
			##
			depGraph.add_node( i, label= nodelabel ) 
		
		#shortest path as edge sequence to faciliate search below
		shortest_path_edgesequence= []
		for i in range(len(shortest_path) -1 ) :
			shortest_path_edgesequence.append( (shortest_path[i], shortest_path[i+1])  )

#		#from depedges, we take directed edges as well as new vertices from the dependency edge labels 
		for (src,end,deptype) in depedges : 
			#every labelled dependency edge to be broken into one more intermediate node - to incorporate the edge label as vertex label
			newvertex  =  str(src)+":"+str(end)
			#check if this edge is part of shortest dependency path
			if (src,end) in shortest_path_edgesequence  or (end,src) in shortest_path_edgesequence :
				nodelabel= [ deptype+"_IP"]
				depGraph.add_node( newvertex, label= nodelabel )		
				depGraph.add_edge( src, newvertex, weight= SHORTEST_PATH_EDGE_WEIGHT)
				depGraph.add_edge( newvertex, end, weight= SHORTEST_PATH_EDGE_WEIGHT)
			else:
				nodelabel= [ deptype ]
				depGraph.add_node( newvertex, label= nodelabel )		
				depGraph.add_edge( src, newvertex, weight= DEP_EDGE_WEIGHT)
				depGraph.add_edge( newvertex, end, weight= DEP_EDGE_WEIGHT)
	
		return depGraph		
	#####
	def getFullGraph(self, e1, e2):# the graph as defined in http://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-S11-S2
		if (e1,e2) in  self.fullgraph_for_entity_pair :
			return self.fullgraph_for_entity_pair[(e1,e2)]

		#form the full graph, i.e labels and adjaceny matrices L, A for each of the entity pair (e1-e2) 
		nodes,  edges, labels =self.get_labelled_linearsequence(e1,e2)
		#nodes=[ l0,l1...ln ]
		#edges =  [ (src,end,edge_weight)*]
		#labels: labels[n] is labels of node n = [ A, B, ...]` 
		
		#incorporate the other dependency graph
		#nodes
		depGraph = self.get_labelled_dependency_graph(e1,e2)
		for n in depGraph.nodes():
			nodes.append( n )
		#edges
		for (a,b) in depGraph.edges() : 
			edges.append(   (a,b, depGraph.edge[a][b]['weight'])  )
		#labels
		for n in depGraph.nodes(): 
			#print n , depGraph.node[n]['label']
			labels[n]= depGraph.node[n]['label']
		#print "labels", labels
		#print "nodes", nodes
		#print "edges", edges 

		#return labels, nodes, edges #
		self.fullgraph_for_entity_pair[(e1,e2) ] = (labels, nodes, edges) #
		return self.fullgraph_for_entity_pair[(e1,e2) ]

#################################################
def getGraphMatrix(labels_to_ids, node_labels , nodes, edges): #to make matrix G ..	
	#now make label allocation matrix Lmat  (L*V) and adjacency matrix Adj (V*V) for first graph
	nodesToIds= {}
	for n in nodes :
		if n in nodesToIds : 
			print >>sys.stderr, "duplicate nodes !!"
			sys.exit(-1)
		else:
			nodesToIds[n] = len(nodesToIds)

	n = len(nodesToIds)
	l = len(labels_to_ids)

	Adj = np.zeros(n*n).reshape(n,n)
	for (src,end,wt) in edges : 
		Adj[nodesToIds[src]][nodesToIds[end]]	= wt
	##
	I =  np.identity(n)  #identity matrix
	##
	Lmat =  np.zeros( l* n ).reshape(l,n) 
	for n in node_labels:
		for l in node_labels[n] :
			Lmat[labels_to_ids[l]][nodesToIds[n]] = 1.0
	####
	W =  linalg.inv( I - Adj) - I
	
	G =  np.mat(Lmat)  *  np.mat(W) *  np.mat(Lmat.transpose())  

	return G   #l*l

################################################################
__entity_to_doc_map= {}
def get_doc_obj(e1,e2):
	if e1.sentenceId != e2.sentenceId  or e1.documentId!= e2.documentId:
		print >>sys.stderr, "problem cross sentence entity pairs in get_doc_obj", e1.get_display(), e2.get_display()
		sys.exit(-1)

	if e1.documentId not in __entity_to_doc_map  :
		obj = coreNLP()
		obj.parse( e1.documentId + ".txt.out")
		__entity_to_doc_map[e1.documentId] =  obj

	return __entity_to_doc_map[e1.documentId]

################################################################
def  graphKernel(e1, e2, e3, e4):
	obj1 = get_doc_obj(e1,e2)
	obj2 = get_doc_obj(e3,e4)

	l1, n1, edges1 = obj1.getFullGraph(e1, e2)
	l2, n2, edges2 = obj2.getFullGraph(e3, e4)
	
	#first collect all labels - and assign an id to it
	all_labels = {}
	for ll in l1.values():
		for l in ll :  
			if l not in all_labels : all_labels[l] = len(all_labels)
	###
	for ll in l2.values():
		for l in ll :  
			if l not in all_labels : all_labels[l] = len(all_labels)
	##
	G1 = getGraphMatrix(all_labels, l1, n1, edges1) 
	G2 = getGraphMatrix(all_labels, l2, n2, edges2) 

	retval = 0
	for li in all_labels:
		for lj in all_labels :
			i =  all_labels[li]
			j =  all_labels[lj]
			#print "accessing indexes, ", i, j , li, lj
			p1 = G1[i,j]
			p2= G2[i,j]
			#print "got ", p1, p2
			retval += (p1*p2)
			
	return retval 

#####################################################################################################################
def testDepKernel():
	s1="T1@AGL15@Protein@0@5@0@data/BioNLP-ST-2016_SeeDev-binary_train/SeeDev-binary-10662856-1"
	s2="T2@AGAMOUS-like 15@Protein@7@22@0@data/BioNLP-ST-2016_SeeDev-binary_train/SeeDev-binary-10662856-1"
	e1 = clsEntity.createEntityFromString(s1)
	e2 = clsEntity.createEntityFromString(s2)

	s3="T27@AG@Protein@1220@1222@6@data/BioNLP-ST-2016_SeeDev-binary_train/SeeDev-binary-10662856-1"
	s4="T26@AGAMOUS@Protein@1211@1218@6@data/BioNLP-ST-2016_SeeDev-binary_train/SeeDev-binary-10662856-1"

	e3 = clsEntity.createEntityFromString(s3)
	e4 = clsEntity.createEntityFromString(s4)

	return graphKernel(e1, e2, e3, e4)
	
#####################################################################################################################

def testVariables():
	str1= "T1@AGL15@Protein@0@5@0@data/BioNLP-ST-2016_SeeDev-binary_train/SeeDev-binary-10662856-1"
	str2= "T4@MADS domain family@Protein_Family@43@61@0@data/BioNLP-ST-2016_SeeDev-binary_train/SeeDev-binary-10662856-1"

	e1 = clsEntity.createEntityFromString(str1)
	e2 = clsEntity.createEntityFromString(str2)
	myobj= coreNLP()
	myobj.parse( e1.documentId + ".txt.out" )
	#print "checking for ", e1.get_display(), e2.get_display()
	#print "in ",  myobj.get_display( e1.sentenceId)

	tokspan1=  myobj.getTokenSpan( e1.start, e1.end)
	tokspan2=  myobj.getTokenSpan( e2.start, e2.end)
	#print "e1 tok span ", tokspan1
	#print "e2 tok span ", tokspan2
	#print "e1 tokens from its span ", [myobj.tokens[e1.sentenceId][i] for i in tokspan1 ]
	#print "e2 tokens from its span ", [myobj.tokens[e2.sentenceId][i] for i in tokspan2 ]

	return  myobj, e1, e2
				
###################				
if __name__ == "__main__":

		
	print testDepKernel()

