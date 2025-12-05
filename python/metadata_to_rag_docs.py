#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path
from .metadata_model import TableMetadata


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
        text_parts.append(f"Columnas incluidas: {', '.join(column_names[:10])}")
        if len(column_names) > 10:
            text_parts.append(f"... y {len(column_names) - 10} columnas más")
            
    
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
        f"Tipo de dato: {column_metadata.data_type}"
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


def build_rag_documents_from_file(json_path: str) -> list[dict]:
    json_file = Path(json_path)
    
    if not json_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {json_path}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    table_metadata = TableMetadata.from_json(content)
    
    documents = []
    
    table_doc = _build_table_document(table_metadata)
    documents.append(table_doc)
    
    for col in table_metadata.columns:
        col_doc = _build_column_document(col, table_metadata.table_name)
        documents.append(col_doc)
    
    return documents


def print_documents_summary(documents: list[dict]) -> None:
    total = len(documents)
    table_docs = [d for d in documents if d['id'].startswith('TABLE:')]
    column_docs = [d for d in documents if d['id'].startswith('COL:')]
    
    print(f"\nResumen de documentos generados:")
    print(f"  Total: {total}")
    print(f"  Documentos de tabla: {len(table_docs)}")
    print(f"  Documentos de columna: {len(column_docs)}")
    
    if documents:
        print(f"\nEjemplos de títulos:")
        for doc in documents[:3]:
            print(f"  - {doc['title']}")


def main():
    parser = argparse.ArgumentParser(
        description='Genera documentos RAG desde metadatos JSON de tablas INEGI'
    )
    
    parser.add_argument(
        '--json',
        required=True,
        help='Ruta al archivo JSON de metadatos'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"Cargando metadatos desde: {args.json}")
        
        documents = build_rag_documents_from_file(args.json)
        
        print_documents_summary(documents)
        
        if len(documents) > 0:
            print(f"\nEjemplo de documento completo:")
            example = documents[0]
            print(f"  ID: {example['id']}")
            print(f"  Título: {example['title']}")
            print(f"  Texto: {example['text']}")
            print(f"  Tags: {', '.join(example['tags'])}")
        
        if len(documents) > 1:
            print(f"\nOtro ejemplo (columna):")
            example = documents[1]
            print(f"  ID: {example['id']}")
            print(f"  Título: {example['title']}")
            print(f"  Texto: {example['text'][:150]}...")
            print(f"  Tags: {', '.join(example['tags'][:5])}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())