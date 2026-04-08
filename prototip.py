# script: python

# --- COLLISION ---
class Collidable:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def check(self, other):
        return self.x < other.x + other.width and self.x + self.width > other.x and self.y < other.y + other.height and self.y + self.height > other.y


# --- HELPER ---
def move_towards(a, b, v):
    if a < b:
        return min(a + v, b)
    else:
        return max(a - v, b)


# --- PLAYER ---
class Player:
    def __init__(self):
        self.attackTimer = 0

        self.x = 50
        self.y = 50
        self.width = 14
        self.height = 14

        self.hsp = 0
        self.vsp = 0
        
        self.on_ground = False
        self.coyote_timer = 0
        self.coyote_time_max = 10

        self.jump_buffer = 0
        self.jump_buffer_max = 30

        self.max_jumps = 2
        self.jumps_left = 2

        # DASH
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_time_max = 6

        self.dash_cooldown = 0
        self.dash_cooldown_max = 30

        self.dash_speed = 4
        self.facing = 1  # 1 = desno, -1 = lijevo

    def check_collision(self, dx, dy, colliders):
        self.x += dx
        self.y += dy

        hit = False
        for c in colliders:
            if c.check(self):
                hit = True
                break

        self.x -= dx
        self.y -= dy

        return hit

    def update(self, colliders):
        # LEFT / RIGHT
        self.on_ground = self.check_collision(0, 1, colliders)

        if self.on_ground:
            self.coyote_timer = self.coyote_time_max
            self.jumps_left = self.max_jumps
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        # DEBUG
        print("ground: " + str(self.on_ground), 2, 2, 12)
        print("coyote: " + str(self.coyote_timer), 2, 10, 11)
        print("buffer: " + str(self.jump_buffer), 2, 18, 10)
        print("jumps: " + str(self.jumps_left), 2, 26, 9)
        print("dash cd: " + str(self.dash_cooldown), 2, 34, 8)

        if key(1):
            self.facing = -1
        elif key(4):
            self.facing = 1
        if not self.is_dashing:
            if key(1):
                self.hsp = move_towards(self.hsp, -2, 0.3)
            elif key(4):
                self.hsp = move_towards(self.hsp, 2, 0.3)
            else:
                self.hsp = move_towards(self.hsp, 0, 0.3)
        else:
            self.hsp = self.facing * self.dash_speed

        # JUMP INPUT
        if keyp(23):
            self.jump_buffer = 12

        # JUMP / GRAVITY
        if not self.is_dashing:
            # JUMP
            if self.jump_buffer > 0:
                # prvi jump sa poda ili coyote time
                if self.coyote_timer > 0 and self.jumps_left == self.max_jumps:
                    self.vsp = -4
                    self.coyote_timer = 0
                    self.jump_buffer = 0
                    self.jumps_left -= 1
                    print("GROUND JUMP", 2, 58, 9)

                # drugi jump u zraku
                elif not self.on_ground and self.jumps_left > 0:
                    self.vsp = -4
                    self.jump_buffer = 0
                    self.jumps_left -= 1
                    print("DOUBLE JUMP", 2, 66, 8)

        # GRAVITY
            if not self.check_collision(0, self.vsp + 1, colliders):
                self.vsp += 0.25
            else:
                self.vsp = 0
        else:
            slef.vsp = 0
        
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        move_x = self.hsp
        steps = int(abs(move_x))

        for i in range(steps):
            step = 1 if move_x > 0 else -1

            if not self.check_collision(step, 0, colliders):
                self.x += step
            else:
                self.hsp = 0
                self.is_dashing = False
                break

        remainder = move_x - int(move_x)
        if remainder != 0:
            if not self.check_collision(remainder, 0, colliders):
                self.x += remainder
            else:
                self.hsp = 0
                self.is_dashing = False

        # --- MOVE Y ---
        move_y = self.vsp
        steps = int(abs(move_y))

        for i in range(steps):
            step = 1 if move_y > 0 else -1

            if not self.check_collision(0, step, colliders):
                self.y += step
            else:
                self.vsp = 0
                break

        remainder = move_y - int(move_y)
        if remainder != 0:
            if not self.check_collision(0, remainder, colliders):
                self.y += remainder
            else:
                self.vsp = 0

    def draw(self):
        rect(int(self.x), int(self.y), int(self.width), int(self.height), 12)


