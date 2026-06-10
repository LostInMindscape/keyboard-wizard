from engine.vec2 import Vec2
import os
import pygame

class Tile:
    def __init__(
            self,
            solid: bool = False,
            texture: pygame.Surface | None = None,
            toggle: int | None = None,
    ) -> None:
        self.solid: bool = solid
        self.texture: pygame.Surface | None = texture
        self.toggle: int | None = toggle


class TileMap:
    def __init__(self, tile_size: Vec2, map: list[list[int]] | None = None) -> None:
        self.tile_size: Vec2 = tile_size

        self.tileset: list[Tile] = []
        self.map: list[list[int]] = [] if map is None else map
        self.base_map: list[list[int]] = []
        if map is not None:
            for row in map:
                self.base_map.append(row.copy())

        self.width: int = len(map[0]) if len(map) > 0 else 0
        self.height: int = len(map)


    def reset(self) -> None:
        self.map.clear()

        for row in self.base_map:
            self.map.append(row.copy())


    def add_to_tileset(self, tile: Tile) -> None:
        self.tileset.append(tile)


    def tileset_from_dict(self, data: dict, texture_folder: str) -> None:
        for tile_data in data:
            txt: pygame.Surface | None = None
            if tile_data.get("texture") is not None:
                txt = pygame.image.load(os.path.join(texture_folder, tile_data["texture"])).convert_alpha()

            self.add_to_tileset(Tile(
                solid = tile_data.get("solid", False),
                texture = txt,
                toggle = tile_data.get("toggle", None)
            ))


    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        self.map[y][x] = tile_id


    def get_tile_at(self, x: int, y: int) -> Tile:
        return self.tileset[self.map[y][x]]


    def draw(self, surface: pygame.Surface, offset: Vec2) -> None:
        if -surface.get_width() > offset.x or -surface.get_height() > offset.y:
            return

        y_range: range = range(
            int(offset.y / self.tile_size.y),
            int((offset.y + surface.get_height()) / self.tile_size.y)
        )
        x_range: range = range(
            int(offset.x / self.tile_size.x),
            int((offset.x + surface.get_width()) / self.tile_size.x)
        )

        for y in y_range:
            for x in x_range:
                if self.get_tile_at(x, y).texture is not None:
                    surface.blit(
                        self.get_tile_at(x, y).texture,
                        (
                            self.tile_size.x * x - offset.x,
                            self.tile_size.y * y - offset.y
                        )
                    )