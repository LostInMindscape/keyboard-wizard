import os
from typing import Any

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

        self.tilemap: tilemap.TileMap = tilemap.TileMap(
            Vec2(50,50)
        )
        self.tilemap.load_from_file(
            os.path.join("assets", "map2.txt")
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

        # Drawing current room
        current_room: Vec2 = Vec2(
            math.floor((self.player.position.x + self.player.size.x * 0.5) / self.room_size_pixels.x),
            math.floor((self.player.position.y + self.player.size.y * 0.5) / self.room_size_pixels.y)
        )

        if current_room.x >= 0 and current_room.y >= 0:
            y_range: range = range(
                int(self.room_size_tiles.y * current_room.y),
                int(self.room_size_tiles.y * current_room.y + self.room_size_tiles.y)
            )
            x_range: range = range(
                int(self.room_size_tiles.x * current_room.x),
                int(self.room_size_tiles.x * current_room.x + self.room_size_tiles.x)
            )

            offset: Vec2 = Vec2(
                current_room.x * self.room_size_pixels.x,
                current_room.y * self.room_size_pixels.y
            )

            for y in y_range:
                for x in x_range:

                    # TODO: Change to drawing textures defined by tilemap.Tile
                    if self.tilemap.get_tile_at(x, y).solid:
                        window.fill(
                            pygame.Color(0x50, 0x50, 0x50),
                            (
                                self.tilemap.tile_size.x * x - offset.x,
                                self.tilemap.tile_size.y * y - offset.y,
                                self.tilemap.tile_size.x,
                                self.tilemap.tile_size.y
                            )
                        )

        # Drawing player
        px: float = self.player.position.x - current_room.x * self.room_size_pixels.x
        py: float = self.player.position.y - current_room.y * self.room_size_pixels.y

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

