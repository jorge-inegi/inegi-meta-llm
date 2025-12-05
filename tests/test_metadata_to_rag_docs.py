import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.metadata_to_rag_docs import build_rag_documents_from_file


def test_build_rag_documents_from_file():
    json_path = Path(__file__).parent / "data" / "metadatos_tr_ejemplo.json"
    
    documents = build_rag_documents_from_file(str(json_path))
    
    assert len(documents) > 0
    
    table_docs = [d for d in documents if d['id'].startswith('TABLE:')]
    column_docs = [d for d in documents if d['id'].startswith('COL:')]
    
    assert len(table_docs) >= 1
    assert len(column_docs) >= 1


def test_table_document_structure():
    json_path = Path(__file__).parent / "data" / "metadatos_tr_ejemplo.json"
    
    documents = build_rag_documents_from_file(str(json_path))
    
    table_docs = [d for d in documents if d['id'].startswith('TABLE:')]
    table_doc = table_docs[0]
    
    assert 'id' in table_doc
    assert 'title' in table_doc
    assert 'text' in table_doc
    assert 'tags' in table_doc
    
    assert 'Tabla' in table_doc['title']
    assert table_doc['text'] != ""
    assert 'tabla' in table_doc['tags']


def test_column_documents_structure():
    json_path = Path(__file__).parent / "data" / "metadatos_tr_ejemplo.json"
    
    documents = build_rag_documents_from_file(str(json_path))
    
    column_docs = [d for d in documents if d['id'].startswith('COL:')]
    
    for col_doc in column_docs:
        assert 'id' in col_doc
        assert 'title' in col_doc
        assert 'text' in col_doc
        assert 'tags' in col_doc
        
        assert 'Columna' in col_doc['title']
        assert col_doc['text'] != ""
        assert 'columna' in col_doc['tags']


def test_documents_contain_metadata_info():
    json_path = Path(__file__).parent / "data" / "metadatos_tr_ejemplo.json"
    
    documents = build_rag_documents_from_file(str(json_path))
    
    all_text = " ".join([d['text'] for d in documents])
    
    assert 'Tabla' in all_text or 'tabla' in all_text.lower()
    assert 'Columna' in all_text or 'columna' in all_text.lower()
    assert 'Tipo' in all_text or 'tipo' in all_text.lower()


def test_no_empty_documents():
    json_path = Path(__file__).parent / "data" / "metadatos_tr_ejemplo.json"
    
    documents = build_rag_documents_from_file(str(json_path))
    
    for doc in documents:
        assert doc['text'] != ""
        assert doc['title'] != ""
        assert doc['id'] != ""