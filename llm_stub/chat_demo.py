#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_stub.metadata_document_builder import build_documents_from_file
from llm_stub.simple_retriever import SimpleRetriever
from llm_stub.local_llm_client import LocalLlmClient


def is_table_fields_question(question: str) -> bool:
    patterns = [
        r'qu[eé]\s+campos?\s+tiene',
        r'qu[eé]\s+columnas?\s+tiene',
        r'cu[aá]les?\s+son\s+los\s+campos',
        r'lista.*campos',
        r'lista.*columnas'
    ]
    
    question_lower = question.lower()
    return any(re.search(pattern, question_lower) for pattern in patterns)


def extract_column_info(doc: dict) -> dict:
    text = doc.get('text', '')
    
    info = {
        'name': '',
        'type': '',
        'function': '',
        'level': ''
    }
    
    parts = text.split('.')
    for part in parts:
        part = part.strip()
        if part.startswith('Columna:'):
            info['name'] = part.replace('Columna:', '').strip()
        elif part.startswith('Tipo:'):
            info['type'] = part.replace('Tipo:', '').strip()
        elif part.startswith('Función:'):
            info['function'] = part.replace('Función:', '').strip()
        elif part.startswith('Nivel de desagregación:'):
            info['level'] = part.replace('Nivel de desagregación:', '').strip()
    
    if not info['name'] and 'tags' in doc:
        tags = doc['tags']
        for tag in tags:
            if tag not in ['columna', 'tabla'] and len(tag) > 3:
                info['name'] = tag
                break
    
    return info


def answer_table_fields_question(retriever: SimpleRetriever, question: str) -> str:
    entities = retriever.extract_entities_from_question(question)
    
    if not entities['tables']:
        return None
    
    table_name = entities['tables'][0]
    
    table_docs = [doc for doc in retriever.search_by_table(table_name) if doc['id'].startswith('TABLE:')]
    column_docs = [doc for doc in retriever.search_by_table(table_name) if doc['id'].startswith('COL:')]
    
    if not column_docs:
        return None
    
    response_lines = [f"La tabla {table_name} tiene {len(column_docs)} columnas:\n"]
    
    for doc in column_docs[:15]:
        info = extract_column_info(doc)
        
        line_parts = [f"• {info['name']}"]
        
        if info['type']:
            line_parts.append(f"tipo {info['type']}")
        
        if info['function']:
            line_parts.append(f"Función: {info['function']}")
        
        if info['level']:
            line_parts.append(f"Nivel: {info['level']}")
        
        response_lines.append(". ".join(line_parts) + ".")
    
    if len(column_docs) > 15:
        response_lines.append(f"\n... y {len(column_docs) - 15} columnas más.")
    
    return "\n".join(response_lines)


def main():
    parser = argparse.ArgumentParser(description='Chat interactivo con metadatos INEGI')
    
    parser.add_argument('--json', required=False, help="Ruta al JSON de metadatos (si se omite, se usa un archivo por defecto de output/).",)
    parser.add_argument('--model', default=None, help="Ruta al JSON de metadatos (si se omite, se usa un archivo por defecto de output/).",)
    
    args = parser.parse_args()
    if args.json:
        json_path = Path(args.json)
    else:
        # Buscar un JSON por defecto en output/
        output_dir = Path("output")
        candidates = sorted(output_dir.glob("metadata_*.json"))
        if not candidates:
            print("ERROR: No se encontraron archivos metadata_*.json en la carpeta output/.")
            return

        json_path = candidates[-1]
        print(f"No se especificó --json; usando por defecto: {json_path}")
    #
    json_path = Path(args.json)
    if not json_path.exists():
        print(f"ERROR: No se encontró el archivo {json_path}")
        return 1
    
    print(f"Cargando metadatos desde {json_path}...")
    documents = build_documents_from_file(str(json_path))
    print(f"Documentos cargados: {len(documents)}")
    
    retriever = SimpleRetriever(documents)
    llm_client = LocalLlmClient(model_name=args.model)
    
    print("\n" + "="*60)
    print("Chat de metadatos INEGI")
    print("="*60)
    print("Escribe 'salir' o 'exit' para terminar\n")
    
    while True:
        try:
            question = input("Tu pregunta: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['salir', 'exit', 'quit']:
                print("¡Hasta luego!")
                break
            
            if is_table_fields_question(question):
                response = answer_table_fields_question(retriever, question)
                if response:
                    print(f"\n{response}\n")
                    continue
            
            candidates = retriever.search_from_question(question)
            
            if not candidates:
                print("\nNo encontré información relevante en los metadatos para responder esta pregunta.\n")
                continue
            
            print(f"\n[Encontrados {len(candidates)} documentos relevantes]")
            
            response = llm_client.generate_with_template(question, candidates)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())