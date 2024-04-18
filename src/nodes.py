from rdflib import Namespace, Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
from urllib.parse import quote
import urllib.error
from nltk.corpus import wordnet as wn
import queries
import re
from namespaces import *
import logging
from SPARQLWrapper import SPARQLExceptions

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

lilaPosMapping = {'N' : LILA.noun, 'ADJ' : LILA.adjective, 'V' : LILA.verb}
lexinfoPosMapping = {'N' : LEXINFO.noun , 'ADJ' : LEXINFO.adjective, 'V' : LEXINFO.verb}

def updateEntry(entry, llkg, g: Graph):
    g.add((llkg, LIME.entry, entry))

def addResourceNode(resource: str, label: str, g: Graph):
    resource = URIRef(resource)
    g.add((resource, RDF.type, RDFS.Resource))
    g.add((resource, RDFS.label, Literal(label, lang='en')))

def addFormNode(writtenRep, pos, id, g: Graph):
    try:
        result = queries.queryRetry(query = queries.lemmaQuery, initNs = {'ontolex' : ONTOLEX, 'lila': LILA}, initBindings={'written': Literal(writtenRep), 'pos' : URIRef(lilaPosMapping[pos]) })
    except urllib.error.URLError or TimeoutError as e:
        print('{} occurred'.format(e))
    else:
        for r in result:
            lemma = r.lemma   
            g.add((lemma, RDF.type, ONTOLEX.Form))
            g.add((lemma, RDFS.label, Literal(writtenRep)))
            g.add((lemma, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))
            g.add((lemma, ONTOLEX.writtenRep, Literal(writtenRep, lang='la'))) 
            g.add((lemma, LEXINFO.partOfSpeech, URIRef(lexinfoPosMapping[pos])))

def addLexicalEntryNode(entry, id, language, iso, llkg, g: Graph):
    wordString = str(entry).lower()
    wordURI = URIRef(LEXVO+'{}/{}'.format(language, quote(wordString)))
    if not (wordURI, None, None) in g:
        updateEntry(wordURI, llkg, g)
        if bool(re.search(r'\s', wordString)):
            g.add((wordURI, RDF.type, ONTOLEX.MultiwordExpression))
        elif wordString.startswith('-') or wordString.endswith('-'):
            g.add((wordURI, RDF.type, ONTOLEX.Affix))
        else:
            g.add((wordURI, RDF.type, ONTOLEX.Word))
        g.add((wordURI, RDFS.label, Literal(wordString)))
        lang = g.value(subject=None, predicate=LLKG.iso639+iso, object=Literal(language, datatype=XSD.string))
        if lang != None:
            g.add((wordURI, DCTERMS.language, URIRef(str(lang))))
        g.add((wordURI, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))
    else:
        g.add((wordURI, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))

def addLexicalSenseNode(resource, sense, gloss, id, g: Graph):
    senseURI = None
    resourceNode = URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal(resource, lang='en'))))
    
    if resource == 'Lewis-Short Dictionary':
        senseURI = URIRef(LLKG+sense)
        if not (senseURI, None, None) in g:
            g.add((senseURI, RDF.type, ONTOLEX.LexicalSense))
            g.add((senseURI, RDFS.label, Literal(sense, datatype=XSD.string)))
            g.add((senseURI, DCTERMS.source, resourceNode))
            g.add((senseURI, DCTERMS.description, Literal(gloss, lang='en')))    

    elif resource == 'Universal WordNet':
        wn30sense = wn.synset(sense)
        wn30offset = str(wn30sense.offset())
        wn30pos = str(wn30sense.pos())
        wn30id = '{}-{}'.format(wn30offset.zfill(8),wn30pos)
        senseURI = URIRef(UWN+'{}{}'.format(wn30pos, wn30offset))
        if not (senseURI, None, None) in g:     
            g.add((senseURI, RDF.type, ONTOLEX.LexicalSense))
            g.add((senseURI, RDFS.label, Literal(sense, datatype=XSD.string)))
            g.add((senseURI, DCTERMS.source, resourceNode))
            g.add((senseURI, DCTERMS.description, Literal(gloss, lang='en')))
            g.add((senseURI, LLKG.wn30ID, Literal(wn30id, datatype=XSD.string)))

    g.add((senseURI, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))

def addLexicalConceptNode(concept, g: Graph): #    UNAVAILABLE DATA, TBD
    conceptURI = URIRef(concept)
    g.add((conceptURI, RDF.type, ONTOLEX.LexicalConcept))
    g.add((conceptURI, RDFS.label, Literal(concept, datatype=XSD.string)))

