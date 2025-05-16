import pygame

def check_collision_rects(rect1, rect2):
    """Simple collision check between two rectangles."""
    return rect1.colliderect(rect2)

def check_collision_with_walls(hitbox, game_map, tile_size):
    """Checks if a given hitbox collides with any solid wall (optimized)."""
    start_x = max(0, hitbox.left // tile_size - 1)
    end_x = min(len(game_map.tiles[0]), (hitbox.right // tile_size) + 1)
    start_y = max(0, hitbox.top // tile_size - 1)
    end_y = min(len(game_map.tiles), (hitbox.bottom // tile_size) + 1)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile_kind = game_map.tile_kinds[game_map.tiles[y][x]]
            if tile_kind.is_solid:
                wall_rect = pygame.Rect(
                    x * tile_size,
                    y * tile_size,
                    tile_size,
                    tile_size
                )
                if hitbox.colliderect(wall_rect):
                    return True
    return False

def get_colliding_walls(hitbox, game_map, tile_size):
    """Returns a list of walls currently colliding with a hitbox (optimized)."""
    walls = []
    start_x = max(0, hitbox.left // tile_size - 1)
    end_x = min(len(game_map.tiles[0]), (hitbox.right // tile_size) + 1)
    start_y = max(0, hitbox.top // tile_size - 1)
    end_y = min(len(game_map.tiles), (hitbox.bottom // tile_size) + 1)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile_kind = game_map.tile_kinds[game_map.tiles[y][x]]
            if tile_kind.is_solid:
                wall_rect = pygame.Rect(
                    x * tile_size,
                    y * tile_size,
                    tile_size,
                    tile_size
                )
                if hitbox.colliderect(wall_rect):
                    walls.append(wall_rect)
    return walls

def check_collision_with_enemies(player_hitbox, enemies):
    """Checks if the player collides with any enemy in the list."""
    for enemy in enemies:
        if player_hitbox.colliderect(enemy.hitbox):
            return enemy
    return None