import org.cads.vs.roboticArm.hal.ICaDSRoboticArm;
import org.cads.vs.roboticArm.hal.simulation.CaDSRoboticArmSimulation;
import org.cads.vs.roboticArm.hal.real.CaDSRoboticArmReal;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class RobotArmManager implements Runnable {
    private final ICaDSRoboticArm arm;
    private final int serverPort;
    private boolean running = true;
    private final ExecutorService threadPool = Executors.newCachedThreadPool();

    public RobotArmManager(int serverPort, boolean isSimulation, String robotIP, int robotPort) {
        this.serverPort = serverPort;
        if (isSimulation) {
            this.arm = new CaDSRoboticArmSimulation();
        } else {
            this.arm = new CaDSRoboticArmReal(robotIP, robotPort);
        }
    }

    @Override
    public void run() {
        try (ServerSocket serverSocket = new ServerSocket(serverPort)) {
            System.out.println("Paralleler RobotArmServer gestartet auf Port " + serverPort);

            while (running && !Thread.currentThread().isInterrupted()) {
                try {
                    Socket clientSocket = serverSocket.accept();
                    System.out.println("Neuer Client verbunden: " + clientSocket.getInetAddress());
                    threadPool.execute(() -> handleClient(clientSocket));

                } catch (IOException e) {
                    if (running) System.err.println("Fehler bei Verbindungsannahme: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Server-Fehler: " + e.getMessage());
        } finally {
            threadPool.shutdown();
            System.out.println("RobotArmManager gestoppt.");
        }
    }

    private void handleClient(Socket socket) {
        try (socket;
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {

            String line;
            while ((line = in.readLine()) != null) {
                if (line.trim().isEmpty()) continue;
                processCommand(line, out);
            }
        } catch (IOException e) {
            System.err.println("Verbindung zu Client " + socket.getInetAddress() + " verloren.");
        }
        System.out.println("Verbindung beendet: " + socket.getInetAddress());
    }

    private void processCommand(String json, PrintWriter out) {
        try {
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
                } else {
                    String response = String.format("{\"befehl\": \"error\", \"code\": \"unbekannter befehl\"}");
                    out.println(response);
                }

                if (!achse.isEmpty()) {
                    sendConfirmation(achse, wert, out);
                }
            }
        } catch (Exception e) {
            System.err.println("Fehler beim Verarbeiten: " + json + " -> " + e.getMessage());
        }
    }

    private void sendConfirmation(String achse, int wert, PrintWriter out) {
        String response = String.format("{\"befehl\": \"executed\", \"achse\": \"%s\", \"wert\": %d}", achse, wert);
        out.println(response);
    }

    private int extractValue(String json, String key) {
        String search = "\"" + key + "\":";
        int start = json.indexOf(search) + search.length();
        int end = json.indexOf(",", start);
        if (end == -1) end = json.indexOf("}", start);
        String valText = json.substring(start, end).replaceAll("[^0-9-]", "").trim();
        return Integer.parseInt(valText);
    }

    public void stop() {
        this.running = false;
        threadPool.shutdownNow();
    }
}