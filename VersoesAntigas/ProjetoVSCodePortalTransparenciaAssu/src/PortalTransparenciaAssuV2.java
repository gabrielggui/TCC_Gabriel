import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class PortalTransparenciaAssuV2 {

    private static final String URL_BASE = "https://transparencia.e-publica.net/epublica-portal/rest/assu/api/v1/";

    private static final List<String> tiposConsultaGrupo1 = Arrays.asList("despesa", "despesaOrcamentaria");
    private static final List<String> tiposConsultaGrupo2 = Arrays.asList(""); //Arrays.asList("licitacao", "contrato");
    private static final List<String> tiposConsultaGrupo3 = Arrays.asList("");

    public static void main(String[] args) throws Exception {

        List<String> tiposDadosAbertos = new ArrayList<>();
        tiposDadosAbertos.addAll(tiposConsultaGrupo1);
        tiposDadosAbertos.addAll(tiposConsultaGrupo2);
        tiposDadosAbertos.addAll(tiposConsultaGrupo3);

        for (String tipo : tiposDadosAbertos) {

            LocalDate start = LocalDate.of(2021, 1, 1); //LocalDate.of(2018, 1, 1);
            LocalDate end = LocalDate.now();

            while (start.isBefore(end)) {
                LocalDate periodStart = start;
                LocalDate periodEnd = start.plusMonths(12).minusDays(1);

                if (periodEnd.isAfter(end)) {
                    periodEnd = end;
                }

                String period = null;
                String fileName = null;

                URL apiUrl = null;

                if (tiposConsultaGrupo3.contains(tipo)) {
                    for (int i = 1; i <= 12; i++) {
                        LocalDate monthReference = periodEnd.withMonth(i);

                        if (monthReference.isAfter(end)) {
                            break;
                        }

                        period = monthReference.format(DateTimeFormatter.ofPattern("MM/yyyy"));
                        fileName = getFileName(tipo, period);
                        apiUrl = new URL(getApiUrl(tipo, monthReference));

                        System.out.println("Mês de referência: " + period);
                        System.out.println(apiUrl);

                        saveToJsonFile(apiUrl, fileName);
                    }
                } else {
                    System.out.println("inicio: " + periodStart);
                    System.out.println("fim: " + periodEnd);

                    period = periodStart.getMonthValue() + " a " +
                            periodEnd.getMonthValue() + " - " + periodStart.getYear();
                    fileName = getFileName(tipo, period);
                    apiUrl = new URL(getApiUrl(tipo, periodStart, periodEnd));

                    System.out.println(apiUrl);

                    saveToJsonFile(apiUrl, fileName);
                }
                start = periodEnd.plusDays(1);
            }
        }

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

        String periodStartStr;
        String periodEndStr;

        if (tiposConsultaGrupo1.contains(tipo)) {
            periodStartStr = periodStart.format(DateTimeFormatter.ofPattern("MM/yyyy"));
            periodEndStr = periodEnd.format(DateTimeFormatter.ofPattern("MM/yyyy"));
        } else if (tiposConsultaGrupo2.contains(tipo)) {
            periodStartStr = periodStart.format(DateTimeFormatter.ofPattern("dd/MM/yyyy"));
            periodEndStr = periodEnd.format(DateTimeFormatter.ofPattern("dd/MM/yyyy"));
        } else {
            throw new RuntimeException();
        }

        return URL_BASE + tipo +
                "?periodo_inicial=" + periodStartStr +
                "&periodo_final=" + periodEndStr +
                "&codigo_unidade=2";
    }

    private static String getApiUrl(String tipo, LocalDate monthReference) {

        String monthReferenceStr;

        if (tiposConsultaGrupo3.contains(tipo)) {
            monthReferenceStr = monthReference.format(DateTimeFormatter.ofPattern("MM/yyyy"));
        } else {
            throw new RuntimeException();
        }

        return URL_BASE + tipo + "?referencia=" + monthReferenceStr + "&codigo_unidade=2";
    }
}
