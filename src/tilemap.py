from engine.vec2 import Vec2
import pygame

class Tile:
    def __init__(self, solid: bool) -> None:
        self.solid = solid


class TileMap:
    def __init__(self, tile_size: Vec2, map: list[list[int]] | None = None) -> None:
        self.tile_size: Vec2 = tile_size

        self.tileset: list[Tile] = []
        self.map: list[list[int]] = [] if map is None else map

        self.width: int = len(map[0]) if len(map) > 0 else 0
        self.height: int = len(map)


    @staticmethod
    def load_from_file(filename: str, tile_size: Vec2) -> TileMap | None:
        try:
            with open(filename, "r") as file:
                map: list[list[int]] = []
                width: int = 0
                height: int = 0

                for line in file:
                    map.append([])

                    split = line.split()
                    for i in range(len(split)):
                        map[height].append(int(split[i]))

                    if height == 0:
                        width = len(split)
                    elif width != len(split):
                        print("Lines in map file must have equal amount of elements")
                        return None

                    height += 1

                return TileMap(tile_size, map)
        except OSError:
            print("Failed to open map file")

        return None


    ## Returns ID of added tile
    def add_to_tileset(self, tile: Tile) -> int:
        self.tileset.append(tile)
        return len(self.tileset) - 1


    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        self.map[y][x] = tile_id


    def get_tile_at(self, x: int, y: int) -> Tile:
        return self.tileset[self.map[y][x]]


    def draw(self, window: pygame.Surface, offset: Vec2) -> None:
        if -window.get_width() > offset.x or -window.get_height() > offset.y:
            return

        y_range: range = range(
            int(offset.y / self.tile_size.y),
            int((offset.y + window.get_height()) / self.tile_size.y)
        )
        x_range: range = range(
            int(offset.x / self.tile_size.x),
            int((offset.x + window.get_width()) / self.tile_size.x)
        )

        for y in y_range:
            for x in x_range:

                # TODO: Change to drawing textures defined by tilemap.Tile
                if self.get_tile_at(x, y).solid:
                    window.fill(
                        pygame.Color(0x50, 0x50, 0x50),
                        (
                            self.tile_size.x * x - offset.x,
                            self.tile_size.y * y - offset.y,
                            self.tile_size.x,
                            self.tile_size.y
                        )
                    )