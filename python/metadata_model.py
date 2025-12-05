from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import json

@dataclass
class ColumnMetadata:
    name: str
    table_name: str
    data_type: str
    length: Optional[int] = None
    precision: Optional[int] = None
    function: Optional[str] = None
    aggregation_level: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColumnMetadata':
        return cls(**data)


@dataclass
class TableMetadata:
    table_name: str
    columns: List[ColumnMetadata] = field(default_factory=list)
    schema: Optional[str] = None
    source_sheet: Optional[str] = None
    source_file: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'table_name': self.table_name,
            'columns': [col.to_dict() for col in self.columns]
        }
        
        if self.schema is not None:
            result['schema'] = self.schema
        if self.source_sheet is not None:
            result['source_sheet'] = self.source_sheet
        if self.source_file is not None:
            result['source_file'] = self.source_file
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TableMetadata':
        columns_data = data.pop('columns', [])
        columns = [ColumnMetadata.from_dict(col) for col in columns_data]
        return cls(columns=columns, **data)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TableMetadata':
        data = json.loads(json_str)
        return cls.from_dict(data)