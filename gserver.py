
import socket
import threading
import json
import time

HOST = "0.0.0.0"
PORT = 5555
BALL_COUNT = 25
BALL_STATE = {}
CLICK_COUNTS = {}
LOCKED_BY = {}
CLIENTS = []
COLORS = ["red", "green", "blue"]
PLAYER_COUNT = 3
TIMER = 45
lock = threading.Lock()
game_over = False

def broadcast_state():
    data = json.dumps({
        "type": "state",
        "ball_state": BALL_STATE,
        "click_counts": CLICK_COUNTS,
        "locked_by": LOCKED_BY
    })
    for client in CLIENTS:
        try:
            client.sendall((data + "\n").encode())
        except:
            pass

        

def send_end_game():
    result = {c: list(BALL_STATE.values()).count(c) for c in COLORS}
    data = json.dumps({"type": "end", "result": result})
    for c in CLIENTS:
        try:
            c.sendall((data + "\n").encode())
        except:
            pass

def handle_client(conn, addr, player_id):
    global game_over
    color = COLORS[player_id]
    conn.sendall((json.dumps({
        "type": "init",
        "player_id": player_id,
        "color": color
    }) + "\n").encode())

    while True:
        try:
            data = conn.recv(4096*8)
            if not data:
                break
            msg = json.loads(data.decode())
            if msg["type"] == "click":
                ball_id = msg["ball_id"]
                with lock:
                    if game_over or ball_id in BALL_STATE:
                        continue

                    if ball_id in LOCKED_BY and LOCKED_BY[ball_id] != color:
                        continue

                    if ball_id not in CLICK_COUNTS:
                        CLICK_COUNTS[ball_id] = {}

                    if ball_id not in LOCKED_BY:
                        LOCKED_BY[ball_id] = color

                    if color not in CLICK_COUNTS[ball_id]:
                        CLICK_COUNTS[ball_id][color] = 0

                    CLICK_COUNTS[ball_id][color] += 1

                    if CLICK_COUNTS[ball_id][color] >= 10:
                        BALL_STATE[ball_id] = color
                        LOCKED_BY.pop(ball_id, None)

                    broadcast_state()

                    if len(BALL_STATE) == BALL_COUNT and not game_over:
                        game_over = True
                        send_end_game()
        except:
            break

    conn.close()

def game_timer():
    global game_over
    time.sleep(TIMER)
    with lock:
        if not game_over:
            game_over = True
            send_end_game()

def main():
    print("Server started...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    for i in range(PLAYER_COUNT):
        conn, addr = s.accept()
        CLIENTS.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr, i)).start()

    # Synchronize game start
    time.sleep(1)
    for client in CLIENTS:
        try:
            client.sendall((json.dumps({"type": "start"}) + "\n").encode())
        except:
            pass

    threading.Thread(target=game_timer).start()

if __name__ == "__main__":
    main()
