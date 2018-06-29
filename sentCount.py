from VUSentimentLexiconLight import LexiconSent

class sentCounter:
    '''Simple count using VUSentimentLexicon'''

    def __init__(self, ignoreIfNegated = True):
        '''
        Sentiment lexicon class
        
        keyword args:
        ignoreIfNegated -- Ignore words between negator and end of sentence (default = True)
        '''
        self.lex = LexiconSent().sentLex
        self.ignoreIfNegated = ignoreIfNegated
        self.negators = ['niet','geen','nooit']
    
    def count(self, text):
        '''
        Count sentiment words in a text input. 
        Expected POS tags are from tagset {'adj', 'noun', 'other', 'verb', 'punct'}

        keyword args:
        text -- List containing (lemma,pos) for an entire text
        '''
        res = {'positive':0,'negative':0,'total':0}
        ignore = False
        for lemma,pos in text:
            if pos != 'punct':
                res['total'] += 1
            if ignore:
                if pos == 'punct':
                    if lemma in ['!','?','.']:
                        ignore = False
                continue #No need to do anything else with an end of sentence either, so continue anyway
            
            if lemma in self.negators:
                ignore = True
                continue

            if (lemma,pos) in self.lex:
                res[self.lex[(lemma,pos)]] += 1
            
        return res
            
posMap = {
    'ADJ' : 'adj',
    'N' : 'noun',
    'WW' : 'verb',
    'LET' : 'punct',
    'LID' : 'other',
    'BW' : 'other',
    'SPEC' : 'other',
    'TSW' : 'other',
    'TW' : 'other',
    'VG' : 'other',
    'VNW' : 'other',
    'VZ' : 'other'
}
