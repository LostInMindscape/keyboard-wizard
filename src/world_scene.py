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
        self.player.update_from_dict(data["player"], TEXTURES_PATH)

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

        room: tuple[int, int] = self.get_current_room()
        rf: RoomFeatures = self.get_room_features(room)

        if rf.spawnpoint is not None:
            sp_rect: pygame.Rect = pygame.Rect(
                rf.spawnpoint.x, rf.spawnpoint.y,
                self.spawnpoint_texture.get_width(), self.spawnpoint_texture.get_height()
            )

            if sp_rect.colliderect(self.player.get_rect()):
                self.player.touching_spawnpoint = room
            else:
                self.player.touching_spawnpoint = None

        else:
            self.player.touching_spawnpoint = None


    def draw(self, window: pygame.Surface) -> None:
        current_room: tuple[int, int] = self.get_current_room()

        offset: Vec2 = Vec2(
            current_room[0] * window.get_width(),
            current_room[1] * window.get_height()
        )

        window.fill(pygame.Color(0x20, 0x20, 0x20))

        rf: RoomFeatures = self.get_current_room_features()

        rf.try_draw_background(window)

        self.tilemap.draw(window, offset)

        rf.try_draw_spawnpoint(window, self.spawnpoint_texture)

        self.player.draw(window, offset)

        rf.try_draw_overlay(window)


    def get_current_room(self) -> tuple[int, int]:
        return (
            int((self.player.position.x + self.player.size.x * 0.5) / self.room_size_pixels.x),
            int((self.player.position.y + self.player.size.y * 0.5) / self.room_size_pixels.y)
        )


    def get_room_features(self, room: tuple[int, int]) -> RoomFeatures:
        return self.room_features.get(room, self.empty_room)


    def get_current_room_features(self) -> RoomFeatures:
        return self.get_room_features(self.get_current_room())


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

