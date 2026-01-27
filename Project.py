import random
import arcade
from arcade import Camera2D
import math

WORLD_WIDTH = 5000
WORLD_HEIGHT = 5000
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "PyArcade Game"
CAMERA_LERP = 0.12
ENEMY_COLLISION_RADIUS = 25
FIRE_ARROW_SPEED = 12
ARROW_COOLDOWN = 1.0
ICE_BALL_SPEED = 10
ICE_BALL_COOLDOWN = 2.0
HERO_ATTACK_RANGE = 100
HERO_ATTACK_DAMAGE = 20
HERO_ATTACK_COOLDOWN = 0.5
HERO_MAX_HP = 200
ENEMY_MAX_HP = 100
BOSS_MAX_HP = 500


class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__('images/пудж.png', scale=0.25)
        self.center_x = WORLD_WIDTH // 2
        self.center_y = WORLD_HEIGHT // 2
        self.max_hp = HERO_MAX_HP
        self.hp = self.max_hp
        self.attack_cooldown = 0
        self.change_x = 0
        self.change_y = 0
        self.speed = 8
        self.collision_radius = 40


class FireArrow(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__('images/fire_arrow.jpg', scale=0.05)
        self.center_x = x
        self.center_y = y
        self.speed = FIRE_ARROW_SPEED
        self.damage = 10
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            self.change_x = (dx / distance) * self.speed
            self.change_y = (dy / distance) * self.speed
            self.angle = math.degrees(math.atan2(dy, dx)) - 90
        self.collision_radius = 15

    def update(self, delta_time=0):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if (self.center_x < 0 or self.center_x > WORLD_WIDTH or
                self.center_y < 0 or self.center_y > WORLD_HEIGHT):
            self.remove_from_sprite_lists()


class IceBall(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__('images/ice_ball.jpg', scale=0.25)
        self.center_x = x
        self.center_y = y
        self.speed = ICE_BALL_SPEED
        self.damage = 25
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            self.change_x = (dx / distance) * self.speed
            self.change_y = (dy / distance) * self.speed
            self.angle = math.degrees(math.atan2(dy, dx)) - 90
        self.collision_radius = 20

    def update(self, delta_time=0):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if (self.center_x < 0 or self.center_x > WORLD_WIDTH or
                self.center_y < 0 or self.center_y > WORLD_HEIGHT):
            self.remove_from_sprite_lists()


class EnemyBase(arcade.Sprite):
    def __init__(self, image, scale, x, y, target, collision_radius):
        super().__init__(image, scale)
        self.center_x = x
        self.center_y = y
        self.max_hp = ENEMY_MAX_HP
        self.hp = self.max_hp
        self.target = target
        self.collision_radius = collision_radius

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        return self.hp <= 0


class EnemiesPudge(EnemyBase):
    def __init__(self, x, y, target):
        super().__init__('images/enemy_pudge.png', 0.05, x, y, target, 35)
        self.speed = 1.5

    def update(self, delta_time):
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            self.center_x += (dx / distance) * self.speed
            self.center_y += (dy / distance) * self.speed


class FireArchers(EnemyBase):
    def __init__(self, x, y, target):
        super().__init__('images/fire_archer.jpg', 0.05, x, y, target, 30)
        self.speed = 1.5
        self.arrow_cooldown = 0
        self.shooting = False
        self.stop_distance = 200

    def fire_arrow(self):
        if self.arrow_cooldown <= 0:
            arrow = FireArrow(
                self.center_x,
                self.center_y,
                self.target.center_x,
                self.target.center_y
            )
            self.arrow_cooldown = ARROW_COOLDOWN
            return arrow
        return None

    def update(self, delta_time):
        if self.arrow_cooldown > 0:
            self.arrow_cooldown -= delta_time

        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            if distance > self.stop_distance:
                self.center_x += (dx / distance) * self.speed
                self.center_y += (dy / distance) * self.speed
                self.shooting = False
            else:
                self.shooting = True


class BossDragon(EnemyBase):
    def __init__(self, x, y, target):
        super().__init__('images/ice_dragon.jpg', 0.5, x, y, target, 80)
        self.max_hp = BOSS_MAX_HP
        self.hp = self.max_hp
        self.speed = 3
        self.ice_cooldown = 0
        self.shooting = False
        self.stop_distance = 750

    def ice_ball(self):
        if self.ice_cooldown <= 0:
            ball = IceBall(
                self.center_x,
                self.center_y,
                self.target.center_x,
                self.target.center_y
            )
            self.ice_cooldown = ICE_BALL_COOLDOWN
            return ball
        return None

    def update(self, delta_time):
        if self.ice_cooldown > 0:
            self.ice_cooldown -= delta_time

        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            if distance > self.stop_distance:
                self.center_x += (dx / distance) * self.speed
                self.center_y += (dy / distance) * self.speed
                self.shooting = False
            else:
                self.shooting = True


class Game(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.map = arcade.load_texture('images/map.jpg')

        self.hero = Hero()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.hero)

        self.fire_archers_list = arcade.SpriteList()
        self.pudge_list = arcade.SpriteList()
        self.fire_arrows_list = arcade.SpriteList()
        self.ice_balls_list = arcade.SpriteList()
        self.boss_list = arcade.SpriteList()

        self.world_camera.position = (self.hero.center_x, self.hero.center_y)
        self.create_enemies()

    def create_enemies(self):
        boss = BossDragon(
            random.randint(500, WORLD_WIDTH - 500),
            random.randint(500, WORLD_HEIGHT - 500),
            self.hero
        )
        self.boss_list.append(boss)

        enemies_created = 0
        min_distance = 200
        all_positions = [(boss.center_x, boss.center_y)]

        while enemies_created < 30:
            x = random.randint(100, WORLD_WIDTH - 100)
            y = random.randint(100, WORLD_HEIGHT - 100)

            hero_distance = math.sqrt((x - self.hero.center_x) ** 2 + (y - self.hero.center_y) ** 2)
            if hero_distance < 500:
                continue

            too_close = False
            for pos in all_positions:
                dist = math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
                if dist < min_distance:
                    too_close = True
                    break

            if not too_close:
                pudge = EnemiesPudge(x, y, self.hero)
                self.pudge_list.append(pudge)
                all_positions.append((x, y))
                enemies_created += 1

        enemies_created = 0
        while enemies_created < 30:
            x = random.randint(100, WORLD_WIDTH - 100)
            y = random.randint(100, WORLD_HEIGHT - 100)

            hero_distance = math.sqrt((x - self.hero.center_x) ** 2 + (y - self.hero.center_y) ** 2)
            if hero_distance < 500:
                continue

            too_close = False
            for pos in all_positions:
                dist = math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
                if dist < min_distance:
                    too_close = True
                    break

            if not too_close:
                archer = FireArchers(x, y, self.hero)
                self.fire_archers_list.append(archer)
                all_positions.append((x, y))
                enemies_created += 1

    def prevent_collisions(self):
        all_entities = []
        all_entities.extend(self.pudge_list)
        all_entities.extend(self.fire_archers_list)
        all_entities.extend(self.boss_list)
        all_entities.append(self.hero)

        for i in range(len(all_entities)):
            entity1 = all_entities[i]
            for j in range(i + 1, len(all_entities)):
                entity2 = all_entities[j]

                dx = entity2.center_x - entity1.center_x
                dy = entity2.center_y - entity1.center_y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                min_separation = entity1.collision_radius + entity2.collision_radius + 5

                if distance < min_separation and distance > 0:
                    overlap = min_separation - distance
                    move_x = (dx / distance) * overlap * 0.5
                    move_y = (dy / distance) * overlap * 0.5

                    entity1.center_x -= move_x
                    entity1.center_y -= move_y
                    entity2.center_x += move_x
                    entity2.center_y += move_y
                    self.keep_in_bounds(entity1)
                    self.keep_in_bounds(entity2)

    def keep_in_bounds(self, entity):
        radius = entity.collision_radius
        if entity.center_x - radius <= 0:
            entity.center_x = radius
        if entity.center_x + radius >= WORLD_WIDTH:
            entity.center_x = WORLD_WIDTH - radius
        if entity.center_y - radius <= 0:
            entity.center_y = radius
        if entity.center_y + radius >= WORLD_HEIGHT:
            entity.center_y = WORLD_HEIGHT - radius

    def hero_attack(self):
        for enemy in self.pudge_list:
            distance = math.sqrt((enemy.center_x - self.hero.center_x) ** 2 + (enemy.center_y - self.hero.center_y) ** 2)
            if distance <= HERO_ATTACK_RANGE:
                if enemy.take_damage(HERO_ATTACK_DAMAGE):
                    enemy.remove_from_sprite_lists()

        for archer in self.fire_archers_list:
            distance = math.sqrt((archer.center_x - self.hero.center_x) ** 2 + (archer.center_y - self.hero.center_y) ** 2)
            if distance <= HERO_ATTACK_RANGE:
                if archer.take_damage(HERO_ATTACK_DAMAGE):
                    archer.remove_from_sprite_lists()

        for boss in self.boss_list:
            distance = math.sqrt((boss.center_x - self.hero.center_x) ** 2 + (boss.center_y - self.hero.center_y) ** 2)
            if distance <= HERO_ATTACK_RANGE:
                if boss.take_damage(HERO_ATTACK_DAMAGE):
                    boss.remove_from_sprite_lists()

    def draw_health_bar(self):
        hp_text = f"HP: {self.hero.hp}/{self.hero.max_hp}"
        arcade.draw_text(hp_text, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40, arcade.color.WHITE, 24, bold=True)

        hp_percentage = self.hero.hp / self.hero.max_hp
        bar_width = 200
        bar_height = 20
        bar_x = SCREEN_WIDTH - bar_width - 10
        bar_y = SCREEN_HEIGHT - 80

        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_width, bar_height, arcade.color.DARK_GRAY)

        current_width = bar_width * hp_percentage
        if current_width > 0:
            color = arcade.color.GREEN if hp_percentage > 0.5 else arcade.color.YELLOW if hp_percentage > 0.2 else arcade.color.RED
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, current_width, bar_height, color)

    def on_draw(self):
        self.clear()
        self.world_camera.use()

        rect = arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        arcade.draw_texture_rect(self.map, rect)

        self.pudge_list.draw()
        self.fire_archers_list.draw()
        self.fire_arrows_list.draw()
        self.ice_balls_list.draw()
        self.boss_list.draw()
        self.player_list.draw()

        self.gui_camera.use()
        self.draw_health_bar()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.hero.attack_cooldown <= 0:
            self.hero_attack()
            self.hero.attack_cooldown = HERO_ATTACK_COOLDOWN

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.hero.change_y = self.hero.speed
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.hero.change_y = -self.hero.speed
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.hero.change_x = -self.hero.speed
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.hero.change_x = self.hero.speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S):
            self.hero.change_y = 0
        if key in (arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D):
            self.hero.change_x = 0

    def on_update(self, delta_time):
        if self.hero.attack_cooldown > 0:
            self.hero.attack_cooldown -= delta_time

        self.player_list.update()
        self.pudge_list.update(delta_time)
        self.fire_arrows_list.update(delta_time)
        self.ice_balls_list.update(delta_time)

        for archer in self.fire_archers_list:
            archer.update(delta_time)
            if archer.shooting:
                arrow = archer.fire_arrow()
                if arrow:
                    self.fire_arrows_list.append(arrow)

        for boss in self.boss_list:
            boss.update(delta_time)
            if boss.shooting:
                ice_ball = boss.ice_ball()
                if ice_ball:
                    self.ice_balls_list.append(ice_ball)

        self.prevent_collisions()

        self.hero.center_x += self.hero.change_x
        self.hero.center_y += self.hero.change_y

        if self.hero.center_y + self.hero.height // 2 >= WORLD_HEIGHT:
            self.hero.center_y = WORLD_HEIGHT - self.hero.height // 2
        if self.hero.center_y - self.hero.height // 2 <= 0:
            self.hero.center_y = self.hero.height // 2
        if self.hero.center_x + self.hero.width // 2 >= WORLD_WIDTH:
            self.hero.center_x = WORLD_WIDTH - self.hero.width // 2
        if self.hero.center_x - self.hero.width // 2 <= 0:
            self.hero.center_x = self.hero.width // 2

        for arrow in self.fire_arrows_list:
            if arcade.check_for_collision(arrow, self.hero):
                self.hero.hp -= arrow.damage
                arrow.remove_from_sprite_lists()
                if self.hero.hp <= 0:
                    self.hero.hp = 0

        for ball in self.ice_balls_list:
            if arcade.check_for_collision(ball, self.hero):
                self.hero.hp -= ball.damage
                ball.remove_from_sprite_lists()
                if self.hero.hp <= 0:
                    self.hero.hp = 0

        target = (self.hero.center_x, self.hero.center_y)
        cx, cy = self.world_camera.position
        smooth_x = cx + (target[0] - cx) * CAMERA_LERP
        smooth_y = cy + (target[1] - cy) * CAMERA_LERP

        half_w = SCREEN_WIDTH / 2
        half_h = SCREEN_HEIGHT / 2

        cam_x = max(half_w, min(WORLD_WIDTH - half_w, smooth_x))
        cam_y = max(half_h, min(WORLD_HEIGHT - half_h, smooth_y))

        self.world_camera.position = (cam_x, cam_y)


def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()