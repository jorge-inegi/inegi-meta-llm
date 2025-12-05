import re


class SimpleRetriever:
    
    def __init__(self, documents: list[dict]):
        self.documents = documents
    
    def search_by_table(self, table_name: str) -> list[dict]:
        table_normalized = table_name.strip().lower()
        
        results = []
        for doc in self.documents:
            if table_normalized in doc['title'].lower() or table_normalized in doc['text'].lower():
                results.append(doc)
            
            if 'tags' in doc and any(table_normalized in tag.lower() for tag in doc['tags']):
                if doc not in results:
                    results.append(doc)
        
        return results
    
    def search_by_column(self, column_name: str) -> list[dict]:
        column_normalized = column_name.strip().lower()
        
        results = []
        for doc in self.documents:
            if doc['id'].startswith('COL:'):
                if column_normalized in doc['title'].lower() or column_normalized in doc['text'].lower():
                    results.append(doc)
                
                if 'tags' in doc and any(column_normalized in tag.lower() for tag in doc['tags']):
                    if doc not in results:
                        results.append(doc)
        
        return results
    
    def search_by_keyword(self, keyword: str) -> list[dict]:
        keyword_normalized = keyword.strip().lower()
        
        results = []
        for doc in self.documents:
            if keyword_normalized in doc['text'].lower() or keyword_normalized in doc['title'].lower():
                results.append(doc)
        
        return results
    
    def get_all_tables(self) -> list[dict]:
        return [doc for doc in self.documents if doc['id'].startswith('TABLE:')]
    
    def get_all_columns(self) -> list[dict]:
        return [doc for doc in self.documents if doc['id'].startswith('COL:')]
    
    def extract_entities_from_question(self, question: str) -> dict:
        question_upper = question.upper()
        
        table_pattern = r'\bTR_[A-Z0-9_]+\b'
        tables = re.findall(table_pattern, question_upper)
        tables = list(set(tables))
        
        column_pattern = r'\b[A-Z]{2,}[0-9_]+[A-Z0-9_]*\b'
        columns = re.findall(column_pattern, question_upper)
        columns = [c for c in columns if not c.startswith('TR_')]
        columns = list(set(columns))
        
        return {
            'tables': tables,
            'columns': columns
        }
    
    def search_from_question(self, question: str) -> list[dict]:
        entities = self.extract_entities_from_question(question)
        
        results = []
        
        if entities['columns']:
            for column in entities['columns']:
                col_results = self.search_by_column(column)
                for r in col_results:
                    if r not in results:
                        results.append(r)
        
        if not results and entities['tables']:
            table_results = self.search_by_table(entities['tables'][0])
            results.extend(table_results)
        
        if not results:
            clean_question = re.sub(r'[¿?¡!.,;:]', '', question).lower()
            words = clean_question.split()
            keywords = [w for w in words if len(w) > 4]
            
            for keyword in keywords[:3]:
                kw_results = self.search_by_keyword(keyword)
                for r in kw_results:
                    if r not in results:
                        results.append(r)
        
        return results