from rdflib import Namespace, Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
from urllib.parse import quote
from nltk.corpus import wordnet as wn
import queries
from queries import q
import re
from namespaces import *
import urllib.error


def addCanonicalForm(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry ontolex:canonicalForm ontolex:Form

    subj: ontolex:LexicalEntry
    obj: ontolex:Form
    '''
    if subj != obj :
        domain = [ONTOLEX.MultiwordExpression, ONTOLEX.Word, ONTOLEX.Affix]
        if g.value(subject=subj, predicate=RDF.type, object=None) in domain and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.Form:
            g.add((URIRef(str(subj)), ONTOLEX.canonicalForm, URIRef(str(obj))))  

def addSense(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry ontolex:sense ontolex:LexicalSense
    ontolex:LexicalSense ontolex:isSenseOf ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalSense
    '''
    domain = [ONTOLEX.MultiwordExpression, ONTOLEX.Word, ONTOLEX.Affix]
    if g.value(subject=subj, predicate=RDF.type, object=None) in domain and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalSense:
        for o in g.objects(subject = subj, predicate=RDF.type):
            if o != ONTOLEX.Form: # according to Ontolex schema, Form entities are not directly linked to LexicalSense entities
                g.add((URIRef(str(subj)), ONTOLEX.sense, URIRef(str(obj))))
                g.add((URIRef(str(obj)), ONTOLEX.isSenseOf, URIRef(str(subj))))

                lemmaURI = g.value(subject = subj, predicate = ONTOLEX.canonicalForm, object=None)
                addSeeAlso(obj, lemmaURI, g)

def addSeeAlso(obj, lemmaURI, g: Graph):
    '''
    uwn:sense rdfs:seeALso URI
    '''
    for o in g.objects(subject = obj, predicate=OWL.sameAs):
        wnID = g.value(subject = o, predicate=DUMMY.wn30ID, object=None)
        try:
            lilaURI = queries.queryRetry(query = queries.senseQuery.format(wnID), initNs = {'ontolex' : ONTOLEX, 'lime': LIME}, initBindings={'lemmaURI': URIRef(lemmaURI)})
        except urllib.error.URLError or TimeoutError as e:
            print('{} occurred'.format(e))
        else:
            for res in lilaURI:
                g.add((o, RDFS.seeAlso, URIRef(res.senseURI)))

def addSenseRel(subj, obj, g: Graph):
    '''
    ontolex:LexicalSense vartrans:senseRel ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalSense
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalSense and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalSense:
        g.add((URIRef(str(subj)), VARTRANS.senseRel, URIRef(str(obj)))) # TO NVESTIGATE IF SYMMETRIC


def addLexicalRel(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalEntry vartrans:lexicalRel ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    domain = [ONTOLEX.MultiwordExpression, ONTOLEX.Word, ONTOLEX.Affix]
    if g.value(subject=subj, predicate=RDF.type, object=None) in domain and g.value(subject=obj, predicate=RDF.type, object=None) in domain:
        g.add((URIRef(str(subj)), VARTRANS.lexicalRel, URIRef(str(obj)))) # TO NVESTIGATE IF SYMMETRIC


def addSameAs(subj, obj, g: Graph):
    '''
    ontolex:LexicalSense owl:sameAs ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalSense
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalSense and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalSense:
        if g.value(subject=subj, predicate=DCTERMS.source, object=None) != g.value(subject=obj, predicate=DCTERMS.source, object=None):
            g.add((URIRef(str(subj)), OWL.sameAs, URIRef(str(obj))))
            g.add((URIRef(str(obj)), OWL.sameAs, URIRef(str(subj))))

def addLexicalizedSense(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalSense ontolex:isLexicalizedSenseOf ontolex:LexicalConcept
    ontolex:LexicalConcept ontolex:lexicalizedSense ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalConcept
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalSense and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalConcept:
        g.add((URIRef(str(subj)), ONTOLEX.isLexicalizedSenseOf, URIRef(str(obj)))) 
        g.add((URIRef(str(obj)), ONTOLEX.lexicalizedSense, URIRef(str(subj)))) 

def addEvokes(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalEntry ontolex:evokes ontolex:LexicalConcept
    ontolex:LexicalConcept ontolex:isEvokedBy ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalConcept
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalConcept:
        g.add((URIRef(str(subj)), ONTOLEX.evokes, URIRef(str(obj)))) 
        g.add((URIRef(str(obj)), ONTOLEX.isEvokedBy, URIRef(str(subj)))) 


def addDCTIsPartOf(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry dct:isPartOf wn:Example

    subj: ontolex:LexicalEntry
    obj: wn:Example
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == WORDNET.Example:
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
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalSense and g.value(subject=obj, predicate=RDF.type, object=None) == WORDNET.Example:
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
    domain = [SCHEMA.CreativeWorks, SCHEMA.Quotation]
    if g.value(subject=subj, predicate=RDF.type, object=None) in domain and g.value(subject=obj, predicate=RDF.type, object=None) == SCHEMA.Person:
        g.add((URIRef(str(subj)), SCHEMA.author, URIRef(str(obj))))
    elif g.value(subject=subj, predicate=RDF.type, object=None) == SCHEMA.Collection and g.value(subject=obj, predicate=RDF.type, object=None) == SCHEMA.Organization:
        g.add((URIRef(str(subj)), SCHEMA.author, URIRef(str(obj))))

def addHasOccupation(subj, obj, g: Graph):
    '''
    schema:Person schema:hasOccupation schema:Occupation

    subj: schema:Person
    obj: schema:Occupation
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == SCHEMA.Person and g.value(subject=obj, predicate=RDF.type, object=None) == SCHEMA.Occupation:
        g.add((URIRef(str(subj)), SCHEMA.hasOccupation, URIRef(str(obj))))

def convertDate(date): # ISO-8601
    if date < 0:
        if date == -1 : dateString = '+0000'
        else: dateString = '-'+str((date+1)*(-1)).zfill(4)    
    else: dateString = '+'+str(date).zfill(4)

    return dateString      

def addDateInterval(subj, start, end, relation, g: Graph):
    '''
    schema:CreativeWorks schema:datePublished schema:Date
    schema:Quotation schema:datePublished schema:Date
    schema:Collection schema:datePublished schema:Date
    schema:Person schema:birthDate schema:Date
    schema:Person schema:deathDate schema:Date

    subj: schema:CreativeWorks OR schema:Quotation OR schema:Collection OR schema:Person
    start: schema:Date
    end: schema:Date
    relation: PUBLISHED_IN OR BORN OR DIED
    '''
    startString = convertDate(start)
    endString = convertDate(end)
    date = Literal('{}/{}'.format(startString, endString), datatype=SCHEMA.Date)

    domain = [SCHEMA.CreativeWorks, SCHEMA.Quotation, SCHEMA.Collection]
    if g.value(subject=subj, predicate=RDF.type, object=None) in domain:
        if relation == 'PUBLISHED_IN': g.add((URIRef(str(subj)), SCHEMA.datePublished, date))
    elif g.value(subject=subj, predicate=RDF.type, object=None) == SCHEMA.Person:
        if relation == 'BORN': g.add((URIRef(str(subj)), SCHEMA.birthDate, date))
        elif relation == 'DIED': g.add((URIRef(str(subj)), SCHEMA.deathDate, date))
      

def addDatePoint(subj, point, relation, g: Graph):
    '''
    schema:CreativeWorks schema:datePublished schema:Date
    schema:Quotation schema:datePublished schema:Date
    schema:Collection schema:datePublished schema:Date
    schema:Person schema:birthDate schema:Date
    schema:Person schema:deathDate schema:Date

    subj: schema:CreativeWorks OR schema:Quotation OR schema:Collection OR schema:Person
    point: schema:Date
    relation: PUBLISHED_IN OR BORN OR DIED
    '''
    pointString = convertDate(point)
    date = Literal(pointString, datatype=SCHEMA.Date)

    domain = [SCHEMA.CreativeWorks, SCHEMA.Quotation, SCHEMA.Collection]
    if g.value(subject=subj, predicate=RDF.type, object=None) in domain:
        if relation == 'PUBLISHED_IN': g.add((URIRef(str(subj)), SCHEMA.datePublished, date))
    elif g.value(subject=subj, predicate=RDF.type, object=None) == SCHEMA.Person:
        if relation == 'BORN': g.add((URIRef(str(subj)), SCHEMA.birthDate, date)) #    UNAVAILABLE DATA
        elif relation == 'DIED': g.add((URIRef(str(subj)), SCHEMA.deathDate, date)) #    UNAVAILABLE DATA

def addSCHEMAIsPartOf(subj, obj, g: Graph):
    '''
    schema:Quotation schema:isPartOf schema:CreativeWorks
    schema:CreativeWorks schema:isPartOf schema:Collection

    subj: schema:CreativeWorks OR schema:Quotation
    obj: schema:CreativeWorks OR schema:Collection
    '''
    domain = [SCHEMA.CreativeWorks, SCHEMA.Quotation, SCHEMA.Collection]
    if g.value(subject=subj, predicate=RDF.type, object=None) in domain and g.value(subject=obj, predicate=RDF.type, object=None) in domain:
        g.add((URIRef(str(subj)), SCHEMA.isPartOf, URIRef(str(obj))))

def addEtymology(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymology ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry:
        g.add((URIRef(str(subj)), DUMMY.etymology, URIRef(str(obj))))

def addEtymologicalOrigin(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymologicalOriginOf ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry:
        g.add((URIRef(str(subj)), DUMMY.etymologicalOriginOf, URIRef(str(obj))))

def addEtymologicallyRelated(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymologicallyRelated ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry:
        g.add((URIRef(str(subj)), DUMMY.etymologicallyRelated, URIRef(str(obj))))

def addHasDerivedForm(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :hasDerivedForm ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry:
        g.add((URIRef(str(subj)), DUMMY.hasDerivedForm, URIRef(str(obj))))

def addIsDerivedFrom(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :isDerivedFrom ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry:
        g.add((URIRef(str(obj)), DUMMY.isDerivedFrom, URIRef(str(subj))))

def addOrthographyVariant(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :orthographyVariant ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry and g.value(subject=obj, predicate=RDF.type, object=None) == ONTOLEX.LexicalEntry:
        g.add((URIRef(str(subj)), DUMMY.orthographyVariant, URIRef(str(obj))))

