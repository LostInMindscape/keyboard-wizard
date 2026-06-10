import json

import engine.game
import engine.scene
from engine.vec2 import Vec2
import os
import player
import pygame
from pygame import freetype
from room_features import RoomFeatures
import sys
import tilemap

TEXTURES_PATH: str               = os.path.join("assets", "textures")
TILESET_TEXTURES_PATH: str       = os.path.join(TEXTURES_PATH, "tileset")
ROOM_FEATURE_TEXTURES_PATH: str  = os.path.join(TEXTURES_PATH, "room_features")


class WorldScene(engine.scene.Scene):
    def __init__(self):
        self.command_input_state: bool = False
        self.command: str = ""
        self.fps: int = 0

        json_text: str
        with open(os.path.join("assets", "map.json"), "r") as f:
            json_text = f.read()
        data: dict = json.loads(json_text)

        # loading font
        self.font: freetype.Font = \
            freetype.Font(
                data["font"]["name"],
                data["font"].get("size", 30)
            ) if "font" in data and "name" in data["font"] else \
            freetype.SysFont(
                freetype.get_default_font().removesuffix(".ttf"), 30
            )

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
            pygame.image.load(os.path.join(ROOM_FEATURE_TEXTURES_PATH, "spawnpoint.png")).convert_alpha()


    def update(self, delta: float) -> None:
        for event in pygame.event.get():
            self._process_event(event)

        if delta != 0.0:
            self.fps = int(1 / delta)

        self._update_player(delta)


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

        if self.command_input_state:
            self._draw_command_input(window)

        self.font.render_to(window, (5, 5), "FPS: " + str(self.fps))


    def get_current_room(self) -> tuple[int, int]:
        return (
            int((self.player.position.x + self.player.size.x * 0.5) / self.room_size_pixels.x),
            int((self.player.position.y + self.player.size.y * 0.5) / self.room_size_pixels.y)
        )


    def get_room_features(self, room: tuple[int, int]) -> RoomFeatures:
        return self.room_features.get(room, self.empty_room)


    def get_current_room_features(self) -> RoomFeatures:
        return self.get_room_features(self.get_current_room())


    def _draw_command_input(self, window: pygame.Surface) -> None:
        background: pygame.Surface = pygame.Surface((window.get_width() - 20, self.font.size + 10))
        background.fill(pygame.Color(0x40, 0x40, 0x40))
        background.set_alpha(191)

        text_surface: pygame.Surface = self.font.render(">" + self.command + "_", (0x80, 0x80, 0xB0))[0]
        background.blit(text_surface, (5, background.get_height() - 5 - text_surface.get_height()))

        window.blit(background, (10, window.get_height() - self.font.size - 20))


    def _process_event(self, event: pygame.Event) -> None:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif self.command_input_state:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._process_command()
                    self.command_input_state = False
                elif event.key == pygame.K_BACKSPACE and len(self.command) > 0:
                    self.command = self.command[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.command_input_state = False
                    self.command = ""
                elif pygame.K_a <= event.key <= pygame.K_z or event.key == pygame.K_SPACE:
                    self.command += event.unicode

        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.command_input_state = True
                self.player.direction = 0.0
            else:
                self.player.handle_event(event)


    def _update_player(self, delta: float) -> None:
        # move
        self.player.move(self.tilemap, delta)

        # check collision with spawnpoint
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


    def _process_command(self):
        if self.command == "":
            pass

        elif self.command == "recall":
            sp: Vec2 = self.get_room_features(self.player.saved_spawnpoint).spawnpoint
            self.player.position.x = \
                self.player.saved_spawnpoint[0] * self.room_size_pixels.x + sp.x - self.player.size.x * 0.5
            self.player.position.y = \
                self.player.saved_spawnpoint[1] * self.room_size_pixels.y + sp.y - self.player.size.y

            self.tilemap.reset()

        elif self.command == "toggle":
            room: tuple[int, int] = self.get_current_room()
            y_range: range = range(int(self.room_size_tiles.y) * room[1], int(self.room_size_tiles.y) * (room[1] + 1))
            x_range: range = range(int(self.room_size_tiles.x) * room[0], int(self.room_size_tiles.x) * (room[0] + 1))

            for y in y_range:
                for x in x_range:
                    if self.tilemap.get_tile_at(x, y).toggle is not None:
                        self.tilemap.map[y][x] = self.tilemap.get_tile_at(x, y).toggle

        elif self.command == "light":
            rf: RoomFeatures = self.get_current_room_features()
            rf.draw_overlay = not rf.draw_overlay

        self.command = ""


    def _load_room_features(self, features_list: list) -> None:
        for data in features_list:
            room_id: tuple[int, int] = (int(data["room"][0]), int(data["room"][1]))
            self.room_features[room_id] = RoomFeatures.from_dict(data, ROOM_FEATURE_TEXTURES_PATH)


if __name__ == "__main__":
    main_window: pygame.Surface = pygame.display.set_mode((1600, 900))
    scene = WorldScene()
    g = engine.game.Game(main_window, scene, 144)
    g.run()

