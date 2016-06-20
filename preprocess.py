import sys
import nltk
from nltk.tokenize import sent_tokenize

from  corenlpparse import coreNLP
from  corenlpparse import clsEntity


def get_all_relations(a2file):
	relations={}
	try :
		for line in open(a2file).readlines():
			(relid, relname, entity1, entity2) = line.split()
			role1, e1 = entity1.split(":")
			role2, e2 = entity2.split(":")
        
			relations[ (e1,e2) ] = relname
	except:
		print >>sys.stderr, "no a2file ", a2file , "empty relations"

	#print "all relations", relations
	return relations
		

#############		
def get_relation_label(entity1, entity2, a2filedata ):
	#if et1== "Gene" and et2 == "Genotype" : return "Presence_In_Genotype"
	#else: return None
	
	import re
	#E6      Regulates_Development_Phase Agent:T39 Development:T36

	#TODO - why are we getting the braces around the label.. shud just get the label like Regulated_Development_Phase .. 
	m = re.match( ".*\s+(.*)\s(\w+):"+entity1.entityId+"\s(\w+):"+entity2.entityId+"[^\d]" , a2filedata, re.DOTALL) 
	if m :
		#print "found a match ", m.groups()
		#lets only look for PROTEIN_DOMAIN_OF relation for now
		relation_label = m.group(1)
		#if "Is_Protein_Domain_Of" == relation_label :
		#	return 1
		#else: 	
		#	return -1 
		return relation_label
	else:
		return  "NOT_RELATED"


#####################################################33
def get_entitylist_from_a1file( a1file, nlpObj ):			
	listOfEntities= []
	for line in open(a1file).readlines():
		entityId 			=line.split("\t")[0].strip()
		entityDesc			=line.split("\t")[2].strip()
		try :
			tarr				= line.split("\t")[1].replace(";"," ").split()
			entityType, start, end		= tarr[0], tarr[1], tarr[2] #line.split("\t")[1].split(" ")
			start 				= int(start)
			end 				= int(end)
			sentenceId 			= nlpObj.getSentenceId(start,end)
		except Exception, e:
			print >>sys.stderr, "BROKEN ANNOTATION NOT HANDLED", line , tarr
			print >>sys.stderr, "from file ", a1file
			print >>sys.stderr, "exception ", str(e)
			sys.exit(-1)
			continue

#		if sentenceId == -1 : 
#			#trying to adjust entities within a sentence -- annotation errors?
#			prevSentBoundary = 0
#			sentNo    = 0 
#			#print >>sys.stderr, "searching problematic", entityDesc, " in ", nlpObj.rawText
#			for sentRawText in nlpObj.rawText:
#				if entityDesc in sentRawText :
#					print >>sys.stderr, "fixing erroenous entity annotation from ", start, end, 
#					sentenceId = sentNo
#					start =  prevSentBoundary + sentRawText.find(entityDesc) 
#					end = start+ len(entityDesc)
#					print >>sys.stderr, " to ", start, end
#					break
#				else:
#					#print >>sys.stderr, "not found ", entityDesc , " in ", sentRawText
#					prevSentBoundary = nlpObj.sentenceBoundaries[ sentNo ]
#					sentNo += 1

		if sentenceId == -1 : # if it is still -1, give up
			print >>sys.stderr, "giving up",
			print >>sys.stderr, "invalid entity ?.." , documentId, sentenceId, entityType, entityDesc, start, end
			import re
			print >>sys.stderr, "did not find ", re.sub("[\s\n]+", "_", entityDesc, re.DOTALL) , " in ", nlpObj.rawText
			sys.exit(-1)

		listOfEntities.append(  clsEntity(entityId, entityDesc, entityType, start, end, sentenceId, documentId) )

	return listOfEntities

