import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;

//Usando jackson: https://github.com/FasterXML/jackson
public class JsonParser {

    public static void main(String[] args) {
        String fileName = "receita - 1 a 12 - 2022.json";
        StringBuilder conteudo = new StringBuilder();

        try (BufferedReader file = new BufferedReader(new FileReader(fileName))) {
            try {
                String line;
                while ((line = file.readLine()) != null) {
                    conteudo.append(line);
                }
            } finally {
                file.close();
            }
        } catch (IOException e) {
            System.out.println("Falha ao ler o arquivo " + fileName);
            e.printStackTrace();
        }

        System.out.println(conteudo);
        JsonParser parser = new JsonParser();
        List<Map<String, String>> listaReceitas = parser.parse(conteudo.toString());

        for (Map<String, String> receita : listaReceitas) {
            for (Map.Entry<String, String> entry : receita.entrySet()) {
                System.out.println(entry.getKey() + ": " + entry.getValue());
            }
            System.out.println();
        }
    }

    public List<Map<String, String>> parse(String json) {
        ObjectMapper objectMapper = new ObjectMapper();
        return null;
    }
}