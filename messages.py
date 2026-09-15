import pygame


class StoryMessage:
    def __init__(self, trigger_x, text):
        self.trigger_x = trigger_x
        self.text = text
        self.triggered = False


class MessageManager:
    def __init__(self, story_messages, duration_frames=200):
        self.messages = story_messages
        self.duration = duration_frames
        self.timer = 0
        self.current_text = ""

    def update(self, player_x):
        for msg in self.messages:
            if not msg.triggered and player_x >= msg.trigger_x:
                msg.triggered = True
                self.current_text = msg.text
                self.timer = self.duration

        if self.timer > 0:
            self.timer -= 1

    def show(self, text, duration_frames=90):
        """Muestra un mensaje inmediato, sin esperar a una posicion
        del mapa. Usado por ejemplo al recoger un coleccionable."""
        self.current_text = text
        self.timer = duration_frames

    def draw(self, surface, font):
        if self.timer <= 0:
            return

        text_surface = font.render(self.current_text, True, (255, 255, 255))
        box_width = text_surface.get_width() + 40
        box_height = 50
        box_x = surface.get_width() // 2 - box_width // 2
        box_y = surface.get_height() - 90

        box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box, (20, 20, 30, 220), box.get_rect(), border_radius=8)
        pygame.draw.rect(box, (255, 215, 0), box.get_rect(), width=3, border_radius=8)
        surface.blit(box, (box_x, box_y))
        surface.blit(text_surface, (box_x + 20, box_y + 15))
