from rdflib import Namespace, Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
from urllib.parse import quote
from nltk.corpus import wordnet as wn
import queries
import re
from namespaces import *

def addCanonicalForm(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry ontolex:canonicalForm ontolex:Form

    subj: ontolex:LexicalEntry
    obj: ontolex:Form
    '''
    if subj != obj :
        g.add((URIRef(str(subj)), ONTOLEX.canonicalForm, URIRef(str(obj)))) # 

def addSense(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry ontolex:sense ontolex:LexicalSense
    ontolex:LexicalSense ontolex:isSenseOf ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalSense
    '''
    for o in g.objects(subject = subj, predicate=RDF.type):
        if o != ONTOLEX.Form: # according to Ontolex schema, Form entities are not directly linked to LexicalSense entities
            g.add((URIRef(str(subj)), ONTOLEX.sense, URIRef(str(obj))))
            g.add((URIRef(str(obj)), ONTOLEX.isSenseOf, URIRef(str(subj))))

def addSenseRel(subj, obj, g: Graph):
    '''
    ontolex:LexicalSense vartrans:senseRel ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalSense
    '''
    g.add((URIRef(str(subj)), VARTRANS.senseRel, URIRef(str(obj)))) # TO NVESTIGATE IF SYMMETRIC

def addSameAs(subj, obj, g: Graph):
    '''
    ontolex:LexicalSense owl:sameAs ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalSense
    '''
    g.add((URIRef(str(subj)), OWL.sameAs, URIRef(str(obj))))

def addLexicalizedSense(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalSense ontolex:isLexicalizedSenseOf ontolex:LexicalConcept
    ontolex:LexicalConcept ontolex:lexicalizedSense ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalConcept
    '''
    g.add((URIRef(str(subj)), ONTOLEX.isLexicalizedSenseOf, URIRef(str(obj)))) 
    g.add((URIRef(str(obj)), ONTOLEX.lexicalizedSense, URIRef(str(subj)))) 

def addEvokes(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalEntry ontolex:evokes ontolex:LexicalConcept
    ontolex:LexicalConcept ontolex:isEvokedBy ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalConcept
    '''
    g.add((URIRef(str(subj)), ONTOLEX.evokes, URIRef(str(obj)))) 
    g.add((URIRef(str(obj)), ONTOLEX.isEvokedBy, URIRef(str(subj)))) 


def addDCTIsPartOf(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry dct:isPartOf wn:Example

    subj: ontolex:LexicalEntry
    obj: wn:Example
    '''
    g.add((URIRef(str(subj)), DCTERMS.isPartOf, URIRef(str(obj))))
    #g.add((URIRef(str(obj), POWLA.start, Literal())))              UNAVAILABLE DATA
    #g.add((URIRef(str(obj), POWLA.end, Literal())))                UNAVAILABLE DATA

def addExample(subj, obj, grade, g: Graph):
    '''
    ontolex:LexicalSense wn:example wn:Example
    wn:Example :grade xsd:float

    subj: ontolex:LexicalSense
    obj: wn:Example
    grade: float value assigned according to DuRel annotation framework
    '''
    g.add((URIRef(str(subj)), WORDNET.example, URIRef(str(obj))))
    g.add((URIRef(str(obj)), DUMMY.grade, Literal(grade, datatype=XSD.float)))

def addAuthor(subj, obj, g: Graph):
    '''
    schema:CreativeWorks schema:author schema:Person
    schema:Quotation schema:author schema:Person
    schema:Collection schema:author schema:Organization
    
    subj: schema:CreativeWorks OR schema:Quotation OR schema:Collection
    obj: schema:Person OR schema:Organization
    '''
    g.add((URIRef(str(subj)), SCHEMA.author, URIRef(str(obj))))

def addHasOccupation(subj, obj, g: Graph):
    '''
    schema:Person schema:hasOccupation schema:Occupation

    subj: schema:Person
    obj: schema:Occupation
    '''
    g.add((URIRef(str(subj)), SCHEMA.hasOccupation, URIRef(str(obj))))

def addDatePublished(subj, obj, g: Graph):
    '''
    schema:CreativeWorks schema:datePublished schema:Date
    schema:Quotation schema:datePublished schema:Date
    schema:Collection schema:datePublished schema:Date

    subj: schema:CreativeWorks OR schema:Quotation OR schema:Collection
    obj: schema:Date
    '''
    g.add((URIRef(str(subj)), SCHEMA.datePublished, URIRef(str(obj))))

def addBirthDate(subj, obj, g: Graph): #    UNAVAILABLE DATA

    '''
    schema:Person schema:birthDate schema:Date

    subj: schema:Person
    obj: schema:Date
    '''
    g.add((URIRef(str(subj)), SCHEMA.birthDate, URIRef(str(obj)))) 

def addDeathDate(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    schema:Person schema:deathDate schema:Date

    subj: schema:Person
    obj: schema:Date
    '''
    g.add((URIRef(str(subj)), SCHEMA.deathDate, URIRef(str(obj))))

def addSCHEMAIsPartOf(subj, obj, g: Graph):
    '''
    schema:Quotation schema:isPartOf schema:CreativeWorks
    schema:CreativeWorks schema:isPartOf schema:Collection

    subj: schema:CreativeWorks OR schema:Quotation
    obj: schema:CreativeWorks OR schema:Collection
    '''
    g.add((URIRef(str(subj)), SCHEMA.isPartOf, URIRef(str(obj))))

def addEtymology(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymology ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    g.add((URIRef(str(subj)), DUMMY.etymology, URIRef(str(obj))))

def addEtymologicalOrigin(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymologicalOriginOf ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    g.add((URIRef(str(subj)), DUMMY.etymologicalOriginOf, URIRef(str(obj))))

def addEtymologicallyRelated(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymologicallyRelated ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    g.add((URIRef(str(subj)), DUMMY.etymologicallyRelated, URIRef(str(obj))))

def addHasDerivedForm(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :hasDerivedForm ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    g.add((URIRef(str(subj)), DUMMY.hasDerivedForm, URIRef(str(obj))))

def addIsDerivedFrom(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :isDerivedFrom ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    g.add((URIRef(str(obj)), DUMMY.isDerivedFrom, URIRef(str(subj))))

def addOrthographyVariant(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :orthographyVariant ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    g.add((URIRef(str(subj)), DUMMY.orthographyVariant, URIRef(str(obj))))