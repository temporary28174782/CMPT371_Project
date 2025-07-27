
import pygame
import sys
import socket
import threading
import json

WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 40
PADDING = 20
BALLS_PER_ROW = 5
BALL_COUNT = 20
ball_positions = []
ball_state = {}
click_counts = {}
player_id = None
player_color = None
winner_text = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 5555))

def listen_server():
    global ball_state, click_counts, winner_text
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
    for i, (x, y) in enumerate(ball_positions):
        color = ball_state.get(str(i), "gray")
        pygame.draw.circle(WIN, pygame.Color(color), (x, y), BALL_RADIUS)

        font = pygame.font.SysFont(None, 24)
        text = font.render(str(i+1), True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        WIN.blit(text, text_rect)

        if str(i) not in ball_state:
            count = click_counts.get(str(i), {}).get(player_color, 0)
            if count > 0:
                progress_font = pygame.font.SysFont(None, 20)
                progress_text = progress_font.render(f"{count}/10", True, (100, 100, 100))
                progress_rect = progress_text.get_rect(center=(x, y + BALL_RADIUS + 12))
                WIN.blit(progress_text, progress_rect)

    if player_color:
        font = pygame.font.SysFont(None, 36)
        turn_text = font.render(f"You are: {player_color}", True, (0, 0, 0))
        WIN.blit(turn_text, (WIDTH // 2 - 100, 20))

    if winner_text:
        font = pygame.font.SysFont(None, 48)
        text = font.render(winner_text, True, (0, 128, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        WIN.blit(text, rect)

    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not winner_text:
                mx, my = pygame.mouse.get_pos()
                for i, (x, y) in enumerate(ball_positions):
                    if str(i) in ball_state:
                        continue
                    if (mx - x) ** 2 + (my - y) ** 2 <= BALL_RADIUS ** 2:
                        msg = json.dumps({"type": "click", "ball_id": i})
                        client.sendall(msg.encode())
                        break

if __name__ == "__main__":
    main()
