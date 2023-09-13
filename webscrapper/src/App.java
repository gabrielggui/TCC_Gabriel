import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;

public class App {

    private static final String URL_BASE = "https://transparencia.e-publica.net/epublica-portal/rest/assu/api/v1/";

    public static void main(String[] args) throws Exception {

        Arrays.asList("despesa", "despesaOrcamentaria").parallelStream().forEach(tipo -> {

            LocalDate start = LocalDate.of(LocalDate.now().minusYears(5).getYear(), 1, 1);
            LocalDate end = LocalDate.now();

            while (start.isBefore(end)) {
                LocalDate periodStart = start;
                LocalDate periodEnd = start.plusMonths(12).minusDays(1);

                if (periodEnd.isAfter(end)) {
                    periodEnd = end;
                }

                String period = periodStart.getMonthValue() + " a " +
                        periodEnd.getMonthValue() + " - " + periodStart.getYear();
                String fileName = getFileName(tipo, period);

                URL apiUrl = null;

                try {
                    apiUrl = new URL(getApiUrl(tipo, periodStart, periodEnd));
                } catch (MalformedURLException e) {
                    e.printStackTrace();
                }

                System.out.println("inicio: " + periodStart + "\n"
                        + "fim: " + periodEnd + "\n"
                        + apiUrl);

                saveToJsonFile(apiUrl, fileName);

                start = periodEnd.plusDays(1);
            }
        });
    }

    private static void saveToJsonFile(URL url, String fileName) {
        HttpURLConnection conn = null;
        fileName = fileName.replace("/", "");

        try {
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            try (BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
                String inputLine;
                StringBuffer response = new StringBuffer();

                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }

                try (FileWriter file = new FileWriter(fileName)) {
                    file.write(response.toString());
                    System.out.println("Arquivo " + fileName + " criado com sucesso.");
                } catch (IOException e) {
                    System.out.println("Falha ao criar o arquivo " + fileName);
                    e.printStackTrace();
                }
            } catch (IOException e) {
                System.out.println("Falha ao ler o InputStream");
                e.printStackTrace();
            }
        } catch (IOException e) {
            System.out.println("Falha ao acessar a API " + url);
            e.printStackTrace();
        } finally {
            conn.disconnect();
        }
    }

    private static String getFileName(String tipo, String period) {
        return tipo + " - " + period + ".json";
    }

    private static String getApiUrl(String tipo, LocalDate periodStart, LocalDate periodEnd) {
        String periodStartStr = periodStart.format(DateTimeFormatter.ofPattern("MM/yyyy"));
        String periodEndStr = periodEnd.format(DateTimeFormatter.ofPattern("MM/yyyy"));

        return URL_BASE + tipo +
                "?periodo_inicial=" + periodStartStr +
                "&periodo_final=" + periodEndStr +
                "&codigo_unidade=2";
    }

}
