package mx.inegi.meta.generator;

import mx.inegi.meta.model.ColumnMetadata;
import mx.inegi.meta.model.TableMetadata;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class JavaClassGenerator {
    
    public Path generateFor(TableMetadata metadata, Path outputDir, String packageName) throws IOException {
        String className = sanitizeClassName(metadata.getTableName());
        
        Path packageDir = outputDir.resolve(packageName.replace('.', '/'));
        Files.createDirectories(packageDir);
        
        Path javaFile = packageDir.resolve(className + ".java");
        
        try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(javaFile))) {
            writeClass(writer, metadata, className, packageName);
        }
        
        return javaFile;
    }
    
    private String sanitizeClassName(String tableName) {
        if (tableName == null || tableName.trim().isEmpty()) {
            return "GeneratedTable";
        }
        
        String sanitized = tableName.trim().replaceAll("[^a-zA-Z0-9_]", "_");
        
        if (!Character.isJavaIdentifierStart(sanitized.charAt(0))) {
            sanitized = "T_" + sanitized;
        }
        
        return sanitized;
    }
    
    private void writeClass(PrintWriter writer, TableMetadata metadata, String className, String packageName) {
        writer.println("package " + packageName + ";");
        writer.println();
        writer.println("public class " + className + " {");
        writer.println();
        
        for (ColumnMetadata col : metadata.getColumns()) {
            String fieldName = col.getName();
            String fieldType = mapDataType(col);
            
            writer.println("    private " + fieldType + " " + fieldName + ";");
        }
        
        writer.println();
        
        writer.println("    public " + className + "() {");
        writer.println("    }");
        writer.println();
        
        for (ColumnMetadata col : metadata.getColumns()) {
            String fieldName = col.getName();
            String fieldType = mapDataType(col);
            String capitalizedName = capitalizeFirst(fieldName);
            
            writer.println("    public " + fieldType + " get" + capitalizedName + "() {");
            writer.println("        return " + fieldName + ";");
            writer.println("    }");
            writer.println();
            
            writer.println("    public void set" + capitalizedName + "(" + fieldType + " " + fieldName + ") {");
            writer.println("        this." + fieldName + " = " + fieldName + ";");
            writer.println("    }");
            writer.println();
        }
        
        writer.println("    @Override");
        writer.println("    public String toString() {");
        writer.println("        return \"" + className + "{\" +");
        
        for (int i = 0; i < metadata.getColumns().size(); i++) {
            ColumnMetadata col = metadata.getColumns().get(i);
            String fieldName = col.getName();
            
            if (i == 0) {
                writer.println("                \"" + fieldName + "=\" + " + fieldName + " +");
            } else if (i < metadata.getColumns().size() - 1) {
                writer.println("                \", " + fieldName + "=\" + " + fieldName + " +");
            } else {
                writer.println("                \", " + fieldName + "=\" + " + fieldName + " +");
            }
        }
        
        writer.println("                '}';");
        writer.println("    }");
        
        writer.println("}");
    }
    
    private String mapDataType(ColumnMetadata col) {
        String dataType = col.getDataType();
        
        if (dataType == null) {
            return "String";
        }
        
        String normalized = dataType.toUpperCase().trim();
        
        if (normalized.equals("NUMBER") || normalized.equals("NUMERIC") || normalized.equals("DECIMAL")) {
            Integer precision = col.getPrecision();
            if (precision != null && precision > 0) {
                return "Double";
            }
            return "Long";
        }
        
        if (normalized.equals("INTEGER") || normalized.equals("INT")) {
            return "Long";
        }
        
        if (normalized.equals("FLOAT")) {
            return "Double";
        }
        
        if (normalized.equals("BOOLEAN") || normalized.equals("BOOL")) {
            return "Boolean";
        }
        
        if (normalized.equals("DATE") || normalized.equals("TIMESTAMP")) {
            return "java.time.LocalDateTime";
        }
        
        return "String";
    }
    
    private String capitalizeFirst(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }
}