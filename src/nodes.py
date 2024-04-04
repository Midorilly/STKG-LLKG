from rdflib import Namespace, Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
from urllib.parse import quote
import urllib.error
from nltk.corpus import wordnet as wn
import queries
from queries import q
import re
from namespaces import *

lilaPosMapping = {'N' : LILA.noun, 'ADJ' : LILA.adjective, 'V' : LILA.verb}
lexinfoPosMapping = {'N' : LEXINFO.noun , 'ADJ' : LEXINFO.adjective, 'V' : LEXINFO.verb}

def updateEntry(entry, llkg, g: Graph):
    g.add((llkg, LIME.entry, entry))

def addResourceNode(resource: str, label: str ,g: Graph):
    resource = URIRef(resource)
    g.add((resource, RDF.type, RDFS.Resource))
    g.add((resource, RDFS.label, Literal(label, lang='en')))

def addFormNode(writtenRep, pos, id, g: Graph):
    try:
        result = queries.queryRetry(query = queries.lemmaQuery, initNs = {'ontolex' : ONTOLEX, 'lila': LILA}, initBindings={'entry': Literal(writtenRep), 'pos' : URIRef(lilaPosMapping[pos]) })
    except urllib.error.URLError or TimeoutError as e:
        print('{} occurred'.format(e))
    else:
        for r in result:
            lemma = r.lemma   
            g.add((lemma, RDF.type, ONTOLEX.Form))
            g.add((lemma, RDFS.label, Literal(writtenRep)))
            g.add((lemma, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))
            g.add((lemma, ONTOLEX.writtenRep, Literal(writtenRep, lang='la'))) 
            g.add((lemma, LEXINFO.partOfSpeech, URIRef(lexinfoPosMapping[pos])))
            #g.add((lemma, DCTERMS.language, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal('Latin', lang='en'), any=False)))))

def addLexicalEntryNode(entry, id, language, iso, llkg, g: Graph):
    wordString = str(entry).lower()
    word = URIRef(LEXVO+language+'/'+quote(wordString))
    if not (word, None, None) in g:
        updateEntry(word, llkg, g)
        if bool(re.search(r'\s', wordString)):
            g.add((word, RDF.type, ONTOLEX.MultiwordExpression))
        elif wordString.startswith('-') or wordString.endswith('-'):
            g.add((word, RDF.type, ONTOLEX.Affix))
        else:
            g.add((word, RDF.type, ONTOLEX.Word))
        g.add((word, RDFS.label, Literal(wordString)))
        '''lang = g.value(subject=None, predicate=DUMMY.iso639+iso, object=Literal(language, datatype=XSD.string))
        if lang != None:
            g.add((word, DCTERMS.language, URIRef(str(lang))))'''
        g.add((word, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))
    else:
        g.add((word, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))

def addLexicalSenseNode(resource, sense, gloss, id, g: Graph):
    senseURI = None
    resourceNode = URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal(resource, lang='en'))))

    if resource == 'Lewis-Short Dictionary':
        senseURI = URIRef(DUMMY+sense)
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
        g.add((senseURI, RDF.type, ONTOLEX.LexicalSense))
        g.add((senseURI, RDFS.label, Literal(sense, datatype=XSD.string)))
        g.add((senseURI, DCTERMS.source, resourceNode))
        g.add((senseURI, DCTERMS.description, Literal(gloss, lang='en')))
        g.add((senseURI, DUMMY.wn30ID, Literal(wn30id, datatype=XSD.string)))

    g.add((senseURI, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))

def addLexicalConceptNode(concept, g: Graph): #    UNAVAILABLE DATA, TBD
    conceptURI = URIRef(concept)
    g.add((conceptURI, RDF.type, ONTOLEX.LexicalConcept))
    g.add((conceptURI, RDFS.label, Literal(concept, datatype=XSD.string)))

def addPersonNode(firstname, lastname, id, df, g: Graph):
    if not lastname:
        wikiEntity = df.loc[(df['name'] == firstname), 'id'].values             
    else:
        wikiEntity = df.loc[((df['name'] == firstname) & (df['lastname'] == lastname)), 'id'].values

    if wikiEntity.size > 0:
        author = URIRef(WIKIENTITY+wikiEntity[0])
        g.add((author, RDF.type, SCHEMA.Person))
        if len(firstname)>0:
            g.add((author, SCHEMA.givenName, Literal(firstname, datatype=SCHEMA.Text)))
        if len(lastname)>0:
            g.add((author, SCHEMA.familyName, Literal(lastname, datatype=SCHEMA.Text)))
        g.add((author, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))

