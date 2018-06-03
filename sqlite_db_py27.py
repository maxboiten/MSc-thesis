import sqlite3
import os.path
import re

class noSuchTable(Exception):
    def __init__(self,table):
        super(noSuchTable,self).__init__('Table \''+table+'\' does not exist')

class duplicateColumn(Exception):
    def __init__(self,column,table):
        super(duplicateColumn,self).__init__('Column \''+column+'\' already exists in table \''+table+'\'')

class noSuchColumn(Exception):
    def __init__(self,column,table):
        super(noSuchColumn,self).__init__('Column \''+column+'\' does not exist in table \''+table+'\'')

class corpusDB:

    def __init__(self, filename, columnsDict = dict()):
        '''Set up a connection to a corpusDB, either pre-existing of new.

        Keyword arguments:
        filename -- str, path to location where db is or should be setup
        columnsDict -- dict, stores the names of columns that should be created plus their types
            in an iterable of tuples. Possible elements: documents, tokens, entities. The minimum
            they contain is an id (INTEGER) for the documents. The tokens and entities contain a 
            column referring to their document, an id to make them unique and a text field. Any 
            other columns are to be specified here. Example: {'tokens':[('pos','TEXT')]}
        '''
        preExists = os.path.isfile(filename)

        self.file = filename
        self.connect() #This creates a file if it does not yet exist

        if preExists:
            cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.tables = [name for (name,) in cursor.fetchall()]
            if not all(tab in self.tables for tab in ['documents','tokens','entities']):
                raise Exception('Wrong database setup')

            self.columns = dict()
            for table in ['documents','tokens','entities']:
                cursor = self.conn.execute('PRAGMA table_info('+table+');')
                self.columns[table] = [row[1] for row in cursor]
        else: 
            if 'documents' in columnsDict:
                documentsCommand = ' '.join(('CREATE TABLE documents (id INTEGER PRIMARY KEY ASC,',
                    ','.join([n+' '+t for (n,t) in columnsDict['documents']]),
                    ')'))
            else:
                documentsCommand = 'CREATE TABLE documents (id INTEGER PRIMARY KEY ASC)'                
            self.conn.execute(documentsCommand)
            if 'tokens' in columnsDict:
                tokensCommand = ' '.join(('CREATE TABLE tokens (id INTEGER PRIMARY KEY ASC, token TEXT,',
                    'docid INTEGER, position INTEGER,',
                    ','.join([n+' '+t for (n,t) in columnsDict['tokens']]),
                    ', FOREIGN KEY (docid) REFERENCES documents(id))'))
            else:
                tokensCommand = 'CREATE TABLE tokens (id INTEGER PRIMARY KEY ASC, token TEXT)'
            self.conn.execute(tokensCommand)
            if 'entities' in columnsDict:
                entitiesCommand = ' '.join(('CREATE TABLE entities (id INTEGER PRIMARY KEY ASC, entity TEXT,',
                    'docid INTEGER, ',
                    ','.join([n+' '+t for (n,t) in columnsDict['entities']]),
                    ', FOREIGN KEY (docid) REFERENCES documents(id))'))
            else:
                entitiesCommand = 'CREATE TABLE entities (id INTEGER PRIMARY KEY ASC, entity TEXT)'
            self.conn.execute(entitiesCommand)
            self.commit()
            self.tables = ['documents','tokens','entities']

            self.columns = dict()
            self.columns['documents'] = ['id']
            if 'documents' in columnsDict:
                self.columns['documents'] += [name for (name,x) in columnsDict['documents']]
            self.columns['tokens'] = ['id','token','position','docid']
            if 'tokens' in columnsDict:
                self.columns['tokens'] += [name for (name,x) in columnsDict['tokens']]
            self.columns['entities'] = ['id','entity','docid']
            if 'entities' in columnsDict:
                self.columns['entities'] += [name for (name,x) in columnsDict['entities']]
    
    def addColumns(self, table, namePairs):
        '''Add multiple columns from the vector namePairs to a table.

        Keyword arguments:
        table -- str, table name (see corpusDB.tables for options)
        namePairs -- iterable of tuples (name, SQL_type). Example ('pos','TEXT')
        '''
        for (name,SQL_type) in namePairs:
            self.addColumn(table, (name,SQL_type))
    
    def addColumn(self, table, namePair):
        '''Add one column to a table.

        Keyword arguments:
        table -- str, table name (see corpusDB.tables for options)
        namePair -- tuple (name, SQL_type). Example ('pos','TEXT')
        '''
        if table not in self.tables:
            raise noSuchTable('Table \''+table+'\' does not exist')
        if namePair[0] in self.columns[table]:
            raise duplicateColumn(namePair[0],table)
        self.conn.execute('ALTER TABLE '+table+' ADD COLUMN '+' '.join(namePair))
        self.commit()
        self.columns[table].append(namePair[0])

    def close(self):
        '''Close the connection to the database object'''
        self.conn.close()
    
    def connect(self):
        '''Open a connection to the database object'''
        self.conn = sqlite3.connect(self.file)
    
    def insertRow(self, table, rowDict, commit = True):
        '''Add a row to a table
        
        Keyword arguments:
        table -- str, name of the table to add data to
        rowDict -- dict, set of pairs to add. Example: {'token':'"boeken"','lemma':'"boek"','pos':'"N"'}
        '''
        if table not in self.tables:
            raise noSuchTable(table)
        for column in rowDict.keys():
            if column not in self.columns[table]:
                raise noSuchColumn(column,table)
        
        insertStatement = ' '.join(('INSERT INTO', table, '(',
            ', '.join([key for key in rowDict.keys()]),')',
            'VALUES (',
            ', '.join([value for key,value in rowDict.items()]),')'
        ))
        
        cursor = self.conn.cursor()
        cursor.execute(insertStatement)
        rowid = cursor.lastrowid
        cursor.close()
        if commit:
            self.commit()
        return rowid
    
    def commit(self):
        '''Commit pending changes. Can be postponed if multiple changes are made.'''
        self.conn.commit()
    
    def getDocText(self,docid):
        '''Retrieve a document by its docid'''
    
    def getEntities(self, returnColumns = None, searchTerms = None):
        '''Get entities from the corpus. By default all, but can be restricted.
        
        Keyword arguments:
        returnColumns -- list of all columns to be returned (default= None, return all)
        otherSearchTerms -- dict, specification of search terms for entity properties (default = None)
            example: {'docid' : 15}

        Returns cursor with all rows that fit the specifications
        '''
        statement = 'SELECT '

        if returnColumns:
            statement += ', '.join(returnColumns)
            for column in returnColumns:
                if column not in self.columns['entities']:
                    raise noSuchColumn(column,'entities')
        else:
            statement += '*'
        
        statement += ' FROM entities'
        if searchTerms:
            statement += ' WHERE '
            statement += ' AND '.join([key+' = '+value for key, value in searchTerms.items()])
        
        return self.conn.execute(statement)

    def getTokens(self, returnColumns = None, searchTerms = None):
        '''Get tokens from the corpus. By default all, but can be restricted.
        
        Keyword arguments:
        returnColumns -- list of all columns to be returned (default= None, return all)
        otherSearchTerms -- dict, specification of search terms for entity properties (default = None)
            example: {'docid' : 15}

        Returns cursor with all rows that fit the specifications
        '''
        statement = 'SELECT '

        if returnColumns:
            statement += ', '.join(returnColumns)
            for column in returnColumns:
                if column not in self.columns['tokens']:
                    raise noSuchColumn(column,'tokens')
        else:
            statement += '*'
        
        statement += ' FROM tokens'
        if searchTerms:
            statement += ' WHERE '
            statement += ' AND '.join([key+' = '+value for key, value in searchTerms.items()])
        
        return self.conn.execute(statement)
        
    def getDocuments(self, returnColumns = None, searchTerms = None):
        '''Get tokens from the corpus. By default all, but can be restricted.
        
        Keyword arguments:
        returnColumns -- list of all columns to be returned (default= None, return all)
        otherSearchTerms -- dict, specification of search terms for entity properties (default = None)
            example: {'id' : '15'}

        Returns cursor with all rows that fit the specifications
        '''
        statement = 'SELECT '

        if returnColumns:
            statement += ', '.join(returnColumns)
            for column in returnColumns:
                if column not in self.columns['documents']:
                    raise noSuchColumn(column,'documents')
        else:
            statement += '*'
        
        statement += ' FROM documents'
        if searchTerms:
            statement += ' WHERE '
            statement += ' AND '.join([key+' = '+value for key, value in searchTerms.items()])
        
        return self.conn.execute(statement)

    def getDocIDs(self, searchTerms):
        '''Get docid from the corpus by search terms.
        
        Keyword arguments:
        searchTerms -- dict, specification of search terms for entity properties (default = None)
            example: {'medium' : 'De Volkskrant'}

        Returns list of all rows that fit the specifications
        '''
        cur = self.getDocuments(['id'],searchTerms)
        return cur.fetchall()
    
    def getUniques(self, table, column):
        '''Get unique values from a column'''

        statement = 'SELECT DISTINCT '+column+' FROM '+table
        return [element for (element,) in self.conn.execute(statement).fetchall()]
    
    def updateRow(self, table, rowid, dictRow, commit = True):
        '''Get docid from the corpus by search terms.
        
        Keyword arguments:
        table -- str, name of table
        rowid -- int, rowid to be updated as an integer
        dictRow -- dict, columns+data to be added

        Returns list of all rows that fit the specifications
        '''
        statement = 'UPDATE '+table+' SET '
        statement += ', '.join([key+' = '+str(value) for key, value in dictRow.items()])
        statement += ' WHERE id = '+str(rowid)
        self.conn.execute(statement)

    def getVarnames(self, table):
        '''Get varnames from a table'''
        return [e[1] for e in self.conn.execute('PRAGMA table_info('+table+');')]

