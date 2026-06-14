from engine.vec2 import Vec2
import math
import os
import pygame
import tilemap


def sign(x: float) -> float:
    if x == 0.0:
        return 0.0

    if x >= 0:
        return 1.0

    return -1.0


def move_towards(current: float, target: float, step: float) -> float:
    return current + sign(target - current) * min(abs(target - current), abs(step))


class Player:
    def __init__(
            self,
            position: Vec2 = Vec2(0, 0),
            size: Vec2 = Vec2(100, 100),
    ) -> None:
        self.sprites: list[pygame.Surface] | None  = None
        self.position: Vec2                     = position
        self.velocity: Vec2                     = Vec2(0.0, 0.0)
        self.size: Vec2                         = size

        self.energy: int                        = 1
        self.max_energy: int                    = 1

        self.acceleration: float                = 2400.0
        self.max_speed: float                   = 600.0
        self.gravity: float                     = 2000.0
        self.jump_acceleration: float           = 1000.0
        self.boosted_jump_acceleration: float   = 2000.0
        self.jump_cancel: float                 = 500.0

        self.direction: int                     = 0
        self.on_ground: bool                    = False
        self.can_jump_cancel: bool              = False
        self.boosted_jump: bool                 = False

        self.touched_spawnpoint: tuple[int, int] | None  = None
        self.saved_spawnpoint: tuple[int, int] | None    = None

        self.sprite_timer: float = 0.0
        self.sprite_dir: float = 1.0


    def update_from_dict(self, data: dict, textures_folder: str) -> None:
        if data.get("sprites") is not None:
            self.sprites = []
            for name in data["sprites"]:
                self.sprites.append(pygame.image.load(os.path.join(textures_folder, name)).convert_alpha())

        if data.get("position") is not None:
            self.position = Vec2(data["position"][0], data["position"][1])

        if data.get("size") is not None:
            self.size = Vec2(data["size"][0], data["size"][1])

        if data.get("acceleration") is not None:
            self.acceleration = data["acceleration"]

        if data.get("max_speed") is not None:
            self.max_speed = data["max_speed"]

        if data.get("gravity") is not None:
            self.gravity = data["gravity"]

        if data.get("jump_acceleration") is not None:
            self.jump_acceleration = data["jump_acceleration"]

        if data.get("boosted_jump_acceleration") is not None:
            self.boosted_jump_acceleration = data["boosted_jump_acceleration"]

        if data.get("jump_cancel") is not None:
            self.jump_cancel = data["jump_cancel"]



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

                    if self.boosted_jump:
                        self.velocity.y -= self.boosted_jump_acceleration
                        self.boosted_jump = False
                    else:
                        self.velocity.y -= self.jump_acceleration

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.direction += 1.0
            elif event.key == pygame.K_d:
                self.direction -= 1.0
            elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
                if self.can_jump_cancel and self.velocity.y < 0:
                    self.can_jump_cancel = False
                    self.velocity.y += self.jump_cancel

        self.direction = max(-1, min(1, self.direction))


    def draw(self, surface: pygame.Surface, negative_offset: Vec2) -> None:
        px: float = self.position.x - negative_offset.x + (self.size.x - self.sprites[0].get_width()) / 2
        py: float = self.position.y - negative_offset.y + (self.size.y - self.sprites[0].get_height()) / 2

        py += math.sin(self.sprite_timer) * 10

        if self.direction > 0:
            self.sprite_dir = 1.0
        elif self.direction < 0:
            self.sprite_dir = -1.0

        if self.sprite_dir > 0:
            surface.blit(self.sprites[int(self.sprite_timer) % len(self.sprites)], (px, py))
        else:
            surface.blit(
                pygame.transform.flip(self.sprites[int(self.sprite_timer) % len(self.sprites)], True, False),
                (px, py)
            )


    def update(self, tile_map: tilemap.TileMap, delta: float) -> None:
        self.sprite_timer += delta

        # self.velocity.x = self.direction * self.max_speed
        self.velocity.x = move_towards(self.velocity.x, self.direction * self.max_speed, self.acceleration * delta)
        self.velocity.y += self.gravity * delta

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

                if collided:
                    self.velocity.x = 0.0
                else:
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
