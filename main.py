import pygame
import sys
import math
import time
import random
from objects.deck_ob import Hero, Card, setup_new_game, GameRoomUI
from objects.battle_ob import BattleManager # Import the new BattleManager

# --- Game Constants ---
WIDTH, HEIGHT = 480, 720
FPS = 30  # Frames per second

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
GREEN = (11, 102, 35)
NEON_PINK = (255, 0, 255)

# --- Game States ---
GAME_STATE_TITLE = "TITLE_SCREEN"
GAME_STATE_SHUFFLING = "SHUFFLING_SCREEN"
GAME_STATE_GAME_ROOM = "GAME_ROOM"

# --- Game Room Sub-States (within GAME_STATE_GAME_ROOM) ---
GAME_ROOM_SUB_STATE_IDLE = "IDLE"
GAME_ROOM_SUB_STATE_COMBAT_START = "COMBAT_START"
GAME_ROOM_SUB_STATE_PLAYER_TURN = "PLAYER_TURN"
GAME_ROOM_SUB_STATE_ENEMY_TURN = "ENEMY_TURN"
GAME_ROOM_SUB_STATE_COMBAT_END_VICTORY = "COMBAT_END_VICTORY"
GAME_ROOM_SUB_STATE_COMBAT_END_DEFEAT = "COMBAT_END_DEFEAT"
GAME_ROOM_SUB_STATE_DUNGEON_EXIT_ANIMATION = "DUNGEON_EXIT_ANIMATION"
GAME_ROOM_SUB_STATE_REWARD_SCREEN = "REWARD_SCREEN"

# --- Custom Pygame Events ---
# This event will be triggered when it's time for the next turn to process automatically
NEXT_TURN_EVENT = pygame.USEREVENT + 1

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon's Gambit")
clock = pygame.time.Clock()

# --- Title Screen Elements ---
title_font = None
tap_to_start_font = None

try:
    title_font = pygame.font.SysFont("Times New Roman", 80, bold=True)
    tap_to_start_font = pygame.font.SysFont("Arial Black", 30, bold=False)
except Exception:
    title_font = pygame.font.Font(None, 80, bold=True)
    tap_to_start_font = pygame.font.Font(None, 30, bold=False)

title_line1_surface = title_font.render("Dungeon's", True, WHITE)
title_line2_surface = title_font.render("Gambit", True, WHITE)

title_line1_rect = title_line1_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
title_line2_rect = title_line2_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

# --- Tap to Start Animation Variables ---
tap_to_start_text = "Tap to Start"
tap_to_start_original_surface = tap_to_start_font.render(tap_to_start_text, True, LIGHT_GRAY)
tap_to_start_start_time = pygame.time.get_ticks()
animation_duration = 1000
initial_delay_end_time = tap_to_start_start_time + 2000

# --- Game State Variables ---
# THESE LINES WERE LIKELY MISSING OR MISPLACED!
current_game_state = GAME_STATE_TITLE
current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE

# --- Game Variables for Game Room ---
hero = None
main_deck = []
unlocked_cards_pool = []
shuffling_start_time = 0
deck_drawn_card = None  # Holds the currently drawn card for display

# --- Game Room UI Instance ---
game_room_ui = GameRoomUI(WIDTH, HEIGHT) # Instantiate the UI renderer

