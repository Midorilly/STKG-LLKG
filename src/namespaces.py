from rdflib import Namespace, Graph
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS

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
BIGDATA = Namespace("http://www.bigdata.com/rdf#")
LLKG = Namespace("http://llkg.com/")
CC = Namespace("https://creativecommons.org/ns#")

llkgSchema = Graph()

llkgSchema.bind("rdf", RDF)
llkgSchema.bind("rdfs", RDFS)
llkgSchema.bind("xsd", XSD)
llkgSchema.bind("dct", DCTERMS)
llkgSchema.bind("owl", OWL)

llkgSchema.bind("schema", SCHEMA)
llkgSchema.bind("ontolex", ONTOLEX)
llkgSchema.bind("vartrans", VARTRANS)
llkgSchema.bind("lexinfo", LEXINFO)
llkgSchema.bind("lime", LIME)
llkgSchema.bind("wn", WORDNET)

schemaFile = '../STKG-LLKG/schema/llkg-schema.ttl'

llkgSchema.parse(schemaFile, format='ttl')
