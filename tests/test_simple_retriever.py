import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_stub.simple_retriever import SimpleRetriever


@pytest.fixture
def sample_documents():
    return [
        {
            'id': 'TABLE:TR_ENA2025_CUEST_UP1',
            'title': 'Tabla TR_ENA2025_CUEST_UP1',
            'text': 'Tabla: TR_ENA2025_CUEST_UP1. Número de columnas: 5. Contiene información de cuestionarios.',
            'tags': ['tabla', 'TR_ENA2025_CUEST_UP1']
        },
        {
            'id': 'COL:TR_ENA2025_CUEST_UP1.ID_ENA2025_CUEST_UP',
            'title': 'Columna ID_ENA2025_CUEST_UP en TR_ENA2025_CUEST_UP1',
            'text': 'Columna: ID_ENA2025_CUEST_UP. Tabla: TR_ENA2025_CUEST_UP1. Tipo: NUMBER. Longitud: 19.',
            'tags': ['columna', 'TR_ENA2025_CUEST_UP1', 'ID_ENA2025_CUEST_UP', 'NUMBER']
        },
        {
            'id': 'COL:TR_ENA2025_CUEST_UP1.EC110',
            'title': 'Columna EC110 en TR_ENA2025_CUEST_UP1',
            'text': 'Columna: EC110. Tabla: TR_ENA2025_CUEST_UP1. Tipo: NUMBER. Función: Superficie cultivada en hectáreas.',
            'tags': ['columna', 'TR_ENA2025_CUEST_UP1', 'EC110', 'NUMBER']
        },
        {
            'id': 'COL:TR_ENA2025_CUEST_UP1.NOMBRE',
            'title': 'Columna NOMBRE en TR_ENA2025_CUEST_UP1',
            'text': 'Columna: NOMBRE. Tabla: TR_ENA2025_CUEST_UP1. Tipo: VARCHAR2. Longitud: 100.',
            'tags': ['columna', 'TR_ENA2025_CUEST_UP1', 'NOMBRE', 'VARCHAR2']
        }
    ]


def test_search_by_table(sample_documents):
    retriever = SimpleRetriever(sample_documents)
    
    results = retriever.search_by_table("TR_ENA2025_CUEST_UP1")
    
    assert len(results) > 0
    
    table_result = [r for r in results if r['id'].startswith('TABLE:')]
    assert len(table_result) >= 1
    
    first_table = table_result[0]
    assert 'TR_ENA2025_CUEST_UP1' in first_table['title'] or 'TR_ENA2025_CUEST_UP1' in first_table['tags']


def test_search_by_column(sample_documents):
    retriever = SimpleRetriever(sample_documents)
    
    results = retriever.search_by_column("ID_ENA2025_CUEST_UP")
    
    assert len(results) > 0
    
    for result in results:
        assert result['id'].startswith('COL:')
        assert 'ID_ENA2025_CUEST_UP' in result['text'] or 'ID_ENA2025_CUEST_UP' in result['title']


def test_search_by_column_ec110(sample_documents):
    retriever = SimpleRetriever(sample_documents)
    
    results = retriever.search_by_column("EC110")
    
    assert len(results) > 0
    
    ec110_doc = results[0]
    assert 'EC110' in ec110_doc['title']


def test_search_by_keyword(sample_documents):
    retriever = SimpleRetriever(sample_documents)
    
    results = retriever.search_by_keyword("superficie cultivada")
    
    assert len(results) > 0
    
    assert any('cultivada' in r['text'].lower() for r in results)


def test_get_all_tables(sample_documents):
    retriever = SimpleRetriever(sample_documents)
    
    tables = retriever.get_all_tables()
    
    assert len(tables) == 1
    assert tables[0]['id'].startswith('TABLE:')


def test_get_all_columns(sample_documents):
    retriever = SimpleRetriever(sample_documents)
    
    columns = retriever.get_all_columns()
    
    assert len(columns) == 3
    
    for col in columns:
        assert col['id'].startswith('COL:')


def test_empty_retriever():
    retriever = SimpleRetriever([])
    
    assert len(retriever.search_by_table("any")) == 0
    assert len(retriever.search_by_column("any")) == 0
    assert len(retriever.get_all_tables()) == 0