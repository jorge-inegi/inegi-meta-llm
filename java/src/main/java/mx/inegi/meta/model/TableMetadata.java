package mx.inegi.meta.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class TableMetadata {
    
    @JsonProperty("table_name")
    private String tableName;
    
    private String schema;
    
    @JsonProperty("source_sheet")
    private String sourceSheet;
    
    @JsonProperty("source_file")
    private String sourceFile;
    
    private List<ColumnMetadata> columns;
    
    public TableMetadata() {
        this.columns = new ArrayList<>();
    }
    
    public TableMetadata(String tableName) {
        this.tableName = tableName;
        this.columns = new ArrayList<>();
    }
    
    public String getTableName() {
        return tableName;
    }
    
    public void setTableName(String tableName) {
        this.tableName = tableName;
    }
    
    public String getSchema() {
        return schema;
    }
    
    public void setSchema(String schema) {
        this.schema = schema;
    }
    
    public String getSourceSheet() {
        return sourceSheet;
    }
    
    public void setSourceSheet(String sourceSheet) {
        this.sourceSheet = sourceSheet;
    }
    
    public String getSourceFile() {
        return sourceFile;
    }
    
    public void setSourceFile(String sourceFile) {
        this.sourceFile = sourceFile;
    }
    
    public List<ColumnMetadata> getColumns() {
        return columns;
    }
    
    public void setColumns(List<ColumnMetadata> columns) {
        this.columns = columns;
    }
    
    public void addColumn(ColumnMetadata column) {
        this.columns.add(column);
    }
    
    @Override
    public String toString() {
        return "TableMetadata{" +
                "tableName='" + tableName + '\'' +
                ", schema='" + schema + '\'' +
                ", sourceSheet='" + sourceSheet + '\'' +
                ", sourceFile='" + sourceFile + '\'' +
                ", columns=" + columns.size() + " columnas" +
                '}';
    }
}