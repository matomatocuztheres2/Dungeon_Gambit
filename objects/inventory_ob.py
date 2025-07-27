import pygame
import math

class IntventoryManager: # Note: Typo 'IntventoryManager' - should be 'InventoryManager'
    def __init__(self, screen_width, screen_height, game_room_ui_instance):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.game_room_ui = game_room_ui_instance 

        # Define colors 
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0) 
        self.BLUE = (0, 0, 255)
        self.GREEN = (11, 102, 35) # Good for positive buffs like health, XP, equip

        # --- Fonts ---
        # Renamed your existing font for clarity (for floating numbers)
        self.floating_buff_font = pygame.font.SysFont("Arial", 25, bold=True) 
        # --- NEW: Font for the large central pop-ups (like "Treasure!") ---
        self.main_popup_font = pygame.font.SysFont("Arial Black", 50, bold=True) 

        # --- Main Pop-up State Variables (for "Treasure!", "Equipped!", "Sold!" etc.) ---
        self.buff_text_message = "" # The message for the large central pop-up
        self.buff_text_start_time = 0
        self.buff_text_alpha = 0     # Controls transparency (0-255)
        self.buff_text_scale = 0.0   # Controls size (0.0-1.0)
        self.buff_text_active = False
        self.buff_text_display_duration = 2000 # Default duration for main pop-up animation (2 seconds)
        self.buff_text_color = self.WHITE # Default color for the main pop-up

        # Current equipment state information
        self.current_equipment = None # The actual equipment Card object

        # Floating Buff Text Display List (for +HP, +ATK numbers)
        self.buff_display_list = [] # List of {'value': int, 'color': (R,G,B), 'pos': (x,y), 'start_time': ticks}

    # --- Helper to trigger the main central pop-up ---
    def _trigger_main_inventory_popup(self, message, color=None, duration_ms=2000):
        """
        Activates and initializes the main central inventory pop-up message animation.
        """
        self.buff_text_message = message
        self.buff_text_color = color if color is not None else self.WHITE # Use provided color or default white
        self.buff_text_start_time = pygame.time.get_ticks()
        self.buff_text_alpha = 255
        self.buff_text_scale = 0.1 # Start small for zoom-in effect
        self.buff_text_active = True
        self.buff_text_display_duration = duration_ms

    # Your existing _display_buff_text (for floating numbers)
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
    
    # Your existing start_inventory (now uses the new _trigger_main_inventory_popup helper)
    def start_inventory(self, equipment_card):
        """Initializes inventory with a new equipment and starts the 'Treasure!' animation."""
        self.current_equipment = equipment_card
        self._trigger_main_inventory_popup("Treasure!", self.WHITE, 2000) # Trigger main pop-up for "Treasure!"
        return "EQUIPMENT_FOUND" # This is the sub-state that main.py receives

    # Your handle_player_buff (ensure it uses the _trigger_main_inventory_popup and _display_buff_text)
    def handle_player_buff(self, hero_instance):
        """
        Processes the player's buff earned.
        Returns the new sub_state.
        """
        if not self.current_equipment:
            print("Error: No equipment to add.")
            return "IDLE" 
        
        # Store original stats for printing later if needed
        hero_health_before = hero_instance.health
        hero_attack_before = hero_instance.attack
        hero_defense_before = hero_instance.defense
        hero_inventory_before = hero_instance.equipment_slots
        hero_xp_before = hero_instance.experience


        # Check for full inventory/equipment type
        if self.current_equipment.card_type == "equipment" and self.current_equipment.inventory_boost == 0: 
            if len(hero_instance.current_equipment) < hero_instance.equipment_slots:
                hero_instance.current_equipment.append(self.current_equipment) 
                print(f"Added {self.current_equipment.name} to inventory. Inventory size: {len(hero_instance.current_equipment)}/{hero_instance.equipment_slots}")
                self._trigger_main_inventory_popup(f"Equipped {self.current_equipment.name}", self.WHITE, 2000)
            else:
                hero_instance.gain_xp(self.current_equipment.xp_gain) # Use gain_xp if it handles level up
                print(f"All equipment spots are full. {self.current_equipment.name} sold for {self.current_equipment.xp_gain} XP. Total XP: {hero_instance.experience}")
                self._trigger_main_inventory_popup(f"Sold {self.current_equipment.name}\n+{self.current_equipment.xp_gain}XP", self.BLUE, 1500)

        elif self.current_equipment.card_type == "equipment" and self.current_equipment.inventory_boost > 0: # Bags are always added
            hero_instance.equipment_slots += self.current_equipment.inventory_boost 
            hero_instance.current_equipment.append(self.current_equipment) 
            print(f"Added {self.current_equipment.name} to inventory. Inventory size: {len(hero_instance.current_equipment)}/{hero_instance.equipment_slots} (+{self.current_equipment.inventory_boost} slots)")
            self._trigger_main_inventory_popup(f"Bag!\n+{self.current_equipment.inventory_boost} Slots", self.WHITE, 1500)


        # Apply health, attack, defense from card (even if equipment was sold/bagged)
        effective_heal_from_equipment = self.current_equipment.current_health
        effective_attack_from_equipment = self.current_equipment.attack
        effective_defense_from_equipment = self.current_equipment.current_defense

        # Handle health
        if effective_heal_from_equipment > 0:
            original_health_to_add = effective_heal_from_equipment
            hero_instance.health += effective_heal_from_equipment
            if hero_instance.health > hero_instance.max_health:
                excess_heal = hero_instance.health - hero_instance.max_health
                xp_from_excess = excess_heal * self.current_equipment.xp_gain # Assuming XP gain from potion scales with excess
                hero_instance.gain_xp(xp_from_excess) 
                print(f"Excess heal ({excess_heal}) converted to {xp_from_excess} XP. Total XP: {hero_instance.experience}")
                hero_instance.health = hero_instance.max_health 

            actual_healed = hero_instance.health - hero_health_before
            if actual_healed > 0:
                self._display_buff_text(actual_healed, self.GREEN, self.game_room_ui.get_health_rect().center)
                print(f"Health: {hero_health_before} -> {hero_instance.health} (+{actual_healed})")
            
            elif actual_healed <= 0 and original_health_to_add > 0 and hero_instance.health == hero_instance.max_health:
                hero_instance.gain_xp(self.current_equipment.xp_gain) 
                print(f"Potion fully wasted (max health). Gained {self.current_equipment.xp_gain} XP. Total XP: {hero_instance.experience}")
                self._trigger_main_inventory_popup(f"Wasted Heal\n+{self.current_equipment.xp_gain}XP", self.RED, 1500)


        # Apply attack and defense
        if effective_attack_from_equipment > 0:
            hero_instance.attack += effective_attack_from_equipment
            self._display_buff_text(effective_attack_from_equipment, self.GREEN, self.game_room_ui.get_attack_rect().center)
            print(f"Attack: {hero_attack_before} -> {hero_instance.attack} (+{effective_attack_from_equipment})")
        
        if effective_defense_from_equipment > 0:
            hero_instance.defense += effective_defense_from_equipment
            self._display_buff_text(effective_defense_from_equipment, self.GREEN, self.game_room_ui.get_defense_rect().center)
            print(f"Defense: {hero_defense_before} -> {hero_instance.defense} (+{effective_defense_from_equipment})")

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
                zoom_duration = self.buff_text_display_duration * 0.5 # First half zooms in
                fade_duration = self.buff_text_display_duration * 0.5 # Second half fades out

                if elapsed_time < zoom_duration:
                    progress = elapsed_time / zoom_duration
                    self.buff_text_scale = 0.1 + (0.9 * progress) # Scales from 0.1 to 1.0
                    self.buff_text_alpha = 255 # Fully opaque during zoom in
                else:
                    self.buff_text_scale = 1.0 # Stays at full size during fade
                    fade_progress = (elapsed_time - zoom_duration) / fade_duration
                    self.buff_text_alpha = int(255 * (1.0 - fade_progress)) # Fades from 255 to 0

                self.buff_text_alpha = max(0, min(255, self.buff_text_alpha))
                self.buff_text_scale = max(0.0, min(1.0, self.buff_text_scale))

        # 2. Update Floating Buff Texts Animation
        # Filter out texts that have finished their animation
        self.buff_display_list = [
            text_info for text_info in self.buff_display_list
            if current_time - text_info['start_time'] < 1000 # Keep for 1 second
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
                
                # Scale the surface based on current animation scale
                scaled_line_width = int(original_line_surface.get_width() * self.buff_text_scale)
                scaled_line_height = int(original_line_surface.get_height() * self.buff_text_scale)
                
                # Prevent zero dimensions which can cause Pygame errors
                scaled_line_width = max(1, scaled_line_width)
                scaled_line_height = max(1, scaled_line_height)
                
                scaled_line_surface = pygame.transform.scale(original_line_surface, (scaled_line_width, scaled_line_height))
                
                # Apply current alpha (transparency)
                scaled_line_surface.set_alpha(self.buff_text_alpha)
                scaled_surfaces.append(scaled_line_surface)

            # Calculate total height to center multi-line text
            scaled_total_height = sum(s.get_height() for s in scaled_surfaces)
            
            # Position the text at the center of the screen
            current_y = (self.HEIGHT // 2) - (scaled_total_height // 2)
            for s_surface in scaled_surfaces:
                s_rect = s_surface.get_rect(center=(self.WIDTH // 2, current_y + s_surface.get_height() // 2))
                screen.blit(s_surface, s_rect)
                current_y += s_surface.get_height()

        # 2. Draw Floating Buff Texts
        text_fade_duration = 1000 # Floating text fades out over 1 second
        text_float_speed = 0.05 # Pixels per millisecond

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

    # --- Helper to trigger the main central pop-up ---
    def _trigger_main_inventory_popup(self, message, color=None, duration_ms=2000):
        """
        Activates and initializes the main central inventory pop-up message animation.
        """
        self.buff_text_message = message
        self.buff_text_color = color if color is not None else self.WHITE # Use provided color or default white
        self.buff_text_start_time = pygame.time.get_ticks()
        self.buff_text_alpha = 255
        self.buff_text_scale = 0.1 # Start small for zoom-in effect
        self.buff_text_active = True
        self.buff_text_display_duration = duration_ms

    # Your existing _display_buff_text (for floating numbers)
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
    
    # Your existing start_inventory (now uses the new _trigger_main_inventory_popup helper)
    def start_inventory(self, equipment_card):
        """Initializes inventory with a new equipment and starts the 'Treasure!' animation."""
        self.current_equipment = equipment_card
        self._trigger_main_inventory_popup("Treasure!", self.WHITE, 2000) # Trigger main pop-up for "Treasure!"
        return "EQUIPMENT_FOUND" # This is the sub-state that main.py receives

    # Your existing handle_player_buff (now uses _display_buff_text for floating numbers, and could use _trigger_main_inventory_popup for end message)
    def handle_player_buff(self, hero_instance):
        """
        Processes the player's buff earned.
        Returns the new sub_state.
        """
        if not self.current_equipment:
            print("Error: No equipment to add.")
            return "IDLE" 
        
        # Store original stats for printing later if needed
        hero_health_before = hero_instance.health
        hero_attack_before = hero_instance.attack
        hero_defense_before = hero_instance.defense
        hero_inventory_before = hero_instance.equipment_slots
        hero_xp_before = hero_instance.experience # Track XP before changes


        # Check for full inventory/equipment type
        if self.current_equipment.card_type == "equipment" and self.current_equipment.inventory_boost == 0: # If it's equipment (not a bag slot boost)
            if len(hero_instance.current_equipment) < hero_instance.equipment_slots:
                hero_instance.current_equipment.append(self.current_equipment) 
                print(f"Added {self.current_equipment.name} to inventory. Inventory size: {len(hero_instance.current_equipment)}/{hero_instance.equipment_slots}")
                # Potentially trigger a small pop-up like "Equipped Sword!" here
                self._trigger_main_inventory_popup(f"Equipped {self.current_equipment.name}", self.WHITE, 2000)
            else:
                hero_instance.gain_xp(self.current_equipment.xp_gain) # Use gain_xp if it handles level up
                print(f"All equipment spots are full. {self.current_equipment.name} sold for {self.current_equipment.xp_gain} XP. Total XP: {hero_instance.experience}")
                self._trigger_main_inventory_popup(f"Sold {self.current_equipment.name}\n+{self.current_equipment.xp_gain}XP", self.BLUE, 1500)

        elif self.current_equipment.card_type == "equipment" and self.current_equipment.inventory_boost > 0: # Bags are always added
            hero_instance.equipment_slots += self.current_equipment.inventory_boost # Increase slots
            hero_instance.current_equipment.append(self.current_equipment) # Add the bag to inventory
            print(f"Added {self.current_equipment.name} to inventory. Inventory size: {len(hero_instance.current_equipment)}/{hero_instance.equipment_slots} (+{self.current_equipment.inventory_boost} slots)")
            self._trigger_main_inventory_popup(f"Bag!\n+{self.current_equipment.inventory_boost} Slots", self.WHITE, 1500)


        # Apply health, attack, defense from card (even if equipment was sold/bagged)
        effective_heal_from_equipment = self.current_equipment.current_health
        effective_attack_from_equipment = self.current_equipment.attack
        effective_defense_from_equipment = self.current_equipment.current_defense

        # Handle health
        if effective_heal_from_equipment > 0:
            original_health_to_add = effective_heal_from_equipment
            hero_instance.health += effective_heal_from_equipment
            if hero_instance.health > hero_instance.max_health:
                excess_heal = hero_instance.health - hero_instance.max_health
                xp_from_excess = excess_heal * self.current_equipment.xp_gain # Assuming XP gain from potion scales with excess
                hero_instance.gain_xp(xp_from_excess) # Use gain_xp
                print(f"Excess heal ({excess_heal}) converted to {xp_from_excess} XP. Total XP: {hero_instance.experience}")
                hero_instance.health = hero_instance.max_health # Clamp health

            # Display floating heal text for the actual amount healed
            actual_healed = hero_instance.health - hero_health_before
            if actual_healed > 0:
                self._display_buff_text(actual_healed, self.GREEN, self.game_room_ui.get_health_rect().center)
                print(f"Health: {hero_health_before} -> {hero_instance.health} (+{actual_healed})")
            
            # If potion was fully wasted
            elif actual_healed <= 0 and original_health_to_add > 0 and hero_instance.health == hero_instance.max_health:
                hero_instance.gain_xp(self.current_equipment.xp_gain) # Add base XP if potion was 'wasted'
                print(f"Potion fully wasted (max health). Gained {self.current_equipment.xp_gain} XP. Total XP: {hero_instance.experience}")
                self._trigger_main_inventory_popup(f"Wasted Heal\n+{self.current_equipment.xp_gain}XP", self.RED, 1500)


        # Apply attack and defense
        if effective_attack_from_equipment > 0:
            hero_instance.attack += effective_attack_from_equipment
            self._display_buff_text(effective_attack_from_equipment, self.GREEN, self.game_room_ui.get_attack_rect().center)
            print(f"Attack: {hero_attack_before} -> {hero_instance.attack} (+{effective_attack_from_equipment})")
        
        if effective_defense_from_equipment > 0:
            hero_instance.defense += effective_defense_from_equipment
            self._display_buff_text(effective_defense_from_equipment, self.GREEN, self.game_room_ui.get_defense_rect().center)
            print(f"Defense: {hero_defense_before} -> {hero_instance.defense} (+{effective_defense_from_equipment})")

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
            if current_time - text_info['start_time'] < 1000 # Keep for 1 second
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
        text_fade_duration = 1000 # Floating text fades out over 1 second
        text_float_speed = 0.05 # Pixels per millisecond

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