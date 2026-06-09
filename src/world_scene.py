import engine.game
import engine.scene
from engine.vec2 import Vec2
import os
import player
import pygame
from room_content import RoomContent
import sys
import tilemap


class WorldScene(engine.scene.Scene):
    def __init__(self):
        self.player = player.Player(40)
        self.player.position = Vec2(100, 200)

        self.tilemap: tilemap.TileMap = tilemap.TileMap.load_from_file(
            os.path.join("assets", "map.txt"), Vec2(50,50)
        )
        self.tilemap.add_to_tileset(tilemap.Tile(False))
        self.tilemap.add_to_tileset(tilemap.Tile(True))

        self.room_size_tiles: Vec2 = Vec2(32, 18)
        self.room_size_pixels: Vec2 = Vec2(
            self.room_size_tiles.x * self.tilemap.tile_size.x,
            self.room_size_tiles.y * self.tilemap.tile_size.y
        )

        self.empty_room: RoomContent = RoomContent()
        self.room_contents: dict[tuple[int, int], RoomContent] = {
            (1, 0): RoomContent(
                Vec2(300, 850),
                background=pygame.image.load(os.path.join("assets", "textures", "borowka.png"))
            )
        }


    def update(self, delta: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                self.player.handle_event(event)

        self.player.velocity.x = self.player.direction * 600.0
        self.player.velocity.y += 2000.0 * delta
        self.player.move(self.tilemap, delta)


    def draw(self, window: pygame.Surface) -> None:
        current_room_x: int = int((self.player.position.x + self.player.size.x * 0.5) / window.get_width())
        current_room_y: int = int((self.player.position.y + self.player.size.y * 0.5) / window.get_height())

        offset: Vec2 = Vec2(
            current_room_x * window.get_width(),
            current_room_y * window.get_height()
        )

        window.fill(pygame.Color(0x20, 0x20, 0x20))

        rc: RoomContent = self.room_contents.get(
            (current_room_x, current_room_y),
            self.empty_room
        )

        rc.try_draw_background(window)

        self.tilemap.draw(window, offset)

        rc.try_draw_spawnpoint(window)

        self.player.draw(window, offset)

        rc.try_draw_overlay(window)


if __name__ == "__main__":
    scene = WorldScene()
    g = engine.game.Game(scene, 144)
    g.run((
        int(scene.room_size_tiles.x * scene.tilemap.tile_size.x),
        int(scene.room_size_tiles.y * scene.tilemap.tile_size.y)
    ))

