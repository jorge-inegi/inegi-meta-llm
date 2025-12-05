#!/usr/bin/env python3

import argparse
import sys
import pandas as pd
from pathlib import Path
from .excel_to_metadata import build_table_metadata, save_metadata_to_json, list_tables_in_sheet
from .metadata_validator import validate_metadata_strict


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Genera y valida metadatos JSON desde archivos Excel de diseño INEGI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--excel',
        required=False,
        help='Ruta al archivo Excel de diseño'
    )
    
    parser.add_argument(
        '--sheet',
        required=False,
        help='Nombre de la hoja del Excel a procesar'
    )
    
    parser.add_argument(
        '--table-name',
        required=False,
        help='Nombre de la tabla a extraer del diseño'
    )
    
    parser.add_argument(
        '--out-json',
        required=False,
        help='Ruta del archivo JSON de salida para los metadatos'
    )
    
    return parser.parse_args()


def resolve_excel_path(excel_arg):
    if excel_arg:
        return Path(excel_arg)
    
    excel_dir = Path('excel')
    if not excel_dir.exists():
        print(f"ERROR: No se encontró la carpeta 'excel/'", file=sys.stderr)
        return None
    
    xlsx_files = list(excel_dir.glob('*.xlsx'))
    
    if len(xlsx_files) == 0:
        print(f"ERROR: No se encontraron archivos .xlsx en la carpeta 'excel/'", file=sys.stderr)
        return None
    
    if len(xlsx_files) == 1:
        return xlsx_files[0]
    
    print("Se encontraron varios archivos Excel. Selecciona uno:")
    for idx, file in enumerate(xlsx_files, 1):
        print(f"  {idx}. {file.name}")
    
    while True:
        try:
            choice = input("\nIngresa el número del archivo a usar: ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(xlsx_files):
                return xlsx_files[choice_idx]
            else:
                print(f"Opción inválida. Ingresa un número entre 1 y {len(xlsx_files)}")
        except (ValueError, KeyboardInterrupt):
            print("\nOperación cancelada", file=sys.stderr)
            return None


def resolve_table_name(excel_path, sheet_name, table_arg):
    if table_arg:
        return table_arg
    
    try:
        tables = list_tables_in_sheet(str(excel_path), sheet_name)
    except Exception as e:
        print(f"ERROR: No se pudieron listar las tablas: {e}", file=sys.stderr)
        return None
    
    if len(tables) == 0:
        print(f"ERROR: No se encontraron tablas en la hoja '{sheet_name}'", file=sys.stderr)
        return None
    
    if len(tables) == 1:
        return tables[0]
    
    print(f"\nSe encontraron {len(tables)} tablas en la hoja '{sheet_name}'. Selecciona una:")
    for idx, table in enumerate(tables, 1):
        print(f"  {idx}. {table}")
    
    while True:
        try:
            choice = input("\nIngresa el número de la tabla a procesar: ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(tables):
                return tables[choice_idx]
            else:
                print(f"Opción inválida. Ingresa un número entre 1 y {len(tables)}")
        except (ValueError, KeyboardInterrupt):
            print("\nOperación cancelada", file=sys.stderr)
            return None


def main():
    args = parse_arguments()
    
    excel_path = resolve_excel_path(args.excel)
    if not excel_path:
        return 1
    
    if not excel_path.exists():
        print(f"ERROR: No se encontró el archivo Excel: {excel_path}", file=sys.stderr)
        return 1
    
    if args.sheet:
        sheet_name = args.sheet
    else:
        # toma la primera hoja del archivo Excel si no se pasa por argumentos
        try:
            xls = pd.ExcelFile(excel_path)
            sheet_name = xls.sheet_names[0]
        except Exception as e:
            print(f"ERROR: No se pudieron obtener las hojas del Excel: {e}", file=sys.stderr)
            return 1


    table_name = resolve_table_name(excel_path, sheet_name, args.table_name)
    if not table_name:
        return 1
    
    if args.out_json:
        out_json_path = args.out_json
    else:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        table_normalized = table_name.strip().upper().replace(' ', '_')
        out_json_path = str(output_dir / f"metadata_{table_normalized}.json")
    
    try:
        print(f"\nProcesando tabla '{table_name}' desde {excel_path.name}...")
        print(f"  Hoja: {sheet_name}")
        
        table_metadata = build_table_metadata(
            excel_path=str(excel_path),
            sheet_name=sheet_name,
            table_name=table_name
        )
        
        print(f"  Columnas encontradas: {len(table_metadata.columns)}")
        
        save_metadata_to_json(table_metadata, out_json_path)
        print(f"  Metadatos guardados en: {out_json_path}")
        
        print("\nValidando metadatos generados...")
        validate_metadata_strict(out_json_path)
        
        print("✓ Validación exitosa")
        print(f"\nArchivo generado correctamente: {out_json_path}")
        
        return 0
        
    except FileNotFoundError as e:
        if "sheet" in str(e).lower() or "hoja" in str(e).lower():
            print(f"ERROR: No se encontró la hoja '{sheet_name}' en el Excel.", file=sys.stderr)
            print(f"Usa --sheet para especificar otra hoja.", file=sys.stderr)
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
        
    except ValueError as e:
        print(f"ERROR DE VALIDACIÓN:\n{e}", file=sys.stderr)
        return 2
        
    except KeyError as e:
        print(f"ERROR: Columna esperada no encontrada en el Excel: {e}", file=sys.stderr)
        return 3
        
    except Exception as e:
        print(f"ERROR INESPERADO: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 99


if __name__ == '__main__':
    sys.exit(main())