package project_server;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

public class TCPServer implements Runnable {

    private boolean running;
    private final ServerSocket socket;
    
    protected TCPServer(int port) throws IOException {
        running = true;
        socket = new ServerSocket(port);
    }

    @Override
    public void run() {

        //spawn new thread for each connected client
        //TODO: refit this to work for the game
        while (running) {

            if (Thread.interrupted()) {
                break;
            }

            try {
                
                Socket clientSocket = socket.accept();
                ClientHandler client = new ClientHandler(clientSocket);
                Thread clientThread = new Thread(client);
                clientThread.setDaemon(true);
                clientThread.start();

            } catch (IOException e) {
                System.err.println("failed to accept connection");
                e.printStackTrace();
            }

            running = false;
        }
    }
}
