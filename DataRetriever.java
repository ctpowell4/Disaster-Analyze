import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.FileWriter;

public class DataRetriever {

    private static final String SUMMARY_ENDPOINT = "https://www.fema.gov/api/open/v1/FemaWebDisasterSummaries";
    private static final String DECLARATIONS_ENDPOINT = "https://www.fema.gov/api/open/v1/FemaWebDisasterDeclarations";

    public String fetchData(String endpoint) {
        StringBuilder result = new StringBuilder();

        try {
            URL url = new URL(endpoint);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));

            String line;
            while ((line = rd.readLine()) != null) {
                result.append(line);
            }
            rd.close();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return result.toString();
    }

    public static void main(String[] args) {
        DataRetriever retriever = new DataRetriever();
        String summaries = retriever.fetchData(SUMMARY_ENDPOINT);
        String declarations = retriever.fetchData(DECLARATIONS_ENDPOINT);

        // Save the fetched data to files for Python to process
        try (FileWriter summaryFile = new FileWriter("summaries.json")) {
            summaryFile.write(summaries);
        } catch (Exception e) {
            e.printStackTrace();
        }

        try (FileWriter declarationsFile = new FileWriter("declarations.json")) {
            declarationsFile.write(declarations);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
