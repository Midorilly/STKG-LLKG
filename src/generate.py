import logging
import pandas as pd
import csv
import jsonlines
import os
from rdflib import Graph, Literal, URIRef
import oxrdflib
import pyoxigraph
import nodes
import relations
import queries
from namespaces import *
import importlib
import utils.etymwn as etymwn

g = Graph(store='Oxigraph')

g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)
g.bind("dct", DCTERMS)
g.bind("owl", OWL)

g.bind("schema", SCHEMA)
g.bind("ontolex", ONTOLEX)
g.bind("vartrans", VARTRANS)
g.bind("lexinfo", LEXINFO)
g.bind("lime", LIME)
g.bind("wn", WORDNET)
g.bind("lexvo", LEXVO)
g.bind("lvont", LVONT)
g.bind("uwn", UWN)
g.bind("lila", LILA)
g.bind("skos", SKOS08)
g.bind("wd", WIKIENTITY)
g.bind("cc", CC)
g.bind("llkg", LLKG)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
llkg = URIRef(LLKG.LLKG)

def setupGraph():
    g.add((llkg, RDF.type, LIME.Lexicon))
    g.add((llkg, RDFS.label, Literal('Linked Linguistic Knowledge Graph', lang='en')))
    g.add((llkg, CC.license, URIRef('https://creativecommons.org/licenses/by-sa/4.0/deed.en')))

    g.serialize(format='ttl')

def languageNodes():
    l = Graph()
    l.bind('skos', SKOS08)
    l.parse(os.path.join(lexvoFolder, 'lexvo_2013-02-09.nt'))
    logger.info('Generating language nodes...')
    for item in l.subjects(predicate=RDF.type, object=LVONT.Language):
        nodes.addLanguageNode(language=item, l=l, g=g)
    english = g.value(subject=None, predicate=RDFS.label, object=Literal('English', lang='en'))
    g.add((llkg, DCTERMS.language, english))
    l.close()
    logger.info('Language nodes generated!')
    logger.info('Serializing language nodes...')
    g.serialize(format='ttl')

def etymNodes(wordsPath):
    logger.info('Generating words nodes...')

    file = open(os.path.join(etymFolder, wordsPath), mode='r', encoding='utf-8')
    reader = csv.reader(file)
    next(reader, None)
    for item in reader:
        nodes.addLexicalEntryNode(entry=item[1], id=item[0], language=item[2], iso='3',  llkg=llkg, g=g)
        if int(item[0]) % 100000 == 0:
            logger.info('Still alive! {}'.format(item[0]))
 
    file.close()
    logger.info('Word nodes generated!')
    logger.info('Serializing EtymWN nodes...')
    g.serialize(format='ttl')

def etymRelations(wordsDict, dataset):

    logger.info('Connecting nodes...')
    
    for index, value in dataset.iterrows():
        subj = str(value['w1']).split(': ')
        obj = str(value['w2']).split(': ')
        property = str(value['rel']).removeprefix('rel:')
        subject = g.value(subject=None, predicate=LLKG.llkgID, object=Literal(wordsDict[subj[1], subj[0]], datatype=XSD.unsignedInt))
        object = g.value(subject=None, predicate=LLKG.llkgID, object=Literal(wordsDict[obj[1], obj[0]], datatype=XSD.unsignedInt))

        if property == 'etymology':
            relations.addEtymology(subject, object, g)
            relations.addEtymologicalOrigin(object, subject, g)           
        elif property == 'etymologically_related':
            relations.addEtymologicallyRelated(subject, object, g)
        elif property == 'has_derived_form':
            relations.addHasDerivedForm(subject, object, g)
            relations.addIsDerivedFrom(subject, object, g)
        elif property == 'variant:orthography':
            relations.addOrthographyVariant(subject, object, g)

        if index % 100000 == 0:
            logger.info('Still alive! {}'.format(index))

    logger.info('Nodes successfully connected!')
    logger.info('Serializing EtymWN relations...')
    g.serialize(format='ttl')

lkgDataset = '../knowledge-graph/data/lkg/full-dataset-v3.jsonl'
wikidataMap = '../knowledge-graph/data/lkg/wikidata_metadata/'