def addPersonNode(firstname, lastname, id, df, g: Graph):
    if lastname != None: fullname = '{} {}'.format(firstname, lastname)
    else: fullname = firstname + ' '

    if fullname[-1] == ' ': label = fullname[:-1]
    else: label = fullname

    if fullname in df['fullname'].values:
        authorEntity = df.loc[(df['fullname'] == fullname), 'id'].values[0]
        authorURI = URIRef(WIKIENTITY+authorEntity) 
        wikiEntity = []    
    else:
        try: 
            wikiEntity = queries.query(queries.authorQuery.format(label))
        except urllib.error.HTTPError or SPARQLExceptions.EndPointInternalError or urllib.error.URLError as e:
            logger.info('{}'.format(e))
        finally:  
            if len(wikiEntity) > 0:
                authorURI = URIRef(wikiEntity[0]['authorURI'])
            else:
                authorURI = URIRef(LLKG+quote(label))

    g.add((authorURI, RDF.type, SCHEMA.Person))
    g.add((authorURI, RDFS.label, Literal(label, datatype=XSD.string)))
    if len(firstname)>0:
        g.add((authorURI, SCHEMA.givenName, Literal(firstname, datatype=SCHEMA.Text)))
    if len(lastname)>0:
        g.add((authorURI, SCHEMA.familyName, Literal(lastname, datatype=SCHEMA.Text)))

    g.add((authorURI, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))

def addOccupationNode(occupation, id, dict, g: Graph):
    occupationURI = URIRef(WIKIENTITY+dict[occupation])
    g.add((occupationURI, RDF.type, SCHEMA.Occupation))
    g.add((occupationURI, RDFS.label, Literal(occupation, datatype=XSD.string)))
    g.add((occupationURI, SCHEMA.name, Literal(occupation, datatype=SCHEMA.Text)))
    g.add((occupationURI, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))

def addQuotationNode(quotation, language, id, g: Graph):
    text = URIRef(LLKG+'text_{}'.format(id))
    g.add((text, RDF.type, SCHEMA.Quotation))
    g.add((text, SCHEMA.text, Literal(quotation, datatype=SCHEMA.Text)))
    g.add((text, DCTERMS.language, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal(language, lang='en'), any=False))))) 
    g.add((text, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))
    example = URIRef(LLKG+'example_{}'.format(id))
    g.add((example, RDF.type, WORDNET.Example))
    g.add((example, DCTERMS.isPartOf, text))
    g.add((example, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))

def addDummyBookNode(title, id, g: Graph):
    document = URIRef(LLKG+quote(title))
    g.add((document, RDF.type, SCHEMA.Book))
    g.add((document, RDFS.label, Literal(title, datatype=XSD.string)))
    g.add((document, SCHEMA.name, Literal(title, datatype=SCHEMA.Text)))
    g.add((document, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))

def addBookNode(document, author, g: Graph):
    try:
        title = g.value(subject=document, predicate=RDFS.label, object=None)
        authorEntity = author.rsplit('/', 1)[1]
        documentEntity = queries.query(queries.documentQuery.format(authorEntity, title))
    except urllib.error.HTTPError or SPARQLExceptions.EndPointInternalError or urllib.error.URLError as e:
        logger.info('{}'.format(e))
    finally: 
        if len(documentEntity) > 0:
            documentURI = URIRef(documentEntity[0]['documentURI'])
            language = URIRef(str(g.value(subject=None, predicate=LLKG.iso6393, object=Literal(documentEntity[0]['languageISO'], datatype=XSD.string))))
            for s, p, o in g.triples((document, None, None)):
                g.remove((s, p, o))
                g.add((documentURI, p, o))
            g.add((documentURI, DCTERMS.language, language))

def addCollectionNode(title, id, g: Graph):
    corpusURI = URIRef(LLKG+title)
    g.add((corpusURI, RDF.type, SCHEMA.Collection))
    g.add((corpusURI, RDFS.label, Literal(title, datatype=XSD.string)))
    g.add((corpusURI, SCHEMA.name, Literal(title, datatype=SCHEMA.Text)))
    g.add((corpusURI, LLKG.llkgID, Literal(id, datatype=XSD.unsignedInt)))

def addLanguageNode(language, l: Graph, g: Graph):
    languageURI = URIRef(str(language))
    g.add((languageURI, RDF.type, DCTERMS.LinguisticSystem))
    g.add((languageURI, RDFS.label, Literal(l.value(subject=language, predicate=SKOS.prefLabel, object=None), lang='en')))
    iso6391 = l.value(subject=language, predicate=LVONT.iso639P1Code, object=None, any=False)
    if iso6391 != None:
        g.add((languageURI, LLKG.iso6391, Literal(iso6391, datatype=XSD.string)))
    iso6392 = l.value(subject=language, predicate=LVONT.iso6392TCode, object=None, any=False)
    if iso6392 != None:
        g.add((languageURI, LLKG.iso6392, Literal(iso6392, datatype=XSD.string)))
    iso6393 = l.value(subject=language, predicate=LVONT.iso639P3PCode, object=None, any=False)
    if iso6393 != None:
        g.add((languageURI, LLKG.iso6393, Literal(iso6393, datatype=XSD.string)))