# --- Battle Manager Instance ---
battle_manager = BattleManager(WIDTH, HEIGHT, game_room_ui) # Pass UI instance to BattleManager

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
                hero, main_deck, unlocked_cards_pool = setup_new_game()
                shuffling_start_time = pygame.time.get_ticks() # Start timer for shuffling animation
                current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Reset sub-state
            elif current_game_state == GAME_STATE_GAME_ROOM:
                # Only process clicks for drawing cards or dismissing combat/exit messages
                if current_game_room_sub_state == GAME_ROOM_SUB_STATE_IDLE:
                    if game_room_ui.get_deck_rect().collidepoint(event.pos): # Use getter
                        if main_deck:
                            deck_drawn_card = main_deck.pop(0)
                            print(f"Drew card: {deck_drawn_card.name}")

                            if deck_drawn_card.card_type == "enemy":
                                # Delegate combat start to BattleManager
                                current_game_room_sub_state = battle_manager.start_combat(deck_drawn_card)
                                # The battle manager's update_animations will eventually transition to PLAYER_TURN,
                                # and that's where we'll set the initial timer.
                            elif deck_drawn_card.card_type == "dungeon_exit":
                                # Delegate dungeon exit animation to BattleManager
                                current_game_room_sub_state = battle_manager.start_dungeon_exit_animation()
                            else:
                                # For other card types (equipment, level_up)
                                print(f"Drew {deck_drawn_card.card_type}: {deck_drawn_card.name}")
                                # In the future, this would lead to equipping/using the card
                        else:
                            print("Deck is empty!")
                            deck_drawn_card = Card("Empty", "message", name="Deck Empty!")
                
                # --- Combat End Interaction Clicks (only to dismiss messages) ---
                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_COMBAT_END_VICTORY:
                    # After "Victory!" fades, any tap leads to drawing a new card or a reward screen
                    if not battle_manager.combat_text_active: # Only allow click if animation finished
                        current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Back to idle to draw next card
                        deck_drawn_card = None # Clear the defeated enemy card
                        battle_manager.current_enemy = None # Clear current enemy in BattleManager
                        print("Combat ended. Ready to draw next card.")

                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_COMBAT_END_DEFEAT:
                    # After "Defeat!" fades, any tap leads to game over/title screen
                    if not battle_manager.combat_text_active: # Only allow click if animation finished
                        print("Game Over. Returning to title screen.")
                        current_game_state = GAME_STATE_TITLE
                        hero = None # Reset hero
                        main_deck = [] # Clear deck
                        unlocked_cards_pool = [] # Clear unlocked pool
                        deck_drawn_card = None
                        battle_manager.current_enemy = None # Clear current enemy in BattleManager
                        current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Reset sub-state
                        tap_to_start_start_time = pygame.time.get_ticks() # Reset title screen animation timer
                        
                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_DUNGEON_EXIT_ANIMATION:
                    # After "You Survived!" fades, any tap leads to reward screen
                    if not battle_manager.combat_text_active: # Only allow click if animation finished
                        current_game_room_sub_state = GAME_ROOM_SUB_STATE_REWARD_SCREEN
                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_REWARD_SCREEN:
                    # Second tap after reward screen leads to title screen
                    print("Returning to title screen from reward.")
                    current_game_state = GAME_STATE_TITLE
                    hero = None # Reset hero
                    main_deck = [] # Clear deck
                    unlocked_cards_pool = [] # Clear unlocked pool
                    deck_drawn_card = None
                    battle_manager.current_enemy = None # Clear current enemy in BattleManager
                    current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Reset sub-state
                    tap_to_start_start_time = pygame.time.get_ticks() # Reset title screen animation timer

        # --- Custom Events for Timed Actions (Automated Turns) ---
        if event.type == NEXT_TURN_EVENT:
            pygame.time.set_timer(NEXT_TURN_EVENT, 0) # Stop the timer

            if current_game_room_sub_state == GAME_ROOM_SUB_STATE_PLAYER_TURN:
                if hero and battle_manager.current_enemy: # Ensure both exist before attacking
                    new_sub_state = battle_manager.handle_player_attack(hero)
                    current_game_room_sub_state = new_sub_state
                    
                    if new_sub_state == GAME_ROOM_SUB_STATE_ENEMY_TURN:
                        pygame.time.set_timer(NEXT_TURN_EVENT, 1000) # Enemy turn auto-triggers after 1 sec
                else:
                    print("Error: Player or enemy missing during player turn.")
                    current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Fallback to idle

            elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_ENEMY_TURN:
                if hero and battle_manager.current_enemy: # Ensure both exist before attacking
                    new_sub_state = battle_manager.handle_enemy_attack(hero)
                    current_game_room_sub_state = new_sub_state

                    if new_sub_state == GAME_ROOM_SUB_STATE_PLAYER_TURN:
                        pygame.time.set_timer(NEXT_TURN_EVENT, 1000) # Player turn auto-triggers after 1 sec
                else:
                    print("Error: Player or enemy missing during enemy turn.")
                    current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Fallback to idle


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

    elif current_game_state == GAME_STATE_SHUFFLING:
        screen.fill(BLACK) # Clear screen for shuffling

        # Draw shuffling placeholder
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
            current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Enter IDLE state

    elif current_game_state == GAME_STATE_GAME_ROOM:
        # Get shake offsets from BattleManager
        shake_offsets = battle_manager.get_shaken_rects()
        
        # Apply shake offsets to copies of the UI rects before drawing GameRoomUI
        # This approach ensures GameRoomUI itself doesn't need to know about shaking,
        # and BattleManager doesn't directly manipulate GameRoomUI's internal rects.
        shaken_deck_rect = game_room_ui.get_deck_rect().move(shake_offsets['deck_rect'])
        shaken_health_rect = game_room_ui.get_health_rect().move(shake_offsets['health_rect'])

        # Temporarily override rects in game_room_ui for drawing with shake
        # NOTE: This is fine for simple rects, but for complex UI objects,
        # a more robust method might involve GameRoomUI accepting offsets as params.
        original_deck_rect_ui = game_room_ui.deck_rect
        original_health_rect_ui = game_room_ui.health_rect

        game_room_ui.deck_rect = shaken_deck_rect
        game_room_ui.health_rect = shaken_health_rect

        # Pass the current_enemy from battle_manager to draw_game_room
        # This ensures the enemy stats are drawn correctly on the card.
        # Check if current_enemy exists to prevent errors if deck_drawn_card is not an enemy.
        # current_enemy is set inside battle_manager.start_combat().
        game_room_ui.draw_game_room(screen, hero, battle_manager.current_enemy if battle_manager.current_enemy else deck_drawn_card)

        # Restore original rects after drawing to avoid permanent offset
        game_room_ui.deck_rect = original_deck_rect_ui
        game_room_ui.health_rect = original_health_rect_ui

        # Update and draw combat animations (text, damage numbers)
        # The update_animations method might return a new sub-state (e.g., from COMBAT_START to PLAYER_TURN)
        new_sub_state_after_anim = battle_manager.update_animations(current_game_room_sub_state)
        
        # If the sub-state just transitioned to PLAYER_TURN after the combat start animation,
        # immediately set the timer for the player's first auto-attack.
        if new_sub_state_after_anim == GAME_ROOM_SUB_STATE_PLAYER_TURN and current_game_room_sub_state != GAME_ROOM_SUB_STATE_PLAYER_TURN:
            pygame.time.set_timer(NEXT_TURN_EVENT, 1000) # Player's first turn delay
        
        current_game_room_sub_state = new_sub_state_after_anim # Update the main state variable

        battle_manager.draw_combat_elements(screen)

    # --- Update Display ---
    pygame.display.flip()

    # --- Cap Frame Rate ---
    clock.tick(FPS)

# --- Pygame Quit ---
pygame.quit()
sys.exit()