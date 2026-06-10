from engine.vec2 import Vec2
import os
import pygame


class RoomFeatures:
    def __init__(
            self,
            spawnpoint: Vec2 | None = None,
            overlay: pygame.Surface | None = None,
            background: pygame.Surface | None = None
    ) -> None:
        self.spawnpoint: Vec2 | None = spawnpoint
        self.overlay: pygame.Surface | None = overlay
        self.background: pygame.Surface | None = background

        self.draw_overlay: bool = self.overlay is not None


    def try_draw_spawnpoint(self, surface: pygame.Surface, texture: pygame.Surface) -> None:
        if self.spawnpoint is not None:
            surface.blit(
                texture,
                (
                    self.spawnpoint.x - texture.get_width() / 2,
                    self.spawnpoint.y - texture.get_height()
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

        return RoomFeatures(
            spawnpoint=sp,
            overlay=ol,
            background=bg
        )
