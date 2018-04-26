import json
from stanfordcorenlp import StanfordCoreNLP

def getUniqueEntities(text, nlp):
    '''
    Returns a set of tuples (entity,entity_type).
    
    Keyword arguments:
    text -- the text to extract named entities from (type str)
    nlp -- StanfordCoreNLP or spaCy object
    '''
    if isinstance(nlp,StanfordCoreNLP):
        return getUniqueEntitiesCoreNLP(text,nlp)
    else:
        return getUniqueEntitiesSpaCy(text,nlp)
    

def getUniqueEntitiesCoreNLP(text,nlp):
    namedEntities = set()
    
    props = {'annotators': 'ner','pipelineLanguage':'en'}
    
    res = json.loads(nlp.annotate(text, properties = props))
    
    for sentence in res['sentences']:
        entity = ''
        entity_type = 'O'
        for tok in sentence['tokens']:
            if entity == '' and tok['ner'] != 'O': #There is no recorded entity yet and the current token is part of an entity
                entity = tok['originalText']
                entity_type = tok['ner']
            elif entity != '' and tok['ner'] == entity_type: #There already is an entity and the current token belongs to the
                #same category (notable exceptions are unlikely in the categories PERSON and ORGANIZATION)
                entity += ' ' + tok['originalText']
            elif entity != '' and tok['ner'] != entity_type:
                namedEntities.add((entity,entity_type))
                if tok['ner'] != 'O':
                    entity = tok['originalText']
                    entity_type = tok['ner']
                else:
                    entity = ''
                    entity_type = 'O'
    
    return namedEntities

def getUniqueEntitiesSpaCy(text,nlp):
    namedEntities = set()

    for entity in nlp(text).ents:
        namedEntities.add((entity.text,entity.label_))
    
    return namedEntities