import pygame
import random

# --- Game Logic Classes ---
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
        self.name = name if name else card_type.replace('_', ' ').title() # Default name if not provided
        self.theme = theme
        self.card_type = card_type # "enemy", "equipment", "level_up", "dungeon_exit"
        self.health = health # For enemy HP, or equipment/level_up heal amount
        self.attack = attack # For enemy attack, or equipment attack boost
        self.defense = defense # For enemy defense, or equipment defense boost (temp HP)
        self.cost = cost # XP cost for equipment/level_up
        self.xp_gain = xp_gain # XP gained from defeating enemy or selling equipment
        self.inventory_boost = inventory_boost # For backpack equipment

def setup_new_game():
    """Initializes a new game session, including hero, main deck, and unlocked card pool.
    Returns: Tuple (Hero object, main_deck list, unlocked_cards_pool list)
    """
    hero_instance = Hero() # Initialize hero stats

    # Placeholder for 21 starter cards (list of Card objects)
    # This will be replaced with actual card definitions later
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

    main_deck_list = [Card(*data) for data in starter_cards_data]

    # Add the dungeon exit card in the middle section (half way +/- 3 cards)
    dungeon_exit_card = Card("Dungeon", "dungeon_exit", name="Dungeon Exit")
    exit_position = len(main_deck_list) // 2 + random.randint(-3, 3) # Roughly middle +/- 3
    exit_position = max(0, min(exit_position, len(main_deck_list))) # Ensure valid index
    main_deck_list.insert(exit_position, dungeon_exit_card)

    random.shuffle(main_deck_list) # Shuffle the deck

    # Placeholder for the other 80 cards
    # This will be populated with actual cards from other themed sets later
    unlocked_cards_pool_list = [Card("Placeholder", "placeholder") for _ in range(80)]

    return hero_instance, main_deck_list, unlocked_cards_pool_list

