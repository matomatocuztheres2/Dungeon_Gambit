# objects/battle_ob.py
import pygame
import random
import math

class BattleManager:
    def __init__(self, screen_width, screen_height, game_room_ui_instance):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.game_room_ui = game_room_ui_instance # Reference to the UI object to get rects

        # Define colors (re-defining for self-containment, or import from a constants file later)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0) # For damage feedback
        self.BLUE = (0, 0, 255) # For defense/block feedback

        # Fonts
        self.combat_text_font = pygame.font.SysFont("Arial Black", 50, bold=True)
        self.damage_text_font = pygame.font.SysFont("Arial", 25, bold=True) # For floating damage numbers

        # Combat Animation Variables (for "Battle Start!", "Victory!", "Defeat!" text)
        self.combat_text_start_time = 0
        self.combat_text_message = ""
        self.combat_text_alpha = 255 # For fading
        self.combat_text_scale = 0.1 # For zooming
        self.combat_text_active = False # Flag to know if combat text animation is running

        # Shaking Animation Variables
        self.shake_target_rect_name = None # 'enemy_card' or 'hero_health'
        self.shake_start_time = 0
        self.shake_duration = 200 # milliseconds
        self.shake_intensity = 5 # pixels

        # UI Feedback Variables (for floating damage numbers etc.)
        self.damage_display_list = [] # List of {'value': int, 'color': (R,G,B), 'pos': (x,y), 'start_time': ticks}

        # Current combat state information
        self.current_enemy = None # The actual enemy Card object
        self.current_game_room_sub_state = "IDLE" # Managed externally, but useful for internal logic

    def _find_oldest_degradable_armor(self, hero_instance):
        """
        Finds the index of the oldest equipped item that contributes defense
        and is not primarily an attack weapon. Assumes FIFO order.
        """
        for i, item_card in enumerate(hero_instance.current_equipment):
            # Define what constitutes "degradable armor" for your game
            # Example: card_type is "equipment", it provides defense, and no attack.
            # Adjust these conditions as needed for your specific item types.
            if item_card.card_type == "equipment" and item_card.defense > 0 and item_card.attack == 0:
                return i # Return the index of the oldest found
        return -1 # No suitable armor found
    
    def _find_oldest_degradable_weapon(self, hero_instance):
        """
        Finds the index of the oldest equipped item that contributes attack
        and is not primarily a defense item. Assumes FIFO order.
        """
        for i, item_card in enumerate(hero_instance.current_equipment):
            # Define what constitutes a "degradable weapon" for your game
            # Example: card_type is "equipment", it provides attack, and no defense.
            # Adjust these conditions as needed for your specific item types.
            if item_card.card_type == "equipment" and item_card.attack > 0 and item_card.defense == 0:
                return i # Return the index of the oldest found
        return -1 # No suitable weapon found

    def _shake_rect_offset(self, rect, current_time):
        """
        Calculates a shaking offset for a rect based on time if shaking is active for this rect.
        Returns the offset (dx, dy).
        """
        if self.shake_target_rect_name == 'enemy_card' and rect == self.game_room_ui.get_deck_rect():
            elapsed = current_time - self.shake_start_time
            if elapsed < self.shake_duration:
                offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
                return offset_x, offset_y
            else:
                self.shake_target_rect_name = None # Stop shaking
        elif self.shake_target_rect_name == 'hero_health' and rect == self.game_room_ui.get_health_rect():
            elapsed = current_time - self.shake_start_time
            if elapsed < self.shake_duration:
                offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
                return offset_x, offset_y
            else:
                self.shake_target_rect_name = None # Stop shaking
        
        return 0, 0 # No shake offset

    def _display_damage_text(self, value, color, target_rect_center):
        """Adds a damage/healing text element to be displayed."""
        # Position the text slightly above the center of the target rect
        pos_x = target_rect_center[0]
        pos_y = target_rect_center[1] - 30 # 30 pixels above the center
        self.damage_display_list.append({
            'value': value,
            'color': color,
            'pos': (pos_x, pos_y),
            'start_time': pygame.time.get_ticks()
        })

    def start_combat(self, enemy_card):
        """Initializes combat with a new enemy and starts the 'Battle Start!' animation."""
        self.current_enemy = enemy_card
        self.combat_text_message = "Battle\nStart!"
        self.combat_text_start_time = pygame.time.get_ticks()
        self.combat_text_alpha = 255
        self.combat_text_scale = 0.1
        self.combat_text_active = True
        return "COMBAT_START" # Return the sub-state to transition to

    def start_victory_animation(self):
        """Starts the 'Victory!' animation."""
        self.combat_text_message = f"Victory!\n+{self.current_enemy.xp_gain}XP"
        self.combat_text_start_time = pygame.time.get_ticks()
        self.combat_text_alpha = 255
        self.combat_text_scale = 0.1
        self.combat_text_active = True
        return "COMBAT_END_VICTORY"

    def start_defeat_animation(self):
        """Starts the 'Defeat!' animation."""
        self.combat_text_message = "Defeat!"
        self.combat_text_start_time = pygame.time.get_ticks()
        self.combat_text_alpha = 255
        self.combat_text_scale = 0.1
        self.combat_text_active = True
        return "COMBAT_END_DEFEAT"

    def start_dungeon_exit_animation(self):
        """Starts the 'You Survived!' animation for dungeon exit."""
        self.combat_text_message = "You Survived!\nClaim Your Reward!"
        self.combat_text_start_time = pygame.time.get_ticks()
        self.combat_text_alpha = 255
        self.combat_text_scale = 0.1
        self.combat_text_active = True
        return "DUNGEON_EXIT_ANIMATION"


    def handle_player_attack(self, hero_instance):
        """
        Processes the player's attack turn.
        Returns the new sub_state.
        """
        if not self.current_enemy:
            print("Error: No enemy to attack.")
            return "IDLE" # Should not happen in combat state

        print("Player attacks!")
        damage_dealt = hero_instance.attack
        
        effective_damage_to_enemy = max(0, damage_dealt - self.current_enemy.current_defense)
        
        if hero_instance.attack > hero_instance.min_attack:
            if self.current_enemy.current_defense > 0:
                self.current_enemy.current_defense = self.current_enemy.current_defense - 1
            print(f"Attack of {hero_instance.attack} dropping by 1")
            # Reduce hero's aggregate attack by 1 for this hit, but not below min_attack
            hero_instance.attack = max(hero_instance.min_attack, hero_instance.attack - 1)
            print(f"Hero's attack degraded to {hero_instance.attack}.")

            # Now, check if this degradation means an equipment piece should break and be removed.
            # This triggers if the hero's aggregate attack has dropped to their base 'fist' attack.
            if hero_instance.attack <= hero_instance.min_attack:
                print("Hero's attack reached minimum. Checking for weapon to break...")
                
                # Find the oldest weapon piece in the inventory that can break
                weapon_to_remove_index = self._find_oldest_degradable_weapon(hero_instance)

                if weapon_to_remove_index != -1:
                    removed_card = hero_instance.current_equipment.pop(weapon_to_remove_index)
                    
                    # Revert the stats that this specific broken card *originally provided*
                    # This ensures the hero's total attack accurately reflects remaining items.
                    hero_instance.attack -= removed_card.attack 
                    hero_instance.attack = max(hero_instance.attack, hero_instance.min_attack) # Ensure attack doesn't go below actual min

                    print(f"Weapon piece '{removed_card.name}' broke! Removed from inventory.")
                    print(f"Hero's new current Attack: {hero_instance.attack}")
                else:
                    print("No degradable weapon found to remove, despite attack hitting threshold.")

        self.current_enemy.current_health -= effective_damage_to_enemy
        self._display_damage_text(effective_damage_to_enemy, self.RED, self.game_room_ui.get_card_health_rect().center) # Show damage on enemy

        self.shake_target_rect_name = 'enemy_card'
        self.shake_start_time = pygame.time.get_ticks()

        print(f"Enemy {self.current_enemy.name} took {effective_damage_to_enemy} damage. Remaining HP: {self.current_enemy.current_health}")

        if self.current_enemy.current_health <= 0:
            print(f"Enemy {self.current_enemy.name} defeated!")
            # Trigger victory animation
            return self.start_victory_animation()
        else:
            print("It's enemy's turn.")
            return "ENEMY_TURN" # Indicate transition to enemy turn

    def handle_enemy_attack(self, hero_instance):
        """
        Processes the enemy's attack turn.
        Returns the new sub_state.
        """
        if not self.current_enemy:
            print("Error: No enemy to attack hero.")
            return "IDLE"

        print("Enemy attacks!")
        damage_taken = max(0, self.current_enemy.attack - hero_instance.defense) # Defense reduces damage
        
        # First, apply the per-hit degradation to the hero's overall defense stat
        if hero_instance.defense > hero_instance.min_defense:
            print(f"Defense of {hero_instance.defense} dropping by 1")
            # Reduce hero's aggregate defense by 1 for this hit, but not below min_defense
            hero_instance.defense = max(hero_instance.min_defense, hero_instance.defense - 1)
            print(f"Hero's defense degraded to {hero_instance.defense}.")

            # Now, check if this degradation means an equipment piece should break and be removed.
            # This triggers if the hero's aggregate defense has dropped to their base 'fist' defense.
            if hero_instance.defense <= hero_instance.min_defense:
                print("Hero's defense reached minimum. Checking for armor to break...")
                
                # Find the oldest armor piece in the inventory that can break
                armor_to_remove_index = self._find_oldest_degradable_armor(hero_instance)

                if armor_to_remove_index != -1:
                    removed_card = hero_instance.current_equipment.pop(armor_to_remove_index)
                    
                    # Revert the stats that this specific broken card *originally provided*
                    # This ensures the hero's total defense accurately reflects remaining items.
                    hero_instance.defense -= removed_card.defense 
                    hero_instance.defense = max(hero_instance.defense, hero_instance.min_defense) # Ensure defense doesn't go below actual min

                    print(f"Armor piece '{removed_card.name}' broke! Removed from inventory.")
                    print(f"Hero's new current Defense: {hero_instance.defense}")
                else:
                    print("No degradable armor found to remove, despite defense hitting threshold.")

        hero_instance.health -= damage_taken
        self._display_damage_text(damage_taken, self.RED, self.game_room_ui.get_health_rect().center) # Show damage on player
        
        self.shake_target_rect_name = 'hero_health'
        self.shake_start_time = pygame.time.get_ticks()

        print(f"Hero took {damage_taken} damage. Remaining HP: {hero_instance.health}")

        if hero_instance.health <= 0:
            print("Hero defeated! Game Over.")
            # Trigger defeat animation
            return self.start_defeat_animation()
        else:
            print("It's player's turn.")
            return "PLAYER_TURN" # Indicate transition back to player turn

    def update_animations(self, current_game_room_sub_state):
        """
        Updates combat text and shake animations.
        Returns the new sub-state if an animation transition occurs.
        """
        self.current_game_room_sub_state = current_game_room_sub_state # Keep internal state synced

        current_time = pygame.time.get_ticks()

        # Update combat text animation
        if self.combat_text_active:
            elapsed_combat_time = current_time - self.combat_text_start_time
            if elapsed_combat_time < 1000: # Phase 1: Zoom in (first 1 second)
                progress = elapsed_combat_time / 1000.0
                self.combat_text_scale = 0.1 + (1.0 - 0.1) * progress
                self.combat_text_alpha = 255
            elif elapsed_combat_time < 2000: # Phase 2: Fade out (next 1 second)
                progress = (elapsed_combat_time - 1000) / 1000.0
                self.combat_text_scale = 1.0
                self.combat_text_alpha = int(255 * (1.0 - progress))
            else: # Animation complete
                self.combat_text_active = False
                self.combat_text_alpha = 0 # Ensure it's fully transparent
                self.combat_text_scale = 0 # Ensure it's fully shrunk
                
                # Handle sub-state transitions after animation completion
                if current_game_room_sub_state == "COMBAT_START":
                    print("Combat Start animation finished. Transitioning to PLAYER_TURN.")
                    return "PLAYER_TURN" # Auto transition
                # For victory/defeat/dungeon exit, stay in the state until clicked
                
        # Update damage text display list (fading and floating)
        self.damage_display_list = [
            text_info for text_info in self.damage_display_list
            if current_time - text_info['start_time'] < 1000 # Keep for 1 second
        ]
        return current_game_room_sub_state # No state change if combat text not active or animation incomplete

    def draw_combat_elements(self, screen):
        """
        Draws combat-specific UI elements like combat text and floating damage numbers.
        It also handles applying shake offsets before drawing.
        """
        current_time = pygame.time.get_ticks()

        # Draw combat text animation if active
        if self.combat_text_active and self.combat_text_alpha > 0 and self.combat_text_scale > 0:
            lines = self.combat_text_message.split('\n')
            
            scaled_surfaces = []
            for line in lines:
                original_line_surface = self.combat_text_font.render(line, True, self.WHITE)
                
                scaled_line_width = int(original_line_surface.get_width() * self.combat_text_scale)
                scaled_line_height = int(original_line_surface.get_height() * self.combat_text_scale)
                scaled_line_width = max(1, scaled_line_width)
                scaled_line_height = max(1, scaled_line_height)
                
                scaled_line_surface = pygame.transform.scale(original_line_surface, (scaled_line_width, scaled_line_height))
                scaled_line_surface.set_alpha(self.combat_text_alpha)
                scaled_surfaces.append(scaled_line_surface)

            scaled_total_height = sum(s.get_height() for s in scaled_surfaces)
            
            current_y = (self.HEIGHT // 2) - (scaled_total_height // 2)
            for s_surface in scaled_surfaces:
                s_rect = s_surface.get_rect(center=(self.WIDTH // 2, current_y + s_surface.get_height() // 2))
                screen.blit(s_surface, s_rect)
                current_y += s_surface.get_height()
        
        # Draw damage text feedback
        text_fade_duration = 1000 # Damage text fades out over 1 second
        text_float_speed = 0.05 # Pixels per millisecond

        for text_info in self.damage_display_list:
            elapsed_time = current_time - text_info['start_time']
            if elapsed_time < text_fade_duration:
                alpha = int(255 * (1 - (elapsed_time / text_fade_duration)))
                alpha = max(0, alpha)

                float_offset_y = elapsed_time * text_float_speed

                text_surface = self.damage_text_font.render(str(text_info['value']), True, text_info['color'])
                text_surface.set_alpha(alpha)

                text_rect = text_surface.get_rect(center=(text_info['pos'][0], text_info['pos'][1] - float_offset_y))
                screen.blit(text_surface, text_rect)

    # Apply shake offset to relevant UI elements for drawing
    def get_shaken_rects(self):
        """
        Returns a dictionary of current shake offsets for relevant rects.
        { 'deck_rect': (dx, dy), 'health_rect': (dx, dy) }
        """
        offsets = {'deck_rect': (0,0), 'health_rect': (0,0)}
        current_time = pygame.time.get_ticks()

        if self.shake_target_rect_name == 'enemy_card':
            offsets['deck_rect'] = self._shake_rect_offset(self.game_room_ui.get_deck_rect(), current_time)
        elif self.shake_target_rect_name == 'hero_health':
            offsets['health_rect'] = self._shake_rect_offset(self.game_room_ui.get_health_rect(), current_time)
        
        return offsets