import pygame
import sys
import os
from button import Button
from map import Map, TileKind
from soldier import Player
from enemies import Enemy
from collision import check_collision_with_enemies
from diamonds import Diamond, generate_diamonds

# États du jeu
MENU = 0
PLAYING = 1
GAME_OVER = 2

def show_menu(screen):
    screen_width, screen_height = screen.get_size()
    
    # Création des boutons
    start_button = Button(
        screen_width//2 - 75, screen_height//2 - 60, 
        150, 40, 
        "START", (0, 100, 0), (0, 150, 0)
    )
    
    exit_button = Button(
        screen_width//2 - 75, screen_height//2 + 10,
        150, 40,
        "EXIT", (100, 0, 0), (150, 0, 0)
    )

    # Chargement de la musique de fond
    pygame.mixer.music.load(os.path.join("sounds", "background_music.mp3"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)  # Boucle infinie

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        # Fond d'écran simple
        screen.fill((0, 0, 30))
        
        # Titre
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Castle GAME", True, (200, 200, 255))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 50))

        # Boutons
        start_button.draw(screen)
        exit_button.draw(screen)

        # Gestion des clics
        if start_button.check_click(mouse_pos, mouse_clicked):
            return PLAYING
        if exit_button.check_click(mouse_pos, mouse_clicked):
            pygame.quit()
            sys.exit()

        pygame.display.flip()

def show_game_over(screen, won):
    screen_width, screen_height = screen.get_size()
    
    # Boutons
    restart_button = Button(
        screen_width//2 - 75, screen_height//2 + 20,
        150, 40,
        "RESTART", (0, 100, 100), (0, 150, 150)
    )
    
    menu_button = Button(
        screen_width//2 - 75, screen_height//2 + 70,
        150, 40, 
        "MENU", (100, 0, 100), (150, 0, 150)
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        # Fond simple
        screen.fill((0, 0, 30))

        # Message
        font = pygame.font.Font(None, 36)
        text = "YOU WIN!" if won else "GAME OVER"
        color = (0, 255, 0) if won else (255, 0, 0)
        text_surf = font.render(text, True, color)
        screen.blit(text_surf, (screen_width//2 - text_surf.get_width()//2, screen_height//2 - 50))

        # Boutons
        restart_button.draw(screen)
        menu_button.draw(screen)

        # Gestion des clics
        if restart_button.check_click(mouse_pos, mouse_clicked):
            return PLAYING
        if menu_button.check_click(mouse_pos, mouse_clicked):
            return MENU

        pygame.display.flip()

def run_game(screen):
    # Configuration des tuiles
    tile_size = 32
    tile_kinds = [
        TileKind("floor", (200, 200, 200), False),
        TileKind("wall", (50, 50, 50), True),
        TileKind("start", (0, 255, 0), False),
        TileKind("end", (255, 0, 0), False)
    ]
    
    # Chargement des effets sonores
    shoot_sound = pygame.mixer.Sound(os.path.join("sounds", "shoot.wav"))
    death_sound = pygame.mixer.Sound(os.path.join("sounds", "death.wav"))
    diamond_sound = pygame.mixer.Sound(os.path.join("sounds", "diamond.wav"))
    shoot_sound.set_volume(0.5)
    death_sound.set_volume(0.5)
    diamond_sound.set_volume(0.5)
    
    # Chargement de la carte 
    try:
        map_path = os.path.join(os.path.dirname(__file__), "start.map")
        game_map = Map(map_path, tile_kinds, tile_size)
    except FileNotFoundError:
        print("ERREUR: Fichier start.map introuvable!")
        return MENU, False

    # Initialisation des entités
    player = Player(game_map.start_pos[0], game_map.start_pos[1], tile_size)
    enemies = [
        Enemy(5 * tile_size, 3 * tile_size, tile_size, game_map),
        Enemy(8 * tile_size, 7 * tile_size, tile_size, game_map),
        Enemy(13 * tile_size, 13 * tile_size, tile_size, game_map),
        Enemy(13 * tile_size, 15 * tile_size, tile_size, game_map),
        Enemy(13 * tile_size, 17 * tile_size, tile_size, game_map),
        Enemy(16 * tile_size, 1 * tile_size, tile_size, game_map)
    ]
    diamonds = generate_diamonds(game_map, tile_size, density=0.15)
    score = 0
    game_won = False
    font = pygame.font.Font(None, 36)

    clock = pygame.time.Clock()
    
    while True:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return MENU, False
        
        # Mise à jour du jeu
        keys = pygame.key.get_pressed()
        player.handle_movement(keys, game_map)
        
        # Gestion des balles
        for bullet in player.bullets[:]:
            if not bullet.update(game_map):
               player.bullets.remove(bullet)
            else:
                for enemy in enemies[:]:
                   if bullet.hitbox.colliderect(enemy.hitbox):
                      player.bullets.remove(bullet)
                      enemy.health -= 1
                      if enemy.health <= 0:
                         enemies.remove(enemy)
                         score += 20
                      break
        
        # Mise à jour des ennemis
        for enemy in enemies[:]:
            should_remove = enemy.update(player)
            if should_remove:
               enemies.remove(enemy)
               score += 20
        
        # Collisions joueur-ennemi
        if check_collision_with_enemies(player.hitbox, enemies):
            player.take_damage(1)
            if player.health <= 0:
                death_sound.play()
                return GAME_OVER, False
        
        # Collecte des diamants
        for diamond in diamonds[:]:
            if not diamond.collected and player.hitbox.colliderect(diamond.rect):
                diamond.collected = True
                score += 10
                diamonds.remove(diamond)
                diamond_sound.play()
        
        # Condition de victoire
        tile_x = player.hitbox.centerx // tile_size
        tile_y = player.hitbox.centery // tile_size
        if (0 <= tile_y < len(game_map.tiles) and 
            0 <= tile_x < len(game_map.tiles[0])):
            if game_map.tiles[tile_y][tile_x] == 3:
                return GAME_OVER, True

        # Rendu
        screen.fill((0, 0, 0))
        game_map.draw(screen)
        
        # Dessiner les objets dans l'ordre
        for diamond in diamonds:
            diamond.draw(screen)
            
        for bullet in player.bullets:
            bullet.draw(screen)
            
        for enemy in enemies:
            enemy.draw(screen)
            
        player.draw(screen)
        
        # Interface utilisateur
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)