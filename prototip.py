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

class DamageTrigger(Collidable):
    def __init__(self, x, y, w, h, damage):
        Collidable.__init__(self, x, y, w, h)
        
        self.damage = damage

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

        # DASH
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_time_max = 6

        self.dash_cooldown = 0
        self.dash_cooldown_max = 30

        self.dash_speed = 4
        
        self.health = 100
        self.dead = False
        
        self.iframeTimer = 0
        self.iframeTime = 90
        
        self.facing = 1  # 1 = desno, -1 = lijevo
        
        self.hitbox = Collidable(self.x, self.y, self.width, self.height)
        
        self.gun = None

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
    
    def check_damage_trigger(self, damageTriggers):
        for d in damageTriggers:
            if d.check(self.hitbox) and self.iframeTimer <= 0:
                self.health -= d.damage
                self.iframeTimer = self.iframeTime
                if self.health < 1:
                    self.dead = True
                return True
        
        return False

    def update(self, colliders, damageTriggers):
        if (self.dead):
            return
        
        print("Health: " + str(self.health), 175, 2, 12)
        
        # LEFT / RIGHT
        self.on_ground = self.check_collision(0, 1, colliders)

        if self.on_ground:
            self.coyote_timer = self.coyote_time_max
            self.jumps_left = self.max_jumps
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        # DEBUG
        print("ground: " + str(self.on_ground), 6, 2, 12)
        print("coyote: " + str(self.coyote_timer), 6, 10, 11)
        print("buffer: " + str(self.jump_buffer), 6, 18, 10)
        print("jumps: " + str(self.jumps_left), 6, 26, 9)
        print("dash cd: " + str(self.dash_cooldown), 6, 34, 8)

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
            self.vsp = 0
        
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

        remainder = move_y - int(move_y)
        if remainder != 0:
            if not self.check_collision(0, remainder, colliders):
                self.y += remainder
            else:
                self.vsp = 0
        
        self.hitbox.x = self.x
        self.hitbox.y = self.y
        
        self.check_damage_trigger(damageTriggers)
        
        self.iframeTimer -= 1
        if (self.iframeTimer <= 0):
            self.iframeTimer = 0

    def draw(self):
        if(not self.dead): rect(int(self.x), int(self.y), int(self.width), int(self.height), 5)

# --- WEAPONS ---
class Gun:
    def __init__(self, owner):
        self.owner = owner

        self.x = 0
        self.y = 0
        self.width = 4
        self.height = 4

        self.attackTimer = 0
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
        
        if key(24):
            self.attack()
        
        if self.attackTimer > 0:
            self.attackTimer -= 1
        
        if self.attackTimer <= 0:
            self.attackTimer = 0

    def draw(self):
        if (not self.owner.dead):
            rect(int(self.x), int(self.y), int(self.width), int(self.height), 14)

    def attack(self):
        if self.attackTimer <= 0:
            self.attackTimer = self.attackTimeDelay


class Katana(Gun):
    def __init__(self, owner):
        Gun.__init__(self, owner)
        self.owner.attackTimeDelay = 60
        self.damage = 3
        self.width = 8
        self.height = 3

        self.offset_right_x = 14
        self.offset_right_y = 5

        self.offset_left_x = -8
        self.offset_left_y = 5


class RangedWeapon(Gun):
    def __init__(self, owner, attackTimeDelay, damage):
        Gun.__init__(self, owner)
        self.attackTimeDelay = attackTimeDelay
        self.damage = damage
    
    def attack(self):
        if self.attackTimer > 0:
            return
        Gun.attack(self)
        projectile = Projectile(int(self.owner.gun.x), int(self.owner.gun.y), int(self.damage), playerDamageTriggers, int(self.owner.facing))
        projectiles.append(projectile)
        enemyDamageTriggers.append(projectile.contactDamageTrigger)

