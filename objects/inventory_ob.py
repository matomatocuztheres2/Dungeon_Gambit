import pygame
import math

class IntventoryManager:
    def __init__(self, screen_width, screen_height, game_room_ui_instance):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.game_room_ui = game_room_ui_instance # Reference to the UI object to get rects

        # Define colors (re-defining for self-containment, or import from a constants file later)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0) # For damage feedback
        self.BLUE = (0, 0, 255) # For defense/block feedback
        self.GREEN = (11, 102, 35) # For health feedback

        # Fonts
        self.buff_text_font = pygame.font.SysFont("Arial", 25, bold=True) # For floating damage numbers

        # Current combat state information
        self.current_equipment = None # The actual equipment Card object
        self.current_game_room_sub_state = "IDLE" # Managed externally, but useful for internal logic

        self.buff_display_list = [] # List of {'value': int, 'color': (R,G,B), 'pos': (x,y), 'start_time': ticks}

    def _display_buff_text(self, value, color, target_rect_center):
        """Adds a buff/healing text element to be displayed."""
        pos_x = target_rect_center[0]
        pos_y = target_rect_center[1] - 30 # 30 pixels above the center
        self.buff_display_list.append({
            'value': value,
            'color': color,
            'pos': (pos_x, pos_y),
            'start_time': pygame.time.get_ticks()
        })
    
    def start_inventory(self, equipment_card):
        """Initializes inventory with a new equipment and starts the 'Treasure!' animation."""
        self.current_equipment = equipment_card
        self.buff_text_message = "Treasure!"
        self.buff_text_start_time = pygame.time.get_ticks()
        self.buff_text_alpha = 255
        self.buff_text_scale = 0.1
        self.buff_text_active = True
        return "EQUIPMENT_FOUND"
    
    def handle_player_buff(self, hero_instance):
        """
        Processes the player's buff earned.
        Returns the new sub_state.
        """

        if not self.current_equipment:
            print("Error: No equipment to add.")
            return "IDLE" # Should not happen in equipment state
        
        #Temp Test: Delete later
        print("Begin Buff Add - Collecting player data")

        hero_health = hero_instance.health
        hero_attack = hero_instance.attack
        hero_defense = hero_instance.defense
        hero_inventory = hero_instance.equipment_slots
        hero_xp = hero_instance.experience

        #Temp Test: Delete later
        print("--Hero stats pulled--")
        print(f"Hero inventory: {hero_inventory}")

        #Temp Test: Delete later
        print("Begin Buff Add - Updating player data")

        effective_heal_from_equipment = self.current_equipment.current_health
        effective_attack_from_equipment = self.current_equipment.attack
        effective_defense_from_equipment = self.current_equipment.current_defense
        effective_inventory_from_equipment = self.current_equipment.inventory_boost

        if hero_instance.health < hero_instance.max_health:
            hero_instance.health += effective_heal_from_equipment
            if hero_instance.health > hero_instance.max_health:
                effective_heal_from_equipment = 0
                hero_instance.health = hero_instance.max_health
                hero_instance.experience += self.current_equipment.xp_gain
                print(f"Potion could not be fully used the rest was sold for {self.current_equipment.xp_gain}. Total XP: {hero_instance.experience}")
        elif hero_instance.health == hero_instance.max_health:
            effective_heal_from_equipment = 0
            hero_instance.experience += self.current_equipment.xp_gain
            print(f"Potion could not be fully used the rest was sold for {self.current_equipment.xp_gain}. Total XP: {hero_instance.experience}")
        hero_instance.attack += effective_attack_from_equipment
        hero_instance.defense += effective_defense_from_equipment
        hero_instance.equipment_slots += effective_inventory_from_equipment
        
        #Draw buff text
        if effective_heal_from_equipment > 0:
            self._display_buff_text(effective_heal_from_equipment, self.GREEN, self.game_room_ui.get_health_rect().center) # Change to player health rectangle
            print(f"Complete Buff Add - Health added: {hero_health} + {effective_heal_from_equipment} for a total of {hero_instance.health}")

        if effective_attack_from_equipment > 0:
            self._display_buff_text(effective_attack_from_equipment, self.GREEN, self.game_room_ui.get_attack_rect().center) # Change to player attack rectangle
            print(f"Complete Buff Add - Attack added: {hero_attack} + {effective_attack_from_equipment} for a total of {hero_instance.attack}")
        
        if effective_defense_from_equipment > 0:
            self._display_buff_text(effective_defense_from_equipment, self.GREEN, self.game_room_ui.get_defense_rect().center) # Change to player defense rectangle
            print(f"Complete Buff Add - Defense added: {hero_defense} + {effective_defense_from_equipment} for a total of {hero_instance.defense}")

        if effective_inventory_from_equipment > 0:
            #Added floating buff text for a bag later
            print(f"Complete Buff Add - Defense added: {hero_inventory} + {effective_inventory_from_equipment} for a total of {hero_instance.equipment_slots}")

        self.current_equipment = None # Clear the equipment
        return "EQUIPMENT_ADDED"
