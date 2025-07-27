import pygame
import math

class InventoryManager: # CORRECTED TYPO HERE
    def __init__(self, screen_width, screen_height, game_room_ui_instance):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.game_room_ui = game_room_ui_instance 

        # Define colors 
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0) 
        self.BLUE = (0, 0, 255)
        self.GREEN = (11, 102, 35) 

        # --- Fonts ---
        self.floating_buff_font = pygame.font.SysFont("Arial", 25, bold=True) 
        self.main_popup_font = pygame.font.SysFont("Arial Black", 50, bold=True) 

        # --- Main Pop-up State Variables (for "Treasure!", "Equipped!", "Sold!" etc.) ---
        self.buff_text_message = "" 
        self.buff_text_start_time = 0
        self.buff_text_alpha = 0     
        self.buff_text_scale = 0.0   
        self.buff_text_active = False
        self.buff_text_display_duration = 2000 
        self.buff_text_color = self.WHITE 

        # Current equipment state information
        self.current_equipment = None 

        # Floating Buff Text Display List (for +HP, +ATK numbers)
        self.buff_display_list = [] 

    # --- Helper to trigger the main central pop-up ---
    def _trigger_main_inventory_popup(self, message, color=None, duration_ms=2000):
        """
        Activates and initializes the main central inventory pop-up message animation.
        """
        self.buff_text_message = message
        self.buff_text_color = color if color is not None else self.WHITE
        self.buff_text_start_time = pygame.time.get_ticks()
        self.buff_text_alpha = 255
        self.buff_text_scale = 0.1 
        self.buff_text_active = True
        self.buff_text_display_duration = duration_ms

    # Your existing _display_buff_text (for floating numbers)
    def _display_buff_text(self, value, color, target_rect_center):
        """Adds a buff/healing text element to be displayed."""
        pos_x = target_rect_center[0]
        pos_y = target_rect_center[1] - 30 
        self.buff_display_list.append({
            'value': value,
            'color': color,
            'pos': (pos_x, pos_y),
            'start_time': pygame.time.get_ticks()
        })
    
    # Your existing start_inventory (now uses the new _trigger_main_inventory_popup helper)
    def start_inventory(self, equipment_card):
        """Initializes inventory with a new equipment and starts the 'Treasure!' animation."""
        self.current_equipment = equipment_card
        self._trigger_main_inventory_popup("Treasure!", self.WHITE, 2000)
        return "EQUIPMENT_FOUND" 

    # Your handle_player_buff (consolidated and simplified XP)
    def handle_player_buff(self, hero_instance):
        """
        Processes the player's buff earned.
        Returns the new sub_state.
        """
        if not self.current_equipment:
            print("Error: No equipment to add.")
            return "IDLE" 
        
        # Store original stats for printing later if needed
        hero_health = hero_instance.health
        hero_attack = hero_instance.attack
        hero_defense = hero_instance.defense
        hero_inventory = hero_instance.equipment_slots
        hero_xp = hero_instance.experience

        # If it's a POTION
        if self.current_equipment.health > 0:
            if hero_instance.health < hero_instance.max_health:
                actual_heal_amount = min(self.current_equipment.health, hero_instance.max_health - hero_instance.health)
                hero_instance.health += actual_heal_amount
                self._trigger_main_inventory_popup(f"Healed {actual_heal_amount} HP!", self.GREEN)
                self._display_buff_text(str(actual_heal_amount), self.GREEN, self.game_room_ui.get_health_rect().center)
                print(f"Hero healed {actual_heal_amount}. Current HP: {hero_instance.health}")
                
                if actual_heal_amount < self.current_equipment.health or hero_instance.health == hero_instance.max_health:
                    hero_instance.experience += self.current_equipment.xp_gain # Flat XP for potion use/excess
                    self._trigger_main_inventory_popup(f"Potion sold! +{self.current_equipment.xp_gain}XP", self.BLUE)
                    self._display_buff_text(f"+{self.current_equipment.xp_gain}XP", self.BLUE, self.game_room_ui.get_deck_rect().center)
                    print(f"Potion sold, gained {self.current_equipment.xp_gain} XP.")

            else: # Hero is already at max health, potion is sold
                hero_instance.experience += self.current_equipment.xp_gain # Flat XP for wasted heal
                self._trigger_main_inventory_popup(f"Sold Potion!\n+{self.current_equipment.xp_gain}XP", self.RED, 1500)
                self._display_buff_text(f"Sold Potion!\n+{self.current_equipment.xp_gain}XP", self.RED, self.game_room_ui.get_deck_rect().center)
                print(f"Hero already at max HP, gained {self.current_equipment.xp_gain} XP.")

        # If it's EQUIPMENT (including bags)
        elif self.current_equipment.card_type == "equipment":
            # Check if it's a bag (inventory boost)
            if self.current_equipment.inventory_boost > 0:
                hero_instance.equipment_slots += self.current_equipment.inventory_boost 
                print(f"Added {self.current_equipment.name}. Inventory size: {len(hero_instance.current_equipment)}/{hero_instance.equipment_slots} (+{self.current_equipment.inventory_boost} slots)")
                self._trigger_main_inventory_popup(f"Bag!\n+{self.current_equipment.inventory_boost} Slots", self.WHITE, 1500)
            else: # Regular equipment (not a bag)
                # If equipment is already equipped (clicked again to sell)
                if self.current_equipment.card_type == "equipment" and self.current_equipment.inventory_boost == 0 and self.current_equipment.current_health == 0: #Put stuff in your inventory
                    # Attempt to equip if slots available
                    if len(hero_instance.current_equipment) < hero_instance.equipment_slots:
                        hero_instance.current_equipment.append(self.current_equipment) 
                        self._trigger_main_inventory_popup(f"Equipped {self.current_equipment.name}", self.GREEN, 2000)
                        print(f"Equipped {self.current_equipment.name}.")
                        # Add all stats to hero
                        effective_attack_from_equipment = self.current_equipment.attack
                        effective_defense_from_equipment = self.current_equipment.current_defense

                        hero_instance.attack += effective_attack_from_equipment
                        hero_instance.defense += effective_defense_from_equipment

                    else:
                        # No slots, sell automatically
                        hero_instance.experience += self.current_equipment.xp_gain 
                        self._trigger_main_inventory_popup(f"No space!\nSold {self.current_equipment.name}\n+{self.current_equipment.xp_gain}XP", self.BLUE)
                        self._display_buff_text(f"+{self.current_equipment.xp_gain}XP", self.BLUE, self.game_room_ui.get_deck_rect().center)
                        print(f"No equipment slots. Sold {self.current_equipment.name}. Hero XP: {hero_instance.experience}")
        

        self.current_equipment = None # Clear the equipment after processing
        return "EQUIPMENT_ADDED" # This state signals that processing is complete

    # --- NEW METHOD: update_popups (Handles both main and floating texts) ---
    def update_popups(self):
        """
        Updates the animation state for both the main central pop-up
        and the floating buff texts. Call this every frame.
        """
        current_time = pygame.time.get_ticks()

        # 1. Update Main Central Pop-up Animation
        if self.buff_text_active:
            elapsed_time = current_time - self.buff_text_start_time

            if elapsed_time > self.buff_text_display_duration:
                self.buff_text_active = False
                self.buff_text_alpha = 0
                self.buff_text_scale = 0.0
            else:
                zoom_duration = self.buff_text_display_duration * 0.5 
                fade_duration = self.buff_text_display_duration * 0.5 

                if elapsed_time < zoom_duration:
                    progress = elapsed_time / zoom_duration
                    self.buff_text_scale = 0.1 + (0.9 * progress) 
                    self.buff_text_alpha = 255 
                else:
                    self.buff_text_scale = 1.0 
                    fade_progress = (elapsed_time - zoom_duration) / fade_duration
                    self.buff_text_alpha = int(255 * (1.0 - fade_progress))

                self.buff_text_alpha = max(0, min(255, self.buff_text_alpha))
                self.buff_text_scale = max(0.0, min(1.0, self.buff_text_scale))

        # 2. Update Floating Buff Texts Animation
        self.buff_display_list = [
            text_info for text_info in self.buff_display_list
            if current_time - text_info['start_time'] < 1000 
        ]

    # --- NEW METHOD: draw_popups (Draws both main and floating texts) ---
    def draw_popups(self, screen):
        """
        Draws the main central inventory pop-up and all active floating buff texts.
        Call this every frame.
        """
        current_time = pygame.time.get_ticks()

        # 1. Draw Main Central Pop-up
        if self.buff_text_active and self.buff_text_alpha > 0 and self.buff_text_scale > 0:
            lines = self.buff_text_message.split('\n')
            
            scaled_surfaces = []
            for line in lines:
                original_line_surface = self.main_popup_font.render(line, True, self.buff_text_color)
                
                scaled_line_width = int(original_line_surface.get_width() * self.buff_text_scale)
                scaled_line_height = int(original_line_surface.get_height() * self.buff_text_scale)
                
                scaled_line_width = max(1, scaled_line_width)
                scaled_line_height = max(1, scaled_line_height)
                
                scaled_line_surface = pygame.transform.scale(original_line_surface, (scaled_line_width, scaled_line_height))
                
                scaled_line_surface.set_alpha(self.buff_text_alpha)
                scaled_surfaces.append(scaled_line_surface)

            scaled_total_height = sum(s.get_height() for s in scaled_surfaces)
            
            current_y = (self.HEIGHT // 2) - (scaled_total_height // 2)
            for s_surface in scaled_surfaces:
                s_rect = s_surface.get_rect(center=(self.WIDTH // 2, current_y + s_surface.get_height() // 2))
                screen.blit(s_surface, s_rect)
                current_y += s_surface.get_height()

        # 2. Draw Floating Buff Texts
        text_fade_duration = 1000 
        text_float_speed = 0.05 

        for text_info in self.buff_display_list:
            elapsed_time = current_time - text_info['start_time']
            if elapsed_time < text_fade_duration:
                alpha = int(255 * (1 - (elapsed_time / text_fade_duration)))
                alpha = max(0, alpha)

                float_offset_y = elapsed_time * text_float_speed

                text_surface = self.floating_buff_font.render(str(text_info['value']), True, text_info['color'])
                text_surface.set_alpha(alpha)

                text_rect = text_surface.get_rect(center=(text_info['pos'][0], text_info['pos'][1] - float_offset_y))
                screen.blit(text_surface, text_rect)