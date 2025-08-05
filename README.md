# Project: Click-Conquer

Click-Conquer is a real-time, online multiplayer game where players compete to capture the most balls on the screen within a time limit. This project focuses on low-level client-server programming using raw sockets.

## Features

* **Online Multiplayer:** Supports multiple players connecting to a central server from remote machines.
* **Real-Time Gameplay:** Game state is synchronized across all clients in real-time.
* **Concurrency Control:** Implements a locking mechanism for shared objects (the balls), ensuring only one player can attempt to capture a ball at a time.
* **Low Level Implementation:** The client-server communication directly utilizes Python's `socket` library, without any high-level networking or gaming frameworks.

## Tech Description

* **Language:** Python 3
* **Graphics/Frontend:** Pygame library
* **Networking:** Standard Python `socket` library for TCP communication.
* **Data Serialization:** JSON for application-layer messaging.

## Prerequisites

* Python 3.x must be installed.
* The `pygame` library is required. Install it via pip:
    ```bash
    pip install pygame
    ```
* Or anaconda: 
    ```
    conda install conda-forge::pygame
    ```

## How to Run the Game

### 1. For the Server Host: Port Forwarding

For others on the internet to connect to your server, the host must allow **port forwarding** on their router.

* You must create a rule to forward **TCP** traffic on port **5555** to the **private (link-local) IP address** of the machine running the server.
* For best results, have all players on the same LAN, this obviates the need for port forwarding and minimizes latency.

### 2. Start the Server

The person hosting the game can simply run the server script.

```bash
python gserver.py
```

To obtain the server IP address, use the native terminal utility (ipconfig on windows) and relay this address to all players.
**Note that only IPv4 addresses are supported.**

### 3. Start the Client(s)

Each player (including the server host, if they wish to play) must run the client script.

```bash
python gclient.py
```

The client application will launch and prompt for the server's IP address in the console.
1.  Enter the private (link-local) IP address provided by the server host, using ipconfig in the terminal.
2.  Press Enter.
3.  The Pygame window will appear, and the game will begin once all players have connected.

## Gameplay Instructions

* **Objective:** Capture more balls than any other player before the timer at the top right runs out.
* **Your Color:** Your assigned player color is shown at the top-left of the screen.
* **Locking a Ball:** To capture a gray ball, click on it. The first player to click a ball **locks** it. A "LOCKED" message will appear above the ball for other players, and they will be unable to interact with it.
* **Capturing a Ball:** Once you have locked a ball, you must click it a total of **10 times** to capture it. A progress counter (`x/10`) will appear below the ball.
* **Winning:** When the 45-second timer ends or when all balls are claimed, the player whose color appears on the most balls is declared the winner!
