import pygame
import sys
import math
import time
import random
import os

from objects.deck_ob import Hero, Card, setup_new_game
from objects.battle_ob import BattleManager 
from objects.inventory_ob import InventoryManager
from objects.level_ob import LevelManager

# --- Game Constants ---
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
WIDTH, HEIGHT = 480, 720
FPS = 30  # Frames per second

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
GREEN = (11, 102, 35)
NEON_PINK = (255, 0, 255)
NEON_BLUE = (0, 255, 255)
NEON_YELLOW = (255, 255, 0)
NEON_CYAN = (0, 255, 255)
RED = (255, 0, 0)

# --- Game States ---
GAME_STATE_TITLE = "TITLE_SCREEN"
GAME_STATE_SHUFFLING = "SHUFFLING_SCREEN"
GAME_STATE_GAME_ROOM = "GAME_ROOM"

# --- Game Room Sub-States (within GAME_STATE_GAME_ROOM) ---
GAME_ROOM_SUB_STATE_IDLE = "IDLE"
GAME_ROOM_SUB_STATE_EQUIPMENT_START = "EQUIPMENT_FOUND"
GAME_ROOM_SUB_STATE_EQUIPMENT_ADDED = "EQUIPMENT_ADDED"
GAME_ROOM_SUB_STATE_COMBAT_START = "COMBAT_START"
GAME_ROOM_SUB_STATE_PLAYER_TURN = "PLAYER_TURN"
GAME_ROOM_SUB_STATE_ENEMY_TURN = "ENEMY_TURN"
GAME_ROOM_SUB_STATE_COMBAT_END_VICTORY = "COMBAT_END_VICTORY"
GAME_ROOM_SUB_STATE_COMBAT_END_DEFEAT = "COMBAT_END_DEFEAT"
GAME_ROOM_SUB_STATE_LEVEL_UP_START = "LEVEL_UP_FOUND"
GAME_ROOM_SUB_STATE_LEVEL_UP_ADDED = "LEVEL_UP_ADDED"
GAME_ROOM_SUB_STATE_DUNGEON_EXIT_ANIMATION = "DUNGEON_EXIT_ANIMATION"
GAME_ROOM_SUB_STATE_REWARD_SCREEN = "REWARD_SCREEN"

# --- Custom Pygame Events ---
NEXT_TURN_EVENT = pygame.USEREVENT + 1

# --- Pygame Initialization ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon's Gambit")
clock = pygame.time.Clock()

# --- Initialize BG Music ---
# Define music file path
BACKGROUND_MUSIC_PATH = './sounds/2019-02-25_-_Poisonous_-_David_Fesliyan.mp3'

# --- Preaload SFX ---
SOUND_EFFECTS = {} 

try:
    SOUND_EFFECTS['card_draw'] = pygame.mixer.Sound('./sounds/card_draw_so.mp3')
    SOUND_EFFECTS['card_draw'].set_volume(0.3) # Adjust volume if needed, 0.0 to 1.0

    SOUND_EFFECTS['hit_or_trap'] = pygame.mixer.Sound('./sounds/trap_so.wav')
    SOUND_EFFECTS['hit_or_trap'].set_volume(0.5) # Adjust volume if needed

    SOUND_EFFECTS['tap_card'] = pygame.mixer.Sound('./sounds/tap_so.mp3')
    SOUND_EFFECTS['tap_card'].set_volume(0.4) # Adjust volume if needed

    print("Sound effects loaded successfully.")
except pygame.error as e:
    print(f"Error loading sound effect: {e}")
    print("Please ensure sound files exist and are valid audio files.")

# --- Set the volume (0.0 to 1.0) Because no one likes popping their eardrum---
MUSIC_VOLUME = 0.1 # 10% volume

try:
    pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    # Play indefinitely (-1 means loop forever)
    pygame.mixer.music.play(-1) 
    print(f"Background music '{BACKGROUND_MUSIC_PATH}' started at {MUSIC_VOLUME*100}% volume, looping.")
