import os
import pygame
import pixel_art
import settings


class FireSpot:
    """Llama animada, puramente visual. No colisiona."""

    def __init__(self, x, y, w=30, h=42):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface, camera, tick):
        sx, sy = camera.apply(self.rect)
        pixel_art.draw_flame(surface, sx, sy, self.rect.width, self.rect.height, tick)


class SteamSpot:
    """Vapor animado que sube, puramente visual."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 4)

    def draw(self, surface, camera, tick):
        sx, sy = camera.apply(self.rect)
        pixel_art.draw_steam(surface, sx, sy, tick)


class MemoryFrame:
    """Un recuerdo grande pero discreto en el fondo del cielo.
    Se carga desde una imagen con nombre tipo imagen_recuerdo_1.png."""

    def __init__(self, x, y, image_name="imagen_recuerdo_1.png", size=(150, 110), life=220):
        self.x = x
        self.y = y
        self.size = size
        self.life = life
        self.max_life = life
        self.image_name = image_name
        self.image = self._load_image()

    def _load_image(self):
        filename = self.image_name if self.image_name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")) else f"{self.image_name}.png"
        search_paths = [
            os.path.join(settings.BASE_DIR, "assets", "images", filename),
            os.path.join(settings.BASE_DIR, "assets", "images", "recuerdos", filename),
            os.path.join(settings.BASE_DIR, "assets", "images", "background", filename),
            os.path.join(settings.BASE_DIR, filename),
        ]

        for path in search_paths:
            if os.path.isfile(path):
                try:
                    image = pygame.image.load(path).convert_alpha()
                    return pygame.transform.smoothscale(image, self.size)
                except pygame.error:
                    pass

        fallback = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(fallback, (38, 28, 58, 255), (0, 0, self.size[0], self.size[1]))
        pygame.draw.rect(fallback, (255, 220, 120, 255), (8, 8, self.size[0] - 16, self.size[1] - 16), 3)
        return fallback

    def update(self):
        self.life -= 1

    def draw(self, surface, camera):
        if self.life <= 0:
            return

        alpha = max(0, int((self.life / self.max_life) * 255))
        image = self.image.copy()
        image.set_alpha(alpha)
        surface.blit(image, (self.x, self.y))
