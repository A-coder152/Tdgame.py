import pygame
import sys
import time
import math

# Initialize Pygame
pygame.init()
FPS = 60

ROAD = (119, 119, 119)  # Grey
TOWER_SPOT = (0, 255, 0)  # Green
OBSTACLE = (255, 0, 0)  # Red
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BRIGHT_YELLOW = (255, 255, 100)
BLUE = (0, 0, 255)
BRIGHT_BLUE = (100, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 120, 0)
ORANGE = (255, 165, 0)
PURPLE = (200, 0, 200)
ENEMY_COLORS = [RED, BLUE, ORANGE, BLACK]

# Define the game map
game_map = [
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 0],
    [1, 0, 1, 0, 0, 1, 0, 1, 1, 0],
    [0, 0, 1, 0, 1, 0, 0, 1, 0, 0],
    [1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [0, 0, 0, 0, 1, 0, 1, 1, 0, 1],
    [0, 1, 1, 1, 1, 0, 0, 1, 0, 1],
    [0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
]

# Define the size of each tile
TILE_SIZE = 40
SIDEBAR_WIDTH = 400

# Create the screen
screen = pygame.display.set_mode((len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH, len(game_map)*TILE_SIZE))

# Create the sidebar
sidebar = pygame.Surface((SIDEBAR_WIDTH, len(game_map)*TILE_SIZE))
sidebar.fill(WHITE)

# Create a font object
font = pygame.font.Font(None, 36)
font_s = pygame.font.Font(None, 16)


class Tower:
    def __init__(self, x, y, damage, range, tower_type):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range
        self.tower_type = tower_type
        self.level = 1
        if tower_type == 'yellow':
            self.upgrade_cost = 12
            self.initcost = 10
        elif tower_type == 'blue':
            self.upgrade_cost = 30
            self.initcost = 25
        elif tower_type == 'purple':
            self.upgrade_cost = 48
            self.initcost = 40
        elif tower_type == 'coin':
            self.upgrade_cost = 30
            self.initcost = 10
        elif tower_type == 'hammer':
            self.upgrade_cost = 36
            self.initcost = 30
        self.upgrade_cost_2 = self.initcost if not tower_type == 'coin' else self.upgrade_cost

class Enemy:
    def __init__(self, x, y, hp, speed, enemy_type):
        self.x = x-1
        self.target_x = x
        self.target_y = y
        self.y = y
        self.prev_y = y
        self.prev_x = x-1.1
        self.direction = (1, 0)
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.alive = True
        self.move_timer = 0
        self.enemy_type = enemy_type

    def move(self, game_map, dt):
    # If the enemy has reached its target, choose a new target
        if self.x == self.target_x and self.y == self.target_y:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Exclude the opposite direction
            opposite_direction = (-self.direction[0], -self.direction[1])
            directions.remove(opposite_direction)
            for dx, dy in directions:
                new_x, new_y = self.x + dx, self.y + dy
                if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map):
                    if game_map[new_y][new_x] == 0:
                        self.target_x, self.target_y = new_x, new_y
                        self.direction = (dx, dy)
                        break

        # Move towards the target
        if self.x < self.target_x:
            self.prev_x = self.x
            self.x += self.speed * dt
        elif self.x > self.target_x:
            self.prev_x = self.x
            self.x -= self.speed * dt
        if self.y < self.target_y:
            self.prev_y = self.y
            self.y += self.speed * dt
        elif self.y > self.target_y:
            self.prev_y = self.y
            self.y -= self.speed * dt

        # Make sure the enemy doesn't move past its target
        if abs(self.x - self.target_x) < self.speed * dt:
            self.x = self.target_x
        if abs(self.y - self.target_y) < self.speed * dt:
            self.y = self.target_y    

        if self.x == len(game_map[0]) - 1 and self.y == len(game_map) - 1:
            self.target_x +=1
        if self.x == len(game_map[0]) and self.y == len(game_map) - 1:
            self.alive = False
