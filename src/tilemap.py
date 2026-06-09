from src.engine import Vec2

class Tile:
    def __init__(self, solid: bool) -> None:
        self.solid = solid


class TileMap:
    def __init__(self, tile_size: Vec2, width: int = 0, height: int = 0, map: list[list[int]] | None = None) -> None:
        self.tile_size: Vec2 = tile_size

        self.width: int = width
        self.height: int = height

        self.tileset: list[Tile] = []
        self.map: list[list[int]] = [] if map is None else map


    def load_from_file(self, filename: str) -> None:
        try:
            with open(filename, "r") as file:
                del self.map
                self.map = []

                for line in file:
                    self.map.append([])

                    split = line.split()
                    for i in range(len(split)):
                        self.map[self.height].append(int(split[i]))

                    if self.height == 0:
                        self.width = len(split)
                    elif self.width != len(split):
                        raise ValueError("Lines in map file must have equal amount of elements")

                    self.height += 1
        except:
            print("Failed to load map file")


    ## Returns ID of added tile
    def add_to_tileset(self, tile: Tile) -> int:
        self.tileset.append(tile)
        return len(self.tileset) - 1


    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        self.map[y][x] = tile_id


    def get_tile_at(self, x: int, y: int) -> Tile:
        return self.tileset[self.map[y][x]]