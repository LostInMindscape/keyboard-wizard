import math
import os
import random
import sys
import time

import pygame
from pygame import freetype

import engine.scene
from engine.vec2 import Vec2

TITLE_SCREEN_TEXTURES_FOLDER: str = os.path.join("assets", "textures", "title_screen")
FONT_PATH: str = os.path.join("assets", "font", "PressStart2P.ttf")

def _is_point_in_rect(point: tuple[float | int, float | int], position: tuple[float | int, float | int], size: tuple[float | int, float | int]) -> bool:
    return position[0] <= point[0] <= position[0] + size[0] and position[1] <= point[1] <= position[1] + size[1]

class StartScene(engine.scene.Scene):
    STATE_NORMAL: int = 0
    STATE_CREDITS: int = 1
    STATE_TRANSITION: int = 2

    def __init__(self, main_scene: engine.scene.Scene, window_size: tuple[int, int]):
        super().__init__()
        self.main_scene = main_scene
        self.state: int = StartScene.STATE_NORMAL
        self.transition_timer: float = 0.0

        self.font_big: freetype.Font = freetype.Font(FONT_PATH, 70)
        self.font_small: freetype.Font = freetype.Font(FONT_PATH, 50)

        self.font_color: pygame.Color = pygame.Color(0x80, 0x80, 0xc0)
        self.fill_color: pygame.Color = pygame.Color(0x20, 0x20, 0x20)
        self.bg_color: pygame.Color = pygame.Color(0xa0, 0xa0, 0xd0)
        self.accent_color: pygame.Color = pygame.Color(0xe0, 0xe0, 0xe0)

        self.title_upper: pygame.Surface = \
            pygame.image.load(os.path.join(TITLE_SCREEN_TEXTURES_FOLDER, "title_upper.bmp")).convert_alpha()
        self.title_lower: pygame.Surface = \
            pygame.image.load(os.path.join(TITLE_SCREEN_TEXTURES_FOLDER, "title_lower.bmp")).convert_alpha()
        self.play_button: pygame.Surface = \
            pygame.image.load(os.path.join(TITLE_SCREEN_TEXTURES_FOLDER, "play_button.bmp")).convert_alpha()
        self.credits_button: pygame.Surface = \
            pygame.image.load(os.path.join(TITLE_SCREEN_TEXTURES_FOLDER, "credits_button.bmp")).convert_alpha()
        self.exit_button: pygame.Surface = \
            pygame.image.load(os.path.join(TITLE_SCREEN_TEXTURES_FOLDER, "exit_button.bmp")).convert_alpha()

        self.title_upper_position: Vec2     = Vec2((window_size[0] - self.title_upper.get_width()) * 0.5, 100)
        self.title_lower_position: Vec2     = Vec2((window_size[0] - self.title_lower.get_width()) * 0.5, 240)
        self.play_button_position: Vec2     = Vec2((window_size[0] - self.play_button.get_width()) * 0.5, 400)
        self.credits_button_position: Vec2  = Vec2((window_size[0] - self.credits_button.get_width()) * 0.5, 550)
        self.exit_button_position: Vec2     = Vec2((window_size[0] - self.exit_button.get_width()) * 0.5, 701)

        self.credits_renders: list[pygame.Surface] = [
            self.font_big.render("-= Credits =-", self.font_color)[0],
            self.font_big.render("Programming/Art by", self.font_color)[0],
            self.font_small.render("Jakub Demiańczuk", self.font_color)[0],
            self.font_big.render("Font", self.font_color)[0],
            self.font_small.render("Press Start by", self.font_color)[0],
            self.font_small.render("Cody \"CodeMan38\" Boisclair", self.font_color)[0],
            self.font_big.render("Made using Pygame", self.font_color)[0]
        ]
        self.credits_breaks: list[float] = [2, 1.7, 2.5, 1.7, 1.7, 2.5, 1]

        self.details: list[tuple[int, Vec2]] = []
        self.falling_starts_timer: float = 0.0


    def update(self, delta: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif self.state == StartScene.STATE_CREDITS:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = StartScene.STATE_NORMAL

            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._check_for_button_press()

        if self.state == StartScene.STATE_TRANSITION:
            self.transition_timer += delta

            if self.transition_timer > 0.5:
                self.next_scene = self.main_scene

        self.falling_starts_timer += delta

        for d in self.details:
            d[1].y += delta * 150


    def draw(self, window: pygame.Surface):
        window.fill(self.bg_color)
        self._draw_background(window)

        if self.state == StartScene.STATE_CREDITS:
            y: int = 50

            for i in range(len(self.credits_renders)):
                text: pygame.Surface = self.credits_renders[i]
                window.blit(text, ((window.get_width() - text.get_width()) * 0.5, y - math.sin(time.perf_counter() + i) * 5))
                y += text.get_height() * self.credits_breaks[i]

        else:
            window.blit(self.title_upper,
                (self.title_upper_position.x, self.title_upper_position.y + math.cos(time.perf_counter()) * 10))
            window.blit(self.title_lower,
                (self.title_lower_position.x, self.title_lower_position.y + math.sin(time.perf_counter()) * 10))
            window.blit(self.play_button, (self.play_button_position.x, self.play_button_position.y))
            window.blit(self.credits_button, (self.credits_button_position.x, self.credits_button_position.y))
            window.blit(self.exit_button, (self.exit_button_position.x, self.exit_button_position.y))

        if self.state == StartScene.STATE_TRANSITION:
            pygame.draw.circle(
                window,
                self.fill_color,
                (
                    self.play_button_position.x + self.play_button.get_width() * 0.5,
                    self.play_button_position.y + self.play_button.get_height() * 0.5
                ),
                self.transition_timer * 4096
            )


    def _check_for_button_press(self) -> None:
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()

        if _is_point_in_rect(
            mouse_pos, self.play_button_position.to_tuple(),
            (self.play_button.get_width(), self.play_button.get_height())
        ):
            self.state = StartScene.STATE_TRANSITION
            self.transition_timer = 0.0

        elif _is_point_in_rect(
                mouse_pos, self.credits_button_position.to_tuple(),
                (self.credits_button.get_width(), self.credits_button.get_height())
        ):
            self.state = StartScene.STATE_CREDITS

        elif _is_point_in_rect(
            mouse_pos, self.exit_button_position.to_tuple(),
            (self.exit_button.get_width(), self.exit_button.get_height())
        ):
            pygame.quit()
            sys.exit()


    def _draw_background(self, window: pygame.Surface) -> None:
        if self.falling_starts_timer > 0.5:
            size: int = random.randint(30, 60)
            self.details.append((size, Vec2(random.randint(0, window.get_width() - size), -size)))
            self.falling_starts_timer = 0

        for d in self.details:
            window.fill(
                pygame.Color(0x0, 0x0, 0x0),
                (d[1].x, max(0.0, d[1].y), d[0], d[0] if d[1].y > 0 else d[0] + d[1].y)
            )

        return

        if random.random() > 0.01:
            return

        for _ in range(random.randint(2, 5)):
            start: int = random.randint(0, window.get_height() - 50)

            for _ in range(random.randint(2, 5)):
                y = random.randint(4, 8)
                window.fill(self.accent_color, (0, start, window.get_width(), y))
                start += y + 1