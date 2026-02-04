import arcade
import math
import random

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
WITCH_DOKTOR_SPEED = 1.2
WITCH_DOKTOR_BULLET_SPEED = 8
WITCH_DOKTOR_BULLET_COOLDOWN = 3.0
WITCH_DOKTOR_BULLET_DAMAGE = 15
WITCH_DOKTOR_STOP_DISTANCE = 400
WITCH_DOKTOR_MAX_HP = 80
POISON_DURATION = 5.0
POISON_DAMAGE_PER_SECOND = 5
POISON_TICK_INTERVAL = 1.0
ORC_BOSS_MAX_HP = 800
ORC_BOSS_SPEED = 1
ORC_BOSS_DAMAGE = 100
ORC_BOSS_ATTACK_COOLDOWN = 2.0
ORC_BOSS_ATTACK_RANGE = 150
ORC_BOSS_STOP_DISTANCE = 200

MAX_SKILLS = 5

ASSET_DIR = "images"
MAP_IMAGE = f"{ASSET_DIR}/map.png"
HERO_IMAGE = f"{ASSET_DIR}/hero1.png"

MAP_WIDTH = WORLD_WIDTH
MAP_HEIGHT = WORLD_HEIGHT


def load_texture_safe(path):
    try:
        return arcade.load_texture(path)
    except Exception:
        return None


def make_solid_sprite(width, height, color):
    try:
        return arcade.SpriteSolidColor(width, height, color)
    except Exception:
        sprite = arcade.Sprite()
        tex = None
        try:
            tex = arcade.make_soft_square_texture(max(width, height), color, 255, 255)
        except Exception:
            tex = None
        if tex is not None:
            sprite.texture = tex
        sprite.width = width
        sprite.height = height
        return sprite


def make_sprite_from_candidates(candidates, scale, fallback_w, fallback_h, fallback_color):
    for path in candidates:
        try:
            try:
                return arcade.Sprite(path, scale=scale, hit_box_algorithm="Detailed")
            except TypeError:
                return arcade.Sprite(path, scale=scale)
        except Exception:
            continue
    sprite = make_solid_sprite(fallback_w, fallback_h, fallback_color)
    sprite.scale = 1.0
    return sprite


def apply_sprite_look(dst, src):
    try:
        dst.texture = src.texture
    except Exception:
        pass
    try:
        dst.scale = getattr(src, "scale", 1.0)
    except Exception:
        pass
    try:
        dst.width = src.width
        dst.height = src.height
    except Exception:
        pass
    try:
        dst.set_hit_box(src.hit_box)
        return
    except Exception:
        pass
    try:
        dst.set_hit_box(src.hit_box.points)
        return
    except Exception:
        pass
    try:
        dst.set_hit_box(src.hit_box_points)
        return
    except Exception:
        pass


class Hero(arcade.Sprite):
    def __init__(self, texture_candidates, scale=0.25):
        super().__init__()
        sprite = make_sprite_from_candidates(
            texture_candidates,
            scale=scale,
            fallback_w=64,
            fallback_h=64,
            fallback_color=arcade.color.BLUE,
        )
        apply_sprite_look(self, sprite)
        self.center_x = MAP_WIDTH // 2
        self.center_y = MAP_HEIGHT // 2
        self.max_hp = float(HERO_MAX_HP)
        self.hp = float(self.max_hp)
        self.attack_cooldown = 0.0
        self.speed = 8
        self.collision_radius = 40
        self.is_poisoned = False
        self.poison_duration = 0.0
        self.poison_damage_timer = 0.0
        self.poison_last_tick = 0.0
        self.poison_damage_per_second = float(POISON_DAMAGE_PER_SECOND)

    def apply_poison(self, duration=POISON_DURATION, damage_per_second=POISON_DAMAGE_PER_SECOND):
        self.is_poisoned = True
        self.poison_duration = float(duration)
        self.poison_damage_per_second = float(damage_per_second)
        self.poison_damage_timer = 0.0
        self.poison_last_tick = 0.0

    def update_poison(self, delta_time):
        if not self.is_poisoned:
            return
        self.poison_duration -= float(delta_time)
        self.poison_damage_timer += float(delta_time)
        if self.poison_damage_timer - self.poison_last_tick >= float(POISON_TICK_INTERVAL):
            self.hp -= float(self.poison_damage_per_second)
            self.poison_last_tick = self.poison_damage_timer
            if self.hp <= 0:
                self.hp = 0.0
                self.is_poisoned = False
        if self.poison_duration <= 0:
            self.is_poisoned = False


