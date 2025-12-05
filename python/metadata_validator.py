from pathlib import Path
from typing import List
from .metadata_model import TableMetadata

ALLOWED_DATA_TYPES = {
    'NUMBER',
    'CHAR',
    'VARCHAR2',
    'DATE',
    'TIMESTAMP',
    'INTEGER',
    'FLOAT',
    'DECIMAL',
    'NUMERIC',
    'TEXT',
    'BOOLEAN',
    'BLOB',
    'CLOB'
}

def validate_metadata_file(json_path: str) -> List[str]:
    errors = []
    
    json_file = Path(json_path)
    if not json_file.exists():
        errors.append(f"No se encontró el archivo: {json_path}")
        return errors
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read()
        table_metadata = TableMetadata.from_json(content)
    except Exception as e:
        errors.append(f"Error al parsear el JSON: {str(e)}")
        return errors
    
    if not table_metadata.table_name or not table_metadata.table_name.strip():
        errors.append("El campo 'table_name' está vacío")
    
    if not table_metadata.columns:
        errors.append("La lista 'columns' está vacía")
        return errors
    
    for idx, col in enumerate(table_metadata.columns):
        col_id = col.name if col.name else f"índice {idx}"
        
        if not col.name or not col.name.strip():
            errors.append(f"Columna en posición {idx}: falta el nombre del campo")
        
        if not col.data_type:
            errors.append(f"Columna '{col_id}': falta el tipo de dato")
        else:
            dtype_upper = col.data_type.upper().strip()
            if dtype_upper not in ALLOWED_DATA_TYPES:
                errors.append(
                    f"Columna '{col_id}': tipo de dato '{col.data_type}' no permitido"
                )
            
            if dtype_upper in {'CHAR', 'VARCHAR2'}:
                if col.length is None:
                    errors.append(
                        f"Columna '{col_id}': tipo '{col.data_type}' requiere especificar 'length'"
                    )
                elif col.length <= 0:
                    errors.append(
                        f"Columna '{col_id}': 'length' debe ser mayor a 0"
                    )
        
        if col.length is not None:
            if not isinstance(col.length, int) or col.length <= 0:
                errors.append(f"Columna '{col_id}': 'length' debe ser un entero positivo")
        
        if col.precision is not None:
            if not isinstance(col.precision, int) or col.precision < 0:
                errors.append(f"Columna '{col_id}': 'precision' debe ser un entero no negativo")
    
    return errors


def validate_metadata_strict(json_path: str) -> None:
    errors = validate_metadata_file(json_path)
    
    if errors:
        error_msg = f"Se encontraron {len(errors)} errores de validación:\n"
        error_msg += "\n".join(f"  • {error}" for error in errors)
        raise ValueError(error_msg)