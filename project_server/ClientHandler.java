package project_server;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;

public class ClientHandler implements Runnable {
    
    boolean running;
    private final Socket client;

    protected ClientHandler(Socket incoming) {
        running = true;
        client = incoming;
    }

    @Override
    public void run() {

        //open connections
        OutputStream upStream;
        InputStream downStream;

        try {
            upStream = client.getOutputStream();
        } catch (IOException e) {
            System.err.println("unable to get output stream from client socket");
            return;
        }

        try {
            downStream = client.getInputStream();
        } catch (IOException e) {
            System.err.println("unable to get input stream from client socket");
            try {
                upStream.close();
            } catch (IOException e1) {
                System.err.println("real bad stuff happening");
            }
            return;
        }

        PrintWriter send = new PrintWriter(upStream, true);
        BufferedReader receive = new BufferedReader(new InputStreamReader(downStream));

        //TODO: refit this to work for the game
        while (running) {

            if (Thread.interrupted()) {
                break;
            }

            running = false;
        }

        //clean up
        send.close();
        try {
            receive.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            client.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