def resourceNodes():
    logger.info('Generating resources nodes...')
    nodes.addResourceNode(resource='https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.04.0059', label='Lewis-Short Dictionary', g=g)
    nodes.addResourceNode(resource='https://lila-erc.eu/data/lexicalResources/LatinWordNet/Lexicon', label='Latin WordNet', g=g)
    nodes.addResourceNode(resource='https://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/yago-naga/uwn', label='Universal WordNet', g=g)
    logger.info('Serializing resources...')

def frameworkNodes():
    nodes.addFrameworkNode(framework='DuRel', g=g)
    
def lemmaNodes():
    logger.info('Generating lemma nodes...')
    with jsonlines.open(lkgDataset, 'r') as lkg:   
        lemmas = (line for line in lkg if line['jtype'] == 'node' and line['label'] == 'Lemma')
        for line in lemmas:     
            nodes.addFormNode(writtenRep=line['properties']['value'], pos=line['properties']['posTag'], id=line['identity'], llkg=llkg, g=g)      
    
def entryNodes():
    logger.info('Generating entries nodes...')
    with jsonlines.open(lkgDataset, 'r') as lkg:
        lexicalEntries = (line for line in lkg if line['jtype'] == 'node' and line['label'] == 'InflectedWord')  
        for line in lexicalEntries:
            nodes.addLexicalEntryNode(entry=line['properties']['value'], id=line['identity'], language='lat', iso='3', llkg=llkg, g=g)

def senseNodes(): 
    logger.info('Generating lexical sense nodes...')
    with jsonlines.open(lkgDataset, 'r') as lkg:
        lexicalSenses = (line for line in lkg if line['jtype'] == 'node' and line['label'] == 'LexiconConcept')
        for line in lexicalSenses:
            resource = line['properties']['resource']
            if resource == 'Lewis-Short Dictionary':
                nodes.addLexicalSenseNode(resource=resource, sense=line['properties']['id'], gloss=line['properties']['alias'], id=line['identity'], g=g) 
            elif resource == 'Latin WordNet':
                nodes.addLexicalSenseNode(resource='Universal WordNet', sense=line['properties']['alias'], gloss=line['properties']['gloss'], id=line['identity'], g=g) 

def authorNodes():
    logger.info('Generating author nodes...')
    #authors_df = pd.read_csv(os.path.join(wikidataMap, 'annotation.csv'), header=0, usecols=[2,3,4,5], names=['name', 'lastname', 'title', 'id'])
    authors_df = pd.read_csv(os.path.join(wikidataMap, 'annotation.csv'), header=0, usecols=['lastname', 'name', 'work', 'id'])
    authors_df = authors_df.drop_duplicates(subset=['lastname', 'name', 'id'])
    logger.info('{} unique authors'.format(authors_df['id'].nunique()))
    authors_df = authors_df.fillna('')
    authors_df['fullname'] = authors_df['lastname'] + ' ' + authors_df['name']
    print(authors_df['fullname'].values.tolist())
    with jsonlines.open(lkgDataset, 'r') as lkg:
        authors = [line for line in lkg if line['jtype'] == 'node' and line['label'] == 'Person']     
        for line in authors:
           nodes.addPersonNode(firstname=line['properties']['name'], lastname=line['properties']['lastname'], id=line['identity'], df=authors_df, g=g)

def occupationNodes():
    file = open(os.path.join(wikidataMap, 'occupations_map.tsv'), encoding='utf-8', mode='r')
    reader = csv.reader(file, delimiter='\t')
    occupationDict = {}
    for row in reader:
        occupationDict[row[1]] = row[0]
    file.close()

    logger.info('Generating occupation nodes...')
    with jsonlines.open(lkgDataset, 'r') as lkg:
        occupations = [line for line in lkg if line['jtype']=='node' and line['label']=='Occupation']        
        for line in occupations:
           nodes.addOccupationNode(occupation=line['properties']['value'], id=line['identity'], dict=occupationDict, g=g)

def textNodes():
    logger.info('Generating text nodes...')
    with jsonlines.open(lkgDataset, 'r') as lkg:
        occurrences = [line for line in lkg if line['jtype'] == 'node' and line['label'] == 'Text']
        for line in occurrences:
            nodes.addQuotationNode(quotation=line['properties']['value'], language='Latin', id=line['identity'], g=g)