class FireArrow(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        sprite = make_sprite_from_candidates(
            [f"{ASSET_DIR}/fire_arrow.jpg", f"{ASSET_DIR}/fire_arrow.png", "fire_arrow.jpg", "fire_arrow.png"],
            scale=0.08,
            fallback_w=14,
            fallback_h=14,
            fallback_color=arcade.color.ORANGE,
        )
        apply_sprite_look(self, sprite)
        self.center_x = x
        self.center_y = y
        self.speed = float(FIRE_ARROW_SPEED)
        self.damage = 10
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1.0
        self.change_x = (dx / dist) * self.speed
        self.change_y = (dy / dist) * self.speed
        try:
            self.angle = math.degrees(math.atan2(dy, dx)) - 90
        except Exception:
            pass
        self.collision_radius = 15


class IceBall(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        sprite = make_sprite_from_candidates(
            [f"{ASSET_DIR}/ice_ball.jpg", f"{ASSET_DIR}/ice_ball.png", "ice_ball.jpg", "ice_ball.png"],
            scale=0.22,
            fallback_w=18,
            fallback_h=18,
            fallback_color=arcade.color.BLUE,
        )
        apply_sprite_look(self, sprite)
        self.center_x = x
        self.center_y = y
        self.speed = float(ICE_BALL_SPEED)
        self.damage = 25
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1.0
        self.change_x = (dx / dist) * self.speed
        self.change_y = (dy / dist) * self.speed
        try:
            self.angle = math.degrees(math.atan2(dy, dx)) - 90
        except Exception:
            pass
        self.collision_radius = 20


class WitchDoktorBullet(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        sprite = make_sprite_from_candidates(
            [
                f"{ASSET_DIR}/Witch_doctor_bullet.png",
                f"{ASSET_DIR}/witch_doctor_bullet.png",
                "Witch_doctor_bullet.png",
                "witch_doctor_bullet.png",
            ],
            scale=0.1,
            fallback_w=16,
            fallback_h=16,
            fallback_color=arcade.color.GREEN,
        )
        apply_sprite_look(self, sprite)
        self.center_x = x
        self.center_y = y
        self.speed = float(WITCH_DOKTOR_BULLET_SPEED)
        self.damage = int(WITCH_DOKTOR_BULLET_DAMAGE)
        self.poison_duration = float(POISON_DURATION)
        self.poison_damage_per_second = float(POISON_DAMAGE_PER_SECOND)
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1.0
        self.change_x = (dx / dist) * self.speed
        self.change_y = (dy / dist) * self.speed
        try:
            self.angle = math.degrees(math.atan2(dy, dx)) - 90
        except Exception:
            pass
        self.collision_radius = 20


class OrkBossBullet(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        sprite = make_sprite_from_candidates(
            [
                f"{ASSET_DIR}/ork_boss_bullet.png",
                f"{ASSET_DIR}/Witch_doctor_bullet.png",
                "ork_boss_bullet.png",
                "Witch_doctor_bullet.png",
            ],
            scale=0.15,
            fallback_w=20,
            fallback_h=20,
            fallback_color=arcade.color.DARK_RED,
        )
        apply_sprite_look(self, sprite)
        self.center_x = x
        self.center_y = y
        self.speed = float(WITCH_DOKTOR_BULLET_SPEED)
        self.damage = int(ORC_BOSS_DAMAGE)
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1.0
        self.change_x = (dx / dist) * self.speed
        self.change_y = (dy / dist) * self.speed
        try:
            self.angle = math.degrees(math.atan2(dy, dx)) - 90
        except Exception:
            pass
        self.collision_radius = 25


class EnemyBase(arcade.Sprite):
    def __init__(self, texture_candidates, scale, x, y, target, collision_radius):
        super().__init__()
        sprite = make_sprite_from_candidates(
            texture_candidates,
            scale=scale,
            fallback_w=48,
            fallback_h=48,
            fallback_color=arcade.color.DARK_RED,
        )
        apply_sprite_look(self, sprite)
        self.center_x = x
        self.center_y = y
        self.target = target
        self.collision_radius = float(collision_radius)
        self.max_hp = float(ENEMY_MAX_HP)
        self.hp = float(self.max_hp)
        self.damage = int(random.randint(5, 10))
        self.base_speed = 1.5
        self.speed_multiplier = 1.0
        self.slow_timer = 0.0
        self.hit_cooldown = 0.0
        self.is_poisoned = False
        self.poison_duration = 0.0
        self.poison_damage_timer = 0.0
        self.poison_last_tick = 0.0
        self.poison_damage_per_second = float(POISON_DAMAGE_PER_SECOND)
        self.shooting = False

    def take_damage(self, damage):
        self.hp -= float(damage)
        if self.hp <= 0:
            self.hp = 0.0
            return True
        return False

    def apply_slow(self, factor, duration):
        try:
            factor = float(factor)
        except Exception:
            factor = 1.0
        self.speed_multiplier = min(self.speed_multiplier, factor)
        self.slow_timer = max(self.slow_timer, float(duration))

    def apply_poison(self, duration=POISON_DURATION, damage_per_second=POISON_DAMAGE_PER_SECOND):
        self.is_poisoned = True
        self.poison_duration = float(duration)
        self.poison_damage_per_second = float(damage_per_second)
        self.poison_damage_timer = 0.0
        self.poison_last_tick = 0.0

    def update_poison(self, delta_time):
        if not self.is_poisoned:
            return
        self.poison_duration -= float(delta_time)
        self.poison_damage_timer += float(delta_time)
        if self.poison_damage_timer - self.poison_last_tick >= float(POISON_TICK_INTERVAL):
            self.hp -= float(self.poison_damage_per_second)
            self.poison_last_tick = self.poison_damage_timer
            if self.hp <= 0:
                self.hp = 0.0
                self.is_poisoned = False
        if self.poison_duration <= 0:
            self.is_poisoned = False

    def update_state(self, delta_time):
        if self.hit_cooldown > 0:
            self.hit_cooldown = max(0.0, self.hit_cooldown - float(delta_time))
        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - float(delta_time))
            if self.slow_timer == 0.0:
                self.speed_multiplier = 1.0
        if self.is_poisoned:
            self.update_poison(delta_time)

    def try_shoot(self):
        return None


class EnemiesPudge(EnemyBase):
    def __init__(self, x, y, target, level):
        super().__init__(
            [f"{ASSET_DIR}/enemy_pudge.png", "enemy_pudge.png"],
            scale=0.05,
            x=x,
            y=y,
            target=target,
            collision_radius=35,
        )
        self.max_hp = float(40 + level * 8)
        self.hp = float(self.max_hp)
        self.base_speed = 1.7 + min(1.6, level * 0.01)
        self.damage = int(random.randint(5, 10) * (1.0 + level * 0.02))
        self.shooting = False

    def update(self, delta_time: float = 1 / 60):
        self.update_state(delta_time)
        if self.target is None:
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            speed = float(self.base_speed) * float(self.speed_multiplier)
            self.center_x += (dx / dist) * speed
            self.center_y += (dy / dist) * speed


class WitchDoktor(EnemyBase):
    def __init__(self, x, y, target, level):
        super().__init__(
            [f"{ASSET_DIR}/witch_doktor.jpg", f"{ASSET_DIR}/witch_doktor.png", "witch_doktor.jpg", "witch_doktor.png"],
            scale=0.08,
            x=x,
            y=y,
            target=target,
            collision_radius=45,
        )
        self.max_hp = float(WITCH_DOKTOR_MAX_HP + level * 4)
        self.hp = float(self.max_hp)
        self.base_speed = float(WITCH_DOKTOR_SPEED)
        self.damage = int(random.randint(5, 10) * (1.0 + level * 0.02))
        self.bullet_cooldown = 0.0
        self.stop_distance = float(WITCH_DOKTOR_STOP_DISTANCE)
        self.shooting = False

    def witch_doktor_bullet(self):
        if self.bullet_cooldown > 0:
            return None
        self.bullet_cooldown = float(WITCH_DOKTOR_BULLET_COOLDOWN)
        bullet = WitchDoktorBullet(self.center_x, self.center_y, self.target.center_x, self.target.center_y)
        try:
            bullet.damage = int(max(float(bullet.damage), float(self.damage)))
        except Exception:
            pass
        return bullet

    def try_shoot(self):
        return self.witch_doktor_bullet()

    def update(self, delta_time):
        self.update_state(delta_time)
        if self.bullet_cooldown > 0:
            self.bullet_cooldown = max(0.0, self.bullet_cooldown - float(delta_time))
        if self.target is None:
            self.shooting = False
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            if dist > self.stop_distance:
                speed = float(self.base_speed) * float(self.speed_multiplier)
                self.center_x += (dx / dist) * speed
                self.center_y += (dy / dist) * speed
                self.shooting = False
            else:
                self.shooting = True


class FireArchers(EnemyBase):
    def __init__(self, x, y, target, level):
        super().__init__(
            [f"{ASSET_DIR}/fire_archer.jpg", f"{ASSET_DIR}/fire_archer.png", "fire_archer.jpg", "fire_archer.png"],
            scale=0.06,
            x=x,
            y=y,
            target=target,
            collision_radius=30,
        )
        self.max_hp = float(60 + level * 6)
        self.hp = float(self.max_hp)
        self.base_speed = 1.6 + min(1.2, level * 0.006)
        self.damage = int(random.randint(5, 10) * (1.0 + level * 0.02))
        self.arrow_cooldown = 0.0
        self.stop_distance = 260.0
        self.shooting = False

    def fire_arrow(self):
        if self.arrow_cooldown > 0:
            return None
        self.arrow_cooldown = float(ARROW_COOLDOWN)
        arrow = FireArrow(self.center_x, self.center_y, self.target.center_x, self.target.center_y)
        try:
            arrow.damage = int(max(float(arrow.damage), float(self.damage)))
        except Exception:
            pass
        return arrow

    def try_shoot(self):
        return self.fire_arrow()

    def update(self, delta_time):
        self.update_state(delta_time)
        if self.arrow_cooldown > 0:
            self.arrow_cooldown = max(0.0, self.arrow_cooldown - float(delta_time))
        if self.target is None:
            self.shooting = False
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            if dist > self.stop_distance:
                speed = float(self.base_speed) * float(self.speed_multiplier)
                self.center_x += (dx / dist) * speed
                self.center_y += (dy / dist) * speed
                self.shooting = False
            else:
                self.shooting = True


class BossDragon(EnemyBase):
    def __init__(self, x, y, target, level):
        super().__init__(
            [
                f"{ASSET_DIR}/blue_dragon.png",
                f"{ASSET_DIR}/ice_dragon.jpg",
                f"{ASSET_DIR}/ice_dragon.png",
                "blue_dragon.png",
                "ice_dragon.jpg",
                "ice_dragon.png",
            ],
            scale=0.35,
            x=x,
            y=y,
            target=target,
            collision_radius=250,
        )
        self.max_hp = float(BOSS_MAX_HP + level * 40)
        self.hp = float(self.max_hp)
        self.base_speed = 2.6
        self.damage = 40
        self.ice_cooldown = 0.0
        self.stop_distance = 720.0
        self.shooting = False

    def ice_ball(self):
        if self.ice_cooldown > 0:
            return None
        self.ice_cooldown = float(ICE_BALL_COOLDOWN)
        ball = IceBall(self.center_x, self.center_y, self.target.center_x, self.target.center_y)
        try:
            ball.damage = int(max(float(ball.damage), float(self.damage)))
        except Exception:
            pass
        return ball

    def try_shoot(self):
        return self.ice_ball()

    def update(self, delta_time):
        self.update_state(delta_time)
        if self.ice_cooldown > 0:
            self.ice_cooldown = max(0.0, self.ice_cooldown - float(delta_time))
        if self.target is None:
            self.shooting = False
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            if dist > self.stop_distance:
                speed = float(self.base_speed) * float(self.speed_multiplier)
                self.center_x += (dx / dist) * speed
                self.center_y += (dy / dist) * speed
                self.shooting = False
            else:
                self.shooting = True


class OrkBoss(EnemyBase):
    def __init__(self, x, y, target, level):
        super().__init__(
            [f"{ASSET_DIR}/ork_boss.jpg", f"{ASSET_DIR}/ork_boss.png", "ork_boss.jpg", "ork_boss.png"],
            scale=0.7,
            x=x,
            y=y,
            target=target,
            collision_radius=120,
        )
        self.max_hp = float(ORC_BOSS_MAX_HP + level * 30)
        self.hp = float(self.max_hp)
        self.base_speed = float(ORC_BOSS_SPEED)
        self.damage = int(ORC_BOSS_DAMAGE)
        self.attack_cooldown = 0.0
        self.stop_distance = float(ORC_BOSS_STOP_DISTANCE)
        self.attack_range = float(ORC_BOSS_ATTACK_RANGE)
        self.shooting = False

    def ork_boss_attack(self):
        if self.attack_cooldown > 0:
            return None
        self.attack_cooldown = float(ORC_BOSS_ATTACK_COOLDOWN)
        bullet = OrkBossBullet(self.center_x, self.center_y, self.target.center_x, self.target.center_y)
        try:
            bullet.damage = int(max(float(bullet.damage), float(self.damage)))
        except Exception:
            pass
        return bullet

    def try_shoot(self):
        return self.ork_boss_attack()

    def update(self, delta_time):
        self.update_state(delta_time)
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0.0, self.attack_cooldown - float(delta_time))
        if self.target is None:
            self.shooting = False
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            if dist > self.stop_distance:
                speed = float(self.base_speed) * float(self.speed_multiplier)
                self.center_x += (dx / dist) * speed
                self.center_y += (dy / dist) * speed
                self.shooting = False
            elif dist <= self.attack_range:
                self.shooting = True
            else:
                speed = float(self.base_speed) * float(self.speed_multiplier)
                self.center_x += (dx / dist) * speed
                self.center_y += (dy / dist) * speed
                self.shooting = False


Enemies_pudge = EnemiesPudge


class Start_menu(arcade.View):
    def __init__(self):
        super().__init__()
        self.map = load_texture_safe(MAP_IMAGE)
        if self.map is None:
            self.map = load_texture_safe("map.png")
        self.speed = 5
        self.selected_hero = 0
        self.hero_textures = []
        for i in range(4):
            tex = load_texture_safe(f"{ASSET_DIR}/hero{i+1}.png")
            if tex is None:
                tex = load_texture_safe(f"hero{i+1}.png")
            self.hero_textures.append(tex)

    def on_draw(self):
        self.clear()
        rect = arcade.rect.XYWH(
            self.window.width // 2, self.window.height // 2,
            self.window.width, self.window.height)
        if self.map is not None:
            arcade.draw_texture_rect(self.map, rect)
        else:
            arcade.draw_lbwh_rectangle_filled(0, 0, self.window.width, self.window.height, arcade.color.DARK_GRAY)

        title_y = self.window.height - 60
        arcade.draw_text(
            "МЕНЮ",
            self.window.width // 2,
            title_y,
            arcade.color.BLACK,
            42,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_lbwh_rectangle_filled(
            self.window.width // 2 - 220,
            title_y - 10,
            440,
            6,
            arcade.color.BLACK,
        )

        outline_color = arcade.color.BLACK
        fill_color = arcade.color.LIGHT_GRAY

        button1_x = self.window.width // 5 - 80
        button1_y = self.window.height - 210
        button_width = 500
        button_height = 80

        button2_x = self.window.width // 5 - 80
        button2_y = self.window.height - 305

        panel_x = button1_x - 30
        panel_y = button2_y - 35
        panel_w = button_width + 40
        panel_h = (button1_y - button2_y) + button_height + 60
        arcade.draw_lbwh_rectangle_filled(
            panel_x, panel_y, panel_w, panel_h, (255, 255, 255, 190)
        )

        arcade.draw_lbwh_rectangle_filled(
            button1_x, button1_y, button_width, button_height, fill_color)
        arcade.draw_lbwh_rectangle_outline(
            button1_x, button1_y, button_width, button_height, outline_color)

        arcade.draw_lbwh_rectangle_filled(
            button2_x, button2_y, button_width, button_height, fill_color)
        arcade.draw_lbwh_rectangle_outline(
            button2_x, button2_y, button_width, button_height, outline_color)

        arcade.draw_text("НАЧАТЬ ИГРАТЬ", button1_x + button_width // 2, button1_y + 40,
                         arcade.color.BLACK, font_size=20, anchor_x="center", anchor_y="center")
        arcade.draw_text("СМЕНА", button2_x + button_width // 2, button2_y + 40,
                         arcade.color.BLACK, font_size=20, anchor_x="center", anchor_y="center")

        preview_left = self.window.width - 320
        preview_bottom = self.window.height - 420
        preview_w = 300
        preview_h = 320
        arcade.draw_lbwh_rectangle_filled(
            preview_left, preview_bottom, preview_w, preview_h, (255, 255, 255, 190)
        )
        arcade.draw_lbwh_rectangle_outline(
            preview_left, preview_bottom, preview_w, preview_h, arcade.color.BLACK
        )
        arcade.draw_text(
            "Выбранный герой",
            preview_left + preview_w // 2,
            preview_bottom + preview_h - 30,
            arcade.color.BLACK,
            16,
            anchor_x="center",
            bold=True,
        )
        hero_texture = self.hero_textures[self.selected_hero]
        hero_rect = arcade.rect.XYWH(
            preview_left + preview_w // 2,
            preview_bottom + preview_h // 2 - 10,
            160,
            160,
        )
        if hero_texture is not None:
            arcade.draw_texture_rect(hero_texture, hero_rect)
        else:
            placeholder_left = preview_left + preview_w // 2 - 80
            placeholder_bottom = preview_bottom + preview_h // 2 - 10 - 80
            arcade.draw_lbwh_rectangle_filled(
                placeholder_left,
                placeholder_bottom,
                160,
                160,
                arcade.color.LIGHT_GRAY,
            )

    def on_mouse_press(self, x, y, button, modifiers):
        button1_x = self.window.width // 5 - 80
        button1_y = self.window.height - 210
        button_width = 500
        button_height = 80

        button2_x = self.window.width // 5 - 80
        button2_y = self.window.height - 305

        if (button1_x <= x <= button1_x + button_width and
                button1_y <= y <= button1_y + button_height):
            game_view = MyGame(selected_hero=self.selected_hero)
            self.window.show_view(game_view)

        if (button2_x <= x <= button2_x + button_width and
                button2_y <= y <= button2_y + button_height):
            hero_view = HeroSelectView(self)
            self.window.show_view(hero_view)


class HeroSelectView(arcade.View):
    def __init__(self, start_view):
        super().__init__()
        self.start_view = start_view
        self.map = load_texture_safe(MAP_IMAGE)
        if self.map is None:
            self.map = load_texture_safe("map.png")
        self.heroes = []
        for i in range(4):
            tex = load_texture_safe(f"{ASSET_DIR}/hero{i+1}.png")
            if tex is None:
                tex = load_texture_safe(f"hero{i+1}.png")
            self.heroes.append({
                "texture": tex,
                "str": 10 + i * 2,
                "def": 5 + i,
                "hp": HERO_MAX_HP + i * 20,
                "desc": f"Описание героя {i+1}."
            })
        self.selected = self.start_view.selected_hero

    def on_draw(self):
        self.clear()
        rect = arcade.rect.XYWH(
            self.window.width // 2, self.window.height // 2,
            self.window.width, self.window.height)
        if self.map is not None:
            arcade.draw_texture_rect(self.map, rect)
        else:
            arcade.draw_lbwh_rectangle_filled(0, 0, self.window.width, self.window.height, arcade.color.DARK_GRAY)
        panel_left = self.window.width - 320
        panel_right = self.window.width - 40
        panel_top = self.window.height - 80
        panel_bottom = 120

        list_panel_x = 90
        list_panel_y = 120
        list_panel_w = 260
        list_panel_h = 340
        arcade.draw_lbwh_rectangle_filled(
            list_panel_x, list_panel_y, list_panel_w, list_panel_h, (255, 255, 255, 200)
        )

        for i in range(len(self.heroes)):
            y = 400 - i * 70
            color = arcade.color.GRAY if i == self.selected else arcade.color.LIGHT_GRAY

            left = 130
            right = 130 + 180
            bottom = y
            top = y + 50

            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
            arcade.draw_text(
                f"Герой {i+1}",
                left + (right - left) // 2,
                y + 25,
                arcade.color.BLACK,
                16,
                anchor_x="center",
                anchor_y="center",
            )

        arcade.draw_lrbt_rectangle_filled(
            panel_left, panel_right, panel_bottom, panel_top, (255, 255, 255, 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            panel_left, panel_right, panel_bottom, panel_top, arcade.color.BLACK
        )
        hero_data = self.heroes[self.selected]
        texture = hero_data["texture"]
        icon_center_x = (panel_left + panel_right) // 2
        icon_center_y = panel_top - 80
        icon_rect = arcade.rect.XYWH(icon_center_x, icon_center_y, 120, 120)
        if texture is not None:
            arcade.draw_texture_rect(texture, icon_rect)
        else:
            placeholder_left = icon_center_x - 60
            placeholder_bottom = icon_center_y - 60
            arcade.draw_lbwh_rectangle_filled(
                placeholder_left,
                placeholder_bottom,
                120,
                120,
                arcade.color.LIGHT_GRAY,
            )
        stats_x = panel_left + 20
        stats_y = panel_top - 170
        arcade.draw_text(
            f"Урон: {hero_data['str']}",
            stats_x,
            stats_y,
            arcade.color.BLACK,
            22,
            bold=True,
        )
        arcade.draw_text(
            f"Защита: {hero_data['def']}",
            stats_x,
            stats_y - 28,
            arcade.color.BLACK,
            22,
            bold=True,
        )
        arcade.draw_text(
            f"НР: {hero_data['hp']}",
            stats_x,
            stats_y - 56,
            arcade.color.BLACK,
            22,
            bold=True,
        )
        arcade.draw_text(
            hero_data["desc"],
            panel_left + 20,
            panel_bottom + 20,
            arcade.color.BLACK,
            14,
            width=panel_right - panel_left - 40,
        )

        select_button_w = 260
        select_button_h = 50
        select_button_x = self.window.width // 2 - select_button_w // 2
        select_button_y = 40
        self.select_button = (select_button_x, select_button_y, select_button_w, select_button_h)
        arcade.draw_lbwh_rectangle_filled(
            select_button_x, select_button_y, select_button_w, select_button_h, arcade.color.LIGHT_GRAY
        )
        arcade.draw_lbwh_rectangle_outline(
            select_button_x, select_button_y, select_button_w, select_button_h, arcade.color.BLACK
        )
        arcade.draw_text(
            "ВЫБРАТЬ ПЕРСОНАЖА",
            select_button_x + select_button_w // 2,
            select_button_y + select_button_h // 2,
            arcade.color.BLACK,
            16,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        arcade.draw_text(
            "Enter - выбрать, Esc - назад",
            self.window.width // 2,
            10,
            arcade.color.BLACK,
            14,
            anchor_x="center",
        )

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        for i in range(len(self.heroes)):
            y_top = 400 - i * 70
            y_bottom = y_top + 50
            if 130 <= x <= 310 and y_top <= y <= y_bottom:
                self.selected = i
        if hasattr(self, "select_button"):
            btn_x, btn_y, btn_w, btn_h = self.select_button
            if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                self.start_view.selected_hero = self.selected
                self.window.show_view(self.start_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.start_view.selected_hero = self.selected
            self.window.show_view(self.start_view)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.start_view)


class MyGame(arcade.View):
    def __init__(self, selected_hero=0):
        super().__init__()
        self.map = load_texture_safe(MAP_IMAGE)
        if self.map is None:
            self.map = load_texture_safe("map.png")
        hero_image = f"hero{selected_hero + 1}.png"
        self.hero_sprite = Hero([f"{ASSET_DIR}/{hero_image}", hero_image], scale=0.25)
        self.hero_sprite.max_hp = float(HERO_MAX_HP + selected_hero * 20)
        self.hero_sprite.hp = float(self.hero_sprite.max_hp)
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.hero_sprite)
        self.speed = 5
        self.level = 1
        self.damage = float(10 + selected_hero * 2)
        self.defence = 5 + selected_hero
        self.exp = 0
        self.exp_max = 100
        self.exp_multiplier = 100 + selected_hero * 0.05
        self.base_exp_per_kill = 10 + selected_hero * 5
        self.time_elapsed = 0.0
        self.wave = 1
        self.view_width = 800
        self.view_height = 500
        self.viewport_left = 0
        self.viewport_bottom = 0
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.exp_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.boss_list = arcade.SpriteList()
        self.golem_list = arcade.SpriteList()
        self.mobs_killed = 0
        self.boss_spawned = False
        self.game_over = False
        self.win = False
        self.end_timer = 0.0
        self.shoot_timer = 0.0
        self.shot_cooldown = 0.18
        self.skill_selecting = False
        self.skills = []
        self.skill_textures = []
        for i in range(1, 10):
            tex = load_texture_safe(f"{ASSET_DIR}/skils({i}).png")
            if tex is None:
                tex = load_texture_safe(f"{ASSET_DIR}/skils{i}.png")
            if tex is None:
                tex = load_texture_safe(f"skils({i}).png")
            if tex is None:
                tex = load_texture_safe(f"skils{i}.png")
            self.skill_textures.append(tex)
        self.skill_buttons = []
        self.skill_hud_buttons = []
        self.skill1_used = False
        self.skill2_timer = 0.0
        self.skill2_cooldown = 0.0
        self.skill2_tick = 0.0
        self.skill4_cooldown = 0.0
        self.lightning_active = False
        self.lightning_phase = 0
        self.lightning_radius = 0.0
        self.lightning_hit_out = set()
        self.lightning_hit_in = set()
        self.skill5_timer = 0.0
        self.skill5_cooldown = 0.0
        self.skill5_tick = 0.0
        self.skill6_timer = 0.0
        self.skill6_cooldown = 0.0
        self.skill7_timer = 0.0
        self.skill7_cooldown = 0.0
        self.skill8_cooldown = 0.0
        self.golem_life_timer = 0.0
        self.golem_hp = 0.0
        self.golem_armed = False
        self.skill9_chance = 0.25

        self.spawn_wave(self.wave)

    def on_show_view(self):
        if self.window:
            self.view_width = self.window.width
            self.view_height = self.window.height
            self.update_camera(force=True)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.view_width = width
        self.view_height = height
        self.update_camera(force=True)

    def on_draw(self):
        self.clear()
        offset_x = -self.viewport_left
        offset_y = -self.viewport_bottom
        rect = arcade.rect.XYWH(
            MAP_WIDTH // 2 + offset_x,
            MAP_HEIGHT // 2 + offset_y,
            MAP_WIDTH,
            MAP_HEIGHT,
        )
        if self.map is not None:
            arcade.draw_texture_rect(self.map, rect)
        else:
            arcade.draw_lbwh_rectangle_filled(0, 0, self.view_width, self.view_height, arcade.color.DARK_GRAY)
        self.draw_spritelist_with_offset(self.exp_list, offset_x, offset_y)
        self.draw_spritelist_with_offset(self.enemy_list, offset_x, offset_y)
        self.draw_spritelist_with_offset(self.golem_list, offset_x, offset_y)
        self.draw_spritelist_with_offset(self.enemy_bullet_list, offset_x, offset_y)
        self.draw_spritelist_with_offset(self.bullet_list, offset_x, offset_y)
        self.draw_spritelist_with_offset(self.boss_list, offset_x, offset_y)
        self.draw_spritelist_with_offset(self.sprite_list, offset_x, offset_y)
        self.draw_world_effects(offset_x, offset_y)
        self.draw_hud()
        if self.skill_selecting:
            self.draw_skill_select()
        if self.game_over:
            self.draw_end_screen("GAME OVER")
        if self.win:
            self.draw_end_screen("WIN")

    def draw_world_effects(self, offset_x, offset_y):
        hx = self.hero_sprite.center_x + offset_x
        hy = self.hero_sprite.center_y + offset_y
        if self.lightning_active:
            arcade.draw_circle_outline(hx, hy, self.lightning_radius, arcade.color.YELLOW, 3)
        if self.skill5_timer > 0:
            arcade.draw_circle_outline(hx, hy, 220, arcade.color.PURPLE, 3)
        if self.skill7_timer > 0:
            arcade.draw_circle_outline(hx, hy, 80, arcade.color.GRAY, 2)

    def draw_spritelist_with_offset(self, spritelist, offset_x, offset_y):
        if not spritelist:
            return
        for sprite in spritelist:
            sprite.center_x += offset_x
            sprite.center_y += offset_y
        spritelist.draw()
        for sprite in spritelist:
            sprite.center_x -= offset_x
            sprite.center_y -= offset_y

    def draw_hud(self):
        bar_width = 220
        bar_height = 18
        hp_max = float(self.hero_sprite.max_hp) if self.hero_sprite else 0.0
        hp = float(self.hero_sprite.hp) if self.hero_sprite else 0.0
        hp_ratio = hp / hp_max if hp_max else 0
        exp_ratio = self.exp / self.exp_max if self.exp_max else 0

        hp_x = 20
        hp_y = self.view_height - 40
        exp_x = 20
        exp_y = self.view_height - 70

        arcade.draw_lbwh_rectangle_outline(
            hp_x, hp_y, bar_width, bar_height, arcade.color.BLACK
        )
        arcade.draw_lbwh_rectangle_filled(
            hp_x, hp_y, int(bar_width * hp_ratio), bar_height, arcade.color.RED
        )
        arcade.draw_text(
            f"HP: {int(hp)}/{int(hp_max)}",
            hp_x + bar_width + 10,
            hp_y + 2,
            arcade.color.BLACK,
            12,
        )

        arcade.draw_lbwh_rectangle_outline(
            exp_x, exp_y, bar_width, bar_height, arcade.color.BLACK
        )
        arcade.draw_lbwh_rectangle_filled(
            exp_x, exp_y, int(bar_width * exp_ratio), bar_height, arcade.color.BLUE
        )
        arcade.draw_text(
            f"EXP: {int(self.exp)}/{int(self.exp_max)}",
            exp_x + bar_width + 10,
            exp_y + 2,
            arcade.color.BLACK,
            12,
        )

        minutes = int(self.time_elapsed) // 60
        seconds = int(self.time_elapsed) % 60
        arcade.draw_text(
            f"Время: {minutes:02d}:{seconds:02d}",
            self.view_width - 180,
            self.view_height - 40,
            arcade.color.BLACK,
            14,
        )
        arcade.draw_text(
            f"Волна: {self.wave}",
            self.view_width - 180,
            self.view_height - 70,
            arcade.color.BLACK,
            14,
        )
        arcade.draw_text(
            f"LVL: {self.level}",
            20,
            self.view_height - 100,
            arcade.color.BLACK,
            14,
        )
        arcade.draw_text(
            f"DMG: {int(self.damage)}",
            20,
            self.view_height - 120,
            arcade.color.BLACK,
            14,
        )
        arcade.draw_text(
            f"KILLS: {self.mobs_killed}",
            20,
            self.view_height - 140,
            arcade.color.BLACK,
            14,
        )
        if self.boss_list:
            boss = self.boss_list[0]
            boss_hp = getattr(boss, "hp", 0)
            boss_hp_max = getattr(boss, "max_hp", getattr(boss, "hp_max", boss_hp))
            ratio = boss_hp / boss_hp_max if boss_hp_max else 0
            w = 360
            h = 16
            x = self.view_width // 2 - w // 2
            y = self.view_height - 30
            arcade.draw_lbwh_rectangle_outline(x, y, w, h, arcade.color.BLACK)
            arcade.draw_lbwh_rectangle_filled(x, y, int(w * ratio), h, arcade.color.BLUE)
            arcade.draw_text(
                f"BOSS: {int(boss_hp)}/{int(boss_hp_max)}",
                x + w // 2,
                y + h // 2,
                arcade.color.WHITE,
                12,
                anchor_x="center",
                anchor_y="center",
            )
        self.draw_skills_bar()

    def draw_skills_bar(self):
        if not self.skills:
            return
        icon = 44
        gap = 10
        skills_sorted = sorted(self.skills)
        total_w = len(skills_sorted) * icon + (len(skills_sorted) - 1) * gap
        x = self.view_width - total_w - 20
        y = 20
        self.skill_hud_buttons = []
        for skill_id in skills_sorted:
            self.skill_hud_buttons.append((skill_id, x, y, icon, icon))
            tex = self.skill_textures[skill_id - 1] if (skill_id - 1) < len(self.skill_textures) else None
            if tex is not None:
                rct = arcade.rect.XYWH(x + icon // 2, y + icon // 2, icon, icon)
                arcade.draw_texture_rect(tex, rct)
            else:
                arcade.draw_lbwh_rectangle_filled(x, y, icon, icon, arcade.color.LIGHT_GRAY)
                arcade.draw_lbwh_rectangle_outline(x, y, icon, icon, arcade.color.BLACK)
                arcade.draw_text(str(skill_id), x + icon // 2, y + icon // 2, arcade.color.BLACK, 18,
                                 anchor_x="center", anchor_y="center", bold=True)
            arcade.draw_lbwh_rectangle_outline(x, y, icon, icon, arcade.color.BLACK)
            arcade.draw_text(str(skill_id), x + 6, y + 4, arcade.color.BLACK, 12, bold=True)

            cd = 0.0
            active = 0.0
            if skill_id == 1:
                if self.skill1_used:
                    cd = 999.0
            elif skill_id == 2:
                cd = self.skill2_cooldown
                active = self.skill2_timer
            elif skill_id == 4:
                cd = self.skill4_cooldown
                active = 1.0 if self.lightning_active else 0.0
            elif skill_id == 5:
                cd = self.skill5_cooldown
                active = self.skill5_timer
            elif skill_id == 6:
                cd = self.skill6_cooldown
                active = self.skill6_timer
            elif skill_id == 7:
                cd = self.skill7_cooldown
                active = self.skill7_timer
            elif skill_id == 8:
                cd = self.skill8_cooldown

            if skill_id == 8 and self.golem_armed:
                arcade.draw_text("ARM", x + icon // 2, y + icon + 4, arcade.color.BLACK, 10,
                                 anchor_x="center", bold=True)
            if active > 0 and skill_id in (2, 5, 6, 7):
                arcade.draw_text(f"{active:.0f}s", x + icon // 2, y - 14, arcade.color.BLACK, 10,
                                 anchor_x="center", bold=True)
            if skill_id == 4 and self.lightning_active:
                arcade.draw_text("ON", x + icon // 2, y - 14, arcade.color.BLACK, 10,
                                 anchor_x="center", bold=True)
            if skill_id == 8 and self.golem_list:
                arcade.draw_text(f"HP {int(self.golem_hp)}", x + icon // 2, y - 14, arcade.color.BLACK, 10,
                                 anchor_x="center", bold=True)
            if cd > 0 and cd < 900:
                arcade.draw_text(f"CD {cd:.0f}", x + icon // 2, y + icon + 4, arcade.color.BLACK, 10,
                                 anchor_x="center", bold=True)
            if cd >= 900:
                arcade.draw_text("USED", x + icon // 2, y + icon + 4, arcade.color.BLACK, 10,
                                 anchor_x="center", bold=True)
            x += icon + gap

    def on_key_press(self, key, modifiers):
        if self.game_over or self.win:
            if key in (arcade.key.ESCAPE, arcade.key.ENTER):
                self.close_game()
            return
        if self.skill_selecting:
            return
        num = self.key_to_number(key)
        if num is not None:
            self.activate_skill(num)
            return
        if key in (arcade.key.UP, arcade.key.W):
            self.move_up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.move_down = True
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.move_left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.move_right = True
        self.update_movement()

    def on_key_release(self, key, modifiers):
        if self.game_over or self.win:
            return
        if self.skill_selecting:
            return
        if key in (arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S):
            if key in (arcade.key.UP, arcade.key.W):
                self.move_up = False
            if key in (arcade.key.DOWN, arcade.key.S):
                self.move_down = False
        if key in (arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D):
            if key in (arcade.key.LEFT, arcade.key.A):
                self.move_left = False
            if key in (arcade.key.RIGHT, arcade.key.D):
                self.move_right = False
        self.update_movement()

    def key_to_number(self, key):
        try:
            if 49 <= int(key) <= 57:
                return int(key) - 48
        except Exception:
            pass
        for i in range(1, 10):
            a = getattr(arcade.key, f"_{i}", None)
            b = getattr(arcade.key, f"KEY_{i}", None)
            c = getattr(arcade.key, f"NUM_{i}", None)
            d = getattr(arcade.key, f"NUMPAD_{i}", None)
            if key == a or key == b or key == c or key == d:
                return i
        return None

    def update_movement(self):
        dx = 0
        dy = 0
        if self.move_left and not self.move_right:
            dx = -self.speed
        elif self.move_right and not self.move_left:
            dx = self.speed
        if self.move_up and not self.move_down:
            dy = self.speed
        elif self.move_down and not self.move_up:
            dy = -self.speed
        self.hero_sprite.change_x = dx
        self.hero_sprite.change_y = dy

    def base_heal_on_kill(self):
        return 5 + (self.wave // 10) * 5

    def heal_player(self, amount):
        self.hero_sprite.hp = min(self.hero_sprite.hp + float(amount), float(self.hero_sprite.max_hp))

    def damage_player(self, raw_damage, use_defence=True, can_reduce=True):
        dmg = float(raw_damage)
        if use_defence:
            dmg = dmg - float(self.defence)
        if dmg < 1:
            dmg = 1.0
        if can_reduce and 6 in self.skills and self.skill6_timer > 0:
            dmg *= 0.9
        self.hero_sprite.hp -= dmg
        return dmg

    def damage_golem(self, raw_damage):
        if not self.golem_list:
            return
        self.golem_hp -= float(raw_damage)
        if self.golem_hp <= 0:
            self.golem_hp = 0
            for s in list(self.golem_list):
                s.remove_from_sprite_lists()
            self.golem_life_timer = 0.0

    def keep_in_bounds(self, entity):
        r = getattr(entity, "collision_radius", None)
        if r is None:
            r = max(getattr(entity, "width", 0), getattr(entity, "height", 0)) / 2
        try:
            r = float(r)
        except Exception:
            r = 0.0
        if r <= 0:
            return
        if entity.center_x - r <= 0:
            entity.center_x = r
        if entity.center_x + r >= MAP_WIDTH:
            entity.center_x = MAP_WIDTH - r
        if entity.center_y - r <= 0:
            entity.center_y = r
        if entity.center_y + r >= MAP_HEIGHT:
            entity.center_y = MAP_HEIGHT - r

    def prevent_collisions(self):
        entities = []
        entities.extend(list(self.enemy_list))
        entities.extend(list(self.boss_list))
        entities.extend(list(self.golem_list))
        entities.append(self.hero_sprite)
        if len(entities) > 140:
            return
        for i in range(len(entities)):
            e1 = entities[i]
            r1 = getattr(e1, "collision_radius", None)
            if r1 is None:
                r1 = max(getattr(e1, "width", 0), getattr(e1, "height", 0)) / 2
            for j in range(i + 1, len(entities)):
                e2 = entities[j]
                r2 = getattr(e2, "collision_radius", None)
                if r2 is None:
                    r2 = max(getattr(e2, "width", 0), getattr(e2, "height", 0)) / 2
                dx = e2.center_x - e1.center_x
                dy = e2.center_y - e1.center_y
                dist = math.hypot(dx, dy)
                min_sep = float(r1) + float(r2) + 4.0
                if dist < min_sep and dist > 0:
                    overlap = min_sep - dist
                    move_x = (dx / dist) * overlap * 0.5
                    move_y = (dy / dist) * overlap * 0.5
                    e1.center_x -= move_x
                    e1.center_y -= move_y
                    e2.center_x += move_x
                    e2.center_y += move_y
                    self.keep_in_bounds(e1)
                    self.keep_in_bounds(e2)

    def kill_enemy(self, enemy):
        x = enemy.center_x
        y = enemy.center_y
        enemy.remove_from_sprite_lists()
        self.mobs_killed += 1
        value = int(self.base_exp_per_kill * self.exp_multiplier)
        self.spawn_exp_orb(x, y, value)
        if 2 in self.skills:
            heal = self.base_heal_on_kill()
            if self.skill2_timer > 0:
                heal += self.base_heal_on_kill()
            self.heal_player(heal)

    def damage_enemy(self, enemy, amount):
        enemy.hp -= float(amount)
        if enemy.hp <= 0:
            self.kill_enemy(enemy)

    def damage_boss(self, amount):
        if not self.boss_list:
            return
        boss = self.boss_list[0]
        boss.hp -= float(amount)
        if boss.hp <= 0:
            boss.remove_from_sprite_lists()
            self.win = True
            self.end_timer = 0.0

    def apply_slow_to_boss(self, factor, duration):
        if not self.boss_list:
            return
        boss = self.boss_list[0]
        boss.speed_multiplier = min(getattr(boss, "speed_multiplier", 1.0), float(factor))
        boss.slow_timer = max(getattr(boss, "slow_timer", 0.0), float(duration))

    def maybe_proc_skill9(self):
        if 9 not in self.skills:
            return
        if random.random() < self.skill9_chance:
            self.skill2_cooldown = 0.0
            self.skill4_cooldown = 0.0
            self.skill5_cooldown = 0.0
            self.skill6_cooldown = 0.0
            self.skill7_cooldown = 0.0
            self.skill8_cooldown = 0.0

    def activate_skill(self, num):
        if num not in self.skills:
            return
        if num == 2:
            if self.skill2_cooldown > 0:
                return
            self.skill2_timer = 10.0
            self.skill2_cooldown = 25.0
            self.skill2_tick = 0.0
            self.maybe_proc_skill9()
        elif num == 4:
            if self.skill4_cooldown > 0 or self.lightning_active:
                return
            self.lightning_active = True
            self.lightning_phase = 0
            self.lightning_radius = 0.0
            self.lightning_hit_out = set()
            self.lightning_hit_in = set()
            self.skill4_cooldown = 14.0
            self.maybe_proc_skill9()
        elif num == 5:
            if self.skill5_cooldown > 0 or self.skill5_timer > 0:
                return
            self.skill5_timer = 25.0
            self.skill5_cooldown = 60.0
            self.skill5_tick = 0.0
            self.maybe_proc_skill9()
        elif num == 6:
            if self.skill6_cooldown > 0 or self.skill6_timer > 0:
                return
            self.skill6_timer = 20.0
            self.skill6_cooldown = 50.0
            self.maybe_proc_skill9()
        elif num == 7:
            if self.skill7_cooldown > 0 or self.skill7_timer > 0:
                return
            self.skill7_timer = 15.0
            self.skill7_cooldown = 120.0
            self.maybe_proc_skill9()
        elif num == 8:
            if self.skill8_cooldown > 0:
                return
            if self.golem_list:
                return
            self.golem_armed = True

    def try_summon_golem(self, x, y):
        if 8 not in self.skills:
            return
        if self.skill8_cooldown > 0:
            return
        if self.golem_list:
            return
        self.golem_armed = False
        world_x = x + self.viewport_left
        world_y = y + self.viewport_bottom
        golem = make_sprite_from_candidates(
            [f"{ASSET_DIR}/golem.png", "golem.png"],
            scale=0.35,
            fallback_w=90,
            fallback_h=90,
            fallback_color=arcade.color.ORANGE,
        )
        golem.center_x = world_x
        golem.center_y = world_y
        try:
            golem.collision_radius = 55
        except Exception:
            pass
        self.golem_list.append(golem)
        self.golem_hp = 200.0
        self.golem_life_timer = 60.0
        self.skill8_cooldown = 60.0
        self.maybe_proc_skill9()

    def update_lightning(self, delta_time):
        if not self.lightning_active:
            return
        max_r = 260.0
        speed = 520.0
        if self.lightning_phase == 0:
            self.lightning_radius += speed * delta_time
            if self.lightning_radius >= max_r:
                self.lightning_radius = max_r
                self.lightning_phase = 1
        else:
            self.lightning_radius -= speed * delta_time
            if self.lightning_radius <= 0:
                self.lightning_radius = 0.0
                self.lightning_active = False
                return
        hx = self.hero_sprite.center_x
        hy = self.hero_sprite.center_y
        hit_set = self.lightning_hit_out if self.lightning_phase == 0 else self.lightning_hit_in
        for enemy in list(self.enemy_list):
            key = id(enemy)
            if key in hit_set:
                continue
            dist = math.hypot(enemy.center_x - hx, enemy.center_y - hy)
            if dist <= self.lightning_radius:
                hit_set.add(key)
                self.damage_enemy(enemy, 20)
                if hasattr(enemy, "apply_slow"):
                    enemy.apply_slow(0.65, 2.5)
        if self.boss_list:
            boss = self.boss_list[0]
            key = id(boss)
            if key not in hit_set:
                dist = math.hypot(boss.center_x - hx, boss.center_y - hy)
                if dist <= self.lightning_radius:
                    hit_set.add(key)
                    self.damage_boss(20)
                    self.apply_slow_to_boss(0.75, 2.5)

    def update_aura(self, delta_time):
        if self.skill5_timer <= 0:
            return
        self.skill5_tick += delta_time
        while self.skill5_tick >= 1.0 and self.skill5_timer > 0:
            self.skill5_tick -= 1.0
            hx = self.hero_sprite.center_x
            hy = self.hero_sprite.center_y
            for enemy in list(self.enemy_list):
                dist = math.hypot(enemy.center_x - hx, enemy.center_y - hy)
                if dist <= 220:
                    self.damage_enemy(enemy, 10)
                    if hasattr(enemy, "apply_slow"):
                        enemy.apply_slow(0.9, 1.2)
            if self.boss_list:
                boss = self.boss_list[0]
                dist = math.hypot(boss.center_x - hx, boss.center_y - hy)
                if dist <= 220:
                    self.damage_boss(10)
                    self.apply_slow_to_boss(0.9, 1.2)
            self.damage_player(10, use_defence=False, can_reduce=False)

    def on_update(self, delta_time):
        if self.game_over or self.win:
            self.end_timer += delta_time
            if self.end_timer >= 5.0:
                self.close_game()
            return
        if self.skill_selecting:
            return

        self.time_elapsed += delta_time
        self.shoot_timer += delta_time

        self.skill2_cooldown = max(0.0, self.skill2_cooldown - delta_time)
        self.skill4_cooldown = max(0.0, self.skill4_cooldown - delta_time)
        self.skill5_cooldown = max(0.0, self.skill5_cooldown - delta_time)
        self.skill6_cooldown = max(0.0, self.skill6_cooldown - delta_time)
        self.skill7_cooldown = max(0.0, self.skill7_cooldown - delta_time)
        self.skill8_cooldown = max(0.0, self.skill8_cooldown - delta_time)

        if self.skill2_timer > 0:
            self.skill2_timer = max(0.0, self.skill2_timer - delta_time)
        else:
            self.skill2_tick = 0.0

        if self.skill5_timer > 0:
            self.skill5_timer = max(0.0, self.skill5_timer - delta_time)
            self.update_aura(delta_time)
        if self.skill6_timer > 0:
            self.skill6_timer = max(0.0, self.skill6_timer - delta_time)
        if self.skill7_timer > 0:
            self.skill7_timer = max(0.0, self.skill7_timer - delta_time)

        if self.golem_list:
            self.golem_life_timer = max(0.0, self.golem_life_timer - delta_time)
            if self.golem_life_timer <= 0 or self.golem_hp <= 0:
                for s in list(self.golem_list):
                    s.remove_from_sprite_lists()
                self.golem_life_timer = 0.0
                self.golem_hp = 0.0

        self.update_lightning(delta_time)
        try:
            self.hero_sprite.update_poison(delta_time)
        except Exception:
            pass

        self.hero_sprite.center_x += self.hero_sprite.change_x
        self.hero_sprite.center_y += self.hero_sprite.change_y
        if self.hero_sprite.center_y + self.hero_sprite.height // 2 >= MAP_HEIGHT:
            self.hero_sprite.center_y = MAP_HEIGHT - self.hero_sprite.height // 2
        if self.hero_sprite.center_y - self.hero_sprite.height // 2 <= 0:
            self.hero_sprite.center_y = self.hero_sprite.height // 2
        if self.hero_sprite.center_x + self.hero_sprite.width // 2 >= MAP_WIDTH:
            self.hero_sprite.center_x = MAP_WIDTH - self.hero_sprite.width // 2
        if self.hero_sprite.center_x - self.hero_sprite.width // 2 <= 0:
            self.hero_sprite.center_x = self.hero_sprite.width // 2

        for bullet in list(self.bullet_list):
            bullet.center_x += bullet.change_x
            bullet.center_y += bullet.change_y
            if bullet.center_x < 0 or bullet.center_x > MAP_WIDTH or bullet.center_y < 0 or bullet.center_y > MAP_HEIGHT:
                bullet.remove_from_sprite_lists()

        for bullet in list(self.enemy_bullet_list):
            bullet.center_x += bullet.change_x
            bullet.center_y += bullet.change_y
            if bullet.center_x < 0 or bullet.center_x > MAP_WIDTH or bullet.center_y < 0 or bullet.center_y > MAP_HEIGHT:
                bullet.remove_from_sprite_lists()
                continue
            if self.golem_list and arcade.check_for_collision(bullet, self.golem_list[0]):
                self.damage_golem(getattr(bullet, "damage", 10))
                bullet.remove_from_sprite_lists()
                continue
            if self.skill7_timer <= 0 and arcade.check_for_collision(bullet, self.hero_sprite):
                self.damage_player(getattr(bullet, "damage", 10), use_defence=True, can_reduce=True)
                if hasattr(bullet, "poison_duration") and hasattr(self.hero_sprite, "apply_poison"):
                    try:
                        self.hero_sprite.apply_poison(
                            getattr(bullet, "poison_duration", POISON_DURATION),
                            getattr(bullet, "poison_damage_per_second", POISON_DAMAGE_PER_SECOND),
                        )
                    except Exception:
                        pass
                bullet.remove_from_sprite_lists()

        enemy_target = None
        if self.golem_list:
            enemy_target = self.golem_list[0]
        elif self.skill7_timer <= 0:
            enemy_target = self.hero_sprite

        for enemy in list(self.enemy_list):
            enemy.target = enemy_target
            enemy.update(delta_time)
            half_w = enemy.width // 2
            half_h = enemy.height // 2
            enemy.center_x = min(max(enemy.center_x, half_w), MAP_WIDTH - half_w)
            enemy.center_y = min(max(enemy.center_y, half_h), MAP_HEIGHT - half_h)
            if getattr(enemy, "shooting", False) and enemy_target is not None:
                projectile = None
                try:
                    projectile = enemy.try_shoot()
                except Exception:
                    projectile = None
                if projectile is not None:
                    self.enemy_bullet_list.append(projectile)
            if enemy_target is self.hero_sprite:
                if arcade.check_for_collision(enemy, self.hero_sprite):
                    if getattr(enemy, "hit_cooldown", 0.0) <= 0.0:
                        self.damage_player(enemy.damage, use_defence=True, can_reduce=True)
                        enemy.hit_cooldown = 0.6
            elif enemy_target is not None:
                if arcade.check_for_collision(enemy, enemy_target):
                    if getattr(enemy, "hit_cooldown", 0.0) <= 0.0:
                        self.damage_golem(enemy.damage)
                        enemy.hit_cooldown = 0.6

        self.prevent_collisions()

        for bullet in list(self.bullet_list):
            hits = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if hits:
                bullet.remove_from_sprite_lists()
                for enemy in hits:
                    self.damage_enemy(enemy, int(getattr(bullet, "damage", int(self.damage))))

        for bullet in list(self.bullet_list):
            hits = arcade.check_for_collision_with_list(bullet, self.boss_list)
            if hits:
                bullet.remove_from_sprite_lists()
                self.damage_boss(int(getattr(bullet, "damage", int(self.damage))))
                if self.win:
                    return

        collected = arcade.check_for_collision_with_list(self.hero_sprite, self.exp_list)
        if collected:
            for orb in collected:
                self.gain_exp(int(getattr(orb, "value", 0)))
                orb.remove_from_sprite_lists()

        if not self.boss_spawned and self.level >= 100:
            self.spawn_boss()

        if self.boss_list:
            boss = self.boss_list[0]
            boss_target = enemy_target
            if boss_target is None and self.skill7_timer <= 0:
                boss_target = self.hero_sprite
            boss.target = boss_target
            boss.update(delta_time)
            half_w = boss.width // 2
            half_h = boss.height // 2
            boss.center_x = min(max(boss.center_x, half_w), MAP_WIDTH - half_w)
            boss.center_y = min(max(boss.center_y, half_h), MAP_HEIGHT - half_h)
            if getattr(boss, "shooting", False) and boss_target is not None:
                projectile = None
                try:
                    projectile = boss.try_shoot()
                except Exception:
                    projectile = None
                if projectile is not None:
                    self.enemy_bullet_list.append(projectile)
            if boss_target is self.hero_sprite:
                if arcade.check_for_collision(boss, self.hero_sprite):
                    if getattr(boss, "hit_cooldown", 0.0) <= 0.0:
                        self.damage_player(getattr(boss, "damage", 25), use_defence=True, can_reduce=True)
                        boss.hit_cooldown = 0.8
            elif boss_target is not None:
                if arcade.check_for_collision(boss, boss_target):
                    if getattr(boss, "hit_cooldown", 0.0) <= 0.0:
                        self.damage_golem(getattr(boss, "damage", 25))
                        boss.hit_cooldown = 0.8

        if self.hero_sprite.hp <= 0:
            if 1 in self.skills and not self.skill1_used:
                self.skill1_used = True
                self.hero_sprite.hp = max(1.0, float(self.hero_sprite.max_hp) * 0.5)
                try:
                    self.hero_sprite.is_poisoned = False
                except Exception:
                    pass
            else:
                self.hero_sprite.hp = 0.0
                self.game_over = True
                self.end_timer = 0.0
                return

        if self.boss_spawned and not self.boss_list and not self.win:
            self.win = True
            self.end_timer = 0.0
            return

        if not self.boss_spawned and not self.enemy_list:
            self.wave += 1
            self.spawn_wave(self.wave)

        self.update_camera()

    def spawn_wave(self, wave):
        count = min(20 + wave * 4, 120)
        for _ in range(count):
            self.spawn_enemy()

    def spawn_enemy(self):
        min_dist = max(self.view_width, self.view_height) * 1.2
        hx = self.hero_sprite.center_x
        hy = self.hero_sprite.center_y
        x = 0
        y = 0
        for _ in range(50):
            x = random.randint(60, MAP_WIDTH - 60)
            y = random.randint(60, MAP_HEIGHT - 60)
            if (x - hx) ** 2 + (y - hy) ** 2 >= min_dist ** 2:
                break
        r = random.random()
        w = int(getattr(self, "wave", 1) or 1)
        if w < 3:
            enemy = EnemiesPudge(x, y, self.hero_sprite, self.level)
        elif w < 6:
            if r < 0.7:
                enemy = EnemiesPudge(x, y, self.hero_sprite, self.level)
            else:
                enemy = FireArchers(x, y, self.hero_sprite, self.level)
        else:
            if r < 0.6:
                enemy = EnemiesPudge(x, y, self.hero_sprite, self.level)
            elif r < 0.85:
                enemy = FireArchers(x, y, self.hero_sprite, self.level)
            else:
                enemy = WitchDoktor(x, y, self.hero_sprite, self.level)
        self.enemy_list.append(enemy)

    def spawn_exp_orb(self, x, y, value):
        orb = make_solid_sprite(16, 16, arcade.color.LIME_GREEN)
        orb.center_x = x
        orb.center_y = y
        orb.value = value
        self.exp_list.append(orb)

    def spawn_bullet(self, x, y, target_x, target_y, damage):
        bullet = make_sprite_from_candidates(
            [f"{ASSET_DIR}/bull.png", "bull.png"],
            scale=0.12,
            fallback_w=10,
            fallback_h=10,
            fallback_color=arcade.color.GOLD,
        )
        bullet.center_x = x
        bullet.center_y = y
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        speed = 14
        bullet.change_x = (dx / dist) * speed
        bullet.change_y = (dy / dist) * speed
        try:
            bullet.angle = math.degrees(math.atan2(dy, dx))
        except Exception:
            pass
        final_damage = float(damage)
        if 3 in self.skills and random.random() < 0.35:
            final_damage = final_damage * 1.35
        bullet.damage = int(final_damage)
        self.bullet_list.append(bullet)

    def spawn_enemy_bullet(self, x, y, target_x, target_y, damage):
        bullet = make_solid_sprite(12, 12, arcade.color.BLUE)
        bullet.center_x = x
        bullet.center_y = y
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        speed = 9
        bullet.change_x = (dx / dist) * speed
        bullet.change_y = (dy / dist) * speed
        bullet.damage = int(damage)
        self.enemy_bullet_list.append(bullet)

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_max and not self.skill_selecting:
            self.exp -= self.exp_max
            self.level += 1
            if self.level % 5 == 0:
                self.hero_sprite.max_hp += 20.0
                self.hero_sprite.hp = min(self.hero_sprite.hp + 20.0, self.hero_sprite.max_hp)
                self.damage *= 1.05
            self.exp_max = int(100 + (self.level - 1) * 25)
            if self.level >= 100 and not self.boss_spawned:
                self.spawn_boss()
            if self.level % 10 == 0 and len(self.skills) < MAX_SKILLS:
                self.skill_selecting = True
                break

    def draw_skill_select(self):
        w = min(820, self.view_width - 60)
        h = 400
        left = self.view_width // 2 - w // 2
        bottom = self.view_height // 2 - h // 2
        arcade.draw_lbwh_rectangle_filled(left, bottom, w, h, (255, 255, 255, 230))
        arcade.draw_lbwh_rectangle_outline(left, bottom, w, h, arcade.color.BLACK)
        arcade.draw_text(
            "ВЫБЕРИ СКИЛЛ",
            self.view_width // 2,
            bottom + h - 40,
            arcade.color.BLACK,
            22,
            anchor_x="center",
            bold=True,
        )
        size = 78
        gap = 14
        cols = 3
        rows = 3
        grid_w = cols * size + (cols - 1) * gap
        grid_h = rows * size + (rows - 1) * gap
        start_x = self.view_width // 2 - grid_w // 2
        start_y = bottom + 80 + (grid_h - size)
        self.skill_buttons = []
        for r in range(rows):
            for c in range(cols):
                skill_id = r * cols + c + 1
                x = start_x + c * (size + gap)
                y = start_y - r * (size + gap)
                self.skill_buttons.append((skill_id, x, y, size, size))
                if skill_id in self.skills:
                    arcade.draw_lbwh_rectangle_filled(x, y, size, size, arcade.color.DARK_GRAY)
                    arcade.draw_lbwh_rectangle_outline(x, y, size, size, arcade.color.BLACK)
                    arcade.draw_text("✓", x + size // 2, y + size // 2, arcade.color.WHITE, 28,
                                     anchor_x="center", anchor_y="center", bold=True)
                    continue
                tex = self.skill_textures[skill_id - 1] if (skill_id - 1) < len(self.skill_textures) else None
                if tex is not None:
                    rct = arcade.rect.XYWH(x + size // 2, y + size // 2, size, size)
                    arcade.draw_texture_rect(tex, rct)
                    arcade.draw_lbwh_rectangle_outline(x, y, size, size, arcade.color.BLACK)
                else:
                    arcade.draw_lbwh_rectangle_filled(x, y, size, size, arcade.color.LIGHT_GRAY)
                    arcade.draw_lbwh_rectangle_outline(x, y, size, size, arcade.color.BLACK)
                    arcade.draw_text(str(skill_id), x + size // 2, y + size // 2, arcade.color.BLACK, 22,
                                     anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text(
            f"Выбрано: {len(self.skills)}/{MAX_SKILLS}",
            self.view_width // 2,
            bottom + 30,
            arcade.color.BLACK,
            14,
            anchor_x="center",
        )

    def apply_skill(self, idx):
        if idx == 1:
            self.skill1_used = False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over or self.win:
            return
        if self.skill_selecting:
            if button != arcade.MOUSE_BUTTON_LEFT:
                return
            for idx, bx, by, bw, bh in self.skill_buttons:
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    if idx in self.skills:
                        return
                    if len(self.skills) >= MAX_SKILLS:
                        return
                    self.skills.append(idx)
                    self.apply_skill(idx)
                    self.skill_selecting = False
                    self.gain_exp(0)
                    return
            return
        if button == arcade.MOUSE_BUTTON_LEFT and self.skill_hud_buttons:
            for skill_id, bx, by, bw, bh in self.skill_hud_buttons:
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.activate_skill(skill_id)
                    return
        if self.golem_armed and button == arcade.MOUSE_BUTTON_LEFT:
            self.try_summon_golem(x, y)
            return
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.try_summon_golem(x, y)
            return
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.shoot_timer < self.shot_cooldown:
            return
        self.shoot_timer = 0.0
        world_x = x + self.viewport_left
        world_y = y + self.viewport_bottom
        self.spawn_bullet(self.hero_sprite.center_x, self.hero_sprite.center_y, world_x, world_y, self.damage)

    def spawn_boss(self):
        x = random.randint(400, MAP_WIDTH - 400)
        y = random.randint(400, MAP_HEIGHT - 400)
        boss = BossDragon(x, y, self.hero_sprite, self.level)
        self.boss_list.append(boss)
        self.boss_spawned = True

    def draw_end_screen(self, title):
        w = min(720, self.view_width - 80)
        h = 300
        left = self.view_width // 2 - w // 2
        bottom = self.view_height // 2 - h // 2
        arcade.draw_lbwh_rectangle_filled(left, bottom, w, h, (0, 0, 0, 210))
        arcade.draw_lbwh_rectangle_outline(left, bottom, w, h, arcade.color.WHITE)
        arcade.draw_text(
            title,
            self.view_width // 2,
            bottom + h - 70,
            arcade.color.WHITE,
            44,
            anchor_x="center",
            bold=True,
        )
        minutes = int(self.time_elapsed) // 60
        seconds = int(self.time_elapsed) % 60
        arcade.draw_text(
            f"LVL: {self.level}  |  Волна: {self.wave}  |  Время: {minutes:02d}:{seconds:02d}",
            self.view_width // 2,
            bottom + 140,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            f"HP: {int(self.hero_sprite.max_hp)}  |  DMG: {int(self.damage)}  |  DEF: {int(self.defence)}",
            self.view_width // 2,
            bottom + 105,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            f"Убито мобов: {self.mobs_killed}  |  Скиллы: {len(self.skills)}/{MAX_SKILLS}",
            self.view_width // 2,
            bottom + 70,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            "ESC/ENTER - выйти",
            self.view_width // 2,
            bottom + 30,
            arcade.color.WHITE,
            14,
            anchor_x="center",
        )

    def close_game(self):
        window = self.window if self.window else None
        if window and hasattr(window, "close"):
            window.close()
            return
        if hasattr(arcade, "close_window"):
            arcade.close_window()
            return
        if hasattr(arcade, "exit"):
            arcade.exit()

    def update_camera(self, force=False):
        target_x = self.hero_sprite.center_x - self.view_width / 2
        target_y = self.hero_sprite.center_y - self.view_height / 2

        max_x = max(0, MAP_WIDTH - self.view_width)
        max_y = max(0, MAP_HEIGHT - self.view_height)
        target_x = min(max(target_x, 0), max_x)
        target_y = min(max(target_y, 0), max_y)

        if force:
            self.viewport_left = float(target_x)
            self.viewport_bottom = float(target_y)
        else:
            self.viewport_left += (target_x - self.viewport_left) * CAMERA_LERP
            self.viewport_bottom += (target_y - self.viewport_bottom) * CAMERA_LERP


def main():
    try:
        window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
    except Exception:
        window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        try:
            window.set_fullscreen(True)
        except Exception:
            pass
    start_view = Start_menu()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
