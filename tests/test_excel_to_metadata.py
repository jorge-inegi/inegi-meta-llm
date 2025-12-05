import pytest
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.excel_to_metadata import build_table_metadata, save_metadata_to_json
from python.metadata_model import TableMetadata


def test_build_table_metadata_from_excel():
    excel_path = Path(__file__).parent / "data" / "diseno_tabla_ejemplo.xlsx"
    
    table_metadata = build_table_metadata(
        excel_path=str(excel_path),
        sheet_name="BLOQUE 1",
        table_name="TR_ENA2025_CUEST_UP1"
    )
    
    assert table_metadata is not None
    assert table_metadata.table_name == "TR_ENA2025_CUEST_UP1"
    assert len(table_metadata.columns) > 0
    assert table_metadata.source_sheet == "BLOQUE 1"
    assert table_metadata.source_file == "diseno_tabla_ejemplo.xlsx"
    
    column_names = [col.name for col in table_metadata.columns]
    assert "ID_ENA2025_CUEST_UP" in column_names


def test_table_metadata_has_valid_columns():
    excel_path = Path(__file__).parent / "data" / "diseno_tabla_ejemplo.xlsx"
    
    table_metadata = build_table_metadata(
        excel_path=str(excel_path),
        sheet_name="BLOQUE 1",
        table_name="TR_ENA2025_CUEST_UP1"
    )
    
    for col in table_metadata.columns:
        assert col.name is not None
        assert col.table_name == "TR_ENA2025_CUEST_UP1"
        assert col.data_type is not None


def test_save_metadata_to_json(tmp_path):
    excel_path = Path(__file__).parent / "data" / "diseno_tabla_ejemplo.xlsx"
    
    table_metadata = build_table_metadata(
        excel_path=str(excel_path),
        sheet_name="BLOQUE 1",
        table_name="TR_ENA2025_CUEST_UP1"
    )
    
    output_json = tmp_path / "metadata_test.json"
    save_metadata_to_json(table_metadata, str(output_json))
    
    assert output_json.exists()
    
    with open(output_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data['table_name'] == "TR_ENA2025_CUEST_UP1"
    assert 'columns' in data
    assert len(data['columns']) > 0


def test_metadata_roundtrip(tmp_path):
    excel_path = Path(__file__).parent / "data" / "diseno_tabla_ejemplo.xlsx"
    
    original_metadata = build_table_metadata(
        excel_path=str(excel_path),
        sheet_name="BLOQUE 1",
        table_name="TR_ENA2025_CUEST_UP1"
    )
    
    output_json = tmp_path / "metadata_roundtrip.json"
    save_metadata_to_json(original_metadata, str(output_json))
    
    with open(output_json, 'r', encoding='utf-8') as f:
        content = f.read()
    
    loaded_metadata = TableMetadata.from_json(content)
    
    assert loaded_metadata.table_name == original_metadata.table_name
    assert len(loaded_metadata.columns) == len(original_metadata.columns)