import pygame
import random
import sys
import json
from abc import ABC, abstractmethod

# Inicjalizacja Pygame
pygame.init()

# Kolory
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Ustawienia ekranu
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Snake Game")

# Ustawienia gry
GRID_SIZE = 20
SNAKE_SIZE = GRID_SIZE - 2
SPEED = 15

# Czcionki
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

class GameObject(ABC):
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

class ParticleSystem(GameObject):
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, color):
        self.particles.append({"pos": [x, y], "vel": [random.uniform(-1, 1), random.uniform(-1, 1)], "timer": 30, "color": color})

    def update(self):
        for particle in self.particles:
            particle["pos"][0] += particle["vel"][0]
            particle["pos"][1] += particle["vel"][1]
            particle["timer"] -= 1
        self.particles = [p for p in self.particles if p["timer"] > 0]

    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.circle(screen, particle["color"], [int(particle["pos"][0]), int(particle["pos"][1])], 2)

class BackgroundManager(GameObject):
    def __init__(self):
        self.stars = []
        self.color = BLACK
        for _ in range(100):
            self.stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)])

    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, WIDTH)

    def draw(self, screen):
        screen.fill(self.color)
        for star in self.stars:
            pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[2])

    def change_background(self, score):
        if score < 10:
            self.color = BLACK
        elif score < 20:
            self.color = (0, 0, 50)  # Dark blue
        elif score < 30:
            self.color = (50, 0, 50)  # Dark purple
        else:
            self.color = (50, 0, 0)  # Dark red

class Snake(GameObject):
    def __init__(self, color=GREEN):
        self.reset()
        self.color = color

    def reset(self):
        self.body = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (GRID_SIZE, 0)
        self.grow_pending = False

    def update(self):
        head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def grow(self):
        self.grow_pending = True

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            color = self.color if i == 0 else tuple(max(0, c - 50) for c in self.color)
            pygame.draw.rect(screen, color, (segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE))

