import os
import pygame
from bullet import Bullet
from animation import Animation

class Player:
    def __init__(self, x, y, tile_size):
        self.tile_size = tile_size
    
        # Animation system
        self.animations = {
            "Idle": self._load_animation("Idle", 5, 10),
            "Run": self._load_animation("Run", 6, 8),
            "Death": self._load_animation("Death", 8, 12, loop=False)
        }
        self.state = "Idle"
        self.current_anim = self.animations[self.state]
    
        # Get sprite dimensions from first frame
        self.sprite_width, self.sprite_height = self.current_anim.current_frame.get_size()
    
        # Create smaller hitbox (60% of sprite size)
        hitbox_width = int(self.sprite_width * 0.6)
        hitbox_height = int(self.sprite_height * 0.6)
    
        self.hitbox = pygame.Rect(
            x + (tile_size - hitbox_width) // 2,  # Center horizontally
            y + (tile_size - hitbox_height) // 2,  # Center vertically
            hitbox_width,
            hitbox_height
        )
    
        # Movement properties
        self.speed = 4
        self.bullets = []
        self.shoot_cooldown = 0
        self.last_direction = (1, 0)  # Default to facing right
        self.facing_right = True
        self.health = 3
        self.shoot_sound = pygame.mixer.Sound(os.path.join("sounds", "shoot.wav"))
        self.shoot_sound.set_volume(0.5)

    def _load_animation(self, anim_type, frame_count, speed, loop=True):
        """Load complete animation sequence"""
        frames = []
        for i in range(frame_count):
            frame_path = os.path.join("sprites", "player", anim_type, f"{i}.png")
            try:
                frame = pygame.image.load(frame_path).convert_alpha()
                frames.append(frame)
            except:
                raise SystemExit(f"Missing required sprite: {frame_path}")
        return Animation(frames, speed, loop)

    def handle_movement(self, keys, game_map):
        dx, dy = 0, 0
        moving = False
        
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.last_direction = (-1, 0)
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.last_direction = (1, 0)
            self.facing_right = True
            moving = True
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.last_direction = (0, -1)
            moving = True
        if keys[pygame.K_DOWN]:
            dy = self.speed
            self.last_direction = (0, 1)
            moving = True
            
        # Update animation state
        self.state = "Run" if moving else "Idle"
        self.current_anim = self.animations[self.state]
        
        # Shooting logic
        if keys[pygame.K_SPACE] and self.shoot_cooldown == 0:
            self.shoot()
            self.shoot_cooldown = 10  # Cooldown frames
            self.shoot_sound.play()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self._move(dx, dy, game_map)
        self.current_anim.update()

    def shoot(self):
        """Create a new bullet in the last direction faced"""
        bullet_x = self.hitbox.centerx
        bullet_y = self.hitbox.centery
    
        dir_x, dir_y = self.last_direction
        if dir_x == 0 and dir_y == 0:  # Default to right if no direction
            dir_x = 1
    
        new_bullet = Bullet(bullet_x, bullet_y, dir_x, dir_y, self.tile_size)
        self.bullets.append(new_bullet)

    def draw(self, screen):
        """Draw the current animation frame"""
        frame = self.current_anim.current_frame
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        
        draw_x = self.hitbox.centerx - frame.get_width() // 2
        draw_y = self.hitbox.centery - frame.get_height() // 2
        screen.blit(frame, (draw_x, draw_y))

    def take_damage(self, amount):
        """Handle player taking damage"""
        self.health -= amount
        return self.health <= 0

    def _move(self, dx, dy, game_map):
        """Handle movement with collision detection"""
        original_x = self.hitbox.x
        original_y = self.hitbox.y
    
        self.hitbox.x += dx
        walls = self._get_colliding_walls(game_map)
        if walls:
            self.hitbox.x = original_x
            if dx > 0:
                self.hitbox.right = min(wall.left for wall in walls)
            else:
                self.hitbox.left = max(wall.right for wall in walls)
    
        self.hitbox.y += dy
        walls = self._get_colliding_walls(game_map)
        if walls:
            self.hitbox.y = original_y
            if dy > 0:
                self.hitbox.bottom = min(wall.top for wall in walls)
            else:
                self.hitbox.top = max(wall.bottom for wall in walls)

    def _get_colliding_walls(self, game_map):
        """Get list of walls the player is colliding with"""
        walls = []
        start_x = max(0, self.hitbox.left // self.tile_size - 1)
        end_x = min(len(game_map.tiles[0]), (self.hitbox.right // self.tile_size) + 1)
        start_y = max(0, self.hitbox.top // self.tile_size - 1)
        end_y = min(len(game_map.tiles), (self.hitbox.bottom // self.tile_size) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if game_map.tile_kinds[game_map.tiles[y][x]].is_solid:
                    wall_rect = pygame.Rect(
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                    if self.hitbox.colliderect(wall_rect):
                        walls.append(wall_rect)
        return walls