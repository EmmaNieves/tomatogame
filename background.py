import math
import pygame

import settings


class Background:
    """
    Fondo del nivel. Cambia segun la zona en la que esta el jugador:
    zonas exteriores (huerto/cultivo/peligro/casa) usan un cielo con
    gradiente y capas de paralaje; zonas interiores (cocina/estufa/jefe)
    dibujan una pared de interior con paneles a distinta profundidad.
    """

    def __init__(self):
        self._sky_cache = {}

    def _get_sky(self, zone):
        if zone not in self._sky_cache:
            top, bottom = settings.ZONE_SKY_COLORS.get(zone, settings.ZONE_SKY_COLORS["huerto"])
            self._sky_cache[zone] = self._build_gradient(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, top, bottom)
        return self._sky_cache[zone]

    def _build_gradient(self, w, h, top, bottom):
        surf = pygame.Surface((w, h))
        for y in range(h):
            t = y / h
            color = (
                int(top[0] + (bottom[0] - top[0]) * t),
                int(top[1] + (bottom[1] - top[1]) * t),
                int(top[2] + (bottom[2] - top[2]) * t),
            )
            pygame.draw.line(surf, color, (0, y), (w, y))
        return surf

    def draw(self, surface, camera, zone="huerto"):
        if zone in settings.ZONE_INTERIOR:
            self._draw_interior(surface, camera, zone)
        else:
            surface.blit(self._get_sky(zone), (0, 0))
            self._draw_clouds(surface, camera.offset_x)
            self._draw_far_trees(surface, camera.offset_x)
            self._draw_hills(surface, camera.offset_x)
            self._draw_mid_trees(surface, camera.offset_x)
            self._draw_far_fence(surface, camera.offset_x)
            self._draw_near_bushes(surface, camera.offset_x)

    # ---------------------------------------------------
    # INTERIOR: cocina / estufa / arena del jefe
    # ---------------------------------------------------
    def _draw_interior(self, surface, camera, zone):
        colors = settings.ZONE_INTERIOR[zone]
        surface.fill(colors["wall"])

        # linea de zocalo a media altura
        mid_y = settings.SCREEN_HEIGHT - 220
        pygame.draw.rect(surface, colors["wall_dark"], (0, mid_y, settings.SCREEN_WIDTH, 220))

        # paneles de pared lejanos (paralaje suave)
        factor = 0.35
        period = 160
        world = camera.offset_x * factor
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            pygame.draw.rect(surface, colors["trim"], (x, 30, 6, mid_y - 60))

        # estantes/silueta media
        factor2 = 0.55
        period2 = 210
        world2 = camera.offset_x * factor2
        start_i2 = int(world2 // period2) - 1
        count2 = settings.SCREEN_WIDTH // period2 + 3
        for i in range(start_i2, start_i2 + count2):
            x = i * period2 - world2
            y = mid_y - 90
            pygame.draw.rect(surface, colors["wall_dark"], (x, y, 90, 14))
            pygame.draw.rect(surface, colors["trim"], (x, y + 14, 90, 4))

        if zone in ("estufa", "jefe"):
            self._draw_glow(surface, camera.offset_x, colors)

    def _draw_glow(self, surface, offset_x, colors):
        factor = 0.7
        period = 260
        world = offset_x * factor
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        glow_color = (255, 120, 40)
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = settings.SCREEN_HEIGHT - 260
            glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*glow_color, 40), (60, 60), 60)
            surface.blit(glow, (x, y))

    # ---------------------------------------------------
    # CAPA LEJANA: nubes y siluetas de arboles
    # ---------------------------------------------------
    def _draw_clouds(self, surface, offset_x):
        factor = 0.15
        period = 260
        world = offset_x * factor
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = 50 + (i % 3) * 25
            self._draw_cloud(surface, x, y)

    def _draw_cloud(self, surface, x, y):
        color = (255, 255, 255)
        pygame.draw.ellipse(surface, color, (x, y, 50, 20))
        pygame.draw.ellipse(surface, color, (x + 15, y - 10, 40, 24))
        pygame.draw.ellipse(surface, color, (x + 35, y, 35, 18))

    def _draw_far_trees(self, surface, offset_x):
        factor = 0.3
        period = 150
        world = offset_x * factor
        color = (110, 150, 165)
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = settings.SCREEN_HEIGHT - 230
            trunk_w = 8
            pygame.draw.rect(surface, color, (x + 26, y + 90, trunk_w, 30))
            pygame.draw.polygon(surface, color, [(x, y + 100), (x + 30, y), (x + 60, y + 100)])

    # ---------------------------------------------------
    # CAPA MEDIA: colinas, arboles y cerca lejana
    # ---------------------------------------------------
    def _draw_hills(self, surface, offset_x):
        factor = 0.5
        world = offset_x * factor
        color = (120, 172, 95)
        base_y = settings.SCREEN_HEIGHT - 155
        step = 40
        points = [(0, settings.SCREEN_HEIGHT)]
        for sx in range(-step, settings.SCREEN_WIDTH + step * 2, step):
            wave = math.sin((sx + world) / 90) * 16
            points.append((sx, base_y + wave))
        points.append((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.draw.polygon(surface, color, points)

    def _draw_mid_trees(self, surface, offset_x):
        factor = 0.5
        period = 190
        world = offset_x * factor
        trunk_color = (95, 65, 42)
        leaf_color = (78, 138, 66)
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = settings.SCREEN_HEIGHT - 215
            pygame.draw.rect(surface, trunk_color, (x + 14, y + 40, 10, 40))
            pygame.draw.circle(surface, leaf_color, (x + 19, y + 28), 26)
            pygame.draw.circle(surface, leaf_color, (x + 4, y + 40), 18)
            pygame.draw.circle(surface, leaf_color, (x + 34, y + 40), 18)

    def _draw_far_fence(self, surface, offset_x):
        factor = 0.5
        period = 70
        world = offset_x * factor
        color = (150, 118, 88)
        y = settings.SCREEN_HEIGHT - 168
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            pygame.draw.rect(surface, color, (x, y, 6, 26))
        rail_y = y + 8
        pygame.draw.line(surface, color, (0, rail_y), (settings.SCREEN_WIDTH, rail_y), 3)

    # ---------------------------------------------------
    # CAPA CERCANA: arbustos del huerto
    # ---------------------------------------------------
    def _draw_near_bushes(self, surface, offset_x):
        factor = 0.8
        period = 130
        world = offset_x * factor
        dark = (58, 118, 54)
        light = (85, 150, 75)
        y = settings.SCREEN_HEIGHT - 128
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            pygame.draw.ellipse(surface, dark, (x, y, 60, 30))
            pygame.draw.ellipse(surface, light, (x + 10, y - 8, 40, 26))
