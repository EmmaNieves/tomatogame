import pygame
import settings


class Checkpoint:
    """
    Bandera de guardado. Al tocarla, el jugador respawnea
    ahi en vez de en el inicio del nivel.
    """

    def __init__(self, x, y, w=24, h=70):
        self.rect = pygame.Rect(x, y, w, h)
        self.activated = False
        self.spawn_point = (x, y + h - settings.PLAYER_SIZE[1])

    def check(self, player):
        if not self.activated and player.rect.colliderect(self.rect):
            self.activated = True
            player.spawn_point = self.spawn_point

    def draw(self, surface, camera):
        x, y = camera.apply(self.rect)
        color = (0, 255, 136) if self.activated else (200, 200, 200)
        pole_rect = (x + self.rect.width // 2 - 3, y, 6, self.rect.height)
        flag_rect = (x + self.rect.width // 2, y, self.rect.width // 2, 24)
        pygame.draw.rect(surface, (90, 60, 30), pole_rect)
        pygame.draw.rect(surface, color, flag_rect)