#############################3
#def get_entity_group(etype ) : #entity type to group
#	if etype in ["RNA","Protein","Protein_Family","Protein_Complex","Protein_Domain"]:	return "DNA_Product"
#	if etype in ["Gene","Gene_Family","Box,Promoter"]:					return "DNA" 			
#	if etype in ["DNA_Product","Hormone"]:							return "Functional_Molecule"	
#	if etype in ["DNA","Functional_Molecule"]:						return "Molecule" 		
#	if etype in ["Regulatory_Network","Pathway"]:						return "Dynamic_Process"   
#	if etype in ["Tissue","Development_Phase","Genotype"]:					return "Internal_Factor"   
#	if etype in ["Internal_Factor","Environmental_Factor"]:					return "Factor"			
#
#	return etype #if no grouping possible
#	#print >>sys.stderr, "invalid entity type ", etype
#	#sys.exit(-1)
#
#
#########################			
#def  relation_from_entity_signature(e1, e2): 
#	#allowed relation type from entity signature
#	et1 = e1.entityType
#        et2=  e2.entityType
#	eg1 =  get_entity_group(et1 )
#	eg2 =  get_entity_group(et2 )
#
#	for (relset, arg1set, arg2set) in 	[ \
#		(["Binds_To"], ["Functional_Molecule"], ["Molecule"] 			) , \
#		(["Composes_Primary_Structure"],  ["Box", "Promoter"] , ["DNA"] 	), \
#		(["Composes_Protein_Complex"], ["Amino_Acid_Sequence", "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain"],["Protein_Complex"]),\
#		(["Exists_At_Stage"], ["Functional_Molecule"], ["Development","Development_Phase"]) , \
#		(["Exists_In_Genotype"], ["Molecule"] , ["Genotype"] ),\
#		(["Interacts_With"], ["Molecule"], ["Molecule"]),\
#		(["Is_Involved_In_Process"], ["Molecule"] , ["Dynamic_Process"] ),\
#		(["Is_Member_Of_Family"],["Gene","Gene_Family","Protein","Protein_Domain","Protein_Family","RNA"],["Gene_Family","Protein_Family","RNA"]),\
#		(["Is_Protein_Domain_Of"],["Protein_Domain"],["DNA_Product"]),\
#		(["Occurs_During"],["Dynamic_Process"],["Development_Phase"]),\
#		(["Transcribes_Or_Translates_To"],["DNA","RNA"],["DNA_Product"]),\
#		(["Occurs_In_Genotype"],["Dynamic_Process"],["Genotype"]),\
#		(["Is_Localized_In"], ["Functional_Molecule", "Dynamic_Process"] , ["Tissue"]),\
#		] :
#			if ((et1 in arg1set) or (eg1 in arg1set) ) and  ((et2 in arg2set) or (eg2 in arg2set)) :
#				return relset 
#	
#	#restriction on only one argument 
#	for (relset, arg2set) in 	[ \
#		(["Regulates_Accumulation"],   ["Functional_Molecule"] ),\
#		(["Regulates_Development_Phase"], ["Development_Phase"] ),\
#		(["Regulates_Molecule_Activity"], ["Molecule"] ),\
#		(["Regulates_Expression"], ["DNA"] ),\
#		(["Regulates_Process"],["Dynamic_Process"]),\
#		(["Regulates_Tissue_Development"],["Tissue"]),\
#		]:
#		if  ((et2 in arg2set) or (eg2 in arg2set)) :
#			return relset 
#
#	return ["Has_Sequence_Identical_To", "Is_Functionally_Equivalent_To", "Is_Linked_To"] # relation types that admit any arguments


##################################################################
def get_candidate_pairs( listOfEntities, relation_types):
	e1_lst = []
	e2_lst = []
	for e in listOfEntities :
		if "Binds_To" in relation_types :
			if e.entityType in ["RNA","Protein","Protein_Family", "Protein_Complex", "Protein_Domain", "Hormone"] :
				e1_lst.append( e )
			if e.entityType in ["Gene","Gene_Family" ,"Box", "Promoter", "RNA", "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain","Hormone"] :
				e2_lst.append( e )

		
	retlst = []
	for e1 in e1_lst :
		for e2 in e2_lst :
			if e1.entityId != e2.entityId : #  no self relations possible like t1-t1..
				retlst.append( (e1,e2) )
	return retlst 


##################################################################

