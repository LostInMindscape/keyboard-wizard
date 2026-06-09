from engine.vec2 import Vec2

class RoomContent:
    def __init__(self, spawnpoint: Vec2 | None = None) -> None:
        self.spawnpoint: Vec2 | None = spawnpoint
        # self.overlay - image or none
        # self.background - image or none


    @staticmethod
    def from_json(json_data: dict) -> RoomContent:
        spawnpoint_raw: list[int] | None = json_data["spawnpoint"]
        spawnpoint: Vec2 | None = None      \
            if spawnpoint_raw is None       \
            else Vec2(int(spawnpoint_raw[0]), int(spawnpoint_raw[1]))

        return RoomContent(spawnpoint)
