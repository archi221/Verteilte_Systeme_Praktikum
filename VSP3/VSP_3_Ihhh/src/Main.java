import java.io.*;
import java.net.*;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {

        Config config = askForConnectionSettings();
        String serverAdress = "127.0.0.1";
        int serverPort = 7777;

        connect_to_server(config, serverAdress, serverPort);
        System.out.println("Programm beendet.");
    }

    public static class Config {
        String ip;
        int port;
        String nodeName;
    }

    public static Config askForConnectionSettings() {
        Scanner scanner = new Scanner(System.in);
        Config config = new Config();

        System.out.println("=== Robot Arm Node Setup ===");

        System.out.print("Geben Sie die IP-Adresse des Servers/Roboters ein (z.B. 127.0.0.1): ");
        config.ip = scanner.nextLine();
        if (config.ip.isEmpty()) config.ip = "127.0.0.1"; // Default

        while (true) {
            System.out.print("Geben Sie den Port ein (z.B. 5555): ");
            String portInput = scanner.nextLine();
            try {
                config.port = Integer.parseInt(portInput);
                break; // Erfolgreich geparst
            } catch (NumberFormatException e) {
                System.out.println("Ungültige Eingabe! Bitte geben Sie eine Zahl für den Port ein.");
            }
        }

        System.out.print("Geben Sie den Namen für diesen Node ein: ");
        config.nodeName = scanner.nextLine();
        if (config.nodeName.isEmpty()) config.nodeName = "RobotNode_" + (int)(Math.random() * 100);

        System.out.println("Konfiguration übernommen: " + config.nodeName + " verbindet zu " + config.ip + ":" + config.port);
        System.out.println("-------------------------------------------");

        return config;
    }

    public static void connect_to_server(Config config, String serverAddress, int ServerPort) {
        KeepAliveManager keepAlive = new KeepAliveManager();

        try (Socket socket = new Socket(serverAddress, ServerPort);
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {

            String myIP = socket.getLocalAddress().getHostAddress();
            int myPort = socket.getLocalPort();

            String answer = "";
            int counter = 0;
            String baseName = config.nodeName; // Den ursprünglichen Namen speichern

            do {
                // Falls counter > 0, hänge die Zahl an den Basisnamen an
                String currentName = (counter == 0) ? baseName : baseName + counter;

                String jsonRegistration = String.format(
                        "{\"befehl\": \"register\", \"clientName\": \"%s\", \"ip\": \"%s\", \"port\": %d , \"type\": \"node\"}",
                        currentName, myIP, myPort
                );

                System.out.println("Sende Registrierung (Versuch " + (counter + 1) + "): " + jsonRegistration);
                out.println(jsonRegistration);
                out.flush();
                answer = in.readLine();

                if (!"{\"befehl\": \"Ok\"}".equals(answer)) {
                    System.out.println("Fehler beim Registrieren. Probiere nächsten Namen...");
                    counter++; // Erhöhe die Zahl für den nächsten Durchgang
                }
            } while(answer == null || !answer.equals("{\"befehl\": \"Ok\"}"));

            config.nodeName =  (counter == 0 ? baseName : baseName + counter);
            System.out.println("Erfolgreich registriert als: " + config.nodeName);

            // 2. Keep-Alive starten
            keepAlive.start(out);

            Thread armThread = new Thread(new RobotArmManager(in, out, true, config.ip, config.port));
            armThread.start();

            System.out.println("Verbunden. Drücke ENTER zum Abmelden...");
            Scanner sc = new Scanner(System.in);
            sc.nextLine(); // Das Programm bleibt hier stehen, bis du ENTER drückst

        // Erst wenn der User ENTER drückt, wird der Rest ausgeführt:
            keepAlive.stop();
            armThread.interrupt();
            out.println("{\"befehl\": \"dead\"}");
            out.flush();

        } catch (IOException e) {
            System.err.println("Netzwerkfehler: " + e.getMessage());
            keepAlive.stop();
        }
    }
}