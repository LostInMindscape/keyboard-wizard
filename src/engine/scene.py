import pygame

class Scene:
    def __init__(self):
        self.next_scene: Scene | None = None


    def update(self, delta: float) -> None:
        pass


    def draw(self, window: pygame.Surface) -> None:
        pass