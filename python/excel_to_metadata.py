import pandas as pd
from pathlib import Path
from typing import Optional, List
from .metadata_model import TableMetadata, ColumnMetadata


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(col).strip().upper() for col in df.columns]
    return df


def _safe_string(value) -> Optional[str]:
    if pd.isna(value):
        return None
    value_str = str(value).strip()
    return value_str if value_str else None


def _safe_int(value) -> Optional[int]:
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def build_table_metadata(excel_path: str, sheet_name: str, table_name: str) -> TableMetadata:
    excel_file = Path(excel_path)
    
    if not excel_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {excel_path}")
    
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df = _normalize_column_names(df)
    
    required_columns = {'NOMBRE DE LA TABLA', 'CAMPO', 'TIPO'}
    missing_columns = required_columns - set(df.columns)
    
    if missing_columns:
        raise ValueError(
            f"Faltan columnas requeridas en la hoja '{sheet_name}': {', '.join(missing_columns)}"
        )
    
    table_name_normalized = table_name.strip().upper()
    mask = df['NOMBRE DE LA TABLA'].fillna('').str.strip().str.upper() == table_name_normalized
    filtered_df = df[mask]
    
    if filtered_df.empty:
        raise ValueError(
            f"No se encontraron filas para la tabla '{table_name}' en la hoja '{sheet_name}'"
        )
    
    columns = []
    for _, row in filtered_df.iterrows():
        col = ColumnMetadata(
            name=_safe_string(row.get('CAMPO')),
            table_name=table_name,
            data_type=_safe_string(row.get('TIPO')),
            length=_safe_int(row.get('LONGITUD')),
            precision=_safe_int(row.get('PRECISION')),
            function=_safe_string(row.get('FUNCIÓN')),
            aggregation_level=_safe_string(row.get('NIVEL DE DESAGREGACIÓN'))
        )
        columns.append(col)
    
    return TableMetadata(
        table_name=table_name,
        columns=columns,
        source_sheet=sheet_name,
        source_file=excel_file.name
    )


def save_metadata_to_json(table_metadata: TableMetadata, out_json_path: str) -> None:
    output_path = Path(out_json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(table_metadata.to_json())


def list_tables_in_sheet(excel_path: str, sheet_name: str) -> List[str]:
    excel_file = Path(excel_path)
    
    if not excel_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {excel_path}")
    
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df = _normalize_column_names(df)
    
    if 'NOMBRE DE LA TABLA' not in df.columns:
        raise ValueError(
            f"La hoja '{sheet_name}' no contiene la columna 'NOMBRE DE LA TABLA'"
        )
    
    table_names = df['NOMBRE DE LA TABLA'].fillna('').str.strip()
    table_names = table_names[table_names != '']
    unique_tables = sorted(table_names.unique())
    
    return list(unique_tables)