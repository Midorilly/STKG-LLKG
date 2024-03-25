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