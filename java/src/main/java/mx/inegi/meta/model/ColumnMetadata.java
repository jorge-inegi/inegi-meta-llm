package mx.inegi.meta.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ColumnMetadata {
    
    private String name;
    
    @JsonProperty("table_name")
    private String tableName;
    
    @JsonProperty("data_type")
    private String dataType;
    
    private Integer length;
    
    private Integer precision;
    
    private String function;
    
    @JsonProperty("aggregation_level")
    private String aggregationLevel;
    
    public ColumnMetadata() {
    }
    
    public ColumnMetadata(String name, String tableName, String dataType) {
        this.name = name;
        this.tableName = tableName;
        this.dataType = dataType;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getTableName() {
        return tableName;
    }
    
    public void setTableName(String tableName) {
        this.tableName = tableName;
    }
    
    public String getDataType() {
        return dataType;
    }
    
    public void setDataType(String dataType) {
        this.dataType = dataType;
    }
    
    public Integer getLength() {
        return length;
    }
    
    public void setLength(Integer length) {
        this.length = length;
    }
    
    public Integer getPrecision() {
        return precision;
    }
    
    public void setPrecision(Integer precision) {
        this.precision = precision;
    }
    
    public String getFunction() {
        return function;
    }
    
    public void setFunction(String function) {
        this.function = function;
    }
    
    public String getAggregationLevel() {
        return aggregationLevel;
    }
    
    public void setAggregationLevel(String aggregationLevel) {
        this.aggregationLevel = aggregationLevel;
    }
    
    @Override
    public String toString() {
        return "ColumnMetadata{" +
                "name='" + name + '\'' +
                ", tableName='" + tableName + '\'' +
                ", dataType='" + dataType + '\'' +
                ", length=" + length +
                ", precision=" + precision +
                ", function='" + function + '\'' +
                ", aggregationLevel='" + aggregationLevel + '\'' +
                '}';
    }
}