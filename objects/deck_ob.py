# deck_ob.py
import pygame
import random
import csv # Import the csv module
import time # Import time for seed generation

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

# --- Internal Helper Function to Load Raw Card Data from CSV ---
def _load_raw_card_data_from_csv(file_path):
    """
    Loads raw card data from a CSV file into a list of tuples,
    matching the (theme, type, hp, atk, def, cost, xp_gain, inv_boost, name) format.
    Handles 'Quantity' to duplicate entries and cleans/converts data types.
    """
    raw_card_data = [] # This will conceptually replace your starter_cards_data
    
    print(f"Attempting to load CSV from: {file_path}") # Added debug print
    
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            # Print header to ensure it's read correctly
            print(f"CSV Headers: {reader.fieldnames}") 
            
            row_count = 0 # Added for debugging
            for row in reader:
                row_count += 1
                
                # IMPORTANT: Check if the row itself is None or an empty dictionary
                if row is None or not row:
                    print(f"Warning: Skipping empty or malformed row {row_count}. Content: {row}")
                    continue # Skip to the next row
                    
                try:
                    # Use .get() with a default empty string to prevent NoneType errors
                    # Also, strip whitespace immediately after getting the value
                    theme = row.get('Theme', '').strip()
                    card_type = row.get('Type', '').strip().lower()
                    name = row.get('Name', '').strip()

                    # Convert numeric fields, handling empty or '-' values as 0
                    health = int(row.get('Health', '0').strip().replace('-', '0'))
                    attack = int(row.get('Attack', '0').strip().replace('-', '0'))
                    defense = int(row.get('Defense', '0').strip().replace('-', '0'))
                    
                    # 'Cost' column is not in your CSV, so default to 0
                    cost = 0 
                    
                    # Handle 'XP' suffix and potential '-' values
                    xp_str = row.get('XP', '0').strip().replace('XP', '').replace('-', '0')
                    xp_gain = int(xp_str)
                    
                    inventory_boost = int(row.get('Inventory', '0').strip().replace('-', '0'))
                    quantity = int(row.get('Quantity', '1').strip()) # Default to 1 if not specified

                    # Add the card data tuple 'quantity' times
                    # Only add if theme, card_type, and name are not empty after stripping
                    if theme and card_type and name:
                        for _ in range(quantity):
                            raw_card_data.append((theme, card_type, health, attack, defense, cost, xp_gain, inventory_boost, name))
                    else:
                        print(f"Warning: Skipping row {row_count} due to empty Theme, Type, or Name (after stripping): {row}")
                
                except ValueError as e:
                    print(f"Warning: Could not parse numeric value for row {row_count}: {row}. Error: {e}. Skipping this card entry.")
                except KeyError as e:
                    print(f"Warning: Missing expected column '{e}' in row {row_count}: {row}. Please check CSV headers. Skipping this card entry.")
                except Exception as e: # Catch any other unexpected errors during row processing
                    print(f"An unexpected error occurred while processing row {row_count}: {row}. Error: {e}. Skipping this card entry.")
                    
    except FileNotFoundError:
        print(f"Error: CSV file not found at {file_path}. No cards loaded.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while opening/reading CSV: {e}. No cards loaded.")
        return []

    print(f"Successfully loaded {len(raw_card_data)} raw card entries from CSV.") # Added debug print
    return raw_card_data


def setup_new_game():
    """Initializes a new game session, including hero, main deck, and unlocked card pool.
    Returns: Tuple (Hero object, main_deck list, unlocked_cards_pool list, game_seed)
    """
    # Generate a new seed based on current time
    game_seed = int(time.time() * 1000) # Using milliseconds for better granularity
    random.seed(game_seed) # Set the seed for random operations
    print(f"New game started with seed: {game_seed}") # Added debug print

    hero_instance = Hero() # Initialize hero stats

    # --- CSV File Path ---
    # IMPORTANT: Adjust this path if your 'cards.csv' is in a different location
    csv_file_path = "/home/mat_dev/boot.dev/projects/github.com/matomatocuztheres2/delver_project/data/cards.csv"

    # Load all raw card data from CSV into the desired tuple format
    all_raw_card_data = _load_raw_card_data_from_csv(csv_file_path)

    # Print the requested prompt with the total number of cards loaded
    print(f"The deck currently contains {len(all_raw_card_data)} amount of cards based on the CSV data.")

    main_deck_list = []
    dungeon_exit_card = None

    # Separate Dungeon Exit and other cards from the raw data
    cards_for_theming = []
    for card_tuple in all_raw_card_data:
        # card_type is at index 1 in the tuple
        if len(card_tuple) > 1 and card_tuple[1] == 'dungeon exit':
            dungeon_exit_card = Card(*card_tuple)
        else:
            cards_for_theming.append(card_tuple)
    
    print(f"Found {len(cards_for_theming)} non-Dungeon Exit cards for theme selection.") # Added debug print
    
    # --- Theme Selection and Deck Generation ---
    # Theme is at index 0 in the tuple, ensure card_tuple has at least one element
    themes = list(set(card[0] for card in cards_for_theming if len(card) > 0))
    
    if themes:
        selected_theme = random.choice(themes)
        print(f"Randomly selected dungeon theme: {selected_theme}")
        
        # Populate the main_deck_list with Card objects for the selected theme
        for card_tuple in cards_for_theming:
            # Ensure card_tuple has at least one element for indexing
            if len(card_tuple) > 0 and card_tuple[0] == selected_theme: # Theme is at index 0
                main_deck_list.append(Card(*card_tuple))
        print(f"Main deck populated with {len(main_deck_list)} cards for theme '{selected_theme}'.") # Added debug print
    else:
        print("No themes found to select from, or no non-Dungeon Exit cards available in CSV.")
        # If no cards are loaded, main_deck_list will remain empty

    # Shuffle the main deck BEFORE inserting the dungeon exit
    if main_deck_list:
        random.shuffle(main_deck_list)
        print(f"Main deck shuffled. Current size: {len(main_deck_list)}") # Added debug print

        # Add the dungeon exit card (if it was found in the CSV)
        if dungeon_exit_card:
            exit_position = len(main_deck_list) // 2 + random.randint(-3, 3) # Roughly middle +/- 3
            exit_position = max(0, min(exit_position, len(main_deck_list))) # Ensure valid index
            main_deck_list.insert(exit_position, dungeon_exit_card)
            print(f"Dungeon Exit card inserted at position {exit_position}. New deck size: {len(main_deck_list)}") # Added debug print
        else:
            print("Warning: Dungeon Exit card not found in CSV or could not be created. Game might not have an exit.")
    else:
        print("Main deck is empty after theme selection and card generation.")

    # The unlocked_cards_pool remains empty as per your original code's placeholder
    unlocked_cards_pool_list = []

    return hero_instance, main_deck_list, unlocked_cards_pool_list, game_seed # Return the seed
