import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadow Ninja")

# Load images
current_dir = os.path.dirname(__file__)
catninja_img = pygame.image.load(os.path.join(current_dir, "catninja.jpg"))
boss_img = pygame.image.load(os.path.join(current_dir, "boss.png"))
ninja_star_img = pygame.image.load(os.path.join(current_dir, "ninja_star.jpg"))
dojo_bg = pygame.image.load(os.path.join(current_dir, "dojo_bg.jpg"))

# Resize images
catninja_img = pygame.transform.scale(catninja_img, (50, 50))
boss_img = pygame.transform.scale(boss_img, (100, 100))
ninja_star_img = pygame.transform.scale(ninja_star_img, (20, 20))
dojo_bg = pygame.transform.scale(dojo_bg, (WIDTH, HEIGHT))

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Player settings
player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - player_height - 10
player_speed = 5
player_health = 100
player_exp = 0
player_velocity_y = 0
gravity = 0.8
jump_strength = -15
is_jumping = False

# Platforms
platforms = [
    pygame.Rect(0, HEIGHT - 50, WIDTH, 50),  # Ground
    pygame.Rect(200, 400, 200, 20),
    pygame.Rect(500, 300, 200, 20),
    pygame.Rect(100, 200, 200, 20),
]

# Ninja star settings
ninja_stars = []
ninja_star_speed = 10
ninja_star_cooldown = 0

# Boss settings
boss_health = 100
boss_max_health = 100
boss_x, boss_y = WIDTH // 2, 50
boss_speed = 3
boss_fireballs = []
boss_size_increase = 1.2  # Boss gets bigger each level

# Game states
game_over = False
level = 1

# Clock
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 24)

def draw_player(x, y):
    screen.blit(catninja_img, (x, y))

def draw_ninja_stars(stars):
    for star in stars:
        screen.blit(ninja_star_img, (star[0], star[1]))

def draw_boss(x, y, size):
    scaled_boss_img = pygame.transform.scale(boss_img, (int(100 * size), int(100 * size)))
    screen.blit(scaled_boss_img, (x, y))

def draw_fireballs(fireballs):
    for fireball in fireballs:
        pygame.draw.rect(screen, RED, (fireball[0], fireball[1], 20, 20))

def draw_health_bar(health, max_health, x, y, width, height):
    ratio = health / max_health
    pygame.draw.rect(screen, RED, (x, y, width, height))
    pygame.draw.rect(screen, GREEN, (x, y, width * ratio, height))

def check_collision(player_x, player_y, player_width, player_height, obj_x, obj_y, obj_width, obj_height):
    if (player_x < obj_x + obj_width and player_x + player_width > obj_x and
            player_y < obj_y + obj_height and player_y + player_height > obj_y):
        return True
    return False

def game_over_screen():
    screen.fill(BLACK)
    text = font.render("Game Over! Press R to Restart", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
    pygame.display.update()

def reset_game():
    global player_x, player_y, player_health, player_exp, ninja_stars, boss_health, boss_fireballs, game_over, level, boss_size_increase
    player_x, player_y = WIDTH // 2, HEIGHT - player_height - 10
    player_health = 100
    player_exp = 0
    ninja_stars = []
    boss_health = 100
    boss_fireballs = []
    game_over = False
    level = 1
    boss_size_increase = 1.2

# Main game loop
running = True
while running:
    screen.blit(dojo_bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_a] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_d] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Jumping
        if keys[pygame.K_w] and not is_jumping:
            player_velocity_y = jump_strength
            is_jumping = True

        # Apply gravity
        player_velocity_y += gravity
        player_y += player_velocity_y

        # Check for platform collisions
        for platform in platforms:
            if (player_x < platform.x + platform.width and player_x + player_width > platform.x and
                    player_y + player_height > platform.y and player_y + player_height - player_velocity_y <= platform.y):
                player_y = platform.y - player_height
                player_velocity_y = 0
                is_jumping = False

        # Shooting ninja stars
        if keys[pygame.K_SPACE] and ninja_star_cooldown <= 0:
            ninja_stars.append([player_x + player_width // 2, player_y])
            ninja_star_cooldown = 20

        # Update ninja stars
        for star in ninja_stars:
            star[1] -= ninja_star_speed
            if star[1] < 0:
                ninja_stars.remove(star)

        # Boss movement
        boss_x += boss_speed
        if boss_x <= 0 or boss_x >= WIDTH - 100 * boss_size_increase:
            boss_speed *= -1

        # Boss fireballs
        if random.randint(1, 100) == 1:
            boss_fireballs.append([boss_x + 50 * boss_size_increase, boss_y + 100 * boss_size_increase])

        # Update fireballs
        for fireball in boss_fireballs:
            fireball[1] += 5
            if fireball[1] > HEIGHT:
                boss_fireballs.remove(fireball)

        # Check for collisions
        for star in ninja_stars:
            if check_collision(star[0], star[1], 20, 20, boss_x, boss_y, 100 * boss_size_increase, 100 * boss_size_increase):
                boss_health -= 10
                ninja_stars.remove(star)
                if boss_health <= 0:
                    player_exp += 50
                    level += 1
                    boss_health = boss_max_health
                    boss_size_increase *= 1.2  # Boss gets bigger

        for fireball in boss_fireballs:
            if check_collision(player_x, player_y, player_width, player_height, fireball[0], fireball[1], 20, 20):
                player_health -= 10
                boss_fireballs.remove(fireball)
                if player_health <= 0:
                    game_over = True

        # Draw everything
        for platform in platforms:
            pygame.draw.rect(screen, GREEN, platform)

        draw_player(player_x, player_y)
        draw_ninja_stars(ninja_stars)
        draw_boss(boss_x, boss_y, boss_size_increase)
        draw_fireballs(boss_fireballs)

        # Draw health bars
        draw_health_bar(player_health, 100, 10, 10, 200, 20)
        draw_health_bar(boss_health, boss_max_health, WIDTH // 2 - 100, 10, 200, 20)

        # Display EXP and level
        exp_text = font.render(f"EXP: {player_exp}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(exp_text, (10, 40))
        screen.blit(level_text, (10, 70))

        # Cooldown for ninja stars
        if ninja_star_cooldown > 0:
            ninja_star_cooldown -= 1

    else:
        game_over_screen()
        if keys[pygame.K_r]:
            reset_game()

    pygame.display.update()
    clock.tick(30)

pygame.quit()