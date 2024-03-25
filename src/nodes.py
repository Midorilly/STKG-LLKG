from rdflib import Namespace, Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
from urllib.parse import quote
from nltk.corpus import wordnet as wn
import queries
import re

SCHEMA = Namespace("https://schema.org/")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
VARTRANS = Namespace("http://www.w3.org/ns/lemon/vartrans#")
LEXINFO = Namespace("http://www.lexinfo.net/ontology/2.0/lexinfo#")
LIME = Namespace("http://www.w3.org/ns/lemon/lime#")
WORDNET = Namespace("https://globalwordnet.github.io/schemas/wn#")
LEXVO = Namespace("http://lexvo.org/id/term/")
LVONT = Namespace("http://lexvo.org/ontology#")
UWN = Namespace("http://www.lexvo.org/uwn/entity/s/")
LILA = Namespace("http://lila-erc.eu/ontologies/lila/")
SKOS = Namespace("http://www.w3.org/2008/05/skos#")
WIKIENTITY = Namespace("http://www.wikidata.org/entity/")
WIKIPROP = Namespace("http://www.wikidata.org/prop/direct/")
WIKIBASE = Namespace("http://wikiba.se/ontology#")
DUMMY = Namespace("http://dummy.com/")

lilaPosMapping = {'N' : LILA.noun, 'ADJ' : LILA.adjective, 'V' : LILA.verb}
lexinfoPosMapping = {'N' : LEXINFO.noun , 'ADJ' : LEXINFO.adjective, 'V' : LEXINFO.verb}

def updateEntry(entry, llkg, g: Graph):
    g.add((llkg, LIME.entry, entry))

def addResourceNode(resource: str, label: str ,g: Graph):
    resource = URIRef(resource)
    g.add((resource, RDF.type, RDFS.Resource))
    g.add((resource, RDFS.label, Literal(label, lang='en')))

def addFormNode(line, g: Graph):
    result = g.query(queries.lemmaQuery, initNs = {'ontolex' : ONTOLEX, 'lila': LILA}, initBindings={'entry': Literal(line['properties']['value']), 'pos' : URIRef(lilaPosMapping[line['properties']['posTag']]) })
    for r in result:
        lemma = r.lemma    
        g.add((lemma, RDF.type, ONTOLEX.Form))
        g.add((lemma, RDFS.label, Literal(line['properties']['value'])))
        g.add((lemma, DUMMY.lkgID, Literal(line['identity'], datatype=XSD.unsignedInt)))
        g.add((lemma, ONTOLEX.writtenRep, Literal(line['properties']['value'], lang='la'))) 
        g.add((lemma, LEXINFO.partOfSpeech, URIRef(lexinfoPosMapping[line['properties']['posTag']])))
        g.add((lemma, DCTERMS.language, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal('Latin', lang='en'), any=False)))))

def addLexicalEntryNode(line, llkg, g: Graph):
    value = line['properties']['value'].lower()
    word = URIRef(LEXVO+'lat/{}'.format(value))
    if not (word, None, None) in g:
        updateEntry(word, llkg, g)
        if bool(re.search(r'\s', value)):
            g.add((word, RDF.type, ONTOLEX.MultiwordExpression))
        elif value.startswith('-') or value.endswith('-'):
            g.add((word, RDF.type, ONTOLEX.Affix))
        else:
            g.add((word, RDF.type, ONTOLEX.Word))
        g.add((word, RDFS.label, Literal(value)))
        g.add((word, DCTERMS.language, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal('Latin', lang='en'), any=False)))))
        g.add((word, DUMMY.lkgID, Literal(line['identity'], datatype=XSD.unsignedInt)))
    else:
        g.add((word, DUMMY.lkgID, Literal(line['identity'], datatype=XSD.unsignedInt)))

def addLexicalSenseNode(line, g: Graph):
    senseURI = None

    if line['properties']['resource'] == 'Lewis-Short Dictionary':
        sense = line['properties']['id']
        senseURI = URIRef(sense)
        g.add((senseURI, RDF.type, ONTOLEX.LexicalSense))
        g.add((senseURI, RDFS.label, Literal(sense, datatype=XSD.string)))
        g.add((senseURI, DCTERMS.source, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal('Lewis-Short Dictionary', lang='en'))))))
        g.add((senseURI, DCTERMS.description, Literal(line['properties']['alias'], lang='en')))     

    elif line['properties']['resource'] == 'Latin WordNet':
        sense = line['properties']['alias']
        wn30sense = wn.synset(sense)
        wn30offset = str(wn30sense.offset())
        wn30pos = str(wn30sense.pos())
        wn30id = '{}-{}'.format(wn30offset,wn30pos)
        senseURI = URIRef(UWN+'{}{}'.format(wn30pos, wn30offset))   
        # aggiungere identifier      
        g.add((senseURI, RDF.type, ONTOLEX.LexicalSense))
        g.add((senseURI, RDFS.label, Literal(sense, datatype=XSD.string)))
        g.add((senseURI, DCTERMS.source, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal('Lewis-Short Dictionary', lang='en'))))))
        g.add((senseURI, DCTERMS.description, Literal(line['properties']['gloss'], lang='en')))
        g.add((senseURI, DUMMY.wn30ID, Literal(wn30id, datatype=XSD.string)))

    g.add((senseURI, DUMMY.lkgID, Literal(line['identity'], datatype=XSD.unsignedInt)))

