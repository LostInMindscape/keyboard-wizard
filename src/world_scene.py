import os

import engine.game
import engine.scene
from engine.vec2 import Vec2
import math
import player
import pygame
import sys
import tilemap

class WorldScene(engine.scene.Scene):
    def __init__(self):
        self.player = player.Player(40)
        self.player.position = Vec2(100, 200)

        self.room_size_tiles: Vec2 = Vec2(32, 18)

        self.tilemap: tilemap.TileMap = tilemap.TileMap.load_from_file(
            os.path.join("assets", "map.txt"), Vec2(50,50)
        )
        self.tilemap.add_to_tileset(tilemap.Tile(False))
        self.tilemap.add_to_tileset(tilemap.Tile(True))

        self.room_size_pixels: Vec2 = Vec2(
            self.room_size_tiles.x * self.tilemap.tile_size.x,
            self.room_size_tiles.y * self.tilemap.tile_size.y
        )


    def update(self, delta: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                self.player.handle_event(event)

        self.player.velocity.x = self.player.direction * 300.0
        self.player.velocity.y += 2000.0 * delta
        self.player.move(self.tilemap, delta)


    def draw(self, window: pygame.Surface) -> None:
        window.fill(pygame.Color(0x20, 0x20, 0x20))

        offset: Vec2 = Vec2(
            math.floor((self.player.position.x + self.player.size.x * 0.5) / window.get_width()) * window.get_width(),
            math.floor((self.player.position.y + self.player.size.y * 0.5) / window.get_height()) * window.get_height()
        )

        # Drawing current room
        self.tilemap.draw(window, offset)

        # Drawing player
        px: float = self.player.position.x - offset.x
        py: float = self.player.position.y - offset.y

        window.fill(
            pygame.Color(0x80, 0x80, 0xB0),
            (
                px if px > 0 else 0,
                py if py > 0 else 0,
                self.player.size.x + (px if px < 0 else 0),
                self.player.size.y + (py if py < 0 else 0)
            )
        )


if __name__ == "__main__":
    scene = WorldScene()
    g = engine.game.Game(scene, 144)
    g.run((
        int(scene.room_size_tiles.x * scene.tilemap.tile_size.x),
        int(scene.room_size_tiles.y * scene.tilemap.tile_size.y)
    ))

