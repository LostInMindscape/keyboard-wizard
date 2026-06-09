import pygame

from engine.vec2 import Vec2

class RoomContent:
    def __init__(
            self,
            spawnpoint: Vec2 | None = None,
            overlay: pygame.Surface | None = None,
            background: pygame.Surface | None = None
    ) -> None:
        self.spawnpoint: Vec2 | None = spawnpoint
        self.overlay: pygame.Surface | None = overlay
        self.background: pygame.Surface | None = background


    def try_draw_spawnpoint(self, surface: pygame.Surface) -> None:
        if self.spawnpoint is not None:
            surface.fill(
                pygame.Color(0x40, 0x40, 0xC0),
                (
                    self.spawnpoint.x - 50, self.spawnpoint.y - 80,
                    100, 80
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
        if self.overlay is not None:
            dest: tuple[float, float] = (
                (surface.get_width() - self.overlay.get_width()) / 2,
                (surface.get_height() - self.overlay.get_height()) / 2
            )
            surface.blit(self.overlay, dest)


    @staticmethod
    def from_json(json_data: dict) -> RoomContent:
        spawnpoint_raw: list[int] | None = json_data["spawnpoint"]
        spawnpoint: Vec2 | None = None      \
            if spawnpoint_raw is None       \
            else Vec2(int(spawnpoint_raw[0]), int(spawnpoint_raw[1]))

        return RoomContent(spawnpoint)
