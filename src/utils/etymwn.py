import logging
import pandas as pd
import csv

logger = logging.getLogger(__name__)

def load_dataset(path):
    dataset = pd.read_csv(path, sep='\t', header=None, names=['w1', 'rel', 'w2'])
    entries = pd.concat([dataset['w1'], dataset['w2']], ignore_index=True, axis=0)
    entries = entries.drop_duplicates()

    return dataset, entries

    #load_words(entries)
    #wordsDict = load_dictionary('../data/etymwn/words.csv')
    #load_relations(dataset, wordsDict)

def load_words(entries, wordsPath):
    logger.info('Loading words...')

    words = ['id', 'word', 'language']
    with open(wordsPath, mode='w', newline='', encoding='utf-8') as file:     
        writer = csv.writer(file)
        writer.writerow(words)

        for index, value in entries.items():
            w = str(value).split(': ')
            writer.writerow(['w_{}'.format(index), w[1], w[0]])
        file.close()

    logger.info('Words loaded')

def loadDictionary(wordsPath):
    logger.info('Loading dictionary...')
    words = open(wordsPath, encoding='utf-8', mode='r')
    reader = csv.reader(words)
    wordsDict = {}
    for row in reader:
        wordsDict.update({(row[1], row[2]): row[0]})
    words.close()
    logger.info('Dictionary loaded!')

    return wordsDict

def load_relations(dataset, wordsDict, relationsPath):

    relations = ['subj', 'relation', 'obj']
    with open(relationsPath, mode='w', newline='', encoding='utf-8') as file:
        logger.info('Loading relations...')
        writer = csv.writer(file)
        writer.writerow(relations)

        for index, value in dataset.iterrows():
            subj = str(value['w1']).split(': ')
            obj = str(value['w2']).split(': ')
            rel = str(value['rel']).removeprefix('rel:')

            writer.writerow([wordsDict[subj[1], subj[0]], rel, wordsDict[obj[1], obj[0]]])

        file.close()
    
    logger.info('Relations loaded!')