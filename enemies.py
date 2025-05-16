import os
import pygame
import random
from animation import Animation
from queue import PriorityQueue

class Enemy:
    def __init__(self, x, y, tile_size, game_map):
        self.tile_size = tile_size
        self.game_map = game_map
    
        # Animation system
        self.animations = {
            "Run": self._load_animation("Run", 6, 8),
            "Death": self._load_animation("Death", 8, 12, loop=False)
        }
        self.state = "Run"
        self.current_anim = self.animations[self.state]
    
        # Get sprite dimensions from first frame
        self.sprite_width, self.sprite_height = self.current_anim.current_frame.get_size()
    
        # Create smaller hitbox (60% of sprite size)
        hitbox_width = int(self.sprite_width * 0.6)
        hitbox_height = int(self.sprite_height * 0.6)
    
        self.hitbox = pygame.Rect(
            x + (tile_size - hitbox_width) // 2,
            y + (tile_size - hitbox_height) // 2,
            hitbox_width,
            hitbox_height
        )
    
        # Enemy properties
        self.speed = 2
        self.direction = random.choice([-1, 1])  # -1: left, 1: right
        self.health = 1
        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 30  # Update path every 30 frames

    def _load_animation(self, anim_type, frame_count, speed, loop=True):
        """Load animation frames with error handling"""
        frames = []
        for i in range(frame_count):
            try:
                frame_path = os.path.join("sprites", "enemy", anim_type, f"{i}.png")
                frame = pygame.image.load(frame_path).convert_alpha()
                frames.append(frame)
            except:
                # Create colored placeholder with frame number
                frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
                color = (255, 0, 0) if anim_type == "Run" else (255, 165, 0)
                frame.fill(color)
                font = pygame.font.Font(None, 20)
                text = font.render(f"{anim_type[0]}{i}", True, (255, 255, 255))
                frame.blit(text, (5, 5))
                frames.append(frame)
        return Animation(frames, speed, loop)

    def _find_path(self, player):
        """A* pathfinding to player"""
        start = (self.hitbox.centerx // self.tile_size, self.hitbox.centery // self.tile_size)
        goal = (player.hitbox.centerx // self.tile_size, player.hitbox.centery // self.tile_size)
        
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {start: 0}
        
        while not frontier.empty():
            current = frontier.get()[1]
            
            if current == goal:
                break
                
            for next_pos in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_pos = (current[0] + next_pos[0], current[1] + next_pos[1])
                
                if (0 <= new_pos[0] < len(self.game_map.tiles[0]) and 
                    0 <= new_pos[1] < len(self.game_map.tiles) and
                    not self.game_map.tile_kinds[self.game_map.tiles[new_pos[1]][new_pos[0]]].is_solid):
                    
                    new_cost = cost_so_far[current] + 1
                    
                    if new_pos not in cost_so_far or new_cost < cost_so_far[new_pos]:
                        cost_so_far[new_pos] = new_cost
                        priority = new_cost + self._heuristic(goal, new_pos)
                        frontier.put((priority, new_pos))
                        came_from[new_pos] = current
        
        # Reconstruct path
        current = goal
        path = []
        while current != start:
            if current not in came_from:
                return []  # No path found
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def _heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def update(self, player):
        """Update enemy state with pathfinding"""
        if self.state == "Death":
            self.current_anim.update()
            return self.current_anim.done
            
        # Update path periodically
        self.path_update_timer += 1
        if self.path_update_timer >= self.path_update_interval:
            self.path = self._find_path(player)
            self.path_update_timer = 0
        
        # Follow path
        if self.path:
            next_tile = self.path[0]
            target_x = next_tile[0] * self.tile_size + self.tile_size // 2
            target_y = next_tile[1] * self.tile_size + self.tile_size // 2
            
            dx = target_x - self.hitbox.centerx
            dy = target_y - self.hitbox.centery
            
            # Normalize movement
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                self.direction = -1 if dx < 0 else 1
                
                old_x, old_y = self.hitbox.x, self.hitbox.y
                self.hitbox.x += dx
                self.hitbox.y += dy
                
                if self._check_collision():
                    self.hitbox.x, self.hitbox.y = old_x, old_y
                    self.path = []  # Force path recalculation
                
                # If close to target, remove it from path
                if distance < self.speed:
                    self.path.pop(0)
        
        # Update animation
        self.current_anim.update()

        # Check bullet collisions
        for bullet in player.bullets[:]:
            if self.hitbox.colliderect(bullet.hitbox):
                player.bullets.remove(bullet)
                self.health -= 1
                if self.health <= 0:
                    self._die()
                    return True
        return False

    def _die(self):
        """Handle death sequence"""
        self.state = "Death"
        self.current_anim = self.animations["Death"]
        self.current_anim.reset()
        self.speed = 0

    def draw(self, screen):
        """Draw current animation frame"""
        frame = self.current_anim.current_frame
        if self.direction < 0 and self.state != "Death":
            frame = pygame.transform.flip(frame, True, False)
        
        draw_x = self.hitbox.centerx - frame.get_width() // 2
        draw_y = self.hitbox.centery - frame.get_height() // 2
        screen.blit(frame, (draw_x, draw_y))

    def _check_collision(self):
        """Check collision with walls"""
        start_x = max(0, self.hitbox.left // self.tile_size - 1)
        end_x = min(len(self.game_map.tiles[0]), (self.hitbox.right // self.tile_size) + 1)
        start_y = max(0, self.hitbox.top // self.tile_size - 1)
        end_y = min(len(self.game_map.tiles), (self.hitbox.bottom // self.tile_size) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if self.game_map.tile_kinds[self.game_map.tiles[y][x]].is_solid:
                    wall_rect = pygame.Rect(
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                    if self.hitbox.colliderect(wall_rect):
                        return True
        return False