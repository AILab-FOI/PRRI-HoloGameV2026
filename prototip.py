# script: python

#kolizija
class Collidable:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def check(self, other):
        return self.x < other.x + other.width and self.x + self.width > other.x and self.y < other.y + other.height and self.y + self.height > other.y


def Move(a, b, v):
def Move(a, b, v):
    if a < b:
        return min(a + v, b)
    else:
        return max(a - v, b)


class Player:
    def __init__(self):
        self.x = 50
        self.y = 50
        self.width = 14   # <-- BITNO (nmp zakaj)
        self.height = 14  # <-- BITNO

        self.hsp = 0
        self.vsp = 0

    def collision(self, dx, dy, colls):
        self.x += dx
        self.y += dy

        for c in colls:
            if c.check(self):
                self.x -= dx
                self.y -= dy
                return True

        self.x -= dx
        self.y -= dy
        return False

    def update(self, colls):
        #lijevo/desno
        if key(1):
            self.hsp = Move(self.hsp, -2, 0.3)
        elif key(4):
            self.hsp = Move(self.hsp, 2, 0.3)
        else:
            self.hsp = Move(self.hsp, 0, 0.3)

        #skok (space=48)
        if key(23) and self.collision(0, 1, colls):
            self.vsp = -4

        #gravitacija
        if not self.collision(0, self.vsp + 1, colls):
            self.vsp += 0.25
        else:
            self.vsp = 0

        #kolizija X
        if self.collision(self.hsp, 0, colls):
            self.hsp = 0

        #kolizija Y
        if self.collision(0, self.vsp, colls):
            self.vsp = 0

        #kretnje
        self.x += self.hsp
        self.y += self.vsp

    def draw(self):
        rect(int(self.x), int(self.y), int(self.width), int(self.height), 12)


#init
player = Player()

colls = [
    Collidable(0, 120, 240, 16),   # floor
    Collidable(80, 90, 40, 10),    # platform
    Collidable(140, 70, 40, 10)    # platform 2
]


# --- MAIN LOOP ---
def TIC():
    cls(0)

    player.update(colls)
    player.draw()

    # debug draw kolizija
    for c in colls:
        rect(int(c.x), int(c.y), int(c.width), int(c.height), 1)