def produce_data_points(documentId , outdir ):
	#produce  data points and print it out,  one per line 
	nlpObj  = coreNLP()
	nlpObj.parse( documentId+".txt.out")
	
	#1. list of entities - from .a1
	a1file = documentId + ".a1"
	listOfEntities= get_entitylist_from_a1file( a1file , nlpObj )

			
	#4. Infer Label from .a2
	a2file =     documentId+".a2" 
	all_relations = get_all_relations(a2file)
	####a2filedata = open(documentId+".a2").read()
	

	#2. generate candidate entity pairs
	#2.1 filter out candiate based on event signature
	#2.2 filter out candidates outside sentence boundaries ???? 

	for ptr1 in range(len(listOfEntities)) :
		for ptr2 in range(len(listOfEntities))  :
			if ptr2 == ptr1 : continue # no reflexive,relations ie. relations of type (a,a)

			e1= listOfEntities[ptr1]
			e2= listOfEntities[ptr2]

			#just a heuristic to speed up -- skip entity pairs that are too far apart
			if abs( e1.sentenceId - e2.sentenceId) > 8 :
				continue 

			relation_name=  all_relations.get( (e1.entityId,e2.entityId),  "NOT_RELATED" )  #get_relation_label(e1, e2, a2filedata)

		
			print "EntityArg1:", e1.get_display(), "\t", 
			print "EntityArg2:", e2.get_display(), "\t", 
			print "RelationLabel:", relation_name, "\t", 


			#first feature 
			print "Sentence_Numbers:", e1.sentenceId, e2.sentenceId, "\t", 


			#  compute all other features
			print "Bag_Of_Words:", get_feature_bow(e1, e2, nlpObj), "\t", 
			print "Parse_Tree:",get_feature_parsetree(e1, e2, nlpObj),"\t", 
			#get_feature_pos(e1, e2, documentId), \

			print #end of line - feature

	#3. Generate features for that pair from the document. 
	#5. dump these datapoints entity-pair, label, features. 


######################################################################## add feature definitions here
def get_feature_parsetree( e1, e2, nlpObj):
	#find the sentence corresponding to e1 e2
	s1 = e1.sentenceId # nlpObj.getSentenceId(e1.start, e1.end) 
	s2 = e2.sentenceId # nlpObj.getSentenceId(e2.start, e2.end) 
	if s1 != s2 : 
		#print >>sys.stderr, "entity pair is outside a sentence boundary"
		pt1 = nlpObj.parseTree[ s1 ] 
		pt2 = nlpObj.parseTree[ s2 ] 
		import re
		pt1= re.sub("[\n\s]+"," ", pt1)
		pt2= re.sub("[\n\s]+"," ", pt2)

		retval= pt1 +" SENTENCE_BOUNDARY "+ pt2
	else:
		retval = nlpObj.parseTree[ s1 ] 

	import re
	return re.sub("[\s\n]+", " ", retval) #white space squeeze
####
def get_feature_bow(e1, e2, nlpObj):
	s1 = e1.sentenceId #nlpObj.getSentenceId(e1.start, e1.end) 
	s2 = e2.sentenceId #nlpObj.getSentenceId(e2.start, e2.end) 

	if s1 != s2 : 
		#print >>sys.stderr, "entity pair is outside a sentence boundary"
		retval= nlpObj.rawText[s1] +  " SENTENCE_BOUNDARY "  + nlpObj.rawText[s2]
	else:
		retval= nlpObj.rawText[s1]	

	import re
	return re.sub("[^\w]+", " ", retval) #anything other than alpha-numerals

##################

if __name__ == "__main__":
	#produce_data_points( documentId ) #docmentId is SeeDev-binary-10662856-1.txt  #pmid-passageid

	documentId = sys.argv[1]

#	nlpObj  = coreNLP()
#	nlpObj.parse(documentId+".txt.out")

#	print nlpObj.sentenceBoundaries
#	for sent in nlpObj.rawText  :
#		print len(sent), sent 
#	print nlpObj.getSentenceId(464, 505)

#	a1file = documentId + ".a1"
#	listOfEntities= get_entitylist_from_a1file( a1file , nlpObj )
#	for e in listOfEntities :
#		e.display()
#		#print "\t", nlpObj.rawText[ e.sentenceId - 1].replace("\n", " ")
#		print "\t", nlpObj.rawText[ e.sentenceId ].replace("\n", " ") 
		

	produce_data_points( documentId , outdir="/tmp/" ) #docmentId is SeeDev-binary-10662856-1.txt  #pmid-passageid
