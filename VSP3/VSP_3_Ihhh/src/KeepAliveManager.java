import java.io.PrintWriter;

public class KeepAliveManager {
    private Thread workerThread;

    /**
     * Startet den Heartbeat-Thread.
     * @param out Der PrintWriter des Sockets
     */
    public void start(PrintWriter out) {
        stop();

        workerThread = new Thread(() -> {
            System.out.println("Keep-Alive Thread gestartet.");
            try {
                while (!Thread.currentThread().isInterrupted()) {

                    out.println("{\"befehl\": \"Im Alive\"}");
                    out.flush();

                    Thread.sleep(500);
                }
            } catch (InterruptedException e) {
                System.out.println("Keep-Alive Thread wurde durch Interrupt gestoppt.");
            }
        });

        workerThread.setDaemon(true);
        workerThread.start();
    }

    /**
     * Stoppt den Thread sofort.
     */
    public void stop() {
        if (workerThread != null && workerThread.isAlive()) {
            workerThread.interrupt(); // Das löst die InterruptedException aus
        }
    }
}
