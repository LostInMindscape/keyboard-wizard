import math

from engine.vec2 import Vec2
import os
import pygame
import time


class Processor:
    def __init__(self, color: str, position: Vec2) -> None:
        self.color: str = color
        self.position: Vec2 = position


class RoomFeatures:
    def __init__(
            self,
            spawnpoint: Vec2 | None = None,
            overlay: pygame.Surface | None = None,
            background: pygame.Surface | None = None,
            draw_overlay: bool = True,
            processor: Processor | None = None,
    ) -> None:
        self.spawnpoint: Vec2 | None = spawnpoint
        self.overlay: pygame.Surface | None = overlay
        self.background: pygame.Surface | None = background
        self.draw_overlay: bool = draw_overlay
        self.processor: Processor | None = processor

        self._start_time: float = time.perf_counter()


    def try_draw_spawnpoint(
            self,
            surface: pygame.Surface,
            texture: pygame.Surface,
            player_in_range: bool,
            key_texture: pygame.Surface
    ) -> None:
        if self.spawnpoint is not None:
            surface.blit(
                texture,
                (
                    self.spawnpoint.x - texture.get_width() / 2,
                    self.spawnpoint.y - texture.get_height()
                )
            )

            if player_in_range:
                surface.blit(
                    key_texture,
                    (
                        self.spawnpoint.x - key_texture.get_width() * 0.5,
                        self.spawnpoint.y - texture.get_height() - key_texture.get_height() - 25
                    )
                )


    def try_draw_background(self, surface: pygame.Surface) -> None:
        if self.background is not None:
            dest: tuple[float, float] = (
                (surface.get_width() - self.background.get_width()) / 2,
                (surface.get_height() - self.background.get_height()) / 2
            )
            surface.blit(self.background, dest)


    def try_draw_overlay(self, surface: pygame.Surface) -> None:
        if self.draw_overlay and self.overlay is not None:
            dest: tuple[float, float] = (
                (surface.get_width() - self.overlay.get_width()) / 2,
                (surface.get_height() - self.overlay.get_height()) / 2
            )
            surface.blit(self.overlay, dest)


    def try_draw_processor(self, surface: pygame.Surface, textures: dict[str, pygame.Surface]) -> None:
        if self.processor is not None:
            surface.blit(
                textures[self.processor.color],
                (
                    self.processor.position.x,
                    self.processor.position.y + math.sin((time.perf_counter() - self._start_time) * 2.0) * 30
                )
            )


    @staticmethod
    def from_dict(data: dict, textures_folder: str) -> RoomFeatures:
        sp: Vec2 | None = None
        if data.get("spawnpoint") is not None:
            sp = Vec2(data["spawnpoint"][0], data["spawnpoint"][1])

        ol: pygame.Surface | None = None
        if data.get("overlay") is not None:
            ol = pygame.image.load(os.path.join(textures_folder, data["overlay"])).convert_alpha()

        bg: pygame.Surface | None = None
        if data.get("background") is not None:
            bg = pygame.image.load(os.path.join(textures_folder, data["background"])).convert()

        draw_ol: bool = True
        if data.get("draw_overlay") is not None:
            draw_ol = data["draw_overlay"]

        proc: Processor | None = None
        if data.get("processor") is not None:
            proc = Processor(
                data["processor"]["color"],
                Vec2(data["processor"]["position"][0], data["processor"]["position"][1])
            )

        return RoomFeatures(
            spawnpoint      = sp,
            overlay         = ol,
            background      = bg,
            draw_overlay    = draw_ol,
            processor       = proc
        )
