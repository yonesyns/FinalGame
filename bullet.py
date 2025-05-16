import pygame

class Bullet:
    def __init__(self, x, y, direction_x, direction_y, tile_size):
        self.size = tile_size // 4  # Slightly larger for visibility
        self.hitbox = pygame.Rect(
            x - self.size // 2,  # Center the bullet
            y - self.size // 2,
            self.size,
            self.size
        )
        self.color = (255, 255, 0)  # Yellow
        self.speed = 8
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.lifetime = 60  # Frames before disappearing
        self.active = True

    def update(self, game_map):
        if not self.active:
            return False

        # Move bullet
        self.hitbox.x += self.direction_x * self.speed
        self.hitbox.y += self.direction_y * self.speed
        self.lifetime -= 1

        # Check wall collision
        if self._check_wall_collision(game_map):
            self.active = False
            return False

        # Check lifetime
        if self.lifetime <= 0:
            self.active = False
            return False

        return True

    def _check_wall_collision(self, game_map):
        # Check map boundaries
        if (self.hitbox.x < 0 or self.hitbox.x > len(game_map.tiles[0]) * game_map.tile_size or
            self.hitbox.y < 0 or self.hitbox.y > len(game_map.tiles) * game_map.tile_size):
            return True

        # Check solid tiles
        tile_x = self.hitbox.centerx // game_map.tile_size
        tile_y = self.hitbox.centery // game_map.tile_size
        
        if (0 <= tile_y < len(game_map.tiles) and 
            0 <= tile_x < len(game_map.tiles[0])):
            if game_map.tile_kinds[game_map.tiles[tile_y][tile_x]].is_solid:
                return True
        
        return False

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.hitbox)
            # Optional: Add a glow effect
            glow = pygame.Surface((self.size+4, self.size+4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 0, 100), 
                             (self.size//2+2, self.size//2+2), 
                             self.size//2+2)
            screen.blit(glow, (self.hitbox.x-2, self.hitbox.y-2))