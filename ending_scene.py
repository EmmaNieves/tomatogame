import math
import os

import pygame

import pixel_art
import settings
from checkpoint import Checkpoint
from physics import resolve_platform_collisions
from platform_obj import Platform
from camera import Camera


ENDING_WIDTH = 960
ENDING_FLOOR_Y = settings.GROUND_Y


class CelebrationEnemy:
    def __init__(self, x, enemy_type, size, motion, assets=None):
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, ENDING_FLOOR_Y - size[1], *size)
        self.base_y = self.rect.y
        self.motion = motion
        self.frames = pixel_art.get_enemy_frames(enemy_type, *size)
        self.frame_index = 0
        self.frame_timer = 0
        self.phase = x * 0.07

    def update(self, tick):
        self.frame_timer += 1
        if self.frame_timer >= 14:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        if self.motion == "bounce":
            self.rect.y = self.base_y - int(abs(math.sin(tick * 0.08 + self.phase)) * 10)
        elif self.motion == "sway":
            self.rect.y = self.base_y - int(abs(math.sin(tick * 0.05 + self.phase)) * 4)
        else:
            self.rect.y = self.base_y - int(abs(math.sin(tick * 0.09 + self.phase)) * 7)

    def draw(self, surface, camera):
        x, y = camera.apply(self.rect)
        image = self.frames[self.frame_index]
        surface.blit(image, (x, y))


class EndingDecorations:
    def __init__(self):
        self.items = []
        self._add_many("flor", [80, 145, 215, 760, 830, 900], 0)
        self._add_many("planta_tomate", [120, 250, 710, 875], 0)
        self._add_many("maleza", [55, 185, 680, 790, 930], 0)
        self._add_many("piedra", [300, 645, 920], 0)
        self._add_many("cultivo", [160, 735], 0)

    def _add_many(self, kind, positions, y_offset):
        for index, x in enumerate(positions):
            image = pixel_art.get_decoration_sprite(kind, index)
            self.items.append((x, ENDING_FLOOR_Y - image.get_height() - y_offset, image))

    def draw(self, surface, camera):
        for x, y, image in self.items:
            sx, sy = camera.apply(pygame.Rect(x, y, *image.get_size()))
            surface.blit(image, (sx, sy))


def _draw_ending_background(surface, camera, image=None):
    if image is not None:
        surface.blit(image, (0, 0))
        return

    surface.fill((145, 215, 245))
    pygame.draw.circle(surface, (255, 242, 190), (790, 78), 34)
    for cloud_x, cloud_y in ((120, 70), (480, 105), (835, 145)):
        pygame.draw.ellipse(surface, (245, 252, 255), (cloud_x, cloud_y, 90, 22))
        pygame.draw.circle(surface, (245, 252, 255), (cloud_x + 25, cloud_y), 18)
        pygame.draw.circle(surface, (245, 252, 255), (cloud_x + 58, cloud_y - 5), 24)

    pygame.draw.polygon(
        surface,
        (112, 177, 94),
        [(0, 280), (150, 220), (320, 270), (500, 210), (700, 260), (850, 205), (960, 250), (960, 380), (0, 380)],
    )
    pygame.draw.rect(surface, (95, 170, 78), (0, ENDING_FLOOR_Y - 8, surface.get_width(), 8))

    for x in range(-20, ENDING_WIDTH + 40, 60):
        pygame.draw.rect(surface, (115, 75, 42), (x, 104, 5, 115))
        pygame.draw.circle(surface, (70, 145, 65), (x + 3, 98), 25)
    pygame.draw.rect(surface, (115, 75, 42), (0, 116, ENDING_WIDTH, 5))


def _draw_picnic(surface, camera, tick):
    blanket = pygame.Rect(360, ENDING_FLOOR_Y - 62, 250, 54)
    x, y = camera.apply(blanket)
    pygame.draw.rect(surface, (225, 90, 105), (x, y, blanket.width, blanket.height))
    for stripe_x in range(x + 12, x + blanket.width, 32):
        pygame.draw.rect(surface, (255, 205, 145), (stripe_x, y, 12, blanket.height))
    for stripe_y in range(y + 12, y + blanket.height, 22):
        pygame.draw.rect(surface, (255, 205, 145), (x, stripe_y, blanket.width, 8))

    basket = pygame.Rect(455, ENDING_FLOOR_Y - 105, 55, 43)
    bx, by = camera.apply(basket)
    pygame.draw.rect(surface, (174, 108, 52), (bx, by, basket.width, basket.height), border_radius=5)
    pygame.draw.arc(surface, (115, 67, 38), (bx + 8, by - 23, 39, 38), math.pi, math.tau, 5)
    pygame.draw.rect(surface, (230, 165, 72), (bx + 5, by + 8, 45, 5))

    for fruit_x, color in ((420, (225, 50, 45)), (492, (245, 180, 45)), (545, (205, 45, 55))):
        fx, fy = camera.apply(pygame.Rect(fruit_x, ENDING_FLOOR_Y - 94, 18, 18))
        pygame.draw.circle(surface, color, (fx + 9, fy + 9), 9)
        pygame.draw.rect(surface, (65, 140, 55), (fx + 8, fy - 3, 4, 6))

    for plate_x in (390, 565):
        px, py = camera.apply(pygame.Rect(plate_x, ENDING_FLOOR_Y - 35, 28, 8))
        pygame.draw.ellipse(surface, (245, 245, 235), (px, py, 28, 8))
        pygame.draw.ellipse(surface, (120, 185, 210), (px + 5, py + 2, 18, 4))


