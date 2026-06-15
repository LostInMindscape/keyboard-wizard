from asyncio import print_call_graph

import engine.game
import engine.scene
import pygame

import start_scene
import world_scene

if __name__ == "__main__":
    window_size: tuple[int, int] = (1600, 900)
    main_window: pygame.Surface = pygame.display.set_mode(window_size)

    world_scene: engine.scene.Scene = world_scene.WorldScene()
    start_scene: engine.scene.Scene = start_scene.StartScene(world_scene, window_size)

    game: engine.game.Game = engine.game.Game(main_window, start_scene, 144)
    game.run()
