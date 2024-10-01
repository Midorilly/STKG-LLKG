import re
import jsonlines
import os
from rdflib import RDF, RDFS, Literal, XSD, Graph, DCTERMS, Namespace
#from namespaces import LLKG, ONTOLEX
import logging
import pandas as pd

ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
LLKG = Namespace("http://llkg.com/")

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def countExamples(g: Graph):
    total = 0
    lemmas = g.subjects(predicate=RDF.type, object=ONTOLEX.Form)
    for l in lemmas:
        count = 0
        entries = g.subjects(predicate=ONTOLEX.canonicalForm, object=l)
        for e in entries:
            examples = g.objects(subject=e, predicate=DCTERMS.isPartOf)
            for ex in examples:
                count += 1
        logger.info('{} {} has {} examples'.format(l, g.value(subject=l, predicate=ONTOLEX.writtenRep), count))
        total += count
        
    logger.info(total)

def missingExamplesFile(datasetPath, gr: Graph):

    x = []
    with jsonlines.open(datasetPath, 'r') as lkg:
        ids = [line['object'] for line in lkg if line['jtype'] == 'relationship' and line['name'] == 'HAS_OCCURRENCE']
        with jsonlines.open(datasetPath, 'r') as lkg:
            occurrences = [line['properties']['value'] for line in lkg if line['jtype'] == 'node' and line['identity'] in ids]
            for o in occurrences:
                y = str(o).split()
                x.append(' '.join(y[:5]))

    paths = ['C:/Users/angel/Documents/ComputerScience/1st/II/ML/project/ML/data/fragments/AD', 'C:/Users/angel/Documents/ComputerScience/1st/II/ML/project/ML/data/fragments/BC']
    id = 5300
    for p in paths:
        period = p.rsplit('/', 1)[1]
        for file in os.listdir(p):
            sentsFile = os.fsdecode(file)
            f = open(os.path.join(p, sentsFile))
            sentences = f.readlines()

            with open(os.path.join('../data/lkg/missing', 'data_'+sentsFile), mode='w', encoding='utf-8') as output:
                count = 0
                for s in sentences:
                    target = s.split('\t')
                    t = re.sub(' ', '', target[1])
                    index = gr.value(subject=gr.value(predicate=RDFS.label, object=Literal(t, datatype=XSD.string)), predicate=LLKG.llkgID)
                    sx = s.split()
                    ss = ' '.join(sx[:5])
                    if ss not in x: 
                        output.write('{{"jtype": "node", "identity": {}, "label": "Text", "kb": "", "properties": {{"value": "{}"}}}}\n'.format(id, s))
                        if index != None:
                            output.write('{{"jtype": "relationship", "subject": {}, "object": {}, "name": "HAS_OCCURRENCE", "kb": "", "properties": {{}}}}\n'.format(str(index), id))
                        if period == 'AD':
                            output.write('{{"jtype": "relationship", "subject": {}, "object": 61, "name": "PUBLISHED_IN", "kb": "", "properties": {{}}}}\n'.format(id))
                        elif period == 'BC': 
                            output.write('{{"jtype": "relationship", "subject": {}, "object": 59, "name": "PUBLISHED_IN", "kb": "", "properties": {{}}}}\n'.format(id)) 
                        id += 1
                        count += 1
            logger.info('[MISSING SENTENCES] {} {}'.format(sentsFile.split('_')[0], count))
            output.close()  

