import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")

wave = 100
attack_speed = 1000
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
money = 0  
FPS = 60
clock = pygame.time.Clock()
enemies_spawned = 0
enemies_to_spawn = 0
font = pygame.font.Font(None, 40)

SHOOT_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHOOT_EVENT, attack_speed)

show_upgrade_panel = False  

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("graphics/player.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (int(WIDTH * 0.06), int(HEIGHT * 0.13)))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.angle = 0

    def update(self, enemy=None):
        if enemy:
            rel_x, rel_y = enemy.rect.x - self.rect.centerx, enemy.rect.y - self.rect.centery
            self.angle = (math.degrees(math.atan2(-rel_y, rel_x))) - 90
        else:
            self.angle = 0

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("graphics/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(WIDTH * 0.03), int(HEIGHT * 0.03)))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 1

    def update(self):
        self.rect.y += self.speed
        screen.blit(self.image, self.rect)
        if self.rect.y > HEIGHT:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target):
        super().__init__()
        self.image = pygame.image.load("graphics/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(HEIGHT * 0.02), int(WIDTH * 0.02)))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.speed = 5

        if target:
            target_vector = pygame.Vector2(target.rect.center)
            self.direction = (target_vector - self.pos).normalize()
        else:
            self.direction = pygame.Vector2(0, -1)  

        self.target = target

    def update(self):
        global money
        if not self.target or not self.target.alive():
            self.pos += self.direction * self.speed
        else:
            target_vector = pygame.Vector2(self.target.rect.center)
            self.direction = (target_vector - self.pos).normalize()
            self.pos += self.direction * self.speed

        self.rect.center = self.pos

        if self.rect.y < -100:
            self.kill()

        if self.target and pygame.sprite.collide_rect(self, self.target):
            self.kill()  
            self.target.kill()  
            money += 10

        screen.blit(self.image, self.rect)


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


def draw_button(text, x, y, width, height):
    button_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
    pygame.draw.rect(screen, BLUE, button_rect)
    draw_text(text, font, WHITE, screen, x, y)
    return button_rect


def instructions_page():
    screen.fill(WHITE)
    instructions = [
        "Click the upgrade button to upgrade your main turret.",
        "Upgrading requires stat points which you gain by leveling up.",
        "Killing enemies will reward exp that will level you up.",
        "Make sure no enemies make it to the bottom of your screen and have fun!",
        "*End of instructions"
    ]
    for i, line in enumerate(instructions):
        draw_text(line, font, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 100 + i * 40)
    pygame.display.update()
    pygame.time.wait(4000)


def start_new_wave():
    global wave, enemies_to_spawn, enemies_spawned, time_since_last_spawn
    wave += 1
    enemies_to_spawn = random.randint(wave * 5, wave * 10)
    enemies_spawned = 0
    time_since_last_spawn = 0


menu = True
game_active = False

player = Player()
enemies_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
enemy_spawn_interval = 3000/wave


def wait_between_waves():
    screen.fill(WHITE)
    draw_text(f"Wave {wave} Complete! Starting next wave...", font, BLACK, screen, WIDTH // 2, HEIGHT // 2)
    for bullet in bullets_group:
        bullet.kill()
    pygame.display.flip()
    pygame.time.wait(3000)


def draw_upgrade_panel():
    panel_rect = pygame.Rect(WIDTH - 250, HEIGHT - 200, 200, 150)
    pygame.draw.rect(screen, BLACK, panel_rect)
    
    attack_speed_button = draw_button("Attack Speed", WIDTH - 150, HEIGHT - 175, 150, 40)
    money_multiplier_button = draw_button("Money Multiplier", WIDTH - 150, HEIGHT - 125, 150, 40)
    pierce_button = draw_button("Pierce", WIDTH - 150, HEIGHT - 75, 150, 40)

    return attack_speed_button, money_multiplier_button, pierce_button


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if menu:
                if start_button.collidepoint(mouse_pos):
                    game_active = True
                    menu = False
                elif instructions_button.collidepoint(mouse_pos):
                    instructions_page()

            if show_upgrade_panel:
                if attack_speed_button.collidepoint(mouse_pos):
                    attack_speed = max(100, attack_speed - 100)
                    pygame.time.set_timer(SHOOT_EVENT, attack_speed)
                elif money_multiplier_button.collidepoint(mouse_pos):
                    money += 500  
                elif pierce_button.collidepoint(mouse_pos):
                    pass  

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                show_upgrade_panel = not show_upgrade_panel

        if event.type == SHOOT_EVENT and game_active and len(enemies_group) != 0:
            closest_enemy = min(enemies_group, key=lambda e: e.rect.y)
            bullet = Bullet(player.rect.center, closest_enemy)
            bullets_group.add(bullet)

    if menu:
        screen.fill('black')
        draw_text("Main Menu", font, WHITE, screen, WIDTH // 2, HEIGHT // 4)
        start_button = draw_button("Start", WIDTH // 2, HEIGHT // 2, 200, 50)
        instructions_button = draw_button("Instructions", WIDTH // 2, HEIGHT // 2 + 60, 200, 50)
        pygame.display.update()

    elif game_active:
        screen.fill('black')
        if len(enemies_group) == 0 and enemies_spawned == enemies_to_spawn:
            if wave != 0:
                wait_between_waves()
            start_new_wave()

        if enemies_spawned < enemies_to_spawn:
            time_since_last_spawn += clock.get_time()
            if time_since_last_spawn >= enemy_spawn_interval:
                enemy_start_pos = (random.randint(15, WIDTH - 15), -15)
                enemy = Enemy(enemy_start_pos)
                enemies_group.add(enemy)
                time_since_last_spawn = 0
                enemies_spawned += 1

        enemies_group.update()
        bullets_group.update()

        if len(enemies_group) != 0:
            closest_enemy = min(enemies_group, key=lambda e: e.rect.y)
            player.update(closest_enemy)
        else:
            player.update(None)

        draw_text(f"Money: {money}", font, WHITE, screen, 100, HEIGHT - 30) 

        if show_upgrade_panel:
            attack_speed_button, money_multiplier_button, pierce_button = draw_upgrade_panel()

        pygame.display.flip()
        clock.tick(FPS)