def addOccupationNode(occupation, id, dict, g: Graph):
    occupationURI = URIRef(WIKIENTITY+dict[occupation])
    g.add((occupationURI, RDF.type, SCHEMA.Occupation))
    g.add((occupationURI, RDFS.label, Literal(occupation, datatype=XSD.string)))
    g.add((occupationURI, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))

def addQuotationNode(quotation, language, id, g: Graph):
    text = URIRef(DUMMY+'text_{}'.format(id))
    g.add((text, RDF.type, SCHEMA.Quotation))
    g.add((text, SCHEMA.text, Literal(quotation, datatype=SCHEMA.Text)))
    g.add((text, DCTERMS.language, URIRef(str(g.value(subject=None, predicate=RDFS.label, object=Literal(language, lang='en'), any=False))))) 
    g.add((text, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))
    example = URIRef(DUMMY+'example_{}'.format(id))
    g.add((example, RDF.type, WORDNET.Example))
    g.add((example, DCTERMS.isPartOf, text))
    g.add((example, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))

def addCreativeWorkNode(title, id, g: Graph):
    work = URIRef(DUMMY+quote(title))
    #results = queries.query(queries.documentQuery.format(title))
    #if len(results) > 0:
    #    work = results[0]['document']
    g.add((work, RDF.type, SCHEMA.CreativeWork))
    g.add((work, RDFS.label, work))
    g.add((work, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))

def addCollectionNode(title, id, g: Graph):
    corpus = Literal(title, datatype=XSD.string)
    g.add((corpus, RDF.type, SCHEMA.Collection))
    g.add((corpus, DUMMY.lkgID, Literal(id, datatype=XSD.unsignedInt)))
    #g.add((corpus, RDFS.seeAlso, ))

def addLanguageNode(language, l: Graph, g: Graph):
    languageURI = URIRef(str(language))
    g.add((languageURI, RDF.type, DCTERMS.LinguisticSystem))
    g.add((languageURI, RDFS.label, Literal(l.value(subject=language, predicate=SKOS.prefLabel, object=None), lang='en')))
    iso6391 = l.value(subject=language, predicate=LVONT.iso639P1Code, object=None, any=False)
    if iso6391 != None:
        g.add((languageURI, DUMMY.iso6391, Literal(iso6391, datatype=XSD.string)))
    iso6392 = l.value(subject=language, predicate=LVONT.iso6392TCode, object=None, any=False)
    if iso6392 != None:
        g.add((languageURI, DUMMY.iso6392, Literal(iso6392, datatype=XSD.string)))
    iso6393 = l.value(subject=language, predicate=LVONT.iso639P3PCode, object=None, any=False)
    if iso6393 != None:
        g.add((languageURI, DUMMY.iso6393, Literal(iso6393, datatype=XSD.string)))

'''def addEtymLexicalEntryNode(word, language, iso, id, llkg, g: Graph):
    wordString = str(word)
    word = URIRef(LEXVO+language+'/'+quote(wordString))
    if not (word, None, None) in g:
        updateEntry(word, llkg, g)     
        if bool(re.search(r'\s', wordString)):
            g.add((word, RDF.type, ONTOLEX.MultiwordExpression))
        elif wordString.startswith('-') or wordString.endswith('-'):
            g.add((word, RDF.type, ONTOLEX.Affix))
        else:
            g.add((word, RDF.type, ONTOLEX.Word))
        g.add((word, RDFS.label, Literal(wordString, datatype=XSD.string)))
        g.add((word, DUMMY.etymwnID, Literal(id, datatype=XSD.string)))
        g.add((word, DCTERMS.language, URIRef(str(g.value(subject=None, predicate=DUMMY.iso639+iso, object=Literal(language, datatype=XSD.string))))))
    else:
        g.add((word, DCTERMS.identifier, Literal(id, datatype=XSD.string)))

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
        g.add((word, DUMMY.etymwnID, Literal(line[0], datatype=XSD.string)))
        g.add((word, DCTERMS.language, g.value(subject=None, predicate=DUMMY.iso6393, object=Literal(line[2], datatype=XSD.string))))
    else:
        g.add((word, DCTERMS.identifier, Literal(line[0], datatype=XSD.string)))'''