class Game:
    def __init__(self, game_map):
        self.game_map = game_map
        self.enemies = []
        self.spawn_point = (0, 3)  # The coordinates where enemies will spawn
        self.enemy_hp = [5, 20, 4, 200]  # HP for each type of enemy
        self.enemy_speed = [1, 0.5, 4, 0.3]  # Speed for each type of enemy
        self.waves = [[],[0,0],[0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],[2, 2, 2, 2, 2, 2, 2, 2, 2, 2],[1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 2, 1, 2],[3, 3, 3],[2, 2, 1, 2, 2, 1, 1, 1, 1, 1, 3],[1, 3, 1, 2, 3, 3, 3, 2, 2, 1, 1, 3, 2, 1, 1, 1]]  # Each sublist represents a wave of enemies
        self.enemy_number = 0
        self.towers = []
        self.tower_costs = {"yellow": 10, "blue":25, 'purple':40, "coin":20, 'hammer':35}
        self.tower_stats = [[1, 2], [1, 3.5], [1, 1.5], [0, 1],[4, 2]]

    def spawn_enemy(self, enemy_type):
        new_enemy = Enemy(*self.spawn_point, self.enemy_hp[enemy_type], self.enemy_speed[enemy_type], enemy_type)
        self.enemies.append(new_enemy)
        self.enemy_number += 1

    def draw_next_wave_button(self):
        if len(self.waves) > wave_number + 1:
            if self.wave_over():
                pygame.draw.rect(screen, RED, pygame.Rect(len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH - TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))

    def wave_over(self):
        # Check if all enemies in the current wave have been spawned and are not alive
        return self.enemy_number >= len(self.waves[wave_number]) and all(not enemy.alive for enemy in self.enemies)

    def spawn_tower(self, tower_type, x, y):
        towerpotato = ['yellow', 'blue', 'purple', 'coin', 'hammer']
        if True:
            tower_number = towerpotato.index(tower_type)
            new_tower = Tower(x, y, self.tower_stats[tower_number][0], self.tower_stats[tower_number][1], tower_type=tower_type)  # adjust damage and range as needed
            self.towers.append(new_tower)

    def delete_tower(self, x, y):
        for tower in self.towers:
            if tower.x == x and tower.y == y:
                self.towers.remove(tower)
                break

