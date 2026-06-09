from engine.vec2 import Vec2
import pygame
import tilemap

class Player:
    def __init__(self, size: float) -> None:
        self.position: Vec2         = Vec2(0.0, 0.0)
        self.velocity: Vec2         = Vec2(0.0, 0.0)
        self.direction: float       = 0.0
        self.size: Vec2             = Vec2(size, size)
        self.on_ground: bool        = False
        self.can_jump_cancel: bool  = False


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.direction -= 1.0
            elif event.key == pygame.K_d:
                self.direction += 1.0
            elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
                if self.on_ground:
                    self.can_jump_cancel = True
                    self.velocity.y -= 800.0

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.direction += 1.0
            elif event.key == pygame.K_d:
                self.direction -= 1.0
            elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
                if self.can_jump_cancel and self.velocity.y < 0:
                    self.can_jump_cancel = False
                    self.velocity.y += 300.0


    def draw(self, surface: pygame.Surface, negative_offset: Vec2) -> None:
        px: float = self.position.x - negative_offset.x
        py: float = self.position.y - negative_offset.y

        surface.fill(
            pygame.Color(0x80, 0x80, 0xB0),
            (
                px if px > 0 else 0,
                py if py > 0 else 0,
                self.size.x + (px if px < 0 else 0),
                self.size.y + (py if py < 0 else 0)
            )
        )


    def move(self, tile_map: tilemap.TileMap, delta: float) -> None:
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
