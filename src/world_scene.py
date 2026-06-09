import json

import engine.game
import engine.scene
from engine.vec2 import Vec2
import os
import player
import pygame
from room_features import RoomFeatures
import sys
import tilemap

TEXTURES_PATH: str               = os.path.join("assets", "textures")
TILESET_TEXTURES_PATH: str       = os.path.join(TEXTURES_PATH, "tileset")
ROOM_FEATURE_TEXTURES_PATH: str  = os.path.join(TEXTURES_PATH, "room_features")

class WorldScene(engine.scene.Scene):
    def __init__(self):
        json_text: str
        with open(os.path.join("assets", "map.json"), "r") as f:
            json_text = f.read()

        data: dict = json.loads(json_text)

        # loading player
        self.player = player.Player()
        self.player.update_from_dict(data["player"])

        # loading tilemap
        self.tilemap: tilemap.TileMap = tilemap.TileMap(
            Vec2(data["tile_size"][0], data["tile_size"][1]),
            data["tilemap"]
        )

        # loading tileset
        self.tilemap.tileset_from_dict(data["tileset"], TILESET_TEXTURES_PATH)

        # loading map data
        self.room_size_tiles: Vec2 = Vec2(
            data["room_size_tiles"][0],
            data["room_size_tiles"][1]
        )
        self.room_size_pixels: Vec2 = Vec2(
            self.room_size_tiles.x * self.tilemap.tile_size.x,
            self.room_size_tiles.y * self.tilemap.tile_size.y
        )

        # loading room features
        self.empty_room: RoomFeatures = RoomFeatures()
        self.room_features: dict[tuple[int, int], RoomFeatures] = {}
        self._load_room_features(data["room_features"])
        self.spawnpoint_texture: pygame.Surface = \
            pygame.image.load(os.path.join(ROOM_FEATURE_TEXTURES_PATH, "spawnpoint.png"))


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

        rc: RoomFeatures = self.room_features.get(
            (current_room_x, current_room_y),
            self.empty_room
        )

        rc.try_draw_background(window)

        self.tilemap.draw(window, offset)

        rc.try_draw_spawnpoint(window, self.spawnpoint_texture)

        self.player.draw(window, offset)

        rc.try_draw_overlay(window)


    def _load_room_features(self, features_list: list) -> None:
        for data in features_list:
            room_id: tuple[int, int] = (int(data["room"][0]), int(data["room"][1]))
            self.room_features[room_id] = RoomFeatures.from_dict(data, ROOM_FEATURE_TEXTURES_PATH)


if __name__ == "__main__":
    scene = WorldScene()
    g = engine.game.Game(scene, 144)
    g.run((
        int(scene.room_size_pixels.x),
        int(scene.room_size_pixels.y)
    ))

