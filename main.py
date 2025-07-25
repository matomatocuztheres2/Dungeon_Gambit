import pygame
import sys
import math
import time

# --- Game Constants ---
WIDTH, HEIGHT = 480, 720
FPS = 30  # Frames per second

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
GREEN = (11, 102, 35)


# --- Game States ---
GAME_STATE_TITLE = "TITLE_SCREEN"
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

try:
    title_font = pygame.font.SysFont("Times New Roman", 80, bold=True) # Adding bold
    tap_to_start_font = pygame.font.SysFont("Arial Black", 30, bold=False) # Keep this smaller
    print(f"Using font: Times New Roman")
    
except Exception:
    pass

if title_font is None:
    # Fallback to default Pygame font if none of the preferred fonts are found
    print("Warning: None of the preferred fonts found. Using default Pygame font.")
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

# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_game_state == GAME_STATE_TITLE and pygame.time.get_ticks() > initial_delay_end_time:
                current_game_state = GAME_STATE_GAME_ROOM

    # --- Game State Logic & Drawing ---
    if current_game_state == GAME_STATE_TITLE:
        screen.fill(GREEN)
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

    elif current_game_state == GAME_STATE_GAME_ROOM:
        screen.fill(GRAY)
        game_room_font = pygame.font.SysFont("Arial", 50)
        game_room_text_surface = game_room_font.render("Game Room (Placeholder)", True, WHITE)
        game_room_text_rect = game_room_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_room_text_surface, game_room_text_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