def documentNodes():
    logger.info('Generating document nodes...')
    with jsonlines.open(lkgDataset, 'r') as lkg:
        documents = [line for line in lkg if line['jtype'] == 'node' and line['label'] == 'Document']
        for line in documents: # adds dummy nodes
            nodes.addDummyBookNode(title=line['properties']['title'], id=line['identity'], g=g)

    with jsonlines.open(lkgDataset, 'r') as lkg:
        hasAuthor = [line for line in lkg if line['jtype'] == 'relationship' and line['name'] == 'HAS_AUTHOR']
        for line in hasAuthor:
            document = g.value(predicate=LLKG.llkgID, object=Literal(line['subject'], datatype=XSD.unsignedInt))
            author = g.value(predicate=LLKG.llkgID, object=Literal(line['object'], datatype=XSD.unsignedInt))
            nodes.addBookNode(document=document, author=author, g=g)
            
def corpusNodes():
    logger.info('Generating corpora nodes...')
    with jsonlines.open(lkgDataset, 'r') as lkg:
        corpora = [line for line in lkg if line['jtype'] == 'node' and line['label'] == 'Corpus']
        for line in corpora:
            nodes.addCollectionNode(title=line['properties']['name'], id=line['identity'], g=g)           

def dateDictionary():
    logger.info('Generating dates dictionary...')

    with jsonlines.open(lkgDataset, 'r') as lkg:
        startTimes = [line for line in lkg if line['jtype'] == 'relationship' and line['name'] == 'startTime']
        startDict = {}
        for line in startTimes:
            startDict[line['subject']] = line['object']

    with jsonlines.open(lkgDataset, 'r') as lkg:
        endTimes = [line for line in lkg if line['jtype'] == 'relationship' and line['name'] == 'endTime']
        endDict = {}
        for line in endTimes:
            endDict[line['subject']] = line['object']
        
        intervalsDict = {}
        for k in startDict.keys():
            intervalsDict.update({k : (startDict[k], endDict[k])})

    with jsonlines.open(lkgDataset, 'r') as lkg:
        timePoints = [line for line in lkg if line['jtype'] == 'node' and line['label'] == 'TimePoint']
        pointsDict = {}
        for line in timePoints:
            pointsDict[line['identity']] = line['properties']['Year']

    return intervalsDict, pointsDict

def lkgRelations():

    intervalsDict, pointsDict = dateDictionary()

    with jsonlines.open(lkgDataset, 'r') as lkg:
        relationships = [line for line in lkg if line['jtype'] == 'relationship']
        logger.info('Connecting canonical forms...')
        for line in relationships:
            property = line['name']
            subj = g.value(predicate=LLKG.llkgID, object=Literal(line['subject'], datatype=XSD.unsignedInt))
            obj = g.value(predicate=LLKG.llkgID, object=Literal(line['object'], datatype=XSD.unsignedInt))

            if property == 'HAS_LEMMA':    
                relations.addCanonicalForm(subj, obj, line['subject'], line['object'], g)
    logger.info('Serializing canonical form relation...')
    g.serialize(format='ttl')

    with jsonlines.open(lkgDataset, 'r') as lkg:
        relationships = [line for line in lkg if line['jtype'] == 'relationship']
        logger.info('Connecting nodes...')
        for line in relationships:
            property = line['name']
            subj = g.value(predicate=LLKG.llkgID, object=Literal(line['subject'], datatype=XSD.unsignedInt))
            obj = g.value(predicate=LLKG.llkgID, object=Literal(line['object'], datatype=XSD.unsignedInt))

            if property == 'HAS_SUBCLASS':
                relations.addSenseRel(subj, obj, g)        
            elif property == 'SAME_AS':
                relations.addSameAs(subj, obj, g)
            elif property == 'HAS_AUTHOR':
                relations.addAuthor(subj, obj, g)
            elif property == 'HAS_OCCUPATION':
                relations.addHasOccupation(subj, obj, g)
            elif property == 'BELONG_TO' or property == 'HAS_CORPUS':
                relations.addSCHEMAIsPartOf(subj, obj, g)
            elif property == 'HAS_OCCURRENCE':
                relations.addDCTIsPartOf(subj, obj, line['subject'], line['object'], g)
            elif property == 'HAS_EXAMPLE': 
                relations.addExample(subj, obj, line['properties']['grade'], line['object'], g)     
            elif property == 'PUBLISHED_IN' or property == 'BORN' or property == 'DIED':
                if line['object'] in intervalsDict.keys():
                    s, e = intervalsDict[line['object']]
                    start = pointsDict[s]
                    end = pointsDict[e]
                    relations.addDateInterval(subj, start, end, property, g)
                elif line['object'] in pointsDict.keys():
                    relations.addDatePoint(subj, pointsDict[line['object']], property, g)
    logger.info('Nodes successfully connected!')