class thesisDB(corpusDB, object):
    def __init__(self, filename):
        colDict = {'documents' : [
            ('date','INTEGER'), ('headline','TEXT'), ('byline','TEXT'),
            ('medium','TEXT'), ('length','INTEGER'), ('section','TEXT')],
            'tokens': [('lemma','TEXT'),('pos','TEXT'),('pos_long','TEXT'),('paragraph_no','INTEGER'),],
            'entities': [('category','TEXT')]}
        super(thesisDB,self).__init__(filename,colDict)
    
    def getDocument(self, rowid):
        '''Get document with update method for easy updating'''
        varnames = self.getVarnames('documents')
        values = self.getDocuments(searchTerms = {'id':str(rowid)}).fetchone()

        return docData(varnames, values, True)

def enclose(string):
    return '"'+re.sub('[\'"]','',string)+'"'

class docData:
    #Nothing special, just exists to carry data back and forth
    def __init__(self, varnames, values, fromDb = False):
        self.table = 'documents'
        values = [enclose(value) if isinstance(value,str) else str(value) for value in values]
        self.data = {var:value for var,value in zip(varnames,values) if value != 'None'}
        self.fromDb = fromDb #Tells you whether to update or instert in database
    
    def toDB(self, db, commit = True):
        if self.fromDb:
            db.updateRow(self.table, rowid = self.data['id'], dictRow = self.data, commit = commit)
            return -1
        else:
            return db.insertRow(self.table, self.data)
    
    def setVar(self, varname, value):
        if varname == 'id':
            raise Exception('You do not want to change the id.')
        self.data[varname] = value