import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class PortalTransparenciaAssuV1 {

    public static void main(String[] args) throws Exception {

        //licitacao tem que ser o periodo_inicial=dd/MM/YYYY&periodo_final=dd/MM/YYYY
        //contrato  tem que ser o periodo_inicial=dd/MM/YYYY&periodo_final=dd/MM/YYYY
        //pessoal tem que ser referencia=MM/YYYY
        //String[] tiposDadosAbertos = { "receita", "despesa", "despesaOrcamentaria", "licitacao", "contrato", "pessoal" };
        String[] tiposDadosAbertos = { "receita", "despesa", "despesaOrcamentaria"};

        for (String tipo : tiposDadosAbertos) {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/yyyy");

            LocalDate start = LocalDate.of(2018, 1, 1);
            LocalDate end = LocalDate.of(2023, 12, 31);

            while (start.isBefore(end)) {
                LocalDate periodStart = start;
                LocalDate periodEnd = start.plusMonths(12).minusDays(1);

                System.out.println("inicio: " + periodStart);
                System.out.println("fim: " + periodEnd);

                if (periodEnd.isAfter(end)) {
                    periodEnd = end;
                }

                String periodStartStr = periodStart.format(formatter);
                String periodEndStr = periodEnd.format(formatter);

                String period = periodStart.getMonthValue() + " a 12 - " + periodStart.getYear();
                String filename = getFileName(tipo, period);

                URL apiUrl = new URL(getApiUrl(tipo, periodStartStr, periodEndStr));
                System.out.println(apiUrl);
                HttpURLConnection conn = (HttpURLConnection) apiUrl.openConnection();
                conn.setRequestMethod("GET");

                try (BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
                    String inputLine;
                    StringBuffer response = new StringBuffer();

                    while ((inputLine = in.readLine()) != null) {
                        response.append(inputLine);
                    }

                    try (FileWriter file = new FileWriter(filename)) {
                        file.write(response.toString());
                        System.out.println("Arquivo " + filename + " criado com sucesso.");
                    } catch (IOException e) {
                        System.out.println("Falha ao criar o arquivo " + filename);
                        e.printStackTrace();
                    }
                } catch (IOException e) {
                    System.out.println("Falha ao acessar a API " + apiUrl);
                    e.printStackTrace();
                } finally {
                    conn.disconnect();
                }

                start = periodEnd.plusDays(1);
            }
        }
    }

    private static String getFileName(String tipo, String period) {
        return tipo + " - " + period + ".json";
    }

    private static String getApiUrl(String tipo, String periodStartStr, String periodEndStr) {
        return "https://transparencia.e-publica.net:443/epublica-portal/rest/assu/api/v1/" +
                tipo +
                "?periodo_inicial=" +
                periodStartStr +
                "&periodo_final=" +
                periodEndStr;
    }
}
