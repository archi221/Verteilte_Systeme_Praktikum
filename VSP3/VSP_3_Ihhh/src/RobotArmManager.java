import org.cads.vs.roboticArm.hal.ICaDSRoboticArm;
import org.cads.vs.roboticArm.hal.simulation.CaDSRoboticArmSimulation;
import org.cads.vs.roboticArm.hal.real.CaDSRoboticArmReal;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class RobotArmManager implements Runnable {
    private final BufferedReader in;
    private final PrintWriter out;
    private final ICaDSRoboticArm arm;

    public RobotArmManager(BufferedReader in, PrintWriter out, Boolean IsSimulation, String robotIP, int robotPort) {
        this.in = in;
        this.out = out;
        if (IsSimulation) {
            this.arm =  new CaDSRoboticArmSimulation();
        } else {
            this.arm = new CaDSRoboticArmReal(robotIP, robotPort);
        }
    }

    @Override
    public void run() {
        try {
            // Die Schleife prüft zusätzlich auf Interrupts
            while (!Thread.currentThread().isInterrupted()) {
                String line = in.readLine();
                if (line == null) break; // Stream geschlossen

                processCommand(line);
            }
        } catch (IOException e) {
            if (!Thread.currentThread().isInterrupted()) {
                System.err.println("Verbindung verloren.");
            }
        } finally {
            System.out.println("RobotArmManager Thread gestoppt.");
        }
    }


    private void processCommand(String json) {
        try {
            if (json.contains("\"befehl\": \"move\"")) {
                if (json.contains("\"achse\": \"leftRight\"")) {
                    int val = extractValue(json, "wert");
                    arm.setLeftRightPercentageTo(val);

                    // Bestätigung senden
                    out.write("{\"status\": \"executed\", \"achse\": \"leftRight\", \"wert\": " + val + "}\n");
                    out.flush();

                } else if (json.contains("\"achse\": \"upDown\"")) {
                    int val = extractValue(json, "wert");
                    arm.setUpDownPercentageTo(val);

                    // Bestätigung senden
                    out.write("{\"status\": \"executed\", \"achse\": \"upDown\", \"wert\": " + val + "}\n");
                    out.flush();

                } else if (json.contains("\"achse\": \"backForth\"")) {
                    int val = extractValue(json, "wert");
                    arm.setBackForthPercentageTo(val);

                    // Bestätigung senden
                    out.write("{\"status\": \"executed\", \"achse\": \"backForth\", \"wert\": " + val + "}\n");
                    out.flush();

                } else if (json.contains("\"achse\": \"openClose\"")) {
                    int val = extractValue(json, "wert");
                    arm.setOpenClosePercentageTo(val);

                    // Bestätigung senden
                    out.write("{\"status\": \"executed\", \"achse\": \"openClose\", \"wert\": " + val + "}\n");
                    out.flush();
                }
            }
        } catch (Exception e) {
            System.err.println("Fehler beim Verarbeiten des Befehls: " + e.getMessage());
        }
    }

    // Hilfsmethode um Zahlen aus dem JSON-String zu ziehen
    private int extractValue(String json, String key) {
        String search = "\"" + key + "\":";
        int start = json.indexOf(search) + search.length();
        int end = json.indexOf(",", start);
        if (end == -1) end = json.indexOf("}", start);
        return Integer.parseInt(json.substring(start, end).replace("\"", "").trim());
    }
}