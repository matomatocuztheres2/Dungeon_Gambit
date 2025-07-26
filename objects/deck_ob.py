# deck_ob.py
import pygame
import random

# --- Hero and Card Classes ---
class Hero:
    """Represents the player's hero character and their stats."""
    def __init__(self):
        self.health = 5
        self.attack = 1
        self.defense = 0 # Now functions as temporary HP
        self.max_health = 5 # For level up benefit
        self.equipment_slots = 3
        self.current_equipment = [] # List of equipped items
        self.experience = 0

class Card:
    """Represents a single card in the game deck."""
    def __init__(self, theme, card_type, health=0, attack=0, defense=0, cost=0, xp_gain=0, inventory_boost=0, name=""):
        self.name = name if name else card_type.replace('_', ' ').title()
        self.theme = theme
        self.card_type = card_type # "enemy", "equipment", "level_up", "dungeon_exit"
        self.health = health # For enemy HP, or equipment/level_up heal amount
        self.attack = attack # For enemy attack, or equipment attack boost
        self.defense = defense # For enemy defense, or equipment defense boost (temp HP)
        self.cost = cost # XP cost for equipment/level_up
        self.xp_gain = xp_gain # XP gained from defeating enemy or selling equipment
        self.inventory_boost = inventory_boost # For backpack equipment

        # New: Current health for enemies (will be initialized from 'health' for enemy cards)
        self.current_health = health
        # New: Current defense for enemies (will be initialized from 'defense' for enemy cards)
        self.current_defense = defense


def setup_new_game():
    """Initializes a new game session, including hero, main deck, and unlocked card pool.
    Returns: Tuple (Hero object, main_deck list, unlocked_cards_pool list)
    """
    hero_instance = Hero() # Initialize hero stats

    # Placeholder for 21 starter cards (list of Card objects)
    starter_cards_data = [
        # Enemies: (theme, type, hp, atk, def, cost, xp_gain, inv_boost, name)
        ("Starter", "enemy", 1, 1, 0, 0, 10, 0, "Rat"), ("Starter", "enemy", 1, 1, 0, 0, 10, 0, "Rat"),
        ("Starter", "enemy", 1, 1, 0, 0, 10, 0, "Rat"), ("Starter", "enemy", 1, 1, 0, 0, 10, 0, "Rat"),
        ("Starter", "enemy", 2, 1, 0, 0, 20, 0, "Goblin"), ("Starter", "enemy", 2, 1, 0, 0, 20, 0, "Goblin"),
        ("Starter", "enemy", 2, 1, 0, 0, 20, 0, "Goblin"), ("Starter", "enemy", 2, 1, 0, 0, 20, 0, "Goblin"),
        ("Starter", "enemy", 5, 1, 0, 0, 50, 0, "Orc"), ("Starter", "enemy", 5, 1, 0, 0, 50, 0, "Orc"),
        # Equipment: (theme, type, hp, atk, def, cost, xp_gain, inv_boost, name)
        ("Starter", "equipment", 0, 1, 0, 0, 10, 0, "Rusty Sword"), # Attack+1
        ("Starter", "equipment", 0, 0, 2, 0, 10, 0, "Worn Shield"), # Defense+2 (Temp HP)
        ("Starter", "equipment", 0, 0, 0, 0, 10, 1, "Backpack"), # Inventory slot +1
        ("Starter", "equipment", 0, 0, 1, 0, 10, 0, "Leather Vest"), # Defense+1
        ("Starter", "equipment", 0, 0, 0, 0, 10, 0, "Healing Potion"), # Instant heal 3HP (example)
        # Level Up: (theme, type, hp, atk, def, cost, xp_gain, inv_boost, name)
        ("Starter", "level_up", 0, 0, 0, 40, 0, 0, "Heal Spell"), # Resets HP to Max
        ("Starter", "level_up", 5, 0, 0, 40, 0, 0, "HP Boost"), # Increases Max HP by 5
        ("Starter", "level_up", 0, 1, 0, 40, 0, 0, "Strength Training"), # Increases Attack by 1
        ("Starter", "level_up", 0, 0, 1, 40, 0, 0, "Fortitude Training"), # Increases Defense by 1
        ("Starter", "level_up", 0, 0, 0, 40, 0, 0, "Critical Strike") # Special Ability
    ]

    # Convert starter card data to Card objects
    main_deck_list = [Card(*data) for data in starter_cards_data]

    # Shuffle the existing starter cards BEFORE inserting the dungeon exit
    random.shuffle(main_deck_list)

    # Add the dungeon exit card in the middle section (half way +/- 3 cards)
    dungeon_exit_card = Card("Dungeon", "dungeon_exit", name="Dungeon Exit")
    exit_position = len(main_deck_list) // 2 + random.randint(-3, 3) # Roughly middle +/- 3
    exit_position = max(0, min(exit_position, len(main_deck_list))) # Ensure valid index
    main_deck_list.insert(exit_position, dungeon_exit_card)

    # Placeholder for the other 80 cards
    unlocked_cards_pool_list = [Card("Placeholder", "placeholder") for _ in range(80)]

    return hero_instance, main_deck_list, unlocked_cards_pool_list


# --- Game Room UI Class ---
class GameRoomUI:
    """Manages the drawing of elements within the GAME_ROOM state."""
    def __init__(self, screen_width, screen_height):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height

        # Define colors (can also be passed or imported if needed from a constants file)
        self.GRAY = (50, 50, 50)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.NEON_BLUE = (0, 255, 255)
        self.NEON_YELLOW = (255, 255, 0)
        self.NEON_CYAN = (0, 255, 255) # Same as NEON_BLUE but used to differentiate placeholder
        self.RED = (255, 0, 0) # For enemy health

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
        # Position them slightly above the bottom of the drawn card, centered horizontally
        self.enemy_stat_y = self.deck_y + self.deck_rect.height - self.enemy_stat_size - self.padding
        
        # Calculate x positions for enemy stats to be evenly distributed within the card width
        # (drawn_card_x + padding) for left, (drawn_card_x + card_width - padding - enemy_stat_size) for right
        # Or, center all three within the card, with padding in between
        total_enemy_stat_width = (self.enemy_stat_size * 3) + (self.enemy_stat_padding * 2)
        start_x_for_enemy_stats = self.deck_x + (self.deck_rect.width - total_enemy_stat_width) // 2

        self.enemy_health_x = start_x_for_enemy_stats
        self.enemy_attack_x = start_x_for_enemy_stats + self.enemy_stat_size + self.enemy_stat_padding
        self.enemy_defense_x = start_x_for_enemy_stats + (self.enemy_stat_size + self.enemy_stat_padding) * 2

        self.enemy_health_rect = pygame.Rect(self.enemy_health_x, self.enemy_stat_y, self.enemy_stat_size, self.enemy_stat_size)
        self.enemy_attack_rect = pygame.Rect(self.enemy_attack_x, self.enemy_stat_y, self.enemy_stat_size, self.enemy_stat_size)
        self.enemy_defense_rect = pygame.Rect(self.enemy_defense_x, self.enemy_stat_y, self.enemy_stat_size, self.enemy_stat_size)


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

            else: # For non-enemy cards, display generic card info
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