except pygame.error as e:
    print(f"Error loading or playing music: {e}")
    print(f"Please ensure '{BACKGROUND_MUSIC_PATH}' exists and is a valid audio file.")

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
current_game_state = GAME_STATE_TITLE
current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE

# --- Game Variables for Game Room ---
hero = None
main_deck = []
unlocked_cards_pool = []
shuffling_start_time = 0
deck_drawn_card = None  # Holds the currently drawn card for display
game_session_seed = None # New: Variable to store the game seed


# --- Game Room UI Class (Your Original Version) ---
class GameRoomUI:
    """Manages the drawing of elements within the GAME_ROOM state."""
    def __init__(self, screen_width, screen_height):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height

        self.GRAY = (50, 50, 50)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.NEON_BLUE = (0, 255, 255)
        self.NEON_YELLOW = (255, 255, 0)
        self.NEON_CYAN = (0, 255, 255) # Same as NEON_BLUE but used to differentiate placeholder
        self.RED = (255, 0, 0) # For enemy health
        self.GREEN = (0, 200, 0) # Added for inventory items (from previous suggestion)
        self.DARK_GRAY = (30, 30, 30) # Added for empty inventory slots (from previous suggestion)

        # Fonts for game room UI
        self.stat_font = pygame.font.SysFont("Arial Black", 30)
        self.card_text_font = pygame.font.SysFont("Arial", 25)

        # Pre-calculate positions for static elements
        self.deck_x = (self.WIDTH - 360) // 2
        self.deck_y = 40 # 40px from top
        self.deck_rect = pygame.Rect(self.deck_x, self.deck_y, 360, 480)

        self.stat_width = 144
        self.stat_height = 144
        self.padding = 12

        # Player stats positioning
        self.health_x = self.padding
        self.attack_x = self.padding + self.stat_width + self.padding
        self.defense_x = self.padding + self.stat_width + self.padding + self.stat_width + self.padding
        self.stat_y = self.HEIGHT - self.stat_height - self.padding # 10px from bottom

        self.health_rect = pygame.Rect(self.health_x, self.stat_y, self.stat_width, self.stat_height)
        self.attack_rect = pygame.Rect(self.attack_x, self.stat_y, self.stat_width, self.stat_height)
        self.defense_rect = pygame.Rect(self.defense_x, self.stat_y, self.stat_width, self.stat_height)

        # Enemy stat placeholder dimensions
        self.enemy_stat_size = 120
        self.enemy_stat_padding = 2 

        # Calculate enemy stat positions (relative to the drawn card)
        self.enemy_stat_y = self.deck_y + self.deck_rect.height - self.enemy_stat_size - self.padding
        
        # Calculate x positions for enemy stats to be evenly distributed within the card width
        total_enemy_stat_width = (self.enemy_stat_size * 3) + (self.enemy_stat_padding * 2)
        start_x_for_enemy_stats = self.deck_x + (self.deck_rect.width - total_enemy_stat_width) // 2

        self.enemy_health_x = start_x_for_enemy_stats
        self.enemy_attack_x = start_x_for_enemy_stats + self.enemy_stat_size + self.enemy_stat_padding
        self.enemy_defense_x = start_x_for_enemy_stats + (self.enemy_stat_size + self.enemy_stat_padding) * 2

        self.enemy_health_rect = pygame.Rect(self.enemy_health_x, self.enemy_stat_y, self.enemy_stat_size, self.enemy_stat_size)
        self.enemy_attack_rect = pygame.Rect(self.enemy_attack_x, self.enemy_stat_y, self.enemy_stat_size, self.enemy_stat_size)
        self.enemy_defense_rect = pygame.Rect(self.enemy_defense_x, self.enemy_stat_y, self.enemy_stat_size, self.enemy_stat_size)

        #--- Inventory Icon management ---
        self.icon_size = 60
        self.icon_padding = 2 # Padding between icons

        self.inventory_start_x = self.padding # Start from left edge, with padding
        self.inventory_start_y = self.deck_y # Align with the top of the deck

        self.xp_display_area_width = 100 # Approx. width needed for XP text
        self.xp_display_area_height = 80 # Approx. height needed for two lines of text
        self.xp_padding_right = 20 # Padding from the right edge of the screen

        # Calculate the top-left corner of this conceptual area
        self.xp_display_x = self.WIDTH - self.xp_display_area_width - self.xp_padding_right
        self.xp_display_y = self.deck_y # Align with the top of the deck


    def draw_game_room(self, screen, hero_instance, deck_drawn_card): 
        """Draws all game room elements to the screen."""
        screen.fill(self.GRAY) # A distinct color for the game room

        # --- Draw Deck Placeholder ---
        pygame.draw.rect(screen, self.NEON_BLUE, self.deck_rect, 5) # Draw outline for visibility

        # --- Draw Drawn Card Placeholder (if a card is drawn) ---
        if deck_drawn_card:
            drawn_card_x = self.deck_x # Same position as deck for now
            drawn_card_y = self.deck_y
            drawn_card_rect = pygame.Rect(drawn_card_x, drawn_card_y, 360, 480)
            pygame.draw.rect(screen, self.NEON_CYAN, drawn_card_rect) # Drawn card is NEON_CYAN

            # Text on drawn card placeholder
            card_name_surface = self.card_text_font.render(
                f"{deck_drawn_card.name}", True, self.BLACK
            )
            card_name_rect = card_name_surface.get_rect(center=(drawn_card_x + 360 // 2, drawn_card_y + 50)) # Name near top
            screen.blit(card_name_surface, card_name_rect)

            card_type_surface = self.card_text_font.render(
                f"Type: {deck_drawn_card.card_type.replace('_', ' ').title()}", True, self.BLACK
            )
            card_type_rect = card_type_surface.get_rect(center=(drawn_card_x + 360 // 2, drawn_card_y + 80)) # Type below name
            screen.blit(card_type_surface, card_type_rect)


            # --- Draw Enemy Stat Placeholders if the drawn card is an "enemy" ---
            if deck_drawn_card.card_type == "enemy":
                # Enemy Health Placeholder
                pygame.draw.rect(screen, self.RED, self.enemy_health_rect, 3) # Outline
                enemy_health_text_surface = self.stat_font.render(f"HP: {deck_drawn_card.current_health}", True, self.WHITE)
                enemy_health_text_rect = enemy_health_text_surface.get_rect(center=self.enemy_health_rect.center)
                screen.blit(enemy_health_text_surface, enemy_health_text_rect)

                # Enemy Attack Placeholder
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_attack_rect, 3) # Outline
                enemy_attack_text_surface = self.stat_font.render(f"ATK: {deck_drawn_card.attack}", True, self.WHITE)
                enemy_attack_text_rect = enemy_attack_text_surface.get_rect(center=self.enemy_attack_rect.center)
                screen.blit(enemy_attack_text_surface, enemy_attack_text_rect)

                # Enemy Defense Placeholder
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_defense_rect, 3) # Outline
                enemy_defense_text_surface = self.stat_font.render(f"DEF: {deck_drawn_card.current_defense}", True, self.WHITE)
                enemy_defense_text_rect = enemy_defense_text_surface.get_rect(center=self.enemy_defense_rect.center)
                screen.blit(enemy_defense_text_surface, enemy_defense_text_rect)

            elif deck_drawn_card.card_type == "equipment": # This branch also needs its stats displayed correctly
                # Equipment Health Placeholder (for its 'charges' or 'durability' if applicable)
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_health_rect, 3) # Outline
                # Using 'health' as a general stat for equipment, e.g., durability
                equipment_health_text_surface = self.stat_font.render(f"HP: {deck_drawn_card.health}", True, self.WHITE) 
                equipment_health_text_rect = equipment_health_text_surface.get_rect(center=self.enemy_health_rect.center)
                screen.blit(equipment_health_text_surface, equipment_health_text_rect)

                # Equipment Attack Placeholder
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_attack_rect, 3) # Outline
                equipment_attack_text_surface = self.stat_font.render(f"ATK: {deck_drawn_card.attack}", True, self.WHITE)
                equipment_attack_text_rect = equipment_attack_text_surface.get_rect(center=self.enemy_attack_rect.center)
                screen.blit(equipment_attack_text_surface, equipment_attack_text_rect)

                # Equipment Defense Placeholder
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_defense_rect, 3) # Outline
                equipment_defense_text_surface = self.stat_font.render(f"DEF: {deck_drawn_card.defense}", True, self.WHITE)
                equipment_defense_text_rect = equipment_defense_text_surface.get_rect(center=self.enemy_defense_rect.center)
                screen.blit(equipment_defense_text_surface, equipment_defense_text_rect)

            elif deck_drawn_card.card_type == "level up": 
                # Level Up card functions
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_health_rect, 3) # Outline
                # Using 'health' as a general stat for Level, e.g., durability
                level_health_text_surface = self.stat_font.render(f"HP: {deck_drawn_card.health}", True, self.WHITE) 
                level_health_text_rect = level_health_text_surface.get_rect(center=self.enemy_health_rect.center)
                screen.blit(level_health_text_surface, level_health_text_rect)

                # Level Attack Placeholder
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_attack_rect, 3) # Outline
                level_attack_text_surface = self.stat_font.render(f"ATK: {deck_drawn_card.attack}", True, self.WHITE)
                level_attack_text_rect = level_attack_text_surface.get_rect(center=self.enemy_attack_rect.center)
                screen.blit(level_attack_text_surface, level_attack_text_rect)

                # Level Defense Placeholder
                pygame.draw.rect(screen, self.NEON_YELLOW, self.enemy_defense_rect, 3) # Outline
                level_defense_text_surface = self.stat_font.render(f"DEF: {deck_drawn_card.defense}", True, self.WHITE)
                level_defense_text_rect = level_defense_text_surface.get_rect(center=self.enemy_defense_rect.center)
                screen.blit(level_defense_text_surface, level_defense_text_rect)

            else: # For Dungeon Exit
                card_info_surface = self.card_text_font.render(
                    "No info has been added yet", True, self.BLACK
                )
                card_info_rect = card_info_surface.get_rect(center=(drawn_card_x + 360 // 2, drawn_card_y + 480 // 2 + 20))
                screen.blit(card_info_surface, card_info_rect)

        # --- Draw Hero Stat Placeholders ---
        # Health Placeholder
        pygame.draw.rect(screen, self.NEON_YELLOW, self.health_rect, 5) # Outline
        health_text_surface = self.stat_font.render(f"HP: {hero_instance.health}", True, self.WHITE)
        health_text_rect = health_text_surface.get_rect(center=self.health_rect.center)
        screen.blit(health_text_surface, health_text_rect)

        # Attack Placeholder
        pygame.draw.rect(screen, self.NEON_YELLOW, self.attack_rect, 5) # Outline
        attack_text_surface = self.stat_font.render(f"ATK: {hero_instance.attack}", True, self.WHITE)
        attack_text_rect = attack_text_surface.get_rect(center=self.attack_rect.center)
        screen.blit(attack_text_surface, attack_text_rect)

        # Defense Placeholder
        pygame.draw.rect(screen, self.NEON_YELLOW, self.defense_rect, 5) # Outline
        defense_text_surface = self.stat_font.render(f"DEF: {hero_instance.defense}", True, self.WHITE)
        defense_text_rect = defense_text_surface.get_rect(center=self.defense_rect.center)
        screen.blit(defense_text_surface, defense_text_rect)

        # --- CALL THE INVENTORY ICON DRAWING ---
        self.draw_inventory_icons(screen, hero_instance) 

        #--- CALL XP DRAWING ---
        self.draw_xp_display(screen, hero_instance)

    #--- Inventory icon function (this method is correct as is, but needed to be called) ---
    def draw_inventory_icons(self, screen, hero_instance):
        current_x = self.inventory_start_x
        current_y = self.inventory_start_y

        #Quick adjust, code it properly later
        current_x = current_x - 12
        
        # Draw placeholder slots up to hero.equipment_slots
        for i in range(hero_instance.equipment_slots):
            slot_rect = pygame.Rect(current_x, current_y + (self.icon_size + self.icon_padding) * i, self.icon_size, self.icon_size)
            pygame.draw.rect(screen, self.DARK_GRAY, slot_rect, 0) # Draw empty slot background
            pygame.draw.rect(screen, self.GRAY, slot_rect, 1) # Draw slot border

        # Draw actual equipped items
        for i, item_card in enumerate(hero_instance.current_equipment):
            # Calculate position for this item
            item_x = self.inventory_start_x
            item_y = self.inventory_start_y + (self.icon_size + self.icon_padding) * i
            
            #Quick adjust, code it properly later
            item_x = item_x - 12

            item_rect = pygame.Rect(item_x, item_y, self.icon_size, self.icon_size)

            color = (0, 150, 0) if item_card.card_type == "equipment" else (150, 0, 150) # Example colors
            
            # Draw background square
            pygame.draw.rect(screen, color, item_rect)
            # Draw border
            pygame.draw.rect(screen, self.WHITE, item_rect, 2) # White border for equipped item

            text_surface = self.card_text_font.render(item_card.name[0].upper(), True, self.BLACK) # Just first letter
            text_rect = text_surface.get_rect(center=item_rect.center)
            screen.blit(text_surface, text_rect)
    
    def draw_xp_display(self, screen, hero_instance):
        """Draws the hero's current XP as text on the screen, right-aligned."""
        text_right_anchor_x = self.WIDTH - self.xp_padding_right # Use the screen width minus your right padding
        #Quick fix, update properly later
        text_right_anchor_x = text_right_anchor_x + 10

        xp_label_surface = self.stat_font.render("XP", True, self.WHITE) 
        xp_label_rect = xp_label_surface.get_rect(
            topright=(text_right_anchor_x, self.xp_display_y + 10) # 10px down from top, right-aligned
        ) 
        screen.blit(xp_label_surface, xp_label_rect)

        xp_value_surface = self.stat_font.render(f"{hero_instance.experience}", True, self.WHITE)
        xp_value_rect = xp_value_surface.get_rect(
            topright=(text_right_anchor_x, self.xp_display_y + 40) 
        ) 
        screen.blit(xp_value_surface, xp_value_rect)


    def get_deck_rect(self):
        return self.deck_rect
    def get_health_rect(self):
        return self.health_rect
    def get_attack_rect(self):
        return self.attack_rect
    def get_defense_rect(self):
        return self.defense_rect
    def get_enemy_health_rect(self):
        return self.enemy_health_rect
    def get_enemy_attack_rect(self):
        return self.enemy_attack_rect
    def get_enemy_defense_rect(self):
        return self.enemy_defense_rect


# --- Game Room UI Instance ---
game_room_ui = GameRoomUI(WIDTH, HEIGHT) # Instantiate the UI renderer
# --- Battle Manager Instance ---
battle_manager = BattleManager(WIDTH, HEIGHT, game_room_ui) # Pass UI instance to BattleManager
# --- Inventory Manager Instance ---
inventory_manager = InventoryManager(WIDTH, HEIGHT, game_room_ui) # Pass UI instance to EquipmentManager
# --- Level Manager Instance ---
level_manager = LevelManager(WIDTH, HEIGHT, game_room_ui) # Pass UI instance to LevelManager

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

                hero, main_deck, unlocked_cards_pool, game_session_seed = setup_new_game() 
                shuffling_start_time = pygame.time.get_ticks() # Start timer for shuffling animation
                current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Reset sub-state
            elif current_game_state == GAME_STATE_GAME_ROOM:
                if current_game_room_sub_state == GAME_ROOM_SUB_STATE_IDLE:
                    if game_room_ui.get_deck_rect().collidepoint(event.pos): # Use getter
                        if main_deck:
                            deck_drawn_card = main_deck.pop(0)
                            print(f"Drew card: {deck_drawn_card.name}")
                            SOUND_EFFECTS['card_draw'].play()

                            if deck_drawn_card.card_type == "enemy":
                                # Added bug correction to prevent infinite combat
                                if deck_drawn_card.defense > 0:
                                    damage_potentail = deck_drawn_card.defense - (hero.attack - hero.min_attack) # this gives us how much defense will be destroyed
                                    if damage_potentail == hero.min_attack:
                                        if deck_drawn_card.attack == hero.min_defense:
                                            deck_drawn_card.defense = hero.min_attack - 1

                                current_game_room_sub_state = battle_manager.start_combat(deck_drawn_card)
                                
                            elif deck_drawn_card.card_type == "dungeon exit":
                                current_game_room_sub_state = battle_manager.start_dungeon_exit_animation()
                            
                            
                            elif deck_drawn_card.card_type == "equipment":
                                current_game_room_sub_state = inventory_manager.start_inventory(deck_drawn_card)
                                pygame.time.set_timer(NEXT_TURN_EVENT, 2000)

                            elif deck_drawn_card.card_type == "level up": 
                                current_game_room_sub_state = level_manager.start_level_up(deck_drawn_card)
                                pygame.time.set_timer(NEXT_TURN_EVENT, 2000) # Short timer to allow "Level Up!" pop-up to show

                            else:
                                print(f"Drew {deck_drawn_card.card_type}: {deck_drawn_card.name}")
                        else:
                            print("Deck is empty!")
                            deck_drawn_card = Card("Empty", "message", name="Deck Empty!")
                
                # --- Combat End Interaction Clicks (only to dismiss messages) ---
                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_COMBAT_END_VICTORY:
                    if not battle_manager.combat_text_active: # Only allow click if animation finished
                        current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Back to idle to draw next card
                        deck_drawn_card = None # Clear the defeated enemy card
                        hero.experience += battle_manager.current_enemy.xp_gain # Gain XP from defeated enemy
                        print(f"Gained {battle_manager.current_enemy.xp_gain} XP. Total XP: {hero.experience}")
                        battle_manager.current_enemy = None # Clear current enemy in BattleManager
                        print("Combat ended. Ready to draw next card.")

                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_COMBAT_END_DEFEAT:
                    if not battle_manager.combat_text_active: # Only allow click if animation finished
                        print(f"Game Over. Returning to title screen. This Game's Seed was: {game_session_seed}") # Modified line
                        current_game_state = GAME_STATE_TITLE
                        hero = None # Reset hero
                        main_deck = [] # Clear deck
                        unlocked_cards_pool = [] # Clear unlocked pool
                        deck_drawn_card = None
                        battle_manager.current_enemy = None # Clear current enemy in BattleManager
                        current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE # Reset sub-state
                        tap_to_start_start_time = pygame.time.get_ticks() # Reset title screen animation timer

                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_EQUIPMENT_START: # This is the state where "Treasure!" has animated
                    print("NEXT_TURN_EVENT triggered for EQUIPMENT_FOUND state. Transitioning to applying buffs.")
                    current_game_room_sub_state = inventory_manager.handle_player_buff(hero) 
                    pygame.time.set_timer(NEXT_TURN_EVENT, 2000)

                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_LEVEL_UP_START:
                    print("NEXT_TURN_EVENT triggered for LEVEL_UP_FOUND state. Transitioning to applying boosts.")
                    current_game_room_sub_state = level_manager.handle_level_up(hero)
                    pygame.time.set_timer(NEXT_TURN_EVENT, 2000) # Give time for boost pop-ups
                
                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_EQUIPMENT_ADDED:
                    print("Equipment Added. Ready to draw next card.")
                    current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE
                    pygame.time.set_timer(NEXT_TURN_EVENT, 0) # Stop any lingering timers for this state
                    deck_drawn_card = None

                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_LEVEL_UP_ADDED: # --- NEW ---
                    print("NEXT_TURN_EVENT triggered for LEVEL_UP_ADDED state. Transitioning to IDLE.")
                    current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE
                    pygame.time.set_timer(NEXT_TURN_EVENT, 0) # Turn off timer
                        
                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_DUNGEON_EXIT_ANIMATION:
                    if not battle_manager.combat_text_active: # Only allow click if animation finished
                        current_game_room_sub_state = GAME_ROOM_SUB_STATE_REWARD_SCREEN
                elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_REWARD_SCREEN:
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

            # --- Handle Combat TEvents ---
            if current_game_room_sub_state == GAME_ROOM_SUB_STATE_PLAYER_TURN:
                if hero and battle_manager.current_enemy: # Ensure both exist before attacking
                    new_sub_state = battle_manager.handle_player_attack(hero)
                    current_game_room_sub_state = new_sub_state
                    
                    if new_sub_state == GAME_ROOM_SUB_STATE_ENEMY_TURN:
                        pygame.time.set_timer(NEXT_TURN_EVENT, 2000) # Enemy turn auto-triggers after 1 sec
                else:
                    print("Error: Player or enemy missing during player turn.")
                    current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE 

            elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_ENEMY_TURN:
                if hero and battle_manager.current_enemy: # Ensure both exist before attacking
                    new_sub_state = battle_manager.handle_enemy_attack(hero)
                    current_game_room_sub_state = new_sub_state

                    if new_sub_state == GAME_ROOM_SUB_STATE_PLAYER_TURN:
                        pygame.time.set_timer(NEXT_TURN_EVENT, 2000) 
                else:
                    print("Error: Player or enemy missing during enemy turn.")
                    current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE 
            
            elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_EQUIPMENT_START:
                print("NEXT_TURN_EVENT triggered for EQUIPMENT_START state. Transitioning to applying buffs.")
                current_game_room_sub_state = inventory_manager.handle_player_buff(hero)
                pygame.time.set_timer(NEXT_TURN_EVENT, 2000) 

            elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_EQUIPMENT_ADDED:
                print("NEXT_TURN_EVENT triggered for EQUIPMENT_ADDED state. Returning to IDLE.")
                current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE

            elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_LEVEL_UP_START:
                print("NEXT_TURN_EVENT triggered for LEVEL_UP_START state. Transitioning to applying buffs.")
                current_game_room_sub_state = level_manager.handle_level_up(hero) 
                pygame.time.set_timer(NEXT_TURN_EVENT, 2000) 

            elif current_game_room_sub_state == GAME_ROOM_SUB_STATE_LEVEL_UP_ADDED:
                print("NEXT_TURN_EVENT triggered for LEVEL_UP_ADDED state. Returning to IDLE.")
                # Buff animation is done, go back to IDLE
                current_game_room_sub_state = GAME_ROOM_SUB_STATE_IDLE


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
        original_deck_rect_ui = game_room_ui.deck_rect
        original_health_rect_ui = game_room_ui.health_rect

        # Temporarily update the UI instance's rects for drawing
        game_room_ui.deck_rect = original_deck_rect_ui.move(shake_offsets['deck_rect'])
        game_room_ui.health_rect = original_health_rect_ui.move(shake_offsets['health_rect'])

        # Pass the current_enemy from battle_manager to draw_game_room
        game_room_ui.draw_game_room(screen, hero, battle_manager.current_enemy if battle_manager.current_enemy else deck_drawn_card)

        # Restore original rects after drawing to avoid permanent offset for next frame's logic
        game_room_ui.deck_rect = original_deck_rect_ui
        game_room_ui.health_rect = original_health_rect_ui

        # Update and draw combat animations (text, damage numbers)
        new_sub_state_after_anim = battle_manager.update_animations(current_game_room_sub_state)
        
        if new_sub_state_after_anim == GAME_ROOM_SUB_STATE_PLAYER_TURN and current_game_room_sub_state != GAME_ROOM_SUB_STATE_PLAYER_TURN:
            pygame.time.set_timer(NEXT_TURN_EVENT, 1000) # Player's first turn delay
        
        current_game_room_sub_state = new_sub_state_after_anim # Update the main state variable

        inventory_manager.update_popups()
        level_manager.update_popups()

        battle_manager.draw_combat_elements(screen)

        inventory_manager.draw_popups(screen)
        level_manager.draw_popups(screen)

    # --- Update Display ---
    pygame.display.flip()

    # --- Cap Frame Rate ---
    clock.tick(FPS)

pygame.quit()
sys.exit()