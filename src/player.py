from engine.vec2 import Vec2
import os
import pygame
import tilemap

class Player:
    def __init__(
            self,
            position: Vec2 = Vec2(0, 0),
            size: Vec2 = Vec2(100, 100),
    ) -> None:
        self.sprite: pygame.Surface | None  = None
        self.position: Vec2                 = position
        self.velocity: Vec2                 = Vec2(0.0, 0.0)
        self.size: Vec2                     = size

        self.direction: float               = 0.0
        self.on_ground: bool                = False
        self.can_jump_cancel: bool          = False

        self.touched_spawnpoint: tuple[int, int] | None  = None
        self.saved_spawnpoint: tuple[int, int]           = (1, 0)


    def update_from_dict(self, data: dict, textures_folder: str) -> None:
        if data.get("sprite") is not None:
            self.sprite = pygame.image.load(os.path.join(textures_folder, data["sprite"])).convert_alpha()

        if data.get("position") is not None:
            self.position = Vec2(data["position"][0], data["position"][1])

        if data.get("size") is not None:
            self.size = Vec2(data["size"][0], data["size"][1])


    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.direction -= 1.0
            elif event.key == pygame.K_d:
                self.direction += 1.0
            elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
                if self.on_ground:
                    self.can_jump_cancel = True
                    self.velocity.y -= 1000.0
            elif event.key == pygame.K_e:
                if self.touched_spawnpoint is not None:
                    self.saved_spawnpoint = self.touched_spawnpoint

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.direction += 1.0
            elif event.key == pygame.K_d:
                self.direction -= 1.0
            elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
                if self.can_jump_cancel and self.velocity.y < 0:
                    self.can_jump_cancel = False
                    self.velocity.y += 400.0


    def draw(self, surface: pygame.Surface, negative_offset: Vec2) -> None:
        px: float = self.position.x - negative_offset.x + (self.size.x - self.sprite.get_width()) / 2
        py: float = self.position.y - negative_offset.y + (self.size.y - self.sprite.get_height()) / 2

        surface.blit(self.sprite, (px, py))


    def move(self, tile_map: tilemap.TileMap, delta: float) -> None:
        self.velocity.x = self.direction * 600.0
        self.velocity.y += 2000.0 * delta

        if self.velocity.x != 0:
            step: float = self.velocity.x * delta
            step_dir: int = (1 if step > 0 else -1)

            x_start: int = (
                int(self.position.x / tile_map.tile_size.x) if step < 0 else
                int((self.position.x + self.size.x) / tile_map.tile_size.x)
            )
            x_end: int = (
                int((self.position.x + step) / tile_map.tile_size.x) if step < 0 else
                int((self.position.x + self.size.x + step) / tile_map.tile_size.x)
            ) + step_dir

            # If stays on the same tile after moving then we assume collisions here were handled earlier
            if x_start == x_end:
                self.position.x += step

            # Will enter new tiles - we have to check them
            else:
                y_start: int = int(self.position.y / tile_map.tile_size.y)
                y_end: int = int((self.position.y + self.size.y) / tile_map.tile_size.y)

                if self.position.y + self.size.y > y_end * tile_map.tile_size.y:
                    y_end += 1

                collided: bool = False

                for x in range(x_start, x_end, step_dir):
                    for y in range(y_start, y_end):
                        if tile_map.get_tile_at(x, y).solid:
                            # Found collision - stop here
                            collided = True

                            if step > 0:
                                self.position.x = x * tile_map.tile_size.x - self.size.x
                            else:
                                self.position.x = (x + 1) * tile_map.tile_size.x
                            break

                    if collided:
                        break

                if not collided:
                    self.position.x += step

        if self.velocity.y != 0:
            step: float = self.velocity.y * delta
            step_dir: int = (1 if step > 0 else -1)

            y_start: int = (
                int(self.position.y / tile_map.tile_size.y) if step < 0 else
                int((self.position.y + self.size.y) / tile_map.tile_size.y)
            )
            y_end: int = (
                int((self.position.y + step) / tile_map.tile_size.y) if step < 0 else
                int((self.position.y + self.size.y + step) / tile_map.tile_size.y)
            ) + step_dir

            # If stays on the same tile after moving then we assume collisions here were handled earlier
            if y_start == y_end:
                self.position.y += step

            # Will enter new tiles - we have to check them
            else:
                x_start: int = int(self.position.x / tile_map.tile_size.x)
                x_end: int = int((self.position.x + self.size.x) / tile_map.tile_size.x)

                if self.position.x + self.size.x > x_end * tile_map.tile_size.x:
                    x_end += 1

                collided: bool = False

                for y in range(y_start, y_end, step_dir):
                    for x in range(x_start, x_end):
                        if tile_map.get_tile_at(x, y).solid:
                            # Found collision - stop here
                            collided = True

                            if step > 0:
                                self.position.y = y * tile_map.tile_size.y - self.size.y
                            else:
                                self.position.y = (y + 1) * tile_map.tile_size.y

                            break

                    if collided:
                        break

                self.on_ground = collided and self.velocity.y > 0

                if collided:
                    self.velocity.y = 0
                else:
                    self.position.y += step
