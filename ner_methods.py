import json

def getUniqueEntities(text, nlp):
    '''
    Returns a set of tuples (entity,entity_type).
    
    Keyword arguments:
    text -- the text to extract named entities from (type str)
    nlp -- StanfordCoreNLP object to connect to coreNLP server.
    '''
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