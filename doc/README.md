# Linked Linguistic Knowledge Graph

![Linguistic Knowledge Graph](img/LKG.PNG "Linguistic Knowledge Graph")  
Linguistic Knowledge Graph

![Linked Linguistic Knowledge Graph](img/LLKG.svg "Linked Linguistic Knowledge Graph")  
Linked Linguistic Knowledge Graph

## Table of contents
- [Linguistic sub-graph](#linguistic-sub-graph)
- [Date sub-graph](#date-sub-graph)
- [Author sub-graph](#author-sub-graph)
- [Corpus sub-graph](#corpus-sub-graph)
- [Example sub-graph](#example-sub-graph)

### General purpose prefixes
**rdf** : <http://www.w3.org/1999/02/22-rdf-syntax-ns#>   
**rdfs** : <http://www.w3.org/2000/01/rdf-schema#>   
**owl** : <http://www.w3.org/2002/07/owl#>  
**dct** : <http://purl.org/dc/terms/>  
**xsd** : <http://www.w3.org/2001/XMLSchema#>  

## Linguistic sub-graph

### Prefixes
**ontolex** : <http://www.w3.org/ns/lemon/ontolex#>   
**lexinfo** : <http://www.lexinfo.net/ontology/2.0/lexinfo#>    
**vartrans** : <http://www.w3.org/ns/lemon/vartrans#>  
**loc** : <http://id.loc.gov/vocabulary/>

### Entities
| LKG | L-LKG |
|-----|---------|
|LexiconEntry, WordForm|[ontolex:LexicalEntry](https://www.w3.org/2016/05/ontolex/#lexical-entry-class) |
|Lemma|ontolex:LexicalEntry [ontolex:canonicalForm](https://www.w3.org/2016/05/ontolex/#canonical-form-object-property) [ontolex:Form](https://www.w3.org/2016/05/ontolex/#form-class)|
|LexiconConcept|[ontolex:LexicalSense](https://www.w3.org/2016/05/ontolex/#lexicalsense-class) |
|Concept|[ontolex:LexicalConcept](https://www.w3.org/2016/05/ontolex/#lexical-concept-class) |
|Stem|*deprecated*|
|Language|[dct:LinguisticSystem](http://purl.org/dc/terms/LinguisticSystem)|

| Etymological Wordnet | L-LKG |
|-----|---------|
|:word|ontolex:LexicalEntry|
|:language|dct:LinguisticsSystem|


### Properties

| LKG | L-LKG |
|-----|---------|
|**(Entity OR Relation) property: range**| **subject predicate object**  |
|(Lemma) posTag: string| ontolex:Form [lexinfo:partOfSpeech lexinfo:PartOfSpeech](https://www.w3.org/2016/05/ontolex/#morphosyntactic-description) | 
|(Lemma) mwe: boolean| [ontolex:MultiwordExpession](https://www.w3.org/2016/05/ontolex/#multiword-expression-class) rdfs:subClassOf ontolex:LexicalEntry|
|(Lemma) value: string| ontolex:LexicalEntry ontolex:canonicalForm ontolex:Form [ontolex:writtenRep](https://www.w3.org/2016/05/ontolex/#written-representation-datatype-property) rdf:langString|
|(LexiconConcept) resource: string|ontolex:LexicalSense [dct:source](    http://purl.org/dc/terms/source) rdfs:Resource|
|(Language) enName: string|dct:LinguisticSystem [dct:title](http://purl.org/dc/terms/title) rdfs:Literal|
|(Language) iso639-1: string|dct:LinguisticSystem [dct:identifier](    http://purl.org/dc/terms/identifier) [loc:iso639-1](http://id.loc.gov/vocabulary/iso639-1) |
|(Language) iso639-2: string|dct:LinguisticSystem [dct:identifier](    http://purl.org/dc/terms/identifier) [loc:iso639-2](http://id.loc.gov/vocabulary/iso639-2) |
|(LexiconEntry) value: string|ontolex:LexicalEntry [ontolex:lexicalForm](https://www.w3.org/2016/05/ontolex/#lexical-form-object-property) ontolex:Form ontolex:writtenRep rdf:langString |
|(LexiconConcept) alias: string|ontolex:LexicalSense dct:title rdfs:Literal|
|(LexiconConcept) gloss: string|ontolex:LexicalSense dct:description rdfs:Literal|


### Relations

#### <a id="lexical-relations"></a> Mapped relations

| LKG | L-LKG |
|-----|---------|
|LexiconEntry :HAS_LANGUAGE Language |ontolex:LexicalEntry [dct:language](http://purl.org/dc/terms/language) dct:LinguisticSystem |
|WordForm IS_A LeixconEntry|ontolex:LexicalEntry|
|Lemma IS_A LexiconEntry|ontolex:LexicalEntry [ontolex:canonicalForm](https://www.w3.org/2016/05/ontolex/#canonical-form-object-property) ontolex:Form|
|LexiconEntry :{LEX_RELATION} LexiconEntry | ontolex:LexicalEntry [vartrans:lexicalRel](https://www.w3.org/2016/05/ontolex/#lexicalrel-object-property) ontolex:LexicalEntry|
|LexiconConcept :{SEM_RELATION} LexiconConcept| ontolex:LexicalSense [vartrans:senseRel](https://www.w3.org/2016/05/ontolex/#senserel-object-property) ontolex:LexicalSense |
|LexiconEntry :HAS_CONCEPT LexiconConcept|ontolex:LexicalEntry [ontolex:sense](https://www.w3.org/2016/05/ontolex/#sense-object-property) ontolex:LexicalSense|
|LexiconConcept :REFER_TO Concept|ontolex:LexicalSense [ontolex:isLexicalizedSenseOf](https://www.w3.org/2016/05/ontolex/#lexicalized-sense-object-property) ontolex:LexicalConcept |
|LexiconConcept :HAS_DEFINITION Text <sup>1</sup>|ontolex:LexicalSense [dct:description](http://purl.org/dc/terms/description) rdfs:Literal|


> <sup>1</sup> we split the originally merged usage of entity `Text` for representing both a fragment from a text and the actual definition of the word sense.

| Etymological Wordnet | L-LKG |
|-----|---------|
|word-1 :etymology word-2 |ontolex:LexicalEntry :etymology ontolex:LexicalEntry | 
|word-1 :etymological_origin_of word-2|ontolex:LexicalEntry :etymologicalOriginOf ontolex:LexicalEntry |
|word-1 :etymologically_related word-2|ontolex:LexicalEntry :etymologicallyRelated ontolex:LexicalEntry| 
|word-1 :has_derived_form word-2 |ontolex:LexicalEntry :hasDerivedForm ontolex:LexicalEntry |
|word-1 :is_derived_from word-2 |ontolex:LexicalEntry :isDerivedFrom ontolex:LexicalEntry |
|word-1 :variant:orthography word-2 |ontolex:LexicalEntry :orthographyVariant ontolex:LexicalEntry|
|word-1 :language language-1 |  ontolex:LexicalEntry dct:language dct:LinguisticSystem | 


#### New relations

| L-LKG |
|---------|
|ontolex:LexicalEntry [ontolex:evokes](https://www.w3.org/2016/05/ontolex/#evokes-object-property) ontolex:LexicalConcept |
|ontolex:LexicalSense owl:sameAs <sup>2</sup> ontolex:LexicalSense|

> <sup>2</sup> in case of same senses from different resources.

---
---
## Date sub-graph

### Prefixes

**schema** : <https://schema.org/>  

### Entities

| LKG | L-LKG |
|-----|---------|
|TemporalSpecification, TimeInterval, TimePoint|[schema:Date](https://schema.org/Date)| 

### Properties

| LKG | L-LKG |
|-----|---------|
|**(Entity OR Relation) property: range**| **subject predicate object**  |
|(TemporalSpecification) name: string| *deprecated*|
|(TemporalSpecification) description: string| *deprecated*|
|(TimePoint) year: Integer|schema:Date|
|(TimePoint) month: Integer|schema:Date|
|(TimePoint) day: Integer|schema:Date|

### Relations

#### Mapped relations

| LKG | L-LKG |
|-----|---------|
|TimeInterval :startTime TimePoint|schema:Date|
|TimeInterval :endTime :TimePoint|schema:Date|

---
---
## Author sub-graph

### Prefixes

**schema** : <https://schema.org/>  

### <a id="person-entities"></a> Entities

| LKG | L-LKG |
|-----|---------|
|Person <sup>3</sup> |[schema:Person](https://schema.org/Person), [schema:Organization](https://schema.org/Organization) | 
|*missing* |[schema:Occupation](https://schema.org/Occupation) <sup>4</sup> | 

> <sup>3</sup> we split the originally merged usage of entity `Person` for representing both the author of texts and documents, and the author of curated corpora, which usually are the result of an organization project; indeed, `schema:Organization` includes among its specializations [`schema:Project`](https://schema.org/Project) and [`schema:ResearchOrganization`](https://schema.org/ResearchOrganization).  
> <sup>4</sup> Entity Occupation is not mentioned in LKG schema but actually occurrs in the dataset.

### Properties

| LKG | L-LKG |
|-----|---------|
|**(Entity OR Relation) property: range**| **subject predicate object**  |
|(Person) name: string |schema:Person [schema:givenName](https://schema.org/givenName) schema:Text |
|(Person) surname: string |schema:Person [schema:familyName](https://schema.org/familyName) schema:Text |
|(Occupation) value: string |schema:Occupation dct:title rdfs:Literal |

### Relations

#### Mapped relations

| LKG | L-LKG |
|-----|---------|
|Person :BORN TemporalSpecification |schema:Person [schema:birthDate](https://schema.org/birthDate) schema:Date | 
|Person :DIED TemporalSpecification |schema:Person [schema:deathDate](https://schema.org/deathDate) schema:Date | 

#### New relations

| L-LKG |
|---------|
|schema:Person [schema:hasOccupation](https://schema.org/hasOccupation) [schema:Occupation](https://schema.org/Occupation)|   
|schema:Organization dct:title rdfs:Literal|

---
---
## Corpus sub-graph

### Prefixes

**schema** : <https://schema.org/>  

### Entities

| LKG | L-LKG |
|-----|---------|
|Text|[schema:Quotation](https://schema.org/Quotation)| 
|Sentence|*deprecated*|
|Document|[schema:CreativeWork](https://schema.org/CreativeWork)|
|Corpus|[schema:Collection](https://schema.org/Collection)| 

### Properties

| LKG | L-LKG |
|-----|---------|
|**(Entity OR Relation) property: range**| **subject predicate object**  |
|(Text) value: string| schema:Quotation [schema:text](https://schema.org/text) [schema:Text](https://schema.org/Text) |
|(Document) title: string |schema:CreativeWorks dct:title rdfs:Literal | 
|(Corpus) title: string|schema:Collection dct:title rdfs:Literal|

### Relations

#### Mapped relations

| LKG | L-LKG |
|-----|---------|
|Text :BELONG_TO Document | schema:Quotation [schema:isPartOf](https://schema.org/isPartOf) schema:CreativeWork| 
|Document :BELONG_TO Corpus | schema:CreativeWork schema:isPartOf schema:Collection |
|Text :HAS_LANGUAGE Language | schema:Quotation dct:language dct:LinguisticSystem |  
|Document :HAS_LANGUAGE Language | schema:CreativeWork dct:language dct:LinguisticSystem |  
|Corpus :HAS_LANGUAGE Language | schema:Collection dct:language dct:LinguisticSystem | 
|Text :HAS_AUTHOR Person |schema:Quotation [schema:author](https://schema.org/author) schema:Person|
|Document :HAS_AUTHOR Person |schema:CreativeWork [schema:author](https://schema.org/author) schema:Person|  
|Corpus :HAS_AUTHOR Person |schema:Collection [schema:author](https://schema.org/author) schema:Organization [<sup>2</sup>](#person-entities)| 
|Text :PUBLISHED_IN TemporalSpecification |schema:Quotation [schema:datePublished](https://schema.org/datePublished) schema:Date |  
|Document :PUBLISHED_IN TemporalSpecification |schema:CreativeWork schema:datePublished schema:Date |  
|Corpus :PUBLISHED_IN TemporalSpecification |schema:Collection schema:datePublished schema:Date |  


---
---
## Example sub-graph

### Prefixes

**wn** : <https://globalwordnet.github.io/schemas/wn#>  

### Entities

| LKG | L-LKG |
|-----|---------|
|*missing*|[wn:Example](https://globalwordnet.github.io/schemas/wn#Example) <sup>5</sup>|

> <sup>5</sup> LKG schema does not specify Example as an entity, but expresses this concept with the relation [`:HAS_EXAMPLE`](occurrence-properties) between `LexiconConcept` and `Text`, with attributes `begin`, `end` and `grade`; similarly, LKG expresses the concept of a word occurring in a text with the relation [`:HAS_OCCURRENCE`](occurrence-properties) between `LexiconEntry` and `Text`. In our schema, we merge these relations in entity `wn:Example`

### <a id="occurrence-properties"></a> Properties

| LKG | L-LKG |
|-----|---------|
|(:HAS_EXAMPLE) begin: int|wn:Example :beginOffset xsd:unsignedInt|
|(:HAS_OCCURENCE) begin: int|wn:Example :beginOffset xsd:unsignedInt|
|(:HAS_EXAMPLE) end: int|wn:Example :endOffset xsd:unsignedInt|
|(:HAS_OCCURENCE) end: int|wn:Example :endOffset xsd:unsignedInt|
|(:HAS_EXAMPLE) grade: float|wn:Example :grade xsd:float | 

### Relations

#### Mapped relations

| LKG | L-LKG |
|-----|---------|
|LexiconEntry :HAS_OCCURENCE Text [<sup>1</sup>](#lexical-relations)|ontolex:LexicalEntry [dct:isPartOf](http://purl.org/dc/terms/isPartOf) wn:Example|
|LexiconConcept :HAS_EXAMPLE Text [<sup>1</sup>](#lexical-relations)|ontolex:LexicalSense [wn:example](https://globalwordnet.github.io/schemas/wn#example) wn:Example|

#### New relations

| L-LKG |
|---------|
|wn:Example dct:isPartOf schema:Quotation| 

 ---
 ---




