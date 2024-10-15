from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
from nltk.corpus import wordnet as wn
import queries
from namespaces import *
import urllib.error
import logging
from SPARQLWrapper import SPARQLExceptions

relationslinks = 0
occurr = 0

def count():
    global relationslinks
    relationslinks += 1

def countOcc():
    global occurr
    occurr += 1

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

subClassOfLexicalEntry = [s for s in llkgSchema.subjects(predicate=RDFS.subClassOf, object=ONTOLEX.LexicalEntry)]
subClassOfCreativeWork = [s for s in llkgSchema.subjects(predicate=RDFS.subClassOf, object=SCHEMA.CreativeWork)]

canonicalForm = {'domain': subClassOfLexicalEntry, 'range': [ONTOLEX.Form]}

def addCanonicalForm(subj, obj, subjID, objID, g: Graph):
    '''
    ontolex:LexicalEntry ontolex:canonicalForm ontolex:Form

    subj: ontolex:LexicalEntry
    obj: ontolex:Form
    '''
    #logger.info('{} has canonical form {}'.format(subj,obj))
    if g.value(subject=subj, predicate=RDF.type, object=None) in canonicalForm['range']: # should be LexicalEntry subclass
        entries = g.subjects(predicate=RDF.type, object=ONTOLEX.Word)
        for e in entries:
            if g.value(subject=e, predicate=LLKG.llkgID) == Literal(subjID, datatype=XSD.integer):
                subj = e
                break
    if g.value(subject=obj, predicate=RDF.type, object=None) in canonicalForm['domain']: # should be Form class
        lemmas = g.subjects(predicate=RDF.type, object=ONTOLEX.Form)
        for l in lemmas:
            if g.value(subject=l, predicate=LLKG.llkgID) == Literal(objID, datatype=XSD.integer):
                obj = l
                break
    if g.value(subject=subj, predicate=RDF.type, object=None) in canonicalForm['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in canonicalForm['range']:
        g.add((URIRef(str(subj)), ONTOLEX.canonicalForm, URIRef(str(obj))))
      
sense = {'domain': subClassOfLexicalEntry, 'range': [ONTOLEX.LexicalSense]}

def addSense(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry ontolex:sense ontolex:LexicalSense
    ontolex:LexicalSense ontolex:isSenseOf ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalSense
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in sense['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in sense['range']:
        for o in g.objects(subject = subj, predicate=RDF.type):
            if o != ONTOLEX.Form: # according to Ontolex schema, Form entities are not directly linked to LexicalSense entities
                g.add((URIRef(str(subj)), ONTOLEX.sense, URIRef(str(obj))))
                g.add((URIRef(str(obj)), ONTOLEX.isSenseOf, URIRef(str(subj))))

                lemmaURI = g.value(subject = subj, predicate = ONTOLEX.canonicalForm, object=None)
                addSeeAlso(obj, lemmaURI, g)

def addSeeAlso(obj, lemmaURI, g: Graph):
    '''
    ontolex:LexicalSense rdfs:seeALso ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalSense
    '''
    for o in g.objects(subject = obj, predicate=OWL.sameAs):
        wnID = g.value(subject = o, predicate=LLKG.wn31ID, object=None)
        try:
            lilaURI = queries.queryRetry(query = queries.senseQuery.format(wnID), initNs = {'ontolex' : ONTOLEX, 'lime': LIME}, initBindings={'lemmaURI': URIRef(lemmaURI), 'resource': URIRef('http://lila-erc.eu/data/lexicalResources/LatinWordNet/Lexicon')})
        except urllib.error.URLError or TimeoutError as e:
            print('{} occurred'.format(e))
        else:
            if len(lilaURI) > 0:
                for r in lilaURI:
                    if r.senseURI not in g.objects(subject = o, predicate = RDFS.seeAlso):
                        count()
                        logger.info('Addinf seeAlso')
                        g.add((o, RDFS.seeAlso, URIRef(r.senseURI)))

senseRel = {'domain': [ONTOLEX.LexicalSense], 'range': [ONTOLEX.LexicalSense]}

def addSenseRel(subj, obj, g: Graph):
    '''
    ontolex:LexicalSense vartrans:senseRel ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalSense
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in senseRel['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in senseRel['range']:
        g.add((URIRef(str(subj)), VARTRANS.senseRel, URIRef(str(obj)))) # TO NVESTIGATE IF SYMMETRIC

lexicalRel = {'domain':subClassOfLexicalEntry, 'range': subClassOfLexicalEntry}

def addLexicalRel(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalEntry vartrans:lexicalRel ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in lexicalRel['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in lexicalRel['range']:
        g.add((URIRef(str(subj)), VARTRANS.lexicalRel, URIRef(str(obj)))) # TO NVESTIGATE IF SYMMETRIC

sameAs = dict(senseRel)

def addSameAs(subj, obj, g: Graph):
    '''
    ontolex:LexicalSense owl:sameAs ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalSense
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in sameAs['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in sameAs['range']:
        if g.value(subject=subj, predicate=DCTERMS.source, object=None) != g.value(subject=obj, predicate=DCTERMS.source, object=None):
            g.add((URIRef(str(subj)), OWL.sameAs, URIRef(str(obj))))
            g.add((URIRef(str(obj)), OWL.sameAs, URIRef(str(subj))))

isLexicalizedSense = {'domain': [ONTOLEX.LexicalSense], 'range': [ONTOLEX.LexicalConcept]}

def addLexicalizedSense(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalSense ontolex:isLexicalizedSenseOf ontolex:LexicalConcept
    ontolex:LexicalConcept ontolex:lexicalizedSense ontolex:LexicalSense

    subj: ontolex:LexicalSense
    obj: ontolex:LexicalConcept
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in isLexicalizedSense['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in isLexicalizedSense['range']:
        g.add((URIRef(str(subj)), ONTOLEX.isLexicalizedSenseOf, URIRef(str(obj)))) 
        g.add((URIRef(str(obj)), ONTOLEX.lexicalizedSense, URIRef(str(subj)))) 

evokes = {'domain': subClassOfLexicalEntry, 'range': [ONTOLEX.LexicalConcept]}

def addEvokes(subj, obj, g: Graph): #    UNAVAILABLE DATA
    '''
    ontolex:LexicalEntry ontolex:evokes ontolex:LexicalConcept
    ontolex:LexicalConcept ontolex:isEvokedBy ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalConcept
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in evokes['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in evokes['range']:
        g.add((URIRef(str(subj)), ONTOLEX.evokes, URIRef(str(obj)))) 
        g.add((URIRef(str(obj)), ONTOLEX.isEvokedBy, URIRef(str(subj)))) 


DCTIsPartOf = {'domain': subClassOfLexicalEntry, 'range': [WORDNET.Example]}

def addDCTIsPartOf(subj, obj, subjID, objID, g: Graph):
    '''
    ontolex:LexicalEntry dct:isPartOf wn:Example

    subj: ontolex:LexicalEntry
    obj: wn:Example
    '''
    if g.value(subject=subj, predicate=RDF.type) == ONTOLEX.Form:
        entries = g.subjects(predicate=RDF.type, object=ONTOLEX.Word)
        for e in entries:
            if g.value(subject=e, predicate=LLKG.llkgID, object=None) == Literal(subjID, datatype=XSD.integer):
                subj = e
                break 
    if g.value(subject=obj, predicate=RDF.type) == SCHEMA.Quotation:
        examples = g.subjects(predicate=RDF.type, object=WORDNET.Example)
        for e in examples:
            if g.value(subject=e, predicate=LLKG.llkgID, object=None) == Literal(objID, datatype=XSD.integer):
                obj = e
                break
    if g.value(subject=subj, predicate=RDF.type, object=None) in DCTIsPartOf['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in DCTIsPartOf['range']:
        g.add((URIRef(str(subj)), DCTERMS.isPartOf, URIRef(str(obj))))
        #g.add((URIRef(str(obj), POWLA.start, Literal())))              UNAVAILABLE DATA
        #g.add((URIRef(str(obj), POWLA.end, Literal())))                UNAVAILABLE DATA

example = {'domain': [ONTOLEX.LexicalSense], 'range': [WORDNET.Example]}

def addExample(subj, obj, grade, objID, g: Graph):
    '''
    ontolex:LexicalSense wn:example wn:Example
    wn:Example :grade xsd:float

    subj: ontolex:LexicalSense
    obj: wn:Example
    grade: float value assigned according to DuRel annotation framework
    '''
    if g.value(subject=obj, predicate=RDF.type) == SCHEMA.Quotation:
        examples = g.subjects(predicate=RDF.type, object=WORDNET.Example)
        for e in examples:
            if g.value(subject=e, predicate=LLKG.llkgID) == Literal(objID, datatype=XSD.integer):
                obj = e
                break
    if g.value(subject=subj, predicate=RDF.type, object=None) in example['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in example['range']:
        g.add((URIRef(str(subj)), WORDNET.example, URIRef(str(obj))))
        g.add((URIRef(str(obj)), LLKG.grade, Literal(grade, datatype=XSD.float)))
        #g.add((g.value(subject=URIRef(str(obj)), predicate=LLKG.grade), DCTERMS.conformsTo, g.value(predicate=RDFS.label, object=Literal(framework, datatype=XSD.string))))
        

author = {'domain': subClassOfCreativeWork, 'range': [SCHEMA.Person, SCHEMA.Organization]}

def addAuthor(subj, obj, g: Graph):
    '''
    schema:Book schema:author schema:Person
    schema:Quotation schema:author schema:Person
    schema:Collection schema:author schema:Organization
    
    subj: schema:Book OR schema:Quotation OR schema:Collection
    obj: schema:Person OR schema:Organization
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in author['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in author['range']:
        g.add((URIRef(str(subj)), SCHEMA.author, URIRef(str(obj))))
        g.add((URIRef(str(obj)), LLKG.isAuthor, URIRef(str(subj))))
        
            
hasOccupation = {'domain': [SCHEMA.Person], 'range': [SCHEMA.Occupation]}

def addHasOccupation(subj, obj, g: Graph):
    '''
    schema:Person schema:hasOccupation schema:Occupation

    subj: schema:Person
    obj: schema:Occupation
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in hasOccupation['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in hasOccupation['range']:
        g.add((URIRef(str(subj)), SCHEMA.hasOccupation, URIRef(str(obj))))

def convertDate(date): # ISO-8601
    if date < 0:
        if date == -1 : dateString = '+0000'
        else: dateString = '-'+str((date+1)*(-1)).zfill(4)    
    else: dateString = '+'+str(date).zfill(4)

    return dateString      

dateCreativeWork = {'domain': subClassOfCreativeWork, 'range': [SCHEMA.Date]}
datePerson = {'domain': [SCHEMA.Person], 'range': [SCHEMA.Date]}

def addDateInterval(subj, start, end, relation, g: Graph):
    '''
    schema:Book schema:datePublished schema:Date
    schema:Quotation schema:datePublished schema:Date
    schema:Collection schema:datePublished schema:Date
    schema:Person schema:birthDate schema:Date
    schema:Person schema:deathDate schema:Date

    subj: schema:Book OR schema:Quotation OR schema:Collection OR schema:Person
    start: schema:Date
    end: schema:Date
    relation: PUBLISHED_IN OR BORN OR DIED
    '''
    startString = convertDate(start)
    endString = convertDate(end)
    date = Literal('{}/{}'.format(startString, endString), datatype=SCHEMA.Date)
    
    if g.value(subject=subj, predicate=RDF.type, object=None) == WORDNET.Example:
        subj  = g.value(subject=subj, predicate=DCTERMS.isPartOf, object=None)

    if g.value(subject=subj, predicate=RDF.type, object=None) in dateCreativeWork['domain']:
        if relation == 'PUBLISHED_IN': g.add((URIRef(str(subj)), SCHEMA.datePublished, date))
    elif g.value(subject=subj, predicate=RDF.type, object=None) in datePerson['domain']:
        if relation == 'BORN': g.add((URIRef(str(subj)), SCHEMA.birthDate, date)) #    UNAVAILABLE DATA
        elif relation == 'DIED': g.add((URIRef(str(subj)), SCHEMA.deathDate, date)) #    UNAVAILABLE DATA
      

def addDatePoint(subj, point, relation, g: Graph):
    '''
    schema:Book schema:datePublished schema:Date
    schema:Quotation schema:datePublished schema:Date
    schema:Collection schema:datePublished schema:Date
    schema:Person schema:birthDate schema:Date
    schema:Person schema:deathDate schema:Date

    subj: schema:Book OR schema:Quotation OR schema:Collection OR schema:Person
    point: schema:Date
    relation: PUBLISHED_IN OR BORN OR DIED
    '''
    pointString = convertDate(point)
    date = Literal(pointString, datatype=SCHEMA.Date)

    if g.value(subject=subj, predicate=RDF.type, object=None) == WORDNET.Example:
        subj  = g.value(subject=subj, predicate=DCTERMS.isPartOf, object=None)

    if g.value(subject=subj, predicate=RDF.type, object=None) in dateCreativeWork['domain']:
        if relation == 'PUBLISHED_IN': g.add((URIRef(str(subj)), SCHEMA.datePublished, date))
    elif g.value(subject=subj, predicate=RDF.type, object=None) in datePerson['domain']:
        if relation == 'BORN': g.add((URIRef(str(subj)), SCHEMA.birthDate, date)) #    UNAVAILABLE DATA
        elif relation == 'DIED': g.add((URIRef(str(subj)), SCHEMA.deathDate, date)) #    UNAVAILABLE DATA

SCHEMAIsPartOf = {'domain': subClassOfCreativeWork, 'range': subClassOfCreativeWork}

def addSCHEMAIsPartOf(subj, obj, g: Graph):
    '''
    schema:Quotation schema:isPartOf schema:Book
    schema:Book schema:isPartOf schema:Collection

    subj: schema:Book OR schema:Quotation
    obj: schema:Book OR schema:Collection
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) == WORDNET.Example:
        subj  = g.value(subject=subj, predicate=DCTERMS.isPartOf, object=None)
    if g.value(subject=subj, predicate=RDF.type, object=None) in SCHEMAIsPartOf['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in SCHEMAIsPartOf['range']:
        g.add((URIRef(str(subj)), SCHEMA.isPartOf, URIRef(str(obj))))
        g.add((URIRef(str(obj)), SCHEMA.hasPart, URIRef(str(subj))))

etymology = {'domain': subClassOfLexicalEntry, 'range': subClassOfLexicalEntry}

def addEtymology(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymology ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in etymology['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in etymology['range']:
        g.add((URIRef(str(subj)), LLKG.etymology, URIRef(str(obj))))

def addEtymologicalOrigin(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymologicalOriginOf ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in etymology['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in etymology['range']:
        g.add((URIRef(str(subj)), LLKG.etymologicalOriginOf, URIRef(str(obj))))

def addEtymologicallyRelated(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :etymologicallyRelated ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in etymology['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in etymology['range']:
        g.add((URIRef(str(subj)), LLKG.etymologicallyRelated, URIRef(str(obj))))

def addHasDerivedForm(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :hasDerivedForm ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in etymology['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in etymology['range']:
        g.add((URIRef(str(subj)), LLKG.hasDerivedForm, URIRef(str(obj))))

def addIsDerivedFrom(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :isDerivedFrom ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in etymology['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in etymology['range']:
        g.add((URIRef(str(obj)), LLKG.isDerivedFrom, URIRef(str(subj))))

def addOrthographyVariant(subj, obj, g: Graph):
    '''
    ontolex:LexicalEntry :orthographyVariant ontolex:LexicalEntry

    subj: ontolex:LexicalEntry
    obj: ontolex:LexicalEntry
    '''
    if g.value(subject=subj, predicate=RDF.type, object=None) in etymology['domain'] and g.value(subject=obj, predicate=RDF.type, object=None) in etymology['range']:
        g.add((URIRef(str(subj)), LLKG.orthographyVariant, URIRef(str(obj))))

