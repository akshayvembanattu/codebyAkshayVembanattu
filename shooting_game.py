import pygame
import random

# --- Initialization ---
pygame.init()

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
BULLET_WIDTH = 5
BULLET_HEIGHT = 15

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Game Window Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# --- Game Assets (using simple rectangles) ---
# You could replace these with images using pygame.image.load()
player_img = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
player_img.fill(GREEN)

enemy_img = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
enemy_img.fill(RED)

bullet_img = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
bullet_img.fill(BLUE)

# --- Game Clock ---
clock = pygame.time.Clock()

# --- Font for Score ---
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    """Represents the player's spaceship."""
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        """Update player position based on key presses."""
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -8
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 8
        
        self.rect.x += self.speed_x
        
        # Keep player on the screen
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        """Creates a new bullet and adds it to the sprite groups."""
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    """Represents an enemy ship."""
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 4)

    def update(self):
        """Move the enemy downwards."""
        self.rect.y += self.speed_y
        # Respawn if it moves off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 4)

class Bullet(pygame.sprite.Sprite):
    """Represents a bullet fired by the player."""
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10

    def update(self):
        """Move the bullet upwards."""
        self.rect.y += self.speed_y
        # Kill the bullet if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

def show_go_screen():
    """Displays the game over screen."""
    screen.fill(BLACK)
    title_text = font.render("GAME OVER", True, WHITE)
    instructions_text = font.render("Press any key to restart", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, SCREEN_HEIGHT/2 - 50))
    screen.blit(instructions_text, (SCREEN_WIDTH/2 - instructions_text.get_width()/2, SCREEN_HEIGHT/2 + 20))
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                waiting = False

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8): # Create 8 enemies initially
    e = Enemy()
    all_sprites.add(e)
    enemies.add(e)

# --- Game Loop ---
game_over = False
running = True
score = 0

while running:
    if game_over:
        show_go_screen()
        game_over = False
        # Reset the game
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            e = Enemy()
            all_sprites.add(e)
            enemies.add(e)
        score = 0

    # --- Process Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # --- Update ---
    all_sprites.update()

    # --- Collision Detection ---
    # Check for bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10 # Increase score for each hit
        e = Enemy() # Create a new enemy to replace the one hit
        all_sprites.add(e)
        enemies.add(e)

    # Check for player-enemy collisions
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        game_over = True

    # --- Draw / Render ---
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw the score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # --- Flip Display ---
    pygame.display.flip()

    # --- Control Frame Rate ---
    clock.tick(60)

pygame.quit()
