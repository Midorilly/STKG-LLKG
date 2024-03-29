from SPARQLWrapper import SPARQLWrapper, JSON

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