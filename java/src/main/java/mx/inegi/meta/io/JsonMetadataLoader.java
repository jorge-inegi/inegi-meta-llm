package mx.inegi.meta.io;

import com.fasterxml.jackson.databind.ObjectMapper;
import mx.inegi.meta.model.TableMetadata;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class JsonMetadataLoader {
    
    private static final ObjectMapper mapper = new ObjectMapper();
    
    public static TableMetadata loadFromFile(String jsonPath) throws IOException {
        Path path = Paths.get(jsonPath);
        
        if (!Files.exists(path)) {
            throw new IOException("No se encontró el archivo: " + jsonPath);
        }
        
        if (!Files.isReadable(path)) {
            throw new IOException("No se puede leer el archivo: " + jsonPath);
        }
        
        try {
            File file = path.toFile();
            TableMetadata metadata = mapper.readValue(file, TableMetadata.class);
            
            if (metadata.getTableName() == null || metadata.getTableName().trim().isEmpty()) {
                throw new IOException("El JSON no contiene un 'table_name' válido");
            }
            
            if (metadata.getColumns() == null || metadata.getColumns().isEmpty()) {
                throw new IOException("El JSON no contiene columnas");
            }
            
            return metadata;
            
        } catch (IOException e) {
            throw new IOException("Error al parsear el JSON: " + e.getMessage(), e);
        }
    }
    
    public static TableMetadata loadFromString(String jsonContent) throws IOException {
        try {
            TableMetadata metadata = mapper.readValue(jsonContent, TableMetadata.class);
            
            if (metadata.getTableName() == null || metadata.getTableName().trim().isEmpty()) {
                throw new IOException("El JSON no contiene un 'table_name' válido");
            }
            
            return metadata;
            
        } catch (IOException e) {
            throw new IOException("Error al parsear el JSON: " + e.getMessage(), e);
        }
    }
}