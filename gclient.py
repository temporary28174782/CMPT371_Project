# Imports
import pygame
import sys
import socket
import threading
import json
import time

# Global Variables
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 40
PADDING = 30
BALLS_PER_ROW = 5
BALL_COUNT = 25
ball_positions = []
ball_state = {}
click_counts = {}
locked_by = {}
player_id = None
player_color = None
winner_text = None
game_end_time = None
game_started = False
timer = 45

# Socket Initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = input("Enter the server IP address: ")
client.connect((server_ip, 5555))

# Listens to the server and interporate message type
def listen_server():
    global ball_state, click_counts, locked_by, winner_text, game_end_time, game_started
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            msg = json.loads(data.decode())
            if msg["type"] == "init":
                global player_id, player_color
                player_id = msg["player_id"]
                player_color = msg["color"]
            elif msg["type"] == "state":
                ball_state = msg["ball_state"]
                click_counts = msg.get("click_counts", {})
                locked_by = msg.get("locked_by", {})
            elif msg["type"] == "start":
                game_started = True
                game_end_time = time.time() + timer
            elif msg["type"] == "end":
                result = msg["result"]
                max_score = max(result.values())
                winners = [color for color, score in result.items() if score == max_score]
                if len(winners) == 1:
                    winner_text = f"{winners[0].capitalize()} wins!"
                else:
                    winner_text = "It's a tie!"
        except:
            break

threading.Thread(target=listen_server, daemon=True).start()

# Begin the gameplay
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Game")

for i in range(BALL_COUNT):
    row = i // BALLS_PER_ROW
    col = i % BALLS_PER_ROW
    x = 100 + col * (BALL_RADIUS * 2 + PADDING)
    y = 100 + row * (BALL_RADIUS * 2 + PADDING)
    ball_positions.append((x, y))

def draw():
    WIN.fill((255, 255, 255))

    if not game_started:
        font = pygame.font.SysFont(None, 48)
        text = font.render("Waiting for other players...", True, (100, 100, 100))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        WIN.blit(text, rect)
        pygame.display.update()
        return

    # Draw the Board
    for i, (x, y) in enumerate(ball_positions):
        str_i = str(i)
        color = ball_state.get(str_i, "gray")
        pygame.draw.circle(WIN, pygame.Color(color), (x, y), BALL_RADIUS)

        font = pygame.font.SysFont(None, 24)
        text = font.render(str(i+1), True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        WIN.blit(text, text_rect)

        if str_i not in ball_state:
            count = click_counts.get(str_i, {}).get(player_color, 0)
            if count > 0:
                progress_font = pygame.font.SysFont(None, 20)
                progress_text = progress_font.render(f"{count}/10", True, (100, 100, 100))
                progress_rect = progress_text.get_rect(center=(x, y + BALL_RADIUS + 12))
                WIN.blit(progress_text, progress_rect)

            locked = locked_by.get(str_i)
            if locked and locked != player_color:
                lock_font = pygame.font.SysFont(None, 20)
                lock_text = lock_font.render("LOCKED", True, (255, 0, 0))
                lock_rect = lock_text.get_rect(center=(x, y - BALL_RADIUS - 10))
                WIN.blit(lock_text, lock_rect)

    if player_color:
        font = pygame.font.SysFont(None, 36)
        turn_text = font.render(f"You are: {player_color}", True, (0, 0, 0))
        WIN.blit(turn_text, (20, 20))

    if game_end_time and not winner_text:
        remaining = max(0, int(game_end_time - time.time()))
        timer_font = pygame.font.SysFont(None, 36)
        timer_text = timer_font.render(f"Time left: {remaining}s", True, (0, 0, 255))
        WIN.blit(timer_text, (WIDTH - 200, 20))

    if winner_text:
        font = pygame.font.SysFont(None, 48)
        text = font.render(winner_text, True, (0, 128, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        WIN.blit(text, rect)

    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    winner_display_time = None  # Track when winner text was first shown

    while True:
        clock.tick(60)
        draw()

        # Start the timer once winner text is shown
        if winner_text and winner_display_time is None:
            winner_display_time = time.time()

        # Wait 3 seconds after showing winner before exiting
        if winner_display_time and time.time() - winner_display_time >= 3:
            pygame.time.delay(3000)  # Optional: for smoother UI during delay
            pygame.quit()
            client.close()
            sys.exit()

        for event in pygame.event.get():
            draw()
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                sys.exit()
            if game_started and event.type == pygame.MOUSEBUTTONDOWN and not winner_text:
                mx, my = pygame.mouse.get_pos()
                for i, (x, y) in enumerate(ball_positions):
                    str_i = str(i)
                    if str_i in ball_state:
                        continue
                    if str_i in locked_by and locked_by[str_i] != player_color:
                        continue
                    if (mx - x) ** 2 + (my - y) ** 2 <= BALL_RADIUS ** 2:
                        msg = json.dumps({"type": "click", "ball_id": i})
                        client.sendall(msg.encode())
                        break

if __name__ == "__main__":
    main()
