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

def addCanonicalForm(subj, obj, g: Graph):
    if subj != obj :
        g.add((URIRef(str(subj)), ONTOLEX.canonicalForm, URIRef(str(obj))))

def addSense(subj, obj, g: Graph):
    for o in g.objects(subject = subj, predicate=RDF.type):
        if o != ONTOLEX.Form: # according to Ontolex schema, Form entities are not directly linked to LexicalSense entities
            g.add((URIRef(str(subj)), ONTOLEX.sense, URIRef(str(obj))))
            g.add((URIRef(str(obj)), ONTOLEX.isSenseOf, URIRef(str(subj))))

def addSenseRel(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), VARTRANS.senseRel, URIRef(str(obj))))

def addSameAs(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), OWL.sameAs, URIRef(str(obj))))

def addDCTIsPartOf(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), DCTERMS.isPartOf, URIRef(str(obj))))
    #g.add((URIRef(str(obj), POWLA.start, Literal())))              UNAVAILABLE DATA
    #g.add((URIRef(str(obj), POWLA.end, Literal())))                UNAVAILABLE DATA

def addExample(subj, obj, line, g: Graph):
    g.add((URIRef(str(subj)), WORDNET.example, URIRef(str(obj))))
    g.add((URIRef(str(obj)), DUMMY.grade, Literal(line['properties']['grade'], datatype=XSD.float)))

def addAuthor(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), SCHEMA.author, URIRef(str(obj))))

def addHasOccupation(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), SCHEMA.hasOccupation, URIRef(str(obj))))

def addDatePublished(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), SCHEMA.datePublished, URIRef(str(obj))))

def addSCHEMAIsPartOf(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), SCHEMA.isPartOf, URIRef(str(obj))))

def addEtymology(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), DUMMY.etymology, URIRef(str(obj))))

def addEtymologicalOrigin(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), DUMMY.etymologicalOriginOf, URIRef(str(obj))))

def addEtymologicallyRelated(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), DUMMY.etymologicallyRelated, URIRef(str(obj))))

def addHasDerivedForm(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), DUMMY.hasDerivedForm, URIRef(str(obj))))

def addIsDerivedFrom(subj, obj, g: Graph):
    g.add((URIRef(str(obj)), DUMMY.isDerivedFrom, URIRef(str(subj))))

def addOrthographyVariant(subj, obj, g: Graph):
    g.add((URIRef(str(subj)), DUMMY.orthographyVariant, URIRef(str(obj))))