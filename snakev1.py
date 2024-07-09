import pygame
import random

# Inicjalizacja Pygame
pygame.init()

# Kolory
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Ustawienia ekranu
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Modern Snake Game")

# Ustawienia gry
GRID_SIZE = 20
SNAKE_SIZE = GRID_SIZE - 2
SPEED = 15

# Czcionka
font = pygame.font.Font(None, 36)

class Snake:
    def __init__(self):
        self.body = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (GRID_SIZE, 0)
        self.grow_pending = False

    def move(self):
        head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def grow(self):
        self.grow_pending = True

    def draw(self):
        for i, segment in enumerate(self.body):
            color = GREEN if i == 0 else (0, 200, 0)  # Głowa jest jaśniejsza
            pygame.draw.rect(screen, color, (segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE))

class Food:
    def __init__(self):
        self.position = self.randomize_position()

    def randomize_position(self):
        x = random.randint(0, (WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        return (x, y)

    def draw(self):
        pygame.draw.rect(screen, RED, (self.position[0], self.position[1], SNAKE_SIZE, SNAKE_SIZE))

def main():
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food()
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, GRID_SIZE):
                    snake.direction = (0, -GRID_SIZE)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -GRID_SIZE):
                    snake.direction = (0, GRID_SIZE)
                elif event.key == pygame.K_LEFT and snake.direction != (GRID_SIZE, 0):
                    snake.direction = (-GRID_SIZE, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-GRID_SIZE, 0):
                    snake.direction = (GRID_SIZE, 0)

        snake.move()

        # Sprawdzenie kolizji z jedzeniem
        if snake.body[0] == food.position:
            snake.grow()
            food.position = food.randomize_position()
            score += 1

        # Sprawdzenie kolizji ze ścianami
        if (snake.body[0][0] < 0 or snake.body[0][0] >= WIDTH or
            snake.body[0][1] < 0 or snake.body[0][1] >= HEIGHT):
            running = False

        # Sprawdzenie kolizji z własnym ciałem
        if snake.body[0] in snake.body[1:]:
            running = False

        # Rysowanie
        screen.fill(BLACK)
        snake.draw()
        food.draw()

        # Wyświetlanie wyniku
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(SPEED)

    pygame.quit()

if __name__ == "__main__":
    main()