class Gun:
    def __init__(self, owner):
        self.owner = owner

        self.x = 0
        self.y = 0
        self.width = 4
        self.height = 4

        self.attackTimeDelay = 0
        self.damage = 0

        # right offset
        self.offset_right_x = 15
        self.offset_right_y = 4

        # left offset 
        self.offset_left_x = -5
        self.offset_left_y = 4

    def update(self):
        if self.owner.facing == 1:
            self.x = self.owner.x + self.offset_right_x
            self.y = self.owner.y + self.offset_right_y
        else:
            self.x = self.owner.x + self.offset_left_x
            self.y = self.owner.y + self.offset_left_y

    def draw(self):
        rect(int(self.x), int(self.y), int(self.width), int(self.height), 14)

    def attack(self):
        if self.owner.attackTimer <= 0:
            self.owner.attackTimer = self.attackTimeDelay


class Katana(Gun):
    def __init__(self, owner):
        Gun.__init__(self, owner)
        self.attackTimeDelay = 1
        self.damage = 1
        self.width = 8
        self.height = 3

        self.offset_right_x = 14
        self.offset_right_y = 5

        self.offset_left_x = -8
        self.offset_left_y = 5


class RangedWeapon(Gun):
    def __init__(self, owner):
        Gun.__init__(self, owner)
        self.attackTimeDelay = 2
        self.damage = 2


# --- INIT ---
player = Player()
gun = Gun(player)
# gun = Katana(player)

colliders = [
    Collidable(0, 120, 240, 16),
    Collidable(80, 90, 40, 10),
    Collidable(140, 70, 40, 10)
]


# --- MAIN LOOP ---
def TIC():
    cls(0)

    player.update(colliders)
    gun.update()

    player.draw()
    gun.draw()

    # debug draw
    for c in colliders:
        rect(int(c.x), int(c.y), int(c.width), int(c.height), 1)

# <TILES>
# 001:eccccccccc888888caaaaaaaca888888cacccccccacc0ccccacc0ccccacc0ccc
# 002:ccccceee8888cceeaaaa0cee888a0ceeccca0ccc0cca0c0c0cca0c0c0cca0c0c
# 003:eccccccccc888888caaaaaaaca888888cacccccccacccccccacc0ccccacc0ccc
# 004:ccccceee8888cceeaaaa0cee888a0ceeccca0cccccca0c0c0cca0c0c0cca0c0c
# 017:cacccccccaaaaaaacaaacaaacaaaaccccaaaaaaac8888888cc000cccecccccec
# 018:ccca00ccaaaa0ccecaaa0ceeaaaa0ceeaaaa0cee8888ccee000cceeecccceeee
# 019:cacccccccaaaaaaacaaacaaacaaaaccccaaaaaaac8888888cc000cccecccccec
# 020:ccca00ccaaaa0ccecaaa0ceeaaaa0ceeaaaa0cee8888ccee000cceeecccceeee
# </TILES>

# <WAVES>
# 000:00000000ffffffff00000000ffffffff
# 001:0123456789abcdeffedcba9876543210
# 002:0123456789abcdef0123456789abcdef
# </WAVES>

# <SFX>
# 000:000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000304000000000
# </SFX>

# <TRACKS>
# 000:100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </TRACKS>

# <PALETTE>
# 000:1a1c2c5d275db13e53ef7d57ffcd75a7f07038b76425717929366f3b5dc941a6f673eff7f4f4f494b0c2566c86333c57
# </PALETTE>

