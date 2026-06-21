import pygame
from pygame import freetype


class CommandList:
    def __init__(self,
        size: tuple[int, int],
        color: pygame.Color,
        font: freetype.Font,
        font_color: pygame.Color
    ) -> None:
        self.surface: pygame.Surface = pygame.Surface(size)
        self.surface.fill(color)
        self.surface.set_alpha(color.a)

        self.current_y: int = 20
        self.font: freetype.Font = font
        self.font_color: pygame.Color = font_color

        self.commands: set[str] = set()


    def append_command(self, command: str) -> None:
        if command in self.commands:
            return

        self.commands.add(command)
        self.font.render_to(self.surface, (10, self.current_y), ">" + command, self.font_color)
        self.current_y += self.font.size + 20


    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(
            self.surface,
            (
                (surface.get_width() - self.surface.get_width()) * 0.5,
                (surface.get_height() - self.surface.get_height()) * 0.5
            )
        )