import random
import arcade
from arcade import Camera2D
import math

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Игра на PyArcade: карта и герой"
CAMERA_LERP = 0.12
ENEMY_COLLISION_RADIUS = 25  # Радиус для проверки столкновений между врагами
FIRE_ARROW_SPEED = 8  # Скорость полета стрелы
ARROW_COOLDOWN = 1.0  # Задержка между выстрелами в секундах


class FireArrow(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__('images/fire_arrow.jpg', scale=0.05)
        self.center_x = x
        self.center_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = FIRE_ARROW_SPEED
        self.damage = 10

        # Вычисляем направление к цели
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            self.change_x = (dx / distance) * self.speed
            self.change_y = (dy / distance) * self.speed

            # Вычисляем угол поворота для стрелы (чтобы она смотрела острием на цель)
            self.angle = math.degrees(math.atan2(dy, dx)) - 90

    def update(self):
        # Обновляем позицию стрелы
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Удаляем стрелу, если она вышла за пределы экрана
        if (self.center_x < 0 or self.center_x > SCREEN_WIDTH or
                self.center_y < 0 or self.center_y > SCREEN_HEIGHT):
            self.remove_from_sprite_lists()


class fire_archers(arcade.Sprite):
    def __init__(self, x, y, target):
        super().__init__('images/fire_archer.jpg', scale=0.05)
        self.center_x = x
        self.center_y = y
        self.hp = 100
        self.speed = 1
        self.target = target
        self.collision_radius = ENEMY_COLLISION_RADIUS
        self.fire_range = 250  # Дистанция стрельбы
        self.arrow_cooldown = 0  # Таймер для задержки между выстрелами
        self.shooting = False  # Флаг, что лучник стреляет
        self.stop_distance = 200  # Дистанция на которой лучник останавливается

    def fire_arrow(self, *arrow_list):
        arrow_list = list(arrow_list[1:])
        """Создает огненную стрелу и добавляет ее в список стрел"""
        if self.arrow_cooldown <= 0:
            # Создаем стрелу, которая летит в сторону цели
            arrow = FireArrow(
                self.center_x,
                self.center_y,
                self.target.center_x,
                self.target.center_y
            )
            arrow_list.append(arrow)
            self.arrow_cooldown = ARROW_COOLDOWN  # Устанавливаем задержку перед следующим выстрелом
            return True
        return False

    def update(self, delta_time):
        # Обновляем таймер задержки
        if self.arrow_cooldown > 0:
            self.arrow_cooldown -= delta_time

        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            # Если расстояние больше дистанции стрельбы - двигаемся к герою
            if distance > self.stop_distance:
                self.center_x += (dx / distance) * self.speed
                self.center_y += (dy / distance) * self.speed
                self.shooting = False
            else:
                # Если в радиусе стрельбы - смотрим на героя и можем стрелять
                self.shooting = True

                # Поворачиваем лучника лицом к герою
                angle = math.degrees(math.atan2(dy, dx)) - 90
                self.angle = angle


class Enemies_pudge(arcade.Sprite):
    def __init__(self, x, y, target):
        super().__init__('images/enemy_pudge.png', scale=0.05)
        self.center_x = x
        self.center_y = y
        self.hp = 100
        self.speed = 1
        self.target = target
        self.collision_radius = ENEMY_COLLISION_RADIUS

    def update(self, delta_time):
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
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
        self.fire_archers_list = arcade.SpriteList()
        self.pudge_list = arcade.SpriteList()
        self.fire_arrows_list = arcade.SpriteList()  # Список для хранения стрел

        enemies_created = 0
        min_distance = 80  # Увеличили минимальное расстояние для всех врагов

        # Создаем всех врагов с проверкой расстояния между всеми типами
        all_enemies_positions = []  # Будем хранить позиции всех врагов

        # Создаем пуджей
        while enemies_created < 20:
            num = random.randint(1, 4)
            if num == 1:
                x = random.randint(100, self.hero_sprite.center_x - 200)
                y = random.randint(100, SCREEN_HEIGHT - 100)
            elif num == 2:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, self.hero_sprite.center_y - 200)
            elif num == 3:
                x = random.randint(self.hero_sprite.center_x + 200, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 100)
            elif num == 4:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(self.hero_sprite.center_y + 200, SCREEN_HEIGHT - 100)

            # Проверяем расстояние до всех существующих врагов
            too_close = False
            for existing_pos in all_enemies_positions:
                dist = math.sqrt((x - existing_pos[0]) ** 2 + (y - existing_pos[1]) ** 2)
                if dist < min_distance:
                    too_close = True
                    break

            if not too_close:
                pudge = Enemies_pudge(x, y, self.hero_sprite)
                self.pudge_list.append(pudge)
                all_enemies_positions.append((x, y))
                enemies_created += 1

        # Создаем лучников
        enemies_created = 0
        while enemies_created < 20:
            num = random.randint(1, 4)
            if num == 1:
                x = random.randint(100, self.hero_sprite.center_x - 200)
                y = random.randint(100, SCREEN_HEIGHT - 100)
            elif num == 2:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, self.hero_sprite.center_y - 200)
            elif num == 3:
                x = random.randint(self.hero_sprite.center_x + 200, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 100)
            elif num == 4:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(self.hero_sprite.center_y + 200, SCREEN_HEIGHT - 100)

            # Проверяем расстояние до всех существующих врагов (и пуджей и лучников)
            too_close = False
            for existing_pos in all_enemies_positions:
                dist = math.sqrt((x - existing_pos[0]) ** 2 + (y - existing_pos[1]) ** 2)
                if dist < min_distance:
                    too_close = True
                    break

            if not too_close:
                fire_archer = fire_archers(x, y, self.hero_sprite)
                self.fire_archers_list.append(fire_archer)
                all_enemies_positions.append((x, y))
                enemies_created += 1

    def prevent_enemy_overlap(self):
        """Предотвращает наложение всех врагов друг на друга"""
        all_enemies = []

        # Собираем всех врагов в один список
        for pudge in self.pudge_list:
            all_enemies.append(('pudge', pudge))
        for archer in self.fire_archers_list:
            all_enemies.append(('archer', archer))

        # Проверяем все пары врагов
        for i in range(len(all_enemies)):
            type1, enemy1 = all_enemies[i]
            for j in range(i + 1, len(all_enemies)):
                type2, enemy2 = all_enemies[j]

                dx = enemy2.center_x - enemy1.center_x
                dy = enemy2.center_y - enemy1.center_y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                min_separation = enemy1.collision_radius + enemy2.collision_radius

                # Если враги слишком близко, раздвигаем их
                if distance < min_separation and distance > 0:
                    overlap = min_separation - distance
                    move_x = (dx / distance) * overlap * 0.5
                    move_y = (dy / distance) * overlap * 0.5

                    enemy1.center_x -= move_x
                    enemy1.center_y -= move_y
                    enemy2.center_x += move_x
                    enemy2.center_y += move_y

                    # Удерживаем врагов в пределах экрана
                    self.keep_enemy_in_bounds(enemy1)
                    self.keep_enemy_in_bounds(enemy2)

    def keep_enemy_in_bounds(self, enemy):
        enemy_radius = enemy.collision_radius
        if enemy.center_x - enemy_radius <= 0:
            enemy.center_x = enemy_radius
        if enemy.center_x + enemy_radius >= SCREEN_WIDTH:
            enemy.center_x = SCREEN_WIDTH - enemy_radius
        if enemy.center_y - enemy_radius <= 0:
            enemy.center_y = enemy_radius
        if enemy.center_y + enemy_radius >= SCREEN_HEIGHT:
            enemy.center_y = SCREEN_HEIGHT - enemy_radius

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        rect = arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        arcade.draw_texture_rect(self.map, rect)
        self.pudge_list.draw()
        self.fire_archers_list.draw()
        self.fire_arrows_list.draw()  # Рисуем стрелы
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
        # Обновляем все списки спрайтов
        self.player_list.update()
        self.pudge_list.update(delta_time)  # Передаем delta_time для пуджей
        self.fire_arrows_list.update()  # Обновляем стрелы

        # Обновляем лучников и проверяем, могут ли они стрелять
        for archer in self.fire_archers_list:
            archer.update(delta_time)
            # Если лучник может стрелять (находится в радиусе атаки и прошла задержка)
            if archer.shooting:
                archer.fire_arrow(self.fire_arrows_list)

        # Предотвращаем наложение врагов
        self.prevent_enemy_overlap()

        # Обновляем позицию героя
        self.hero_sprite.center_x += self.hero_sprite.change_x
        self.hero_sprite.center_y += self.hero_sprite.change_y

        # Ограничиваем движение героя в пределах экрана
        if self.hero_sprite.center_y + self.hero_sprite.height // 2 >= SCREEN_HEIGHT:
            self.hero_sprite.center_y = SCREEN_HEIGHT - self.hero_sprite.height // 2
        if self.hero_sprite.center_y - self.hero_sprite.height // 2 <= 0:
            self.hero_sprite.center_y = self.hero_sprite.height // 2
        if self.hero_sprite.center_x + self.hero_sprite.width // 2 >= SCREEN_WIDTH:
            self.hero_sprite.center_x = SCREEN_WIDTH - self.hero_sprite.width // 2
        if self.hero_sprite.center_x - self.hero_sprite.width // 2 <= 0:
            self.hero_sprite.center_x = self.hero_sprite.width // 2

        # Проверяем столкновения стрел с героем
        for arrow in self.fire_arrows_list:
            if arcade.check_for_collision(arrow, self.hero_sprite):
                # Здесь можно добавить получение урона героем
                print("Герой получил урон от стрелы!")
                arrow.remove_from_sprite_lists()  # Удаляем стрелу при попадании

        # Обновляем камеру
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