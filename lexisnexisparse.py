import re
import os.path
import codecs

"""
The LexisParser class is a class that can read and parse LexisNexis TXT files from filenames. Initialise the to
load the regex patterns and then use the parse_file(fname) method to parse a file. Returns a list of dicts with
all variables contained in the text file.

Example use:
    lp = LexisParser()
    corpus = lp.parse_file("lexisnexis.txt")
"""

class LexisParser:
    
    def __init__(self):
        self.patterns = {
            "start_article" : re.compile("\d+ of \d+ DOCUMENTS$"),
            "start_text" : re.compile("^LENGTH: \d+ words$"),
            "end_article" : re.compile("^LANGUAGE:.*$"), #Language has multiple formats, so keep it open
            "date" : re.compile("[a-zA-Z]+ \d{1,2},* \d{4}|\d{1,2} [a-zA-Z]+,* \d{4}|^\s+[a-zA-Z]* \d{4}$"),
            "is_show" : re.compile("^\s+SHOW: "),
            "begin_metadata" : re.compile("^LENGTH: |^SECTION: |^BYLINE: |^DATELINE: |^HIGHLIGHT: "),
            "end_metadata" : re.compile("^LOAD-DATE: |^LANGUAGE: |^PUBLICATION-TYPE: |DISTRIBUTION: |JOURNAL-CODE: ")
        }
    
    def parse_file(self, fname: str):
        assert os.path.isfile(fname)

        file_list = [] #Reduce the file to a list of lines
        with codecs.open("lexisnexis_en.txt","r","utf8") as f:
            for line in f:
                line = line.replace("\r\n","")
                file_list.append(line)
        
        output = []
        for article in self.article_generator(file_list):
            output.append(self.parse_art(article))
        
        return output

    def article_generator(self, file_list):
        '''
        Generator function that takes a list of lines from a LexisNexis txt file and makes
        the relevant cuts to yield those parts that represent one article. This allows
        easy iteration over the relevant parts of the semi-structured file.
        ''' 
        article = []
        carry_line = False

        for line in file_list:

            if carry_line:
                article.append(line)

            if re.search(self.patterns['start_article'],line) is not None: 
                #If we reach the start of an article, begin carrying the lines to the article for output
                carry_line = True
            elif re.search(self.patterns['end_article'],line) is not None:
                #If we reach the end of an article, stop carrying lines, then yield the article and reset
                carry_line = False
                yield article[1:] #Remove the first whitespace, which is always there
                article = []
    
    def parse_art(self, article):
        position = 0
        res = {}
        
        #First line is always medium. Extract and remove
        res['MEDIUM'] = article[position].lstrip()
        position += 1
        while article[position] != "":
            res['MEDIUM'] += " " + article[position].lstrip()
            position += 1
        
        #Empty line separating medium and date, detected by above while loop
        position += 1
        
        #Date extraction. There could be an extra note in between, such as the Xinhua
        #News Agency's copyright note. Therefore the while loop is included to skip such
        #extra lines. Date extraction picks up the following formats:
        #1. M dd(,) yyyy - e.g. July 17, 2004
        #2. dd M(,) yyyy - e.g. 17 juli 2004 (common Dutch notation)
        #3. (M) yyyy - e.g. 2005. Restricted to the entire line being (month) year plus whitespace
        
        while True:
            if re.search(self.patterns['date'],article[position]) is not None:
                res['DATE'] = re.search(self.patterns['date'],article[position])[0].lstrip().lower()
                position += 2 #Includes skip for empty line after date
                break
            else:
                position += 1
        
        #Headline extraction. Note that there is not necessarily a headline. It usually is at
        #the next position, though. Exceptions:
        #1. Article is featured in a show. In that case, there is a SHOW metadata field first.
        #2. There is no headline. In that case, the next field is a metadata field from the
        #   following list: ["BYLINE","SECTION","LENGTH","DATELINE","HIGHLIGHT"]
        #So check for both.
        
        if re.search(self.patterns["is_show"],article[position]) is not None:
            res["SHOW"] = article[position].lstrip()[6:] #Strip whitespace and then remove first 6 characters(SHOW: )
            position += 2 #Skip empty line to next field
        
        if re.search(self.patterns["begin_metadata"],article[position]) is None:
            #The next line is NOT metadata --> there is a headline
            res["HEADLINE"] = article[position]
            position += 1
        
            #Check if headline is split over multiple lines
            while article[position] != "":
                res["HEADLINE"] += " " + article[position]
                position += 1
            
            position += 1 #Here, the headline is fully collected, next is a whitespace.
            #Has to be inside the if-block, because otherwise we would skip metadata.
        else:
            res["HEADLINE"] = ""
        
        #Metadata extraction. Possible fields: ["BYLINE","SECTION","LENGTH","DATELINE","HIGHLIGHT"]
        #Extract them one by one and add its contents to the dictionary.
        while re.search(self.patterns["begin_metadata"],article[position]) is not None:
            var = re.search(self.patterns["begin_metadata"],article[position])[0]
            res[var[:-2]] = article[position][len(var):]
            position += 2        
        
        #Text extraction. Text ends with LOAD-DATE field
        res["TEXT"] = ""
        first_line = True
        while re.search(self.patterns["end_metadata"],article[position]) is None:
            
            if first_line & (article[position] != ""):
                res["TEXT"] += article[position]
                first_line = False
            elif article[position] != "":
                res["TEXT"] += " " + article[position]
                
            position += 1
        
        #End of text. From here it is metadata fields until the end.
        while position < len(article):
            var = re.search(self.patterns["end_metadata"],article[position])[0]
            res[var[:-2]] = article[position][len(var):]
            position += 2
        
        return res