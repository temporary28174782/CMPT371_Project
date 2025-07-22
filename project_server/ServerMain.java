package project_server;

import java.io.IOException;

public class ServerMain {

    /**
     * starts the server, launches connection listener thread
     * @param args boilerplate args
     */
    public static void main(String[] args) {
        try {

            TCPServer serverInstance = new TCPServer(Constants.SERVER_PORT);
            Thread serverThread = new Thread(serverInstance);
            serverThread.setDaemon(true);
            serverThread.start();

            try {
                serverThread.join();
            } catch (InterruptedException e) {
                System.err.println("main user thread interrupted");
                e.printStackTrace();
            }

        } catch (IOException e) {
            System.err.println("Failed to start server instance");
            e.printStackTrace();
        }
    }
}
