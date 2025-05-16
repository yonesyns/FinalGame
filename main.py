import pygame
from game import show_menu, show_game_over, run_game

# États du jeu
MENU = 0
PLAYING = 1
GAME_OVER = 2

def main():
    pygame.init()
    screen_width = 640
    screen_height = 640
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Castle Game")
    
    game_state = MENU
    game_result = False
    
    while True:
        if game_state == MENU:
            game_state = show_menu(screen)
        elif game_state == PLAYING:
            game_state, game_result = run_game(screen)
        elif game_state == GAME_OVER:
            game_state = show_game_over(screen, game_result)

if __name__ == "__main__":
    main()