import json
import math
import time

from command_list import CommandList
import engine.scene
from engine.vec2 import Vec2
import os
import player
import pygame
from pygame import freetype
from pygame import mixer
from room_features import RoomFeatures
import sys
import tilemap

FONT_PATH: str                      = os.path.join("assets", "font")
MUSIC_PATH: str                     = os.path.join("assets", "music")
TEXTURES_PATH: str                  = os.path.join("assets", "textures")
PROCESSORS_TEXTURES_PATH: str       = os.path.join(TEXTURES_PATH, "processors")
TILESET_TEXTURES_PATH: str          = os.path.join(TEXTURES_PATH, "tileset")
ROOM_FEATURE_TEXTURES_PATH: str     = os.path.join(TEXTURES_PATH, "room_features")


class WorldScene(engine.scene.Scene):
    STATE_NORMAL: int           = 0
    STATE_COMMAND_INPUT: int    = 1
    STATE_COMMAND_LIST: int     = 2
    STATE_TRANSITION: int       = 3

    def __init__(self):
        super().__init__()

        self.state: int = WorldScene.STATE_TRANSITION
        self.command: str = ""
        self.fps: int = 0
        self.draw_fps: bool = False

        self.transition_timer: float = 0.5
        self.transition_target: Vec2 = Vec2(0, 0)
        self.transition_reset_energy: bool = True

        self.fill_color: pygame.Color = pygame.Color(0x20, 0x20, 0x40)
        self.font_color_energy: pygame.Color = pygame.Color(0x80, 0x80, 0xc0)
        self.font_color_no_energy: pygame.Color = pygame.Color(0xc0, 0x80, 0x80)
        self.list_color: pygame.Color = pygame.Color(0x40, 0x40, 0x40)
        self.transition_color: pygame.Color = pygame.Color(0x20, 0x20, 0x20)

        self.energy_texture: pygame.Surface = \
            pygame.image.load(os.path.join(TEXTURES_PATH, "energy.bmp")).convert_alpha()
        self.portal_off_texture: pygame.Surface = \
            pygame.image.load(os.path.join(TEXTURES_PATH, "portal.bmp")).convert_alpha()
        self.portal_on_texture: pygame.Surface = \
            pygame.image.load(os.path.join(TEXTURES_PATH, "portal_on.bmp")).convert_alpha()

        json_text: str
        with open(os.path.join("assets", "map.json"), "r") as f:
            json_text = f.read()
        data: dict = json.loads(json_text)

        # loading font
        self.font: freetype.Font = freetype.Font(
                os.path.join(FONT_PATH, data["font"]["name"]),
                data["font"].get("size", 30)
            ) if "font" in data and "name" in data["font"] else \
            freetype.SysFont(
                freetype.get_default_font().removesuffix(".ttf"), 30
            )

        # loading player
        self.player_spawn: Vec2 = Vec2(data["player"]["position"][0], data["player"]["position"][1])
        self.player = player.Player()
        self.player.update_from_dict(data["player"], TEXTURES_PATH)
        self.transition_target: Vec2 = Vec2(self.player_spawn.x, self.player_spawn.y)

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
        self.altar_room: tuple[int, int] = (data["altar_room"][0], data["altar_room"][1])
        self.room_features: dict[tuple[int, int], RoomFeatures] = {}
        self._load_room_features(data["room_features"])

        self.key_texture: pygame.Surface = \
            pygame.image.load(os.path.join(ROOM_FEATURE_TEXTURES_PATH, "key_e.png")).convert_alpha()
        self.spawnpoint_texture: pygame.Surface = \
            pygame.image.load(os.path.join(ROOM_FEATURE_TEXTURES_PATH, "spawnpoint.bmp")).convert_alpha()

        # loading processors
        self.processors: dict[str, pygame.Surface] = {}
        self.collected_processors: list[str] = []
        for key in data["processors"]:
            self.processors[key] = \
                pygame.image.load(os.path.join(PROCESSORS_TEXTURES_PATH, data["processors"][key])).convert_alpha()

        # loading portals
        self.portals: dict[tuple[int, int], Vec2] = {}
        self.portals_on: bool = False
        for portal in data["portals"]:
            self.portals[(portal["room"][0], portal["room"][1])] = \
                Vec2(portal["position"][0], portal["position"][1])

        # loading music
        mixer.music.load(os.path.join(MUSIC_PATH, data["sounds"]["music"]))
        mixer.music.play(-1)

        self.sound_input: mixer.Sound = mixer.Sound(os.path.join(MUSIC_PATH, data["sounds"]["input"]))
        self.sound_input_accept: mixer.Sound = mixer.Sound(os.path.join(MUSIC_PATH, data["sounds"]["input_accept"]))
        self.sound_input_error: mixer.Sound = mixer.Sound(os.path.join(MUSIC_PATH, data["sounds"]["input_error"]))

        # creating command list
        self.command_list: CommandList = CommandList(
            (int(self.room_size_pixels.x) - 300, int(self.room_size_pixels.y) - 150),
            pygame.Color(self.list_color.r, self.list_color.g, self.list_color.b, 0xc0),
            self.font,
            self.font_color_energy
        )


    def update(self, delta: float) -> None:
        for event in pygame.event.get():
            self._process_event(event)

        if self.state == WorldScene.STATE_TRANSITION:
            if self.transition_timer < 0.5 <= self.transition_timer + delta:
                self.player.position = self.transition_target
                self.tilemap.reset()
                self.portals_on = False
                if self.transition_reset_energy:
                    self.player.energy = self.player.max_energy

            self.transition_timer += delta

            if self.transition_timer > 1.0:
                self.state = WorldScene.STATE_NORMAL

        if delta != 0.0:
            self.fps = int(1 / delta)

        self._update_player(delta)


    def draw(self, window: pygame.Surface) -> None:
        room: tuple[int, int] = self.get_current_room()

        self._draw_room(window, room)

        self.font.render_to(
            window,
            (5, 5), "Energy: " + str(self.player.energy) + "/" + str(self.player.max_energy),
            self.font_color_no_energy if self.player.energy == 0 else self.font_color_energy,
        )

        if self.state == WorldScene.STATE_COMMAND_INPUT:
            self._draw_command_input(window)
        elif self.state == WorldScene.STATE_COMMAND_LIST:
            self.command_list.draw(window)
        elif self.state == WorldScene.STATE_TRANSITION:
            pygame.draw.circle(
                window, self.transition_color,
                (
                    int(self.player.position.x) % window.get_width(),
                    int(self.player.position.y) % window.get_height()
                ),
                abs(self.transition_timer if self.transition_timer < 0.5 else 1 - self.transition_timer) * 4096
            )

        if self.draw_fps:
            fps_text: pygame.Surface = self.font.render("FPS: " + str(self.fps))[0]
            window.blit(
                fps_text,
                (window.get_width() - 245, 5)
            )
            # self.font.render_to(window, (5, 5), "FPS: " + str(self.fps))


    def _draw_room(self, window: pygame.Surface, room: tuple[int, int]) -> None:
        offset: Vec2 = Vec2(
            room[0] * window.get_width(),
            room[1] * window.get_height()
        )

        window.fill(self.fill_color)

        rf: RoomFeatures = self.get_room_features(room)

        rf.try_draw_background(window)

        self.tilemap.draw(window, offset)

        rf.try_draw_energy(window, self.energy_texture)
        rf.try_draw_spawnpoint(
            window, self.spawnpoint_texture,
            self.player.touched_spawnpoint is not None, self.key_texture
        )

        if room in self.portals.keys():
            window.blit(
                self.portal_on_texture if self.portals_on else self.portal_off_texture,
                (self.portals[room].x, self.portals[room].y)
            )

        self.player.draw(window, offset)

        if rf.processor is not None and rf.processor.color not in self.collected_processors:
            rf.draw_processor(window, self.processors)

        if self.altar_room == room and len(self.collected_processors) != 0:
            vec: Vec2 = Vec2(
                0, 200 + 50 * math.sin(time.perf_counter())
            ).rotated(time.perf_counter() * 0.8)
            mid: Vec2 = Vec2(
                self.room_size_pixels.x * 0.5 - self.processors[self.collected_processors[0]].get_width() * 0.5,
                self.room_size_pixels.y * 0.5 - self.processors[self.collected_processors[0]].get_height() * 0.5
            )
            rot: float = math.tau / len(self.processors)

            for proc in self.collected_processors:
                pos: Vec2 = vec + mid
                window.blit(self.processors[proc], (pos.x, pos.y))
                vec = vec.rotated(rot)

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


    def _draw_command_input(self, window: pygame.Surface) -> None:
        background: pygame.Surface = pygame.Surface((window.get_width() - 20, self.font.size + 10))
        background.fill(pygame.Color(0x40, 0x40, 0x40))
        background.set_alpha(191)

        text_surface: pygame.Surface = \
            self.font.render(">" + self.command + "_", self.font_color_energy)[0] if self.player.energy > 0 else \
            self.font.render(">Insufficient energy_", self.font_color_no_energy)[0]
        background.blit(text_surface, (5, background.get_height() - 5 - text_surface.get_height()))

        window.blit(background, (10, window.get_height() - self.font.size - 20))


    def _process_event(self, event: pygame.Event) -> None:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif self.state == WorldScene.STATE_COMMAND_INPUT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._process_command()
                    if self.state == WorldScene.STATE_COMMAND_INPUT:
                        self.state = WorldScene.STATE_NORMAL
                elif event.key == pygame.K_BACKSPACE and len(self.command) > 0:
                    self.command = self.command[:-1]
                    self.sound_input.play()
                elif event.key == pygame.K_ESCAPE:
                    self.state = WorldScene.STATE_NORMAL
                    self.command = ""
                elif pygame.K_a <= event.key <= pygame.K_z or event.key == pygame.K_SPACE:
                    self.command += event.unicode
                    self.sound_input.play()

        elif self.state == WorldScene.STATE_COMMAND_LIST:
            if event.type == pygame.KEYDOWN:
                self.player.handle_event(event)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_TAB:
                    self.state = WorldScene.STATE_NORMAL
                else:
                    self.player.handle_event(event)

        elif self.state != WorldScene.STATE_TRANSITION:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state = WorldScene.STATE_COMMAND_INPUT
                    self.player.direction = 0

                elif event.key == pygame.K_e:
                    if self.player.touched_spawnpoint is not None:
                        self.player.saved_spawnpoint = self.player.touched_spawnpoint

                        self._start_transition(Vec2(
                            self.player.position.x,
                            self.player.position.y
                        ))

                elif event.key == pygame.K_p:
                    self.draw_fps = not self.draw_fps

                elif event.key == pygame.K_TAB:
                    self.state = WorldScene.STATE_COMMAND_LIST

                else:
                    self.player.handle_event(event)

            elif event.type == pygame.KEYUP:
                self.player.handle_event(event)


    def get_local_player_rect(self, room: tuple[int, int]) -> pygame.Rect:
        return pygame.Rect(
            self.player.position.x - room[0] * self.room_size_pixels.x,
            self.player.position.y - room[1] * self.room_size_pixels.y,
            self.player.size.x, self.player.size.y
        )


    def _update_player(self, delta: float) -> None:
        # move
        self.player.update(self.tilemap, delta)

        # check collision with spawnpoint
        room: tuple[int, int] = self.get_current_room()
        rf: RoomFeatures = self.get_room_features(room)

        if rf.spawnpoint is not None:
            sp_rect: pygame.Rect = pygame.Rect(
                rf.spawnpoint.x - self.spawnpoint_texture.get_width() * 0.5,
                rf.spawnpoint.y - self.spawnpoint_texture.get_height(),
                self.spawnpoint_texture.get_width(), self.spawnpoint_texture.get_height()
            )

            player_rect: pygame.Rect = self.get_local_player_rect(room)

            if sp_rect.colliderect(player_rect):
                self.player.touched_spawnpoint = room
            else:
                self.player.touched_spawnpoint = None
        else:
            self.player.touched_spawnpoint = None

        # check collisions with processor
        if rf.processor is not None and rf.processor.color not in self.collected_processors:
            proc_rect: pygame.Rect = pygame.Rect(
                rf.processor.position.x - self.processors[rf.processor.color].get_width() * 0.5,
                rf.processor.position.y - self.processors[rf.processor.color].get_height() * 0.5,
                self.processors[rf.processor.color].get_width(),
                self.processors[rf.processor.color].get_height()
            )

            player_rect: pygame.Rect = self.get_local_player_rect(room)

            if proc_rect.colliderect(player_rect):
                self.collected_processors.append(rf.processor.color)

        # check collisions with energy
        if rf.energy is not None:
            en_rect: pygame.Rect = pygame.Rect(
                rf.energy.x - self.energy_texture.get_width() * 0.5,
                rf.energy.y - self.energy_texture.get_height() * 0.5,
                self.energy_texture.get_width(),
                self.energy_texture.get_height()
            )

            player_rect: pygame.Rect = self.get_local_player_rect(room)

            if en_rect.colliderect(player_rect):
                rf.energy = None
                self.player.max_energy += 1
                self.player.energy = self.player.max_energy

        # check collisions with portal
        if self.portals_on and self.state == WorldScene.STATE_NORMAL and self.portals.get(room) is not None:
            portal_rect: pygame.Rect = pygame.Rect(
                self.portals[room].x,
                self.portals[room].y,
                self.portal_on_texture.get_width(),
                self.portal_on_texture.get_height()
            )

            player_rect: pygame.Rect = self.get_local_player_rect(room)

            if portal_rect.colliderect(player_rect):
                for key in self.portals.keys():
                    if key != room:
                        self._start_transition(Vec2(
                            key[0] * self.room_size_pixels.x + self.portals[key].x +
                                self.portal_off_texture.get_width()* 0.5,
                            key[1] * self.room_size_pixels.y + self.portals[key].y
                        ), False, False)
                        break


    def _process_command(self):
        valid: bool = True

        if self.player.energy <= 0:
            return

        elif self.command == "recall":
            if self.player.saved_spawnpoint is not None:
                sp: Vec2 = self.get_room_features(self.player.saved_spawnpoint).spawnpoint

                self._start_transition(Vec2(
                    self.player.saved_spawnpoint[0] * self.room_size_pixels.x + sp.x - self.player.size.x * 0.5,
                    self.player.saved_spawnpoint[1] * self.room_size_pixels.y + sp.y - self.player.size.y
                ))

                self.tilemap.reset()
            else:
                valid = False

        elif self.command == "toggle":
            room: tuple[int, int] = self.get_current_room()
            y_range: range = range(int(self.room_size_tiles.y) * room[1], int(self.room_size_tiles.y) * (room[1] + 1))
            x_range: range = range(int(self.room_size_tiles.x) * room[0], int(self.room_size_tiles.x) * (room[0] + 1))

            for y in y_range:
                for x in x_range:
                    if self.tilemap.get_tile_at(x, y).toggle is not None:
                        self.tilemap.map[y][x] = self.tilemap.get_tile_at(x, y).toggle

        elif self.command == "jumpboost":
            self.player.boosted_jump = True

        elif self.command == "return":
            self._start_transition(Vec2(self.player_spawn.x, self.player_spawn.y))

        elif self.command == "light":
            rf: RoomFeatures = self.get_current_room_features()

            if rf.overlay is not None:
                rf.draw_overlay = not rf.draw_overlay
            else:
                valid = False

        elif self.command == "charge" and self.portals.get(self.get_current_room()) is not None:
            self.portals_on = True

        else:
            valid = False
            self.sound_input_error.play()

        if valid:
            self.sound_input_accept.play()
            self.player.energy -= 1
            self.command_list.append_command(self.command)

        self.command = ""


    def _start_transition(self, target: Vec2, reset_energy: bool = True, reset_jumpboost: bool = True) -> None:
        self.state = WorldScene.STATE_TRANSITION
        self.transition_target = target
        self.transition_timer = 0.0
        self.transition_reset_energy = reset_energy

        if reset_jumpboost:
            self.player.boosted_jump = False


    def _load_room_features(self, features_list: list) -> None:
        for data in features_list:
            room_id: tuple[int, int] = (int(data["room"][0]), int(data["room"][1]))
            self.room_features[room_id] = RoomFeatures.from_dict(data, ROOM_FEATURE_TEXTURES_PATH)