class Food(GameObject):
    def __init__(self):
        self.position = self.randomize_position()

    def randomize_position(self):
        x = random.randint(0, (WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        return (x, y)

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.position[0], self.position[1], SNAKE_SIZE, SNAKE_SIZE))

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.particle_system = ParticleSystem()
        self.background_manager = BackgroundManager()
        self.score = 0
        self.high_score = self.load_high_score()
        self.coins = self.load_coins()
        self.available_colors = {
            "Green": {"color": GREEN, "price": 0},
            "Blue": {"color": BLUE, "price": 50},
            "Yellow": {"color": YELLOW, "price": 100},
            "Purple": {"color": PURPLE, "price": 200}
        }
        self.unlocked_colors = self.load_unlocked_colors()

    def reset(self):
        self.snake.reset()
        self.food = Food()
        self.score = 0

    def update(self):
        self.snake.update()
        self.food.update()
        self.particle_system.update()
        self.background_manager.update()
        self.background_manager.change_background(self.score)

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food = Food()
            self.score += 1
            self.coins += 1
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.save_coins()
            self.particle_system.add_particle(self.food.position[0] + SNAKE_SIZE // 2, self.food.position[1] + SNAKE_SIZE // 2, RED)

        if self.check_collision():
            return False
        return True

    def check_collision(self):
        head = self.snake.body[0]
        return (head[0] < 0 or head[0] >= WIDTH or
                head[1] < 0 or head[1] >= HEIGHT or
                head in self.snake.body[1:])

    def draw(self):
        self.background_manager.draw(screen)
        self.snake.draw(screen)
        self.food.draw(screen)
        self.particle_system.draw(screen)
        self.draw_score()

    def draw_score(self):
        score_text = font_small.render(f"Score: {self.score}", True, WHITE)
        high_score_text = font_small.render(f"High Score: {self.high_score}", True, WHITE)
        coins_text = font_small.render(f"Coins: {self.coins}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))
        screen.blit(coins_text, (10, 40))

    def load_high_score(self):
        return self.load_game_data().get("high_score", 0)

    def save_high_score(self):
        data = self.load_game_data()
        data["high_score"] = self.high_score
        self.save_game_data(data)

    def load_coins(self):
        return self.load_game_data().get("coins", 0)

    def save_coins(self):
        data = self.load_game_data()
        data["coins"] = self.coins
        self.save_game_data(data)

    def load_unlocked_colors(self):
        return self.load_game_data().get("unlocked_colors", ["Green"])

    def save_unlocked_colors(self):
        data = self.load_game_data()
        data["unlocked_colors"] = self.unlocked_colors
        self.save_game_data(data)

    def load_game_data(self):
        try:
            with open("game_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_game_data(self, data):
        with open("game_data.json", "w") as file:
            json.dump(data, file)

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def start_screen(game):
    clock = pygame.time.Clock()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_s:
                    shop_screen(game)

        game.background_manager.update()
        game.background_manager.draw(screen)

        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128)) 
        screen.blit(s, (0, 0))

        # Rysowanie tekstu
        draw_text("Snake Game", font_large, GREEN, WIDTH // 2, HEIGHT // 4)
        draw_text("Press SPACE to Start", font_medium, WHITE, WIDTH // 2, HEIGHT // 2)
        draw_text("Press S for Shop", font_medium, YELLOW, WIDTH // 2, HEIGHT * 3 // 4)
        draw_text(f"High Score: {game.high_score}", font_small, GRAY, WIDTH // 2, HEIGHT * 5 // 6)

        pygame.display.flip()
        clock.tick(60) 

def game_over_screen(game):
    game.background_manager.draw(screen)
    draw_text("Game Over", font_large, RED, WIDTH // 2, HEIGHT // 3)
    draw_text(f"Score: {game.score}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text("Press SPACE to Play Again", font_small, GRAY, WIDTH // 2, HEIGHT * 2 // 3)
    draw_text("Press S for Shop", font_small, YELLOW, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_s:
                    shop_screen(game)
        game.background_manager.update()
        game.background_manager.draw(screen)
        pygame.display.flip()

def shop_screen(game):
    selected = 0
    while True:
        game.background_manager.draw(screen)
        draw_text("Snake Color Shop", font_large, YELLOW, WIDTH // 2, HEIGHT // 6)
        draw_text(f"Coins: {game.coins}", font_medium, YELLOW, WIDTH // 2, HEIGHT // 4)

        for i, (color_name, color_data) in enumerate(game.available_colors.items()):
            color = color_data["color"]
            price = color_data["price"]
            if i == selected:
                pygame.draw.rect(screen, WHITE, (WIDTH // 4 - 10, HEIGHT // 3 + i * 60 - 5, WIDTH // 2 + 20, 50), 2)
            
            if color_name in game.unlocked_colors:
                text = f"{color_name} (Unlocked)"
            else:
                text = f"{color_name} - {price} coins"
            
            draw_text(text, font_small, color, WIDTH // 2, HEIGHT // 3 + i * 60)

        draw_text("Press SPACE to select, ESC to return", font_small, GRAY, WIDTH // 2, HEIGHT * 5 // 6)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(game.available_colors)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(game.available_colors)
                elif event.key == pygame.K_SPACE:
                    color_name = list(game.available_colors.keys())[selected]
                    if color_name not in game.unlocked_colors:
                        if game.coins >= game.available_colors[color_name]["price"]:
                            game.coins -= game.available_colors[color_name]["price"]
                            game.unlocked_colors.append(color_name)
                            game.save_coins()
                            game.save_unlocked_colors()
                    game.snake.color = game.available_colors[color_name]["color"]
                elif event.key == pygame.K_ESCAPE:
                    return
        game.background_manager.update()
        game.background_manager.draw(screen)
        pygame.display.flip()

def main():
    game = Game()
    clock = pygame.time.Clock()

    while True:
        start_screen(game)
        game.reset()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and game.snake.direction != (0, GRID_SIZE):
                        game.snake.direction = (0, -GRID_SIZE)
                    elif event.key == pygame.K_DOWN and game.snake.direction != (0, -GRID_SIZE):
                        game.snake.direction = (0, GRID_SIZE)
                    elif event.key == pygame.K_LEFT and game.snake.direction != (GRID_SIZE, 0):
                        game.snake.direction = (-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and game.snake.direction != (-GRID_SIZE, 0):
                        game.snake.direction = (GRID_SIZE, 0)
                    elif event.key == pygame.K_p:
                        pause_game(game, clock)

            running = game.update()
            game.draw()
            pygame.display.flip()
            clock.tick(SPEED)

        game_over_screen(game)

def pause_game(game, clock):
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False

        game.background_manager.draw(screen)
        draw_text("PAUSED", font_large, WHITE, WIDTH // 2, HEIGHT // 2)
        draw_text("Press P to continue", font_medium, GRAY, WIDTH // 2, HEIGHT * 2 // 3)
        pygame.display.flip()
        clock.tick(15)

if __name__ == "__main__":
    main()