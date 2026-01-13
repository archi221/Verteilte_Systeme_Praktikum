import org.cads.vs.roboticArm.hal.ICaDSRoboticArm;
import org.cads.vs.roboticArm.hal.simulation.CaDSRoboticArmSimulation;
import org.cads.vs.roboticArm.hal.real.CaDSRoboticArmReal;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;

public class RobotArmManager implements Runnable {
    private final BufferedReader in;
    private final PrintWriter out;
    private final ICaDSRoboticArm arm;

    public RobotArmManager(BufferedReader in, PrintWriter out, Boolean isSimulation, String robotIP, int robotPort) {
        this.in = in;
        this.out = out;
        if (isSimulation) {
            this.arm = new CaDSRoboticArmSimulation();
        } else {
            this.arm = new CaDSRoboticArmReal(robotIP, robotPort);
        }
    }

    @Override
    public void run() {
        try {
            System.out.println("RobotArmManager bereit für Befehle...");
            String line;
            // Die Schleife läuft, solange der Stream offen ist und der Thread nicht gestoppt wurde
            while (!Thread.currentThread().isInterrupted() && (line = in.readLine()) != null) {
                if (line.trim().isEmpty()) continue;
                processCommand(line);
            }
        } catch (IOException e) {
            if (!Thread.currentThread().isInterrupted()) {
                System.err.println("Verbindung zum Server verloren: " + e.getMessage());
            }
        } finally {
            System.out.println("RobotArmManager Thread gestoppt.");
        }
    }

    private void processCommand(String json) {
        try {
            // Einfache Prüfung auf Befehlstyp
            if (json.contains("\"befehl\": \"move\"") || json.contains("\"befehl\":\"move\"")) {
                String achse = "";
                int wert = extractValue(json, "wert");

                if (json.contains("\"leftRight\"")) {
                    arm.setLeftRightPercentageTo(wert);
                    achse = "leftRight";
                } else if (json.contains("\"upDown\"")) {
                    arm.setUpDownPercentageTo(wert);
                    achse = "upDown";
                } else if (json.contains("\"backForth\"")) {
                    arm.setBackForthPercentageTo(wert);
                    achse = "backForth";
                } else if (json.contains("\"openClose\"")) {
                    arm.setOpenClosePercentageTo(wert);
                    achse = "openClose";
                }

                if (!achse.isEmpty()) {
                    sendConfirmation(achse, wert);
                }
            }
        } catch (Exception e) {
            System.err.println("Fehler beim Verarbeiten: " + json + " -> " + e.getMessage());
        }
    }

    private void sendConfirmation(String achse, int wert) {
        String response = String.format("{\"status\": \"executed\", \"achse\": \"%s\", \"wert\": %d}", achse, wert);
        out.println(response); // Benutze println für automatischen Zeilenumbruch
        out.flush();
    }

    private int extractValue(String json, String key) {
        // Sucht den Key und extrahiert die Zahl dahinter, egal ob Leerzeichen dazwischen sind
        String search = "\"" + key + "\":";
        int start = json.indexOf(search) + search.length();
        int end = json.indexOf(",", start);
        if (end == -1) end = json.indexOf("}", start);

        // Entfernt alle nicht-numerischen Zeichen außer dem Minus-Zeichen
        String valText = json.substring(start, end).replaceAll("[^0-9-]", "").trim();
        return Integer.parseInt(valText);
    }
}