def addPersonNode(line, df, g: Graph):
    name = line['properties']['name']
    lastname = line['properties']['lastname']
    if not lastname:
        wikiEntity = df.loc[(df['name'] == name), 'id'].values             
    else:
        wikiEntity = df.loc[((df['name'] == name) & (df['lastname'] == lastname)), 'id'].values
    
    if wikiEntity.size > 0:
        author = URIRef(WIKIENTITY+wikiEntity[0])
        g.add((author, RDF.type, SCHEMA.Person))
        g.add((Literal(name), RDF.type, SCHEMA.Text))
        g.add((author, SCHEMA.givenName, Literal(name)))
        if len(lastname)>0:
            g.add((Literal(lastname), RDF.type, SCHEMA.Text))
            g.add((author, SCHEMA.familyName, Literal(lastname)))
        g.add((author, DUMMY.lkgID, Literal(line['identity'], datatype=XSD.unsignedInt)))

def addOccupationNode(line, dict, g: Graph):
    value = line['properties']['value']
    occupation = URIRef(WIKIENTITY+dict[value])
    g.add((occupation, RDF.type, SCHEMA.Occupation))
    g.add((occupation, RDFS.label, Literal(value, datatype=XSD.string)))
    g.add((occupation, DUMMY.lkgID, Literal(line['identity'], datatype=XSD.unsignedInt)))

def addQuotationNode(line, id, g: Graph):
    text = Literal('text_{}'.format(id))
    g.add((text, RDF.type, SCHEMA.Quotation))
    g.add((text, SCHEMA.text, Literal(line['properties']['value'], datatype=XSD.string)))
    g.add((text, DCTERMS.language, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal('Latin', lang='en'), any=False))))) 

def addCreativeWorkNode(line, g: Graph):
    # to do
    return 0

def addCollectionNode(line, g: Graph):
    corpus = Literal(line['properties']['name'], datatype=XSD.string)
    g.add((corpus, RDF.type, SCHEMA.Collection))

def addLanguageNode(line, l: Graph, g: Graph):
    language = URIRef(str(line))
    g.add((language, RDF.type, DCTERMS.LinguisticSystem))
    g.add((language, RDFS.label, Literal(l.value(subject=line, predicate=SKOS.prefLabel, object=None), lang='en')))
    g.add((language, DUMMY.iso6391, Literal(l.value(subject=line, predicate=LVONT.iso639P1Code, object=None, any=False), datatype=XSD.string)))
    g.add((language, DUMMY.iso6392, Literal(l.value(subject=line, predicate=LVONT.iso6392TCode, object=None, any=False), datatype=XSD.string)))
    g.add((language, DUMMY.iso6393, Literal(l.value(subject=line, predicate=LVONT.iso639P3PCode, object=None, any=False), datatype=XSD.string)))

def addEtymLexicalEntryNode(line, g: Graph):
    wordString = str(line[1])
    word = URIRef(LEXVO+line[2]+'/'+quote(wordString))
    if not (word, None, None) in g:
        updateEntry(word, line, g)     
        if bool(re.search(r'\s', wordString)):
            g.add((word, RDF.type, ONTOLEX.MultiwordExpression))
        elif wordString.startswith('-') or wordString.endswith('-'):
            g.add((word, RDF.type, ONTOLEX.Affix))
        else:
            g.add((word, RDF.type, ONTOLEX.Word))
        g.add((word, RDFS.label, Literal(wordString, datatype=XSD.string)))
        g.add((word, DCTERMS.identifier, Literal(line[0], datatype=XSD.string)))
        g.add((word, DCTERMS.language, g.value(subject=None, predicate=DUMMY.iso6393, object=Literal(line[2], datatype=XSD.string))))
    else:
        g.add((word, DCTERMS.identifier, Literal(line[0], datatype=XSD.string)))