class Projectile:
    def __init__(self, x, y, damage, damageTriggers, facing = 1):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 4
        
        self.hsp = 2
        self.vsp = 0
        
        self.facing = facing   # 1 = right, -1 = left
        
        self.destroyed = False
        
        self.hitbox = Collidable(self.x, self.y, self.width, self.height)
        self.contactDamageTrigger = DamageTrigger(self.x, self.y, self.width, self.height, damage)
        
        self.damageTriggers = damageTriggers
    
    def check_collision(self, dx, dy, colliders):
        self.x += dx
        self.y += dy

        for c in colliders:
            if c.check(self):
                self.destroy()
                return True

        self.x -= dx
        self.y -= dy
        return False
    
    def check_damage_trigger(self, damageTriggers):
        for d in damageTriggers:
            if d.check(self.hitbox):
                self.destroy()
    
    def update(self, colliders):
        # COLLISION X
        if self.check_collision(self.hsp, 0, colliders):
            self.destroy()

        # COLLISION Y
        if self.check_collision(0, self.vsp, colliders):
            self.destroy()

        # MOVE
        self.x += self.hsp * self.facing
        self.y += self.vsp
        
        self.hitbox.x = self.x
        self.hitbox.y = self.y
        
        self.contactDamageTrigger.x = self.x
        self.contactDamageTrigger.y = self.y
        
        self.draw()
        
        self.check_damage_trigger(self.damageTriggers)
    
    def draw(self):
        if(not self.destroyed): 
            rect(int(self.x), int(self.y), int(self.width), int(self.height), 4)
    
    def destroy(self):
        if self in projectiles:
            projectiles.remove(self)
        if self.contactDamageTrigger in enemyDamageTriggers:
            enemyDamageTriggers.remove(self.contactDamageTrigger)

# --- ENEMIES ---
class Enemy:
    def __init__(self, x, y):
        self.attackTimer = 0

        self.x = x
        self.y = y
        self.width = 14
        self.height = 14
        self.dx = -1

        self.hsp = 0
        self.vsp = 0

        self.facing = 1   # 1 = right, -1 = left
        self.health = 100
        self.dead = False
        
        self.hitbox = Collidable(self.x, self.y, self.width, self.height)
        self.contactDamageTrigger = DamageTrigger(self.x, self.y, self.width, self.height, 25)

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
    
    def check_damage_trigger(self, damageTriggers):
        for d in damageTriggers:
            if d.check(self.hitbox):
                self.health -= d.damage
                if self.health < 1:
                    self.dead = True
                return True
        
        return False

    def update(self, colliders, damageTriggers):
        # MOVEMENT
        self.x = self.x + self.dx
        if not self.dead and self.check_collision(6*self.dx, 0, colliders):
            if not self.check_collision(3*self.dx, -9, colliders):
                if self.check_collision(0, 1, colliders):
                    self.dx = -self.dx
                    self.facing *= -1
        elif not self.dead and self.check_collision(3*self.dx, 0, colliders):
            self.dx = -self.dx
            self.facing *= -1
        if not self.dead and self.x <= 0:
            self.dx = 1
            self.facing = 1
        
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
            
        self.check_damage_trigger(damageTriggers)
        
        self.hitbox.x = self.x
        self.hitbox.y = self.y
        
        self.contactDamageTrigger.x = self.x
        self.contactDamageTrigger.y = self.y

    def draw(self):
        if(not self.dead): 
            rect(int(self.x), int(self.y), int(self.width), int(self.height), 2)
    
    def TakeDamage(self, damage, removeInt):
        self.health = self.health - damage
        if self.health < 1:
            self.dead = True

# --- INIT ---
player = Player()
gun = RangedWeapon(player, 30, 25)
player.gun = gun

enemy = Enemy(150, 90)
# gun = Katana(player)

colliders = [
    Collidable(0, 120, 240, 16),
    Collidable(80, 90, 40, 10),
    Collidable(140, 70, 40, 10),
    Collidable(0, 0, 5, 150),
    Collidable(235, 0, 5, 150)
]

playerDamageTriggers = [
    #DamageTrigger(140, 45, 30, 30, 2)
]
enemyDamageTriggers = [
    #DamageTrigger(150, 90, 30, 30, 2)
]

projectiles = []

enemies = []
enemies.append(enemy)

for e in enemies:
    playerDamageTriggers.append(e.contactDamageTrigger)

# --- MAIN LOOP ---
def TIC():
    cls(0)

    player.update(colliders, playerDamageTriggers)
    gun.update()
    enemy.update(colliders, enemyDamageTriggers)

    player.draw()
    gun.draw()
    enemy.draw()

    # debug draw
    for c in colliders:
        rect(int(c.x), int(c.y), int(c.width), int(c.height), 1)
    
    for pr in projectiles:
        rect(int(pr.x), int(pr.y), int(pr.width), int(pr.height), 4)
        pr.update(colliders)
    
    #for p in playerDamageTriggers:
        #rect(int(p.x), int(p.y), int(p.width), int(p.height), 7)

    #for c in enemies:
        #rect(int(c.x), int(c.y), int(c.width), int(c.height), 2)

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