def missingExamplesCSV(datasetPath, gr: Graph):

    x = []
    with jsonlines.open(datasetPath, 'r') as lkg:
        ids = [line['object'] for line in lkg if line['jtype'] == 'relationship' and line['name'] == 'HAS_OCCURRENCE']
        with jsonlines.open(datasetPath, 'r') as lkg:
            occurrences = [line['properties']['value'] for line in lkg if line['jtype'] == 'node' and line['identity'] in ids]
            for o in occurrences:
                y = str(o).split()
                x.append(' '.join(y[:5]))

    groundtruth = pd.read_csv('../STKG-LLKG/data/lkg/missing-sentences/groundtruth-complete.csv')
    targetWords = groundtruth['word'].values.tolist()
    paths = [('C:/Users/angel/Documents/ComputerScience/1st/II/ML/project/ML/data/fragments/AD', 'ad'), ('C:/Users/angel/Documents/ComputerScience/1st/II/ML/project/ML/data/fragments/BC', 'bc')]
    #id = 5300
    print(targetWords)
    total = 0
    for w in targetWords:
        print(w)
        count = 0
        excelPath = 'C:/Users/angel/Documents/ComputerScience/1st/II/AI/AI-latin-graph/annotated_LatinISE'
        for file in os.listdir(excelPath):
            fileName = os.fsdecode(file)
            if w in fileName:
                excelFile = open(os.path.join(excelPath, fileName))
            break

        excelFrame = pd.read_excel('C:\\Users\\angel\\Documents\\ComputerScience\\1st\\II\\AI\\AI-latin-graph\\annotated_LatinISE\\annotation_task_acerbus_Annie_metadata.xlsx')

        for (p, period) in paths:
            f = open(os.path.join(p, w+'_'+period+'.txt'))
            sentences = f.readlines()
            missingList = []
            for s in sentences:
                target = s.split('\t')
                t = re.sub(' ', '', target[1])
                #index = gr.value(subject=gr.value(predicate=RDFS.label, object=Literal(t, datatype=XSD.string)), predicate=LLKG.llkgID)
                sx = s.split()
                ss = ' '.join(sx[:5])
                if ss not in x: 
                    i = excelFrame[excelFrame['Left context'] in s]['Metadata']
                    #metadata = excelFrame['Metadata'].loc[[i]]
                    missingList.append([i, re.sub('\n', '', s)])
                    count += 1
            df = pd.DataFrame(data=missingList, columns=['metadata', 'sentence'])
            df.to_csv(os.path.join('../STKG-LLKG/data/lkg/missing-sentences', w+'_'+period+'.csv'), index=False, mode='w', encoding='utf-8', quotechar='"', lineterminator='\n')
        logger.info('[MISSING SENTENCES] {} {}'.format(w, count))
        total += count
    logger.info('[TOTAL MISSING SENTENCES] {} '.format(total))




    ''' for (p, period) in paths:
            for file in os.listdir(p):
                fileName = os.fsdecode(file)
                if w in fileName:
                    f = open(os.path.join(p, fileName))
                    sentences = f.readlines()
                    missingList = []
                    for s in sentences:
                        target = s.split('\t')
                        t = re.sub(' ', '', target[1])
                        #index = gr.value(subject=gr.value(predicate=RDFS.label, object=Literal(t, datatype=XSD.string)), predicate=LLKG.llkgID)
                        sx = s.split()
                        ss = ' '.join(sx[:5])
                        if ss not in x: 
                            missingList.append(s)
                            count += 1
                    df = pd.DataFrame(data=missingList, columns=['sentence'])
                    df.to_csv(os.path.join('../STKG-LLKG/data/lkg/missing-sentences', w+'_'+period+'.csv'), index=False)
        total += count
        logger.info('[MISSING SENTENCES] {} {}'.format(w, count))
    logger.info('[TOTAL MISSING SENTENCES] {} '.format(total))'''






    '''for p in paths:
        period = p.rsplit('/', 1)[1]
        for file in os.listdir(p):
            sentsFile = os.fsdecode(file)
            f = open(os.path.join(p, sentsFile))
            sentences = f.readlines()

            #with open(os.path.join('../data/lkg/missing', 'data_'+sentsFile), mode='w', encoding='utf-8') as output:
            count = 0
            missingList = []
            for s in sentences:
                target = s.split('\t')
                t = re.sub(' ', '', target[1])
                index = gr.value(subject=gr.value(predicate=RDFS.label, object=Literal(t, datatype=XSD.string)), predicate=LLKG.llkgID)
                sx = s.split()
                ss = ' '.join(sx[:5])
                if ss not in x: 
                    missingList.append(s)
                    count += 1
                        
            df = pd.DataFrame(data=missingList, columns=['sentence'], index=False)
            df.to_csv(os.path.join('../STKG-LLKG/data/lkg/missing-sentences', sentsFile.split('.')[0]+'.csv'))
            logger.info('[MISSING SENTENCES] {} {}'.format(sentsFile.split('_')[0], count))
            #output.close()  '''

if __name__ == '__main__':
    g = Graph(store='Oxigraph')
    g.parse('c:/Users/angel/Documents/ComputerScience/2nd/KG/STKG-LLKG/data/llkg/llkg-missing-sentences.ttl', format='ttl')
    missingExamplesCSV('C:\\Users\\angel\\Documents\\ComputerScience\\2nd\\KG\\STKG-LLKG\\data\\lkg\\original-dataset.jsonl', g)
