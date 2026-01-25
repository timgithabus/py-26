import random
import arcade
from arcade import Camera2D
import math

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Игра на PyArcade: карта и герой"
CAMERA_LERP = 0.12


class Enemies_pudge(arcade.Sprite):
    def __init__(self, x, y, target):
        super().__init__('images/enemy_pudge.png', scale=0.05)
        self.center_x = x
        self.center_y = y
        self.speed = 2.5
        self.target = target

    def update(self, delta_time: float = 1 / 60):
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        if dx != 0 or dy != 0:
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance > 0:
                self.center_x += (dx / distance) * self.speed
                self.center_y += (dy / distance) * self.speed


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.world_camera.position = (self.width // 2, self.height // 2)

        self.map = arcade.load_texture('images/map.jpg')
        self.hero_sprite = arcade.Sprite('images/пудж.png', scale=0.25)
        self.hero_sprite.center_x = self.width // 2
        self.hero_sprite.center_y = self.height // 2

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.hero_sprite)

        self.speed = 5
        self.pudge_list = arcade.SpriteList()
        for i in range(20):
            num = random.randint(1, 4)
            if num == 1:
                x = random.randint(52, self.hero_sprite.center_x - 100)
                y = random.randint(52, SCREEN_HEIGHT - 52)
            elif num == 2:
                x = random.randint(52, SCREEN_WIDTH - 52)
                y = random.randint(52, self.hero_sprite.center_y - 100)
            elif num == 3:
                x = random.randint(self.hero_sprite.center_x + 100, SCREEN_WIDTH - 52)
                y = random.randint(52, SCREEN_HEIGHT - 52)
            elif num == 4:
                x = random.randint(52, SCREEN_WIDTH - 52)
                y = random.randint(self.hero_sprite.center_y + 100, SCREEN_HEIGHT - 52)

            pudge = Enemies_pudge(x, y, self.hero_sprite)
            self.pudge_list.append(pudge)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        rect = arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        arcade.draw_texture_rect(self.map, rect)
        self.pudge_list.draw()
        self.player_list.draw()
        self.gui_camera.use()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.hero_sprite.change_y = self.speed
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.hero_sprite.change_y = -self.speed
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.hero_sprite.change_x = -self.speed
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.hero_sprite.change_x = self.speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S):
            self.hero_sprite.change_y = 0
        if key in (arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D):
            self.hero_sprite.change_x = 0

    def on_update(self, delta_time):
        self.player_list.update()
        self.pudge_list.update()
        self.hero_sprite.center_x += self.hero_sprite.change_x
        self.hero_sprite.center_y += self.hero_sprite.change_y
        if self.hero_sprite.center_y + self.hero_sprite.height // 2 >= SCREEN_HEIGHT:
            self.hero_sprite.center_y = SCREEN_HEIGHT - self.hero_sprite.height // 2
        if self.hero_sprite.center_y - self.hero_sprite.height // 2 <= 0:
            self.hero_sprite.center_y = self.hero_sprite.height // 2
        if self.hero_sprite.center_x + self.hero_sprite.width // 2 >= SCREEN_WIDTH:
            self.hero_sprite.center_x = SCREEN_WIDTH - self.hero_sprite.width // 2
        if self.hero_sprite.center_x - self.hero_sprite.width // 2 <= 0:
            self.hero_sprite.center_x = self.hero_sprite.width // 2
        target = (self.hero_sprite.center_x, self.hero_sprite.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        cam_x = max(half_w, min(self.width - half_w, smooth[0]))
        cam_y = max(half_h, min(self.height - half_h, smooth[1]))
        self.world_camera.position = (cam_x, cam_y)


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()