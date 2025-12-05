from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from metadata_model import TableMetadata


def load_table_metadata(json_path: str) -> TableMetadata:
    json_file = Path(json_path)
    
    if not json_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {json_path}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return TableMetadata.from_json(content)


def _build_table_document(table_metadata: TableMetadata) -> dict:
    text_parts = [
        f"Tabla: {table_metadata.table_name}",
        f"Número de columnas: {len(table_metadata.columns)}"
    ]
    
    if table_metadata.schema:
        text_parts.append(f"Esquema: {table_metadata.schema}")
    
    if table_metadata.source_file:
        text_parts.append(f"Archivo origen: {table_metadata.source_file}")
    
    if table_metadata.source_sheet:
        text_parts.append(f"Hoja origen: {table_metadata.source_sheet}")
    
    column_names = [col.name for col in table_metadata.columns if col.name]
    if column_names:
        text_parts.append(f"Columnas: {', '.join(column_names[:8])}")
        if len(column_names) > 8:
            text_parts.append(f"y {len(column_names) - 8} más")
    
    return {
        'id': f"TABLE:{table_metadata.table_name}",
        'title': f"Tabla {table_metadata.table_name}",
        'text': ". ".join(text_parts) + ".",
        'tags': ['tabla', table_metadata.table_name]
    }


def _build_column_document(column_metadata, table_name: str) -> dict:
    col_name = column_metadata.name or "sin_nombre"
    
    text_parts = [
        f"Columna: {col_name}",
        f"Tabla: {table_name}",
        f"Tipo: {column_metadata.data_type}"
    ]
    
    if column_metadata.length is not None:
        text_parts.append(f"Longitud: {column_metadata.length}")
    
    if column_metadata.precision is not None:
        text_parts.append(f"Precisión: {column_metadata.precision}")
    
    if column_metadata.function:
        text_parts.append(f"Función: {column_metadata.function}")
    
    if column_metadata.aggregation_level:
        text_parts.append(f"Nivel de desagregación: {column_metadata.aggregation_level}")
    
    tags = ['columna', table_name]
    if column_metadata.name:
        tags.append(column_metadata.name)
    if column_metadata.data_type:
        tags.append(column_metadata.data_type)
    
    return {
        'id': f"COL:{table_name}.{col_name}",
        'title': f"Columna {col_name} en {table_name}",
        'text': ". ".join(text_parts) + ".",
        'tags': tags
    }


def build_documents_from_metadata(table_metadata: TableMetadata) -> list[dict]:
    documents = []
    
    table_doc = _build_table_document(table_metadata)
    documents.append(table_doc)
    
    for col in table_metadata.columns:
        col_doc = _build_column_document(col, table_metadata.table_name)
        documents.append(col_doc)
    
    return documents


def build_documents_from_file(json_path: str) -> list[dict]:
    table_metadata = load_table_metadata(json_path)
    return build_documents_from_metadata(table_metadata)