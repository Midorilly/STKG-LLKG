from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from rdflib import Graph
from namespaces import *
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
import rdflib.query
import urllib.error
import time
import logging
import socket

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

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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

documentQuery = '''SELECT ?documentURI ?languageISO
    WHERE {{
        BIND (wd:{} AS ?authorURI)
        ?documentURI wdt:P50 ?authorURI .
        ?authorURI wdt:P6886 ?language.
        ?language wdt:P220 ?languageISO .
        {{ ?documentURI <http://www.w3.org/2004/02/skos/core#altLabel> ?label ;
            wdt:P407 ?language }}
        UNION
        {{ ?documentURI <http://www.w3.org/2000/01/rdf-schema#label> ?label ;
            wdt:P407 ?language }} 
    FILTER (regex(str(?label), "{}", "i"))
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }} LIMIT 1
'''

authorQuery = '''SELECT ?authorURI 
    WHERE {{
        ?authorURI wdt:P31 wd:Q5 .
        {{ ?authorURI <http://www.w3.org/2004/02/skos/core#altLabel> ?label .}}
        UNION
        {{ ?authorURI <http://www.w3.org/2000/01/rdf-schema#label> ?label . }}
    FILTER (regex(str(?label), "{}", "i"))
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }} LIMIT 1
'''

MAXRETRY = 5
def queryRetry(query: str, initNs, initBindings) -> rdflib.query.Result:
    backoff = 1
    for i in range(MAXRETRY):
        try:
            result = q.query(query, initNs = initNs, initBindings = initBindings)
            result.bindings
            return result
        except urllib.error.URLError or TimeoutError as e:
            if i == MAXRETRY-1:
                raise e
            backoffS = 2 ** backoff
            backoff += 1
            logger.info('{} \nwaiting for {}s and retrying'.format(e, backoffS))
            time.sleep(backoffS)

def transform2dicts(results):
    new_results = []
    for result in results:
        new_result = {}
        for key in result:
            new_result[key] = result[key]['value']
        new_results.append(new_result)
    return new_results

def query(queryString):
    socket.getaddrinfo('localhost',8080)
    endpoint = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(queryString)
    sparql.setReturnFormat(JSON)
    results = []
    n = 2
    for i in range(MAXRETRY):
        try:
            results = sparql.queryAndConvert()['results']['bindings']
            results = transform2dicts(results)
            return results
        except urllib.error.HTTPError or SPARQLExceptions.EndPointInternalError or urllib.error.URLError as e:
            if i == MAXRETRY-1:
                raise e
            else:
                logger.info('{}, waiting 60s'.format(e))
                backoffS = n * 61
                n += 1
                time.sleep(backoffS)        

    
