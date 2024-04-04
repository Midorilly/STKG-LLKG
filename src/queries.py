from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from namespaces import *
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
import rdflib.query
import urllib.error
import time

q = Graph()
q.bind("rdf", RDF)
q.bind("rdfs", RDFS)
q.bind("xsd", XSD)
q.bind("dct", DCTERMS)
q.bind("owl", OWL)

q.bind("schema", SCHEMA)
q.bind("ontolex", ONTOLEX)
q.bind("vartrans", VARTRANS)
q.bind("lexinfo", LEXINFO)
q.bind("lime", LIME)
q.bind("wn", WORDNET)
q.bind("lexvo", LEXVO)
q.bind("lvont", LVONT)
q.bind("uwn", UWN)
q.bind("lila", LILA)
q.bind("skos", SKOS)

q.bind("wd", WIKIENTITY)
q.bind("wdt", WIKIPROP)
q.bind("wikibase", WIKIBASE)
q.bind("bd", BIGDATA)

q.bind("dummy", DUMMY)

lemmaQuery = (""" SELECT ?lemma 
    WHERE {
        SERVICE <https://lila-erc.eu/sparql/lila_knowledge_base/sparql> {
            ?lemma ontolex:writtenRep ?entry ;
            lila:hasPOS ?pos .             
        }
    }""")

senseQuery = '''SELECT ?senseURI
    WHERE {{ SERVICE <https://lila-erc.eu/sparql/lila_knowledge_base/sparql> {{ 
            <http://lila-erc.eu/data/lexicalResources/LatinWordNet/Lexicon> lime:entry ?lexentry.
            ?lexentry ontolex:canonicalForm ?lemmaURI ;
            ontolex:sense ?senseURI .
            FILTER(regex(?senseURI,"{}")).	         
        }}
    }}'''

documentQuery = '''SELECT ?document
    WHERE {{
        VALUES ?title {{ "{}"@la}}
        ?document wdt:P31 wd:Q7725634 ;
           wdt:P1476 ?title.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}   
    }} ''' 

def transform2dicts(results):
    new_results = []
    for result in results:
        new_result = {}
        for key in result:
            new_result[key] = result[key]['value']
        new_results.append(new_result)
    return new_results

def query(queryString):
    endpoint = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(queryString)
    sparql.setReturnFormat(JSON)

    results = sparql.queryAndConvert()['results']['bindings']
    results = transform2dicts(results)

MAXRETRY = 3
def queryRetry(query: str, initNs, initBindings) -> rdflib.query.Result:
    backoff = 0
    for i in range(MAXRETRY):
        try:
            #print('Query tentative {}...'.format(i))
            result = q.query(query, initNs = initNs, initBindings = initBindings)
            result.bindings
            return result
        except urllib.error.URLError or TimeoutError as e:
            if i == MAXRETRY-1:
                raise e
            backoffS = 1.2 ** backoff
            print('Network error {} during query, waiting for {}s and retrying'.format(e, backoffS))
            time.sleep(5)