clock = pygame.time.Clock()
yellow_tower_image = pygame.image.load('yellow.png')
yellow_tower_image = pygame.transform.scale(yellow_tower_image, (TILE_SIZE, TILE_SIZE))
purple_tower_image = pygame.image.load('purple.png')
purple_tower_image = pygame.transform.scale(purple_tower_image, (TILE_SIZE, TILE_SIZE))
blue_tower_image = pygame.image.load('blue.png')
blue_tower_image = pygame.transform.scale(blue_tower_image, (TILE_SIZE, TILE_SIZE))
coin_tower_image = pygame.image.load('coin.png')
coin_tower_image = pygame.transform.scale(coin_tower_image, (TILE_SIZE, TILE_SIZE))
hammer_tower_image = pygame.image.load('hammer.png')
hammer_tower_image = pygame.transform.scale(hammer_tower_image, (TILE_SIZE, TILE_SIZE))
game = Game(game_map)
tower_selected = False
# Game loop
tower_types = ['yellow', 'blue', 'purple', 'coin','hammer']
running = True
coins = 30
tower_to_delete = None
last_time = time.time()
wave_number = 0
enemy_number = 0
last_shoot_time = time.time()
last_spawn_time = time.time()
while running:
    # Limit the frame rate to FPS
    clock.tick(FPS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the position of the mouse click
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if game.wave_over() and len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH - TILE_SIZE <= mouse_x < len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH and 0 <= mouse_y < TILE_SIZE and len(game.waves)>wave_number:
                # Move on to the next wave
                wave_number += 1
                coins += 30 if wave_number > 1 else 0
                for tower in game.towers:
                    if tower.tower_type == 'coin':
                        coins += 5*tower.level
                game.enemy_number = 0
                enemy_number = 0

            if tower_to_delete and mouse_x >= len(game_map[0])*TILE_SIZE and mouse_y >= len(game_map)*TILE_SIZE - TILE_SIZE:
        # Find the corresponding tower in the game.towers list
                for tower in game.towers:
                    if tower.x == tower_to_delete[0] and tower.y == tower_to_delete[1]:
                # Upgrade the tower
                        if coins >= tower.upgrade_cost:
                            if tower.tower_type == 'yellow' or tower.tower_type == 'purple' or tower.tower_type == 'coin':
                                tower.damage += 1  # Increase damage for yellow tower
                            elif tower.tower_type == 'blue':
                                tower.damage += 2  # Increase damage for blue tower
                            elif tower.tower_type == 'hammer':
                                tower.damage += 4
                            coins -= tower.upgrade_cost
                            tower.level += 1 
                            tower.upgrade_cost += int(0.2*tower.initcost)
                            break

            if tower_to_delete and mouse_x >= len(game_map[0])*TILE_SIZE and mouse_y >= len(game_map)*TILE_SIZE - 2*TILE_SIZE and mouse_y < len(game_map)*TILE_SIZE - TILE_SIZE:
        # Find the corresponding tower in the game.towers list
                for tower in game.towers:
                    if tower.x == tower_to_delete[0] and tower.y == tower_to_delete[1]:
                # Upgrade the tower
                        if coins >= tower.upgrade_cost_2:
                            tower.range += 1
                            coins -= tower.upgrade_cost_2
                            tower.level += 1 
                            tower.upgrade_cost_2 += int(1.2*tower.initcost)
                            break

            # Check if the click was in the sidebar
            if mouse_x >= len(game_map[0])*TILE_SIZE:
                if tower_to_delete and mouse_x < len(game_map[0])*TILE_SIZE + TILE_SIZE and mouse_y < TILE_SIZE:
                    # Delete the tower and refund the cost
                    for tower in game.towers:
                        if tower.x == tower_to_delete[0] and tower.y == tower_to_delete[1]:
                            coins += int(tower.initcost*0.8)*tower.level
                    game_map[tower_to_delete[1]][tower_to_delete[0]] = 1
                    game.delete_tower(tower_to_delete[0], tower_to_delete[1])
                    tower_to_delete = None
                # Check if the click was on the cancel button
                if mouse_x < len(game_map[0])*TILE_SIZE + TILE_SIZE and mouse_y < TILE_SIZE:
                    tower_selected = None
                # Select the tower if the player has enough coins
                elif 50 <= mouse_y < 50 + TILE_SIZE and coins >= 10 and len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 4 < mouse_x < len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 4 + 50:
                    tower_selected = 'yellow' if not tower_selected == "yellow" else None
                elif 50 <= mouse_y < 50 + TILE_SIZE and coins >= 35 and len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH//4) *2.5 < mouse_x < len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4*2.5 + 50:
                    tower_selected = 'hammer' if not tower_selected == 'hammer' else None
                elif 50 + TILE_SIZE*1.5 <= mouse_y < 50 + 2.5*TILE_SIZE and coins >= 25:
                    tower_selected = 'blue' if not tower_selected == 'blue' else None
                elif 50 + 3*TILE_SIZE <= mouse_y < 50 + 4*TILE_SIZE and coins >= 40:
                    tower_selected = 'purple' if not tower_selected == 'purple' else None
                elif 50 + 4.5*TILE_SIZE <= mouse_y < 50 + 5.5*TILE_SIZE and coins >= 20:
                    tower_selected = 'coin' if not tower_selected == 'coin' else None
            else:
                # Calculate the tile coordinates
                tile_x, tile_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE


                # Check if the tile is a tower spot
                if tower_selected and game_map[tile_y][tile_x] == 1:
                    # Place the tower and deduct the cost
                    if tower_selected == 'yellow':
                        game_map[tile_y][tile_x] = 3
                        coins -= 10
                    elif tower_selected == 'blue':
                        game_map[tile_y][tile_x] = 4
                        coins -= 25
                    elif tower_selected == 'purple':
                        game_map[tile_y][tile_x] = 5
                        coins -= 40
                    elif tower_selected == 'coin':
                        game_map[tile_y][tile_x] = 6
                        coins -= 20
                    elif tower_selected == 'hammer':
                        game_map[tile_y][tile_x] = 7
                        coins -= 35
                    game.spawn_tower(tower_selected, tile_x, tile_y)
                    tower_selected = None
                elif game_map[tile_y][tile_x] == 3 and not tower_to_delete == (tile_x, tile_y, "yellow"):
                    tower_to_delete = (tile_x, tile_y, "yellow")
                elif game_map[tile_y][tile_x] == 4 and not tower_to_delete == (tile_x, tile_y, "blue"):
                    tower_to_delete = (tile_x, tile_y, "blue")
                elif game_map[tile_y][tile_x] == 5 and not tower_to_delete == (tile_x, tile_y, "purple"):
                    tower_to_delete = (tile_x, tile_y, "purple")
                elif game_map[tile_y][tile_x] == 6 and not tower_to_delete == (tile_x, tile_y, "coin"):
                    tower_to_delete = (tile_x, tile_y, "coin")
                elif game_map[tile_y][tile_x] == 7 and not tower_to_delete == (tile_x, tile_y, "hammer"):
                    tower_to_delete = (tile_x, tile_y, "hammer")
                elif game_map[tile_y][tile_x] in [3, 4, 5, 6, 7]:
                    tower_to_delete = None


    if time.time() - last_spawn_time >= 1:
        if wave_number < len(game.waves):
                # Check if there are more enemies to spawn in the current wave
            if enemy_number < len(game.waves[wave_number]):
            # Spawn the enemy
                enemy_type = game.waves[wave_number][enemy_number]
                game.spawn_enemy(enemy_type)
                enemy_number += 1
                last_spawn_time = time.time()

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Move each enemy
    game.enemies = [enemy for enemy in game.enemies if enemy.alive]
    for enemy in game.enemies:
        enemy.move(game.game_map, dt)

    # Draw the game map
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            if game_map[y][x] == 0:
                pygame.draw.rect(screen, ROAD, pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif game_map[y][x] == 1:
                pygame.draw.rect(screen, TOWER_SPOT, pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif game_map[y][x] == 2:
                pygame.draw.rect(screen, OBSTACLE, pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif game_map[y][x] == 3:
                #pygame.draw.rect(screen, YELLOW if not tower_to_delete == (x, y, 'yellow') else BRIGHT_YELLOW, pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                screen.blit(yellow_tower_image, (x*TILE_SIZE, y*TILE_SIZE))
            elif game_map[y][x] == 4:
                screen.blit(blue_tower_image, (x*TILE_SIZE, y*TILE_SIZE))
            elif game_map[y][x] == 5:
                screen.blit(purple_tower_image, (x*TILE_SIZE, y*TILE_SIZE))      
            elif game_map[y][x] == 6:
                screen.blit(coin_tower_image, (x*TILE_SIZE, y*TILE_SIZE))  
            elif game_map[y][x] == 7:
                screen.blit(hammer_tower_image, (x*TILE_SIZE, y*TILE_SIZE))     

    if time.time() - last_shoot_time >=1:
        last_shoot_time = time.time()
        for tower in game.towers:
            has_shot = 1  # Add a flag to check if the tower has shot an enemy
            for enemy in game.enemies:
                dx = enemy.x - tower.x
                dy = enemy.y - tower.y
                distance = (dx**2 + dy**2)**0.5
                if distance <= tower.range:
                    enemy.hp = enemy.hp - (tower.damage * has_shot)
                    if enemy.hp <= 0:
                        enemy.alive = False
                    has_shot = 0 if not tower.tower_type == 'purple' else 1

    for enemy in game.enemies:
        pygame.draw.circle(screen, ENEMY_COLORS[enemy.enemy_type], (enemy.x*TILE_SIZE + TILE_SIZE//2, enemy.y*TILE_SIZE + TILE_SIZE//2), TILE_SIZE//3)
        # Draw the health bar above the enemy
        pygame.draw.rect(screen, RED, pygame.Rect(enemy.x*TILE_SIZE+TILE_SIZE//5.5, enemy.y*TILE_SIZE - 2, TILE_SIZE//1.5, 5))
        pygame.draw.rect(screen, GREEN, pygame.Rect(enemy.x*TILE_SIZE+TILE_SIZE//5.5, enemy.y*TILE_SIZE - 2, TILE_SIZE//1.5 * enemy.hp / enemy.max_hp, 5))
 # Draw the sidebar
    screen.blit(sidebar, (len(game_map[0])*TILE_SIZE, 0))

    coin_text = font.render(f'Coins: {coins}', True, BLACK)
    text_rect = coin_text.get_rect(center=(len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH // 2, 20))
    screen.blit(coin_text, text_rect)

    for i, tower_type in enumerate(tower_types):
    # Create text surfaces for the cost, damage, and range
        cost_text = font_s.render(f'Cost: {game.tower_costs[tower_type]}', True, BLACK)
        damage_text = font_s.render(f'Damage: {game.tower_stats[i][0]}', True, BLACK)
        range_text = font_s.render(f'Range: {game.tower_stats[i][1]}', True, BLACK)
        if tower_type == 'blue' or tower_type == 'yellow' or tower_type == 'hammer':
            special_text = font_s.render('Basic', True, BLACK)
        elif tower_type == 'purple':
            special_text = font_s.render('Force field', True, BLACK)
        elif tower_type == 'coin':
            special_text = font_s.render('+5 coins/round', True, BLACK)

    # Calculate the positions of the text
        if i < 4:
            cost_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4 + TILE_SIZE, 50 + i*TILE_SIZE*1.5)
            damage_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4 + TILE_SIZE, 50 + i*TILE_SIZE*1.5 + 10)
            range_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4 + TILE_SIZE, 50 + i*TILE_SIZE*1.5 + 20)
            special_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4 + TILE_SIZE, 50 + i*TILE_SIZE*1.5 + 30)
        elif i >= 4:
            cost_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4*2.5 + TILE_SIZE, 50 + (i-4)*TILE_SIZE*1.5)
            damage_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4*2.5 + TILE_SIZE, 50 + (i-4)*TILE_SIZE*1.5 + 10)
            range_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4*2.5 + TILE_SIZE, 50 + (i-4)*TILE_SIZE*1.5 + 20)
            special_text_pos = (len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH//4*2.5 + TILE_SIZE, 50 + (i-4)*TILE_SIZE*1.5 + 30)

    # Draw the text on the screen
        screen.blit(cost_text, cost_text_pos)
        screen.blit(damage_text, damage_text_pos)
        screen.blit(range_text, range_text_pos)
        screen.blit(special_text, special_text_pos)

    if tower_to_delete:
    # Find the corresponding tower in the game.towers list
        for tower in game.towers:
            if tower.x == tower_to_delete[0] and tower.y == tower_to_delete[1]:
            # Create a Surface object with the SRCALPHA flag for translucency
                towerup = tower.upgrade_cost
                rangeup = tower.upgrade_cost_2
                s = pygame.Surface((tower.range*2*TILE_SIZE, tower.range*2*TILE_SIZE), pygame.SRCALPHA)
            # Draw a translucent white circle on the Surface object
                pygame.draw.circle(s, (255, 255, 255, 50), (tower.range*TILE_SIZE, tower.range*TILE_SIZE), tower.range*TILE_SIZE)
            # Blit the Surface object onto the screen at the tower's position
                screen.blit(s, ((tower.x - tower.range)*TILE_SIZE + TILE_SIZE//2, (tower.y - tower.range)*TILE_SIZE + TILE_SIZE//2))
                break
        pygame.draw.rect(screen, BRIGHT_BLUE, pygame.Rect(len(game_map[0])*TILE_SIZE, len(game_map)*TILE_SIZE - TILE_SIZE, SIDEBAR_WIDTH, TILE_SIZE))
        upgrade_cost_text = font.render(f'+1 Damage: {towerup}', True, BLACK) if not tower.tower_type == 'blue' else font.render(f'+2 Damage: {towerup}', True, BLACK)
        thee_rect = upgrade_cost_text.get_rect(center=(len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH // 2, len(game_map)*TILE_SIZE - TILE_SIZE // 2))
        screen.blit(upgrade_cost_text, thee_rect)
        pygame.draw.rect(screen, BRIGHT_BLUE, pygame.Rect(len(game_map[0])*TILE_SIZE, len(game_map)*TILE_SIZE - 2*TILE_SIZE, SIDEBAR_WIDTH, TILE_SIZE))
        range_upgrade_cost_text = font.render(f'+1 Range: {rangeup}', True, BLACK)
        potato_rect = range_upgrade_cost_text.get_rect(center=(len(game_map[0])*TILE_SIZE + SIDEBAR_WIDTH // 2, len(game_map)*TILE_SIZE - 1.5*TILE_SIZE))
        screen.blit(range_upgrade_cost_text, potato_rect)

    pygame.draw.rect(screen, BRIGHT_YELLOW if tower_selected == 'yellow' else WHITE, pygame.Rect(len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 5, 60, TILE_SIZE//2, TILE_SIZE//2))
    screen.blit(yellow_tower_image, (len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 4, 50))
    pygame.draw.rect(screen, BRIGHT_YELLOW if tower_selected == 'blue' else WHITE, pygame.Rect(len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 5, 60+TILE_SIZE*1.5, TILE_SIZE//2, TILE_SIZE//2))
    screen.blit(blue_tower_image, (len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 4, 50+TILE_SIZE*1.5))
    pygame.draw.rect(screen, BRIGHT_YELLOW if tower_selected == 'purple' else WHITE, pygame.Rect(len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 5, 60+TILE_SIZE*3, TILE_SIZE//2, TILE_SIZE//2))
    screen.blit(purple_tower_image, (len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 4, 50+TILE_SIZE*3))
    pygame.draw.rect(screen, BRIGHT_YELLOW if tower_selected == 'coin' else WHITE, pygame.Rect(len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 5, 60+TILE_SIZE*4.5, TILE_SIZE//2, TILE_SIZE//2))
    screen.blit(coin_tower_image, (len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 4, 50+TILE_SIZE*4.5))
    pygame.draw.rect(screen, BRIGHT_BLUE if tower_selected == 'hammer' else WHITE, pygame.Rect(len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH - TILE_SIZE) // 5 * 3, 60, TILE_SIZE//2, TILE_SIZE//2))
    screen.blit(hammer_tower_image, (len(game_map[0])*TILE_SIZE + (SIDEBAR_WIDTH) // 4*2.5, 50))

    if tower_to_delete:
        pygame.draw.rect(screen, RED, pygame.Rect(len(game_map[0])*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
    game.draw_next_wave_button()
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()