def lkgSeeAlso():

    with jsonlines.open(lkgDataset, 'r') as lkg:
        concepts = [line for line in lkg if line['jtype'] == 'relationship' and line['name'] == 'HAS_CONCEPT']
        logger.info('Connecting senses...')
        for line in concepts:
            subj = g.value(predicate=LLKG.llkgID, object=Literal(line['subject'], datatype=XSD.unsignedInt))
            obj = g.value(predicate=LLKG.llkgID, object=Literal(line['object'], datatype=XSD.unsignedInt))

            relations.addSense(subj, obj, g)

    logger.info('Nodes successfully connected!')

def generateEtymologicalNodes(etymFolder, etymwnGraph):
    dataset, entries = etymwn.loadDataset(os.path.join(etymFolder, 'etymwn.tsv'))
    etymwn.writeWords(entries, os.path.join(etymFolder, 'words.csv'))
    wordsDict = etymwn.loadDictionary(os.path.join(etymFolder, 'words.csv'))
    etymNodes(wordsPath='words.csv')
    etymRelations(wordsDict, dataset)
    logger.info('Serializing EtymWN...')
    g.serialize(destination=etymwnGraph,format='ttl',encoding='utf-8')
    logger.info('EtymWN successfully serialized!')
    logger.info('{}, {} external links'.format(nodes.links, relations.relationslinks))

def generateLatinISENodes(etymwnGraph, latiniseGraph):
    logger.info('Parsing EtymWN graph...')
    g.parse(etymwnGraph, format='ttl')
    resourceNodes()
    frameworkNodes()
    lemmaNodes()
    g.serialize(format='ttl')
    entryNodes()
    senseNodes()
    authorNodes()
    occupationNodes()
    textNodes()
    documentNodes()
    corpusNodes()
    logger.info('Serializing LatinISE...')
    g.serialize(destination=latiniseGraph,format='ttl', encoding='utf-8')
    logger.info('LatinISE successfully serialized!')
    logger.info('{}, {} external links'.format(nodes.links, relations.relationslinks))

def generateLinks(latiniseGraph, llkgGraph):
    logger.info('Parsing graph...')
    g.parse(latiniseGraph, format='ttl')
    lkgRelations()
    logger.info('Serializing relations...')
    g.serialize(destination=llkgGraph,format='ttl',encoding='utf-8')
    logger.info('LLKG successfully serialized!')
    logger.info('{}, {} external links'.format(nodes.links, relations.relationslinks))

def generateSeeAlso(llkgGraph, finalGraph):
    logger.info('Parsing graph...')
    g.parse(llkgGraph, format='ttl')
    senseNodes()
    logger.info('Serializing new senses...')
    g.serialize(format='ttl')
    lkgSeeAlso()
    logger.info('Serializing relations...')
    g.serialize(destination=finalGraph,format='ttl',encoding='utf-8')  


etymFolder = '../knowledge-graph/data/etymwn' 
lexvoFolder = '../knowledge-graph/data/lexvo'
etymwnGraph = '../knowledge-graph/data/llkg/etymwn-llkg.ttl'
latiniseGraph = '../knowledge-graph/data/llkg/etymwn-latinise-llkg.ttl'
llkgGraph = '../knowledge-graph/data/llkg/llkg-cr.ttl'
finalGraph = '../knowledge-graph/data/llkg/final-llkg-cr.ttl'

if __name__ == '__main__':
    importlib.reload(nodes)
    importlib.reload(relations)
    importlib.reload(etymwn)
    importlib.reload(queries)

    setupGraph()
    languageNodes()

    generateEtymologicalNodes(etymFolder,etymwnGraph)
    generateLatinISENodes(etymwnGraph, latiniseGraph)
    generateLinks(latiniseGraph,llkgGraph)
    generateSeeAlso(llkgGraph, finalGraph)


