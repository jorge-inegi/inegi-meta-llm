package mx.inegi.meta;

import mx.inegi.meta.io.JsonMetadataLoader;
import mx.inegi.meta.model.TableMetadata;

public class TestLoader {
    public static void main(String[] args) throws Exception {
        TableMetadata metadata = JsonMetadataLoader.loadFromFile("output/metadata_TR_ENA2025_CUEST_UP1.json");
        System.out.println(metadata);
        System.out.println("Columnas: " + metadata.getColumns().size());
    }
}
