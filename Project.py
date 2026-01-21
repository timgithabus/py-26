import arcade
import math

SCREEN_WIDTH = 4000
SCREEN_HEIGHT = 4000
SCREEN_TITLE = "Игра на PyArcade: карта и герой"
CAMERA_LERP = 0.12

MAP_IMAGE = "map.png"
HERO_IMAGE = "пудж.png"

MAP_SCALE = 5.0


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.map = arcade.load_texture('images/map.jpg')
        self.hero_sprite = arcade.Sprite('images/пудж.png', scale=0.25)
        self.hero_sprite.center_x = width // 2
        self.hero_sprite.center_y = height // 2

        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.hero_sprite)

        self.speed = 5

    def on_draw(self):
        self.world_camera.use()
        self.gui_camera.use()
        rect = arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        arcade.draw_texture_rect(self.map, rect)
        self.sprite_list.draw()

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
        position = (
            self.hero_sprite.center_x,
            self.hero_sprite.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            CAMERA_LERP
        )


def setup_game(width, height, title):
    game = MyGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()