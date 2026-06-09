import src.engine.scene as scene
import time
import pygame

pygame.init()


class Game:
    def __init__(self, first_scene: scene.Scene, target_fps: float):
        self._target_fps = target_fps
        self._target_frame_time = 1 / target_fps

        self.next_scene: scene.Scene | None = first_scene


    def run(self, window_size: tuple[int, int]) -> None:
        window: pygame.Surface = pygame.display.set_mode(window_size)

        last_frame_time: float = time.time()
        current_scene: scene.Scene = self.next_scene
        self.next_scene = None

        while True:
            current_time: float = time.time()
            delta: float = current_time - last_frame_time
            last_frame_time = current_time

            current_scene.update(delta)
            current_scene.draw(window)
            pygame.display.flip()

            if self.next_scene is not None:
                current_scene = self.next_scene
                self.next_scene = None

            t: float = time.time()
            diff: float = t - current_time
            if diff < self._target_frame_time:
                time.sleep(self._target_frame_time - diff)


    def set_target_fps(self, target_fps: float):
        self._target_fps = target_fps
        self._target_frame_time = 1 / target_fps
