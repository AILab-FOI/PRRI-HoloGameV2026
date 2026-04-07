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
        self.on_ground = self.check_collision(0, 1, colliders)
        if self.on_ground:
            self.coyote_timer = self.coyote_time_max
            print("coyote timer: "+ str(self.coyote_timer), 2, 2, 12 )
            print("buffer: " + str(self.jump_buffer), 2, 10, 11)
            self.jumps_left = self.max_jumps
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1
                
                print("coyote timer: "+ str(self.coyote_timer), 2, 2, 12)
                print("buffer: " + str(self.jump_buffer), 2, 10, 11)

        if key(1):
            self.hsp = move_towards(self.hsp, -2, 0.3)
        elif key(4):
            self.hsp = move_towards(self.hsp, 2, 0.3)
        else:
            self.hsp = move_towards(self.hsp, 0, 0.3)

        if keyp(23):
            self.jump_buffer = 12
            print("JUMP PRESSED", 2, 18, 10)
        # JUMP
        if self.jump_buffer > 0:
            if self.coyote_timer > 0 and self.jumps_left == self.max_jumps:
                self.vsp = -4
                self.coyote_timer = 0
                self.jump_buffer = 0
                self.jumps_left -= 1
                print("ground jump USED", 2, 26, 9)

            elif not self.on_ground and self.jumps_left > 0:
                self.vsp = -4
                self.jump_buffer = 0
                self.jumps_left -= 1
                print("DOUBLE JUMP", 2, 34, 8)

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

        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        # MOVE
        self.x += self.hsp
        self.y += self.vsp


    def draw(self):
        rect(int(self.x), int(self.y), int(self.width), int(self.height), 12)


# --- INIT ---
player = Player()

colliders = [
    Collidable(0, 120, 240, 16),
    Collidable(80, 90, 40, 10),
    Collidable(140, 70, 40, 10)
]


# --- MAIN LOOP ---
def TIC():
    cls(0)

    player.update(colliders)
    player.draw()

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