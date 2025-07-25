import pygame
import sys
import math
import time
import random 
from objects.deck_ob import Hero, Card, setup_new_game

# --- Game Constants ---
WIDTH, HEIGHT = 480, 720
FPS = 30  # Frames per second

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
GREEN = (11, 102, 35) # Defined by user
NEON_PINK = (255, 0, 255)
NEON_BLUE = (0, 255, 255)
NEON_YELLOW = (255, 255, 0)
NEON_CYAN = (0, 255, 255)

# --- Game States ---
GAME_STATE_TITLE = "TITLE_SCREEN"
GAME_STATE_SHUFFLING = "SHUFFLING_SCREEN" # New state for shuffling animation
GAME_STATE_GAME_ROOM = "GAME_ROOM"

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon's Gambit")
clock = pygame.time.Clock()

# --- Game State Variable ---
current_game_state = GAME_STATE_TITLE

# --- Title Screen Elements ---
title_font = None
tap_to_start_font = None

# Set the fonts based on fixed names as specified in the previous turn
try:
    title_font = pygame.font.SysFont("Times New Roman", 80, bold=True)
    tap_to_start_font = pygame.font.SysFont("Arial Black", 30, bold=False)
    print(f"Using font: Times New Roman (Title), Arial Black (Tap to Start)")
except Exception:
    print("Warning: Specified fonts not found. Using default Pygame fonts.")
    title_font = pygame.font.Font(None, 80, bold=True)
    tap_to_start_font = pygame.font.Font(None, 30, bold=False)

# Render the title text (split into two lines)
title_line1_surface = title_font.render("Dungeon's", True, WHITE)
title_line2_surface = title_font.render("Gambit", True, WHITE)

# Calculate positions to center the title
title_line1_rect = title_line1_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
title_line2_rect = title_line2_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

# --- Tap to Start Animation Variables ---
tap_to_start_text = "Tap to Start"
tap_to_start_original_surface = tap_to_start_font.render(tap_to_start_text, True, LIGHT_GRAY)

tap_to_start_start_time = pygame.time.get_ticks()
animation_duration = 1000
initial_delay_end_time = tap_to_start_start_time + 2000

# --- Game Variables for Game Room ---
hero = None
main_deck = []
unlocked_cards_pool = []
shuffling_start_time = 0
deck_drawn_card = None # Holds the currently drawn card for display


# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_game_state == GAME_STATE_TITLE and pygame.time.get_ticks() > initial_delay_end_time:
                current_game_state = GAME_STATE_SHUFFLING # Transition to shuffling state
                # Initialize game components by calling the function from deck_ob
                hero, main_deck, unlocked_cards_pool = setup_new_game() 
                shuffling_start_time = pygame.time.get_ticks() # Start timer for shuffling animation
            elif current_game_state == GAME_STATE_GAME_ROOM:
                # Check for deck tap
                deck_x = (WIDTH - 360) // 2
                deck_y = 40
                deck_rect = pygame.Rect(deck_x, deck_y, 360, 480)
                if deck_rect.collidepoint(event.pos):
                    if main_deck: # Only draw if deck is not empty
                        deck_drawn_card = main_deck.pop(0) # Draw a card
                        print(f"Drew card: {deck_drawn_card.name}")
                    else:
                        print("Deck is empty!")
                        deck_drawn_card = Card("Empty", "message", name="Deck Empty!") # Use deck_ob.Card for consistency

    # --- Game State Logic & Drawing ---
    if current_game_state == GAME_STATE_TITLE:
        screen.fill(GREEN) # Using GREEN for title screen background as specified by user
        screen.blit(title_line1_surface, title_line1_rect)
        screen.blit(title_line2_surface, title_line2_rect)

        elapsed_time = pygame.time.get_ticks() - tap_to_start_start_time
        animation_phase_time = (elapsed_time % (animation_duration * 2))

        scale_factor = 1.0
        if animation_phase_time < animation_duration:
            scale_factor = 1.0 - 0.5 * (animation_phase_time / animation_duration)
        else:
            time_in_grow_phase = animation_phase_time - animation_duration
            scale_factor = 0.5 + 0.5 * (time_in_grow_phase / animation_duration)

        scaled_width = int(tap_to_start_original_surface.get_width() * scale_factor)
        scaled_height = int(tap_to_start_original_surface.get_height() * scale_factor)
        
        scaled_width = max(1, scaled_width)
        scaled_height = max(1, scaled_height)

        tap_to_start_scaled_surface = pygame.transform.scale(
            tap_to_start_original_surface, (scaled_width, scaled_height)
        )

        tap_to_start_y_pos = (title_line2_rect.bottom + HEIGHT) // 2
        tap_to_start_rect = tap_to_start_scaled_surface.get_rect(center=(WIDTH // 2, tap_to_start_y_pos))
        
        screen.blit(tap_to_start_scaled_surface, tap_to_start_rect)

    elif current_game_state == GAME_STATE_SHUFFLING:
        screen.fill(BLACK) # Clear screen for shuffling
        
        # Draw shuffling placeholder (e.g., NEON_PINK square in the middle)
        placeholder_size = 200
        placeholder_rect = pygame.Rect(
            WIDTH // 2 - placeholder_size // 2,
            HEIGHT // 2 - placeholder_size // 2,
            placeholder_size,
            placeholder_size
        )
        pygame.draw.rect(screen, NEON_PINK, placeholder_rect)

        # Check if 2 seconds have passed
        if pygame.time.get_ticks() - shuffling_start_time > 2000:
            current_game_state = GAME_STATE_GAME_ROOM # Transition to game room

    elif current_game_state == GAME_STATE_GAME_ROOM:
        screen.fill(GRAY) # A distinct color for the game room

        # --- Draw Deck Placeholder ---
        deck_x = (WIDTH - 360) // 2
        deck_y = 40 # 40px from top
        deck_rect = pygame.Rect(deck_x, deck_y, 360, 480)
        pygame.draw.rect(screen, NEON_BLUE, deck_rect, 5) # Draw outline for visibility

        # --- Draw Drawn Card Placeholder (if a card is drawn) ---
        if deck_drawn_card:
            drawn_card_x = deck_x # Same position as deck for now
            drawn_card_y = deck_y
            drawn_card_rect = pygame.Rect(drawn_card_x, drawn_card_y, 360, 480)
            pygame.draw.rect(screen, NEON_CYAN, drawn_card_rect) # Drawn card is NEON_CYAN
            
            # Text on drawn card placeholder
            card_text_font = pygame.font.SysFont("Arial", 25)
            card_text_surface = card_text_font.render(
                f"This is a card: {deck_drawn_card.name}", True, BLACK
            )
            card_info_surface = card_text_font.render(
                "No info has been added yet", True, BLACK
            )
            card_text_rect = card_text_surface.get_rect(center=(drawn_card_x + 360 // 2, drawn_card_y + 480 // 2 - 20))
            card_info_rect = card_info_surface.get_rect(center=(drawn_card_x + 360 // 2, drawn_card_y + 480 // 2 + 20))
            screen.blit(card_text_surface, card_text_rect)
            screen.blit(card_info_surface, card_info_rect)


        # --- Draw Hero Stat Placeholders ---
        stat_width = 144
        stat_height = 144
        padding = 12 # Spacing between elements

        # Calculate X positions for even spacing
        health_x = padding
        attack_x = padding + stat_width + padding
        defense_x = padding + stat_width + padding + stat_width + padding
        stat_y = HEIGHT - stat_height - padding # 10px from bottom

        # Health Placeholder
        health_rect = pygame.Rect(health_x, stat_y, stat_width, stat_height)
        pygame.draw.rect(screen, NEON_YELLOW, health_rect, 5) # Outline
        # Health Text
        stat_font = pygame.font.SysFont("Arial Black", 30)
        health_text_surface = stat_font.render(f"HP: {hero.health}", True, WHITE)
        health_text_rect = health_text_surface.get_rect(center=health_rect.center)
        screen.blit(health_text_surface, health_text_rect)

        # Attack Placeholder
        attack_rect = pygame.Rect(attack_x, stat_y, stat_width, stat_height)
        pygame.draw.rect(screen, NEON_YELLOW, attack_rect, 5) # Outline
        # Attack Text
        attack_text_surface = stat_font.render(f"ATK: {hero.attack}", True, WHITE)
        attack_text_rect = attack_text_surface.get_rect(center=attack_rect.center)
        screen.blit(attack_text_surface, attack_text_rect)

        # Defense Placeholder
        defense_rect = pygame.Rect(defense_x, stat_y, stat_width, stat_height)
        pygame.draw.rect(screen, NEON_YELLOW, defense_rect, 5) # Outline
        # Defense Text
        defense_text_surface = stat_font.render(f"DEF: {hero.defense}", True, WHITE)
        defense_text_rect = defense_text_surface.get_rect(center=defense_rect.center)
        screen.blit(defense_text_surface, defense_text_rect)
        
    # --- Update Display ---
    pygame.display.flip()

    # --- Cap Frame Rate ---
    clock.tick(FPS)

# --- Pygame Quit ---
pygame.quit()
sys.exit()