def _load_ending_image():
    candidates = (
        os.path.join(settings.ASSETS_DIR, "images", "backgrounds", "ending_image.png"),
        os.path.join(settings.ASSETS_DIR, "images", "backgrounds", "ending_image.jpg"),
        os.path.join(settings.ASSETS_DIR, "ending", "images", "ending_image.png"),
        os.path.join(settings.ASSETS_DIR, "ending", "images", "ending_image.jpg"),
    )
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            image = pygame.image.load(path).convert()
            return pygame.transform.scale(image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except pygame.error:
            return None
    return None


def _fade_to_ending(screen, clock):
    overlay = pygame.Surface(screen.get_size())
    for alpha in range(0, 256, 32):
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(settings.FPS)


def run_ending_scene(screen, clock, assets, audio, player, font, font_checkpoint):
    _fade_to_ending(screen, clock)

    ending_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    camera = Camera(ENDING_WIDTH)
    floor = Platform(0, ENDING_FLOOR_Y, ENDING_WIDTH, settings.GROUND_HEIGHT, "dirt")
    player.rect.topleft = (520, ENDING_FLOOR_Y - settings.PLAYER_SIZE[1])
    player.spawn_point = player.rect.topleft
    bear = Checkpoint(
        330,
        ENDING_FLOOR_Y - 32,
        message="",
    )
    bear_dialogue = [
        "Osito: ¡Lo lograste! Nunca subestimes a un tomate.",
        "Tomatito: ...",
        "Osito: Despues de estos 19 años, merecías una celebración.",
        "Osito: Feliz cumpleaños, mi tomate, no podría estar más feliz de vivir esta vida contigo",
        "Osito: Quiero acompañarte en todas las etapas de tu vida, y sean 19 o 40 años, deseo estar a tu lado",
        "Osito: Gracias por ser mi compañero, mi amigo, mi confidente, y mi amor.",
        "Osito: ¡Ahora celebremos! será divertido.",
        "Osito: Y mira... hasta ellos vinieron!",
        "Osito: Gracias por llegar hasta aqui.",
    ]
    decorations = EndingDecorations()
    celebration_enemies = [
        CelebrationEnemy(95, "gusano", (34, 24), "sway"),
        CelebrationEnemy(170, "babosa", (34, 18), "sway"),
        CelebrationEnemy(250, "tomate_podrido", (34, 30), "bounce"),
        CelebrationEnemy(680, "escarabajo", (34, 24), "bounce"),
        CelebrationEnemy(760, "mosca_fruta", (30, 22), "float"),
        CelebrationEnemy(840, "pimenton", (30, 38), "sway"),
        CelebrationEnemy(110, "espina", (34, 24), "bounce"),
        CelebrationEnemy(720, "cuchillo", (34, 22), "sway"),
        CelebrationEnemy(800, "sarten", (38, 25), "bounce"),
        CelebrationEnemy(875, "botella_ketchup", (26, 34), "sway"),
        CelebrationEnemy(610, "tostadora", (32, 24), "bounce"),
    ]
    ending_image = _load_ending_image()
    audio.play_ending_music()
    tick = 0
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_duration = int(settings.FPS * 4.6)
    running = True

    while running:
        clock.tick(settings.FPS)
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                if bear.can_interact(player):
                    if bear.message_visible:
                        if dialogue_index < len(bear_dialogue) - 1:
                            bear.message = bear_dialogue[dialogue_index]
                            dialogue_index += 1
                            dialogue_timer = dialogue_duration
                            audio.play_ending_sfx()
                        else:
                            bear.message_visible = False
                            dialogue_index = 0
                            audio.stop_ending_sfx()
                    else:
                        bear.message = bear_dialogue[dialogue_index]
                        dialogue_index += 1
                        bear.show_message()
                        dialogue_timer = dialogue_duration
                        audio.play_ending_sfx()

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.apply_gravity()
        player.move()
        resolve_platform_collisions(player, [floor])
        player.rect.x = max(24, min(player.rect.x, ENDING_WIDTH - player.rect.width - 24))
        player.update_animation()
        bear.hide_message_if_far(player)
        if bear.message_visible:
            dialogue_timer -= 1
            if dialogue_timer <= 0:
                bear.message_visible = False
                if dialogue_index >= len(bear_dialogue):
                    dialogue_index = 0
        if not bear.message_visible:
            audio.stop_ending_sfx()
        for enemy in celebration_enemies:
            enemy.update(tick)

        _draw_ending_background(ending_surface, camera, ending_image)
        decorations.draw(ending_surface, camera)
        _draw_picnic(ending_surface, camera, tick)
        floor.draw(ending_surface, camera)
        for enemy in celebration_enemies:
            enemy.draw(ending_surface, camera)
        bear.draw(ending_surface, camera)
        player.draw(ending_surface, camera)
        bear.draw_message(ending_surface, font_checkpoint, camera)

        title = font.render("FELIZ CUMPLEAÑOS TOMATITO", True, (255, 255, 255))
        ending_surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 88)))
        scaled = pygame.transform.scale(ending_surface, screen.get_size())
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    audio.stop_ending_sfx()
    return False
