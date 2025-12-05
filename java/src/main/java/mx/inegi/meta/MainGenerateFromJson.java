package mx.inegi.meta;

import mx.inegi.meta.generator.JavaClassGenerator;
import mx.inegi.meta.io.JsonMetadataLoader;
import mx.inegi.meta.model.TableMetadata;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;

public class MainGenerateFromJson {
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("ERROR: Se requiere la ruta del archivo JSON de metadatos");
            System.err.println("Uso: java mx.inegi.meta.MainGenerateFromJson <json-path> [package-name]");
            System.exit(1);
        }
        
        String jsonPath = args[0];
        String packageName = args.length > 1 ? args[1] : "mx.inegi.generated";
        
        try {
            System.out.println("Cargando metadatos desde: " + jsonPath);
            
            TableMetadata metadata = JsonMetadataLoader.loadFromFile(jsonPath);
            
            System.out.println("Tabla encontrada: " + metadata.getTableName());
            System.out.println("Columnas: " + metadata.getColumns().size());
            
            Path outputDir = Paths.get("java/src/generated");
            
            JavaClassGenerator generator = new JavaClassGenerator();
            Path generatedFile = generator.generateFor(metadata, outputDir, packageName);
            
            String className = generatedFile.getFileName().toString().replace(".java", "");
            
            System.out.println("\n✓ Clase generada exitosamente");
            System.out.println("  Nombre de clase: " + className);
            System.out.println("  Package: " + packageName);
            System.out.println("  Archivo: " + generatedFile.toAbsolutePath());
            
        } catch (IOException e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        } catch (Exception e) {
            System.err.println("ERROR INESPERADO: " + e.getMessage());
            e.printStackTrace();
            System.exit(2);
        }
    }
}