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

        self.facing = 1   # 1 = right, -1 = left

    def check_collision(self, dx, dy, colliders):
        self.x += dx
        self.y += dy

        for c in colliders:
            if c.check(self):
                self.x -= dx
                self.y -= dy
                return True

        self.x -= dx
        self.y -= dy
        return False

    def update(self, colliders):
        # LEFT / RIGHT
        if key(1):
            self.hsp = move_towards(self.hsp, -2, 0.3)
            self.facing = -1
        elif key(4):
            self.hsp = move_towards(self.hsp, 2, 0.3)
            self.facing = 1
        else:
            self.hsp = move_towards(self.hsp, 0, 0.3)

        # JUMP
        if key(23) and self.check_collision(0, 1, colliders):
            self.vsp = -4

        # GRAVITY
        if not self.check_collision(0, self.vsp + 1, colliders):
            self.vsp += 0.25
        else:
            self.vsp = 0

        # COLLISION X
        if self.check_collision(self.hsp, 0, colliders):
            self.hsp = 0

        # COLLISION Y
        if self.check_collision(0, self.vsp, colliders):
            self.vsp = 0

        # MOVE
        self.x += self.hsp
        self.y += self.vsp

        if self.attackTimer > 0:
            self.attackTimer -= 1

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

