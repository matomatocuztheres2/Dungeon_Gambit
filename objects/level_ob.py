# File: objects/level_ob.py

import pygame
import math

class LevelManager:
    def __init__(self, screen_width, screen_height, game_room_ui_instance):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.game_room_ui = game_room_ui_instance 

        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)      
        self.BLUE = (0, 0, 255)     
        self.GREEN = (11, 102, 35) 

        self.floating_buff_font = pygame.font.SysFont("Arial", 25, bold=True) 
        self.main_popup_font = pygame.font.SysFont("Arial Black", 50, bold=True) 

        self.buff_text_message = "" 
        self.buff_text_start_time = 0
        self.buff_text_alpha = 0     
        self.buff_text_scale = 0.0   
        self.buff_text_active = False
        self.buff_text_display_duration = 2000 
        self.buff_text_color = self.WHITE 

        self.current_level_up_card = None 

        self.buff_display_list = [] 

    def _trigger_main_level_up_popup(self, message, color=None, duration_ms=2000):
        self.buff_text_message = message
        self.buff_text_color = color if color is not None else self.WHITE
        self.buff_text_start_time = pygame.time.get_ticks()
        self.buff_text_alpha = 255
        self.buff_text_scale = 0.1 
        self.buff_text_active = True
        self.buff_text_display_duration = duration_ms

    def _display_floating_buff_text(self, text, color, target_rect_center):
        pos_x = target_rect_center[0]
        pos_y = target_rect_center[1] - 30 
        self.buff_display_list.append({
            'value': text, 
            'color': color,
            'pos': (pos_x, pos_y),
            'start_time': pygame.time.get_ticks()
        })
    
    def start_level_up(self, level_up_card):
        self.current_level_up_card = level_up_card
        self._trigger_main_level_up_popup("Level Up!", self.WHITE, 2000) 
        return "LEVEL_UP_FOUND"

    def handle_level_up(self, hero_instance):
        """
        Applies permanent level-up buffs to the hero's base stats.
        Uses the card's health, attack, and defense attributes as boost values.
        Returns the new sub_state.
        """
        if not self.current_level_up_card:
            print("Error: No level-up card to apply.")
            return "IDLE" 

        # Store old stats for display
        old_max_health = hero_instance.max_health
        old_min_attack = hero_instance.min_attack
        old_min_defense = hero_instance.min_defense

        # Get boost values directly from the card's attributes
        health_boost = self.current_level_up_card.health
        attack_boost = self.current_level_up_card.attack
        defense_boost = self.current_level_up_card.defense

        # Apply boosts and prepare messages
        boost_message_parts = []

        if health_boost > 0:
            hero_instance.max_health += health_boost
            hero_instance.health += health_boost
            boost_message_parts.append(f"+{health_boost} Max HP")
            self._display_floating_buff_text(f"+{health_boost} Max HP", 
                                                self.GREEN, self.game_room_ui.get_health_rect().center)
            print(f"Max Health: {old_max_health} -> {hero_instance.max_health} (+{health_boost})")

        if attack_boost > 0:
            hero_instance.min_attack += attack_boost
            hero_instance.attack += attack_boost 
            boost_message_parts.append(f"+{attack_boost} Min ATK")
            self._display_floating_buff_text(f"+{attack_boost} Min ATK", 
                                                self.GREEN, self.game_room_ui.get_attack_rect().center)
            print(f"Min Attack: {old_min_attack} -> {hero_instance.min_attack} (+{attack_boost})")

        if defense_boost > 0:
            hero_instance.min_defense += defense_boost
            hero_instance.defense += defense_boost 
            boost_message_parts.append(f"+{defense_boost} Min DEF")
            self._display_floating_buff_text(f"+{defense_boost} Min DEF", 
                                                self.GREEN, self.game_room_ui.get_defense_rect().center)
            print(f"Min Defense: {old_min_defense} -> {hero_instance.min_defense} (+{defense_boost})")
        
        # Trigger a final main pop-up summarizing boosts, if any
        if boost_message_parts:
            final_message = "Level Up Complete!\n" + "\n".join(boost_message_parts)
            self._trigger_main_level_up_popup(final_message, self.GREEN, 2500) 
        else:
            self._trigger_main_level_up_popup("No Stat Boosts!", self.RED, 1500)

        self.current_level_up_card = None 
        return "LEVEL_UP_ADDED" 

    def update_popups(self):
        current_time = pygame.time.get_ticks()

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

        self.buff_display_list = [
            text_info for text_info in self.buff_display_list
            if current_time - text_info['start_time'] < 1000 
        ]

    def draw_popups(self, screen):
        current_time = pygame.time.get_ticks()
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