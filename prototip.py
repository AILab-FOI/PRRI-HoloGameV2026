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
    def __init__(self, x, y, w, h, damage, owner = None):
        Collidable.__init__(self, x, y, w, h)
        
        self.damage = damage
        self.owner = owner

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
        self.facing = 1   # 1 = right, -1 = left
        
        self.hitbox = Collidable(self.x, self.y, self.width, self.height)
        
        self.gun = None
        self.hasGun = True

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
        
        if key(5):
            sfx(2)

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

        #Switch weapons
        if keyp(6):
            if(self.hasGun):
                self.hasGun=False
                
            else:
                self.hasGun=True    

        # JUMP INPUT
        if keyp(23):
            self.jump_buffer = 12
            #sfx(0)

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
                    sfx(10)
                    print("GROUND JUMP", 2, 58, 9)

                # drugi jump u zraku
                elif not self.on_ground and self.jumps_left > 0:
                    self.vsp = -4
                    self.jump_buffer = 0
                    self.jumps_left -= 1
                    sfx(10)
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
        if not self.dead:
            if self.facing == 1:
                spr(258, int(self.x -cam_x), int(self.y -cam_y), 0, 1, 0, 0, 2, 2)
            else:
                spr(256,int(self.x -cam_x), int(self.y -cam_y), 0, 1, 0, 0, 2, 2)
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
        self.offset_right_x = 10
        self.offset_right_y = 6

        # left offset 
        self.offset_left_x = -3
        self.offset_left_y = 6

    def update(self):
        if self.owner.dead:
            return
        if self.owner.facing == 1:
            self.x = self.owner.x + self.offset_right_x
            self.y = self.owner.y + self.offset_right_y
        else:
            self.x = self.owner.x + self.offset_left_x
            self.y = self.owner.y + self.offset_left_y
        
        if keyp(24):
            self.attack()
        
        if self.attackTimer > 0:
            self.attackTimer -= 1
        
        if self.attackTimer <= 0:
            self.attackTimer = 0

    def draw(self):
        if (not self.owner.dead):
            if self.owner.facing == 1:
                spr(266, int(self.x - cam_x), int(self.y - cam_y), 0, 1, 0, 0, 1, 1)
            else:
                spr(266, int(self.x - cam_x), int(self.y - cam_y), 0, 1, 1, 0, 1, 1)
    def attack(self):
        if self.attackTimer <= 0:
            self.attackTimer = self.attackTimeDelay
            sfx(1)


class Katana(Gun):
    def __init__(self, owner, attackTimeDelay, damage):
        Gun.__init__(self, owner)
        self.attackTimeDelay = attackTimeDelay
        self.damage = damage
        self.width = 8
        self.height = 3

        self.offset_right_x = 14
        self.offset_right_y = 5

        self.offset_left_x = -8
        self.offset_left_y = 5
        
    def attack(self):
        if self.attackTimer > 0:
            return
        Gun.attack(self)
        projectile = Projectile(int(self.owner.gun.x), int(self.owner.gun.y), 60, 30, int(self.damage), playerDamageTriggers, 0, int(self.owner.facing), 1, False, False)
        projectiles.append(projectile)
        enemyDamageTriggers.append(projectile.contactDamageTrigger)


class RangedWeapon(Gun):
    def __init__(self, owner, attackTimeDelay, damage):
        Gun.__init__(self, owner)
        self.attackTimeDelay = attackTimeDelay
        self.damage = damage
        self.bigshotTimer = 0
    
    def attack(self, sizeMultiplier = 1, damageMultiplier = 1):
        if self.attackTimer > 0:
            return
        Gun.attack(self)
        projectile = Projectile(int(self.owner.gun.x), int(self.owner.gun.y), 4 * sizeMultiplier, 4 * sizeMultiplier, int(self.damage) * damageMultiplier, playerDamageTriggers, 2, int(self.owner.facing))
        projectiles.append(projectile)
        enemyDamageTriggers.append(projectile.contactDamageTrigger)

    def update(self):
        Gun.update(self)
        if key(24):
            self.bigshotTimer += 1
            if self.bigshotTimer >= 180:
                self.attack(2, 3)
                self.bigshotTimer = 0

class Projectile:
    def __init__(self, x, y, width, height, damage, damageTriggers, hsp = 2, facing = 1, duration = -1, checkCollision = True, drawSelf = True, multiplier = 1):
        self.x = x
        self.y = y - height / 2
        self.width = width
        self.height = height
        
        self.hsp = hsp
        self.vsp = 0
        
        self.facing = facing   # 1 = right, -1 = left
        
        self.destroyed = False
        self.checkCollision = checkCollision
        self.drawSelf = drawSelf

        self.contactDamageTrigger = DamageTrigger(self.x, self.y, self.width, self.height, damage, self)
        
        self.damageTriggers = damageTriggers
        
        self.temporary = False
        self.timer = -1
        if (duration != -1):
            self.temporary = True
            self.timer = duration
            
        if (self.facing == -1):
            self.x -= self.width

    
    def check_collision(self, dx, dy, colliders):
        if (not self.checkCollision): return None 
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
            if d.check(self.contactDamageTrigger):
                self.destroy()
    
    def update(self, colliders):
        # COLLISION X
        if self.check_collision(self.hsp, 0, colliders):
            self.destroy()

        # COLLISION Y
        if self.check_collision(0, self.vsp, colliders):
            self.destroy()
            
        #self.check_damage_trigger(self.damageTriggers)
        
        # MOVE    
        self.x += self.hsp * self.facing
        self.y += self.vsp
        
        self.contactDamageTrigger.x = self.x
        self.contactDamageTrigger.y = self.y
        
        if (self.temporary):
            if self.timer > 0:
                self.timer -= 1
            else: 
                self.destroy()
        
        if(self.drawSelf): self.draw()
    
    def draw(self):  
        if not self.destroyed:
            rect(int(self.x - cam_x), int(self.y - cam_y), int(self.width), int(self.height), 4)

    def destroy(self):
        if self in projectiles:
            projectiles.remove(self)
        if self.contactDamageTrigger in enemyDamageTriggers:
            enemyDamageTriggers.remove(self.contactDamageTrigger)
        
        self.destroyed = True


# --- ENEMIES ---
class Enemy:
    def __init__(self, x, y):
        self.attackTimer = 0

        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.dx = -1
        self.sprite_left = 258
        self.sprite_right = 258

        self.hsp = 0
        self.vsp = 0

        self.facing = 1   # 1 = right, -1 = left
        self.health = 100
        self.dead = False
        
        self.iframe = 0
        self.iframeMax = 10

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
            if d.check(self.contactDamageTrigger):
                if self.iframe <= 0:
                    self.health -= d.damage
                    self.iframe = self.iframeMax
                    sfx(2)
                if self.health < 1:
                    self.dead = True
                    self.destroy()
                
                d.owner.destroy()
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
            
        if self.iframe > 0:
            self.iframe -= 1
            
        self.check_damage_trigger(damageTriggers)

        self.contactDamageTrigger.x = self.x
        self.contactDamageTrigger.y = self.y
        
        #print("Enemy health: " + str(self.health), 100, 20, 3)
        
        if self.iframe > 0:
            self.iframe -= 1

    def draw(self):
        if not self.dead: 
        
            if self.facing == 1:
                spr(262, int(self.x), int(self.y), 0, 1, 1, 0, 2, 2)
            else:
                spr(260, int(self.x), int(self.y), 0, 1, 0, 0, 2, 2)
    
    def TakeDamage(self, damage, removeInt):
        self.health = self.health - damage
        if self.health < 1:
            self.dead = True
            
    def destroy(self):
        if self.contactDamageTrigger in playerDamageTriggers:
            playerDamageTriggers.remove(self.contactDamageTrigger)
        if self in enemies:
            enemies.remove(self)

# --- MISC FUNCTIONS ---
def TileCollisions(objectList, level, level_height):
    collidables = {}
    tile_size = 8
    for object in objectList:
        collisionWidth = 8
        if not isinstance (object, list):
            px = min(max(int(object.x/tile_size) - round(collisionWidth/2), 0), 239)
            py = min(max(int(object.y/tile_size) - round(collisionWidth/2), 0), 135)

            for xx in range(collisionWidth):
                for yy in range(collisionWidth):
                    tileHere = mget(xx + px, yy + py + level*level_height)
                    if tileHere != 0 and tileHere not in background_tile_indexes:
                        pos_key = ("x", xx + px, "y", yy + py)
                        if pos_key not in collidables:
                            collidables[pos_key] = Collidable((xx + px)*tile_size, (yy + py)*tile_size, tile_size, tile_size)
        else:
            for obj in object:
                px = min(max(int(obj.x/tile_size) - round(collisionWidth/2), 0), 239)
                py = min(max(int(obj.y/tile_size) - round(collisionWidth/2), 0), 135)

                for xx in range(collisionWidth):
                    for yy in range(collisionWidth):
                        tileHere = mget(xx + px, yy + py + level*level_height)
                        if tileHere != 0 and tileHere not in background_tile_indexes:
                            pos_key = ("x", xx + px, "y", yy + py)
                            if pos_key not in collidables:
                                collidables[pos_key] = Collidable((xx + px)*tile_size, (yy + py)*tile_size, tile_size, tile_size)

    return list(collidables.values())

# --- INIT ---
player = Player()
gun = RangedWeapon(player, 30, 25)
katana = Katana(player, 60, 25)



enemy = Enemy(120, 70)

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
    
background_tile_indexes = [
    7, 8, 25, 26
]

def update_camera():
    
    global cam_x, cam_y

    cam_x = 0
    cam_y = 0

    cam_x = int(player.x -120)
    cam_y = int(player.y -68)

    if cam_x < 0:
        cam_x = 0
    if cam_y < 0:
        cam_y = 0


# --- MAIN LOOP ---
def TIC():
    cls(0)
    update_camera()
    map(0, 0, 240, 136, -cam_x, -cam_y)
    
    

   
    
    collidables = TileCollisions([player, enemies], 0, 17)
    
    # RESETING GAME
    def reset_game():
        global player, gun, enemy, enemies, projectiles, playerDamageTriggers, enemyDamageTriggers

        player = Player()
        gun = RangedWeapon(player, 30, 25)
        player.gun = gun

        enemy = Enemy(150, 90)
        enemies = [enemy]

        projectiles = []

        playerDamageTriggers = []
        enemyDamageTriggers = []

        for e in enemies:
            playerDamageTriggers.append(e.contactDamageTrigger)

    player.update(collidables, playerDamageTriggers)
    if(player.hasGun): 
        player.gun = gun   
        gun.update()
    else:
        player.gun = katana
        katana.update()
    enemy.update(collidables, enemyDamageTriggers)

    player.draw()
    if(player.hasGun):
        gun.draw()
    else:
        katana.draw()
    enemy.draw()

    # debug draw
    #for c in colliders:
        #rect(int(c.x), int(c.y), int(c.width), int(c.height), 1)
    
    for pr in projectiles:
        pr.update(collidables)

    # death
    if player.dead:
        print("GAME OVER", 90, 60, 12)
        print("Press R to restart", 70, 70, 12)

        if keyp(18):
            reset_game()
        return
    #for p in playerDamageTriggers:
        #rect(int(p.x), int(p.y), int(p.width), int(p.height), 7)

    #for c in enemies:
        #rect(int(c.x), int(c.y), int(c.width), int(c.height), 2)

# <TILES>
# 001:8888888888888888888888888888888888888888888888888888888888888888
# 002:7777777777777777777777777777777777777777777777777777777777777777
# 003:88888888888888888888888888888888888bbbbb888bbbbb888bbbbb888bbb00
# 004:88888888888888888888888888888888bbbbbbbbbbbbbbbbbbbbbbbb00000000
# 005:88888888888888888888888888888888bbbbbbbbbbbbbbbbbbbbbbbb00000000
# 006:88888888888888888888888888888888bbbbb888bbbbb888bbbbb88800bbb888
# 007:6666666666666666666666666666666666666666666666666666666666666666
# 008:666b666666bbb6666bbbbb666bbbbb666bbbbb6666bbb6666666666666666666
# 011:1111111111111111111111111111111111111111111111111111111111111111
# 012:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# 013:4444444444444444444444444444444444444444444444444444444444444444
# 014:2222222222222222222222222222222222222222222222222222222222222222
# 015:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
# 016:888888888888888888b88b88888bb88888bbbb88888bb88888b88b8888888888
# 019:888bbb0d888bbb0d888bbb0d888bbb0d888bbb0d888bbb0d888bbb0c888bbb0c
# 020:ddddddd9dd2dddd9d222ddd9dd2dddd9ddddddd9ddddddddcccccccccccccccc
# 021:9ddddddd9ddddd2d9dddd22299dddd2d99dddddd99dddddd99cccccc99cccccc
# 022:d0bbb888d0bbb888d0bbb888d0bbb888d0bbb888d0bbb888c0bbb888c0bbb888
# 023:66bfeedd6bbfeeddbbffeeddfffeedddeeeeddddeeeddddddddddddddddddddd
# 024:ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66deeefb66eeeefb66
# 025:6666666666666666ccccccccbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# 026:6666666666666666ccccccccbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# 027:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
# 028:ffffffffffffffffffccccffffccccffffccccffffccccffffffffffffffffff
# 029:ccccccccccc22cccccc22cccc222222cc222222cccc22cccccc22ccccccccccc
# 030:ccccccccbbbbbbbbbbbbbbbbcccccccc88888888888888888888888888888888
# 032:6666666666666666bbbbbbbbffffffffeeeeeeeeeeeeeeeeddddddeeddddddde
# 033:bbbbbbbbbeeeeeebbeeeeeebbeeeeeebbeeeeeebbeeeeeebbeeeeeebbbbbbbbb
# 034:6666666666666666bbb66666ffbb6666effbb666eeffbb66eeeffb66eeeefb66
# 035:888bbb0c888bbb0c888bbb0d888bbb0d888bbb0d888bbb0d888bbb0c888bbb0c
# 036:ccccc999ccccc999dddddd99dddddd99dddddd99dddddd99ccccccc9ccccccc9
# 037:99cccccc99ccccccdddddddddddddddd9ddddddd9ddddddd9ccccccc9ccccccc
# 038:c0bbb888c0bbb888d0bbb888d0bbb888d0bbb888d0bbb888c0bbb888c0bbb888
# 039:dddddddeddddddeeeeeeeeeeeeeeeeeeffffffffbbbbbbbb6666666666666666
# 040:eeeefb66eeeffb66eeffbb66effbb666ffbb6666bbb666666666666666666666
# 044:666666666666666666666bbb6666bbff666bbffe66bbffee66bffeee66bfeeee
# 045:6666666666666666bbbbbbbbffffffffeeeeeeeeeeeeeeeeeeddddddeddddddd
# 046:cccccccccbbbbbbccbccccbccbc55cbccbc55cbccbccccbccbbbbbbccccccccc
# 047:eeeeeeeeebbbbbbbebcbcbcbebbbbbbbebbcbcbbebbbcbbbebbbbbbbeeeeeeee
# 048:ddddddddddddddddeeedddddeeeeddddfffeedddbbffeedd6bbfeedd66bfeedd
# 050:eeeefb66deeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66
# 051:888bbb0c888bbb0c888bbb00888bbbbb888bbbbb888bbbbb8888888888888888
# 052:ccccccc9ccccccc900000000bbbbbbbbbbbbbbbbbbbbbbbb8888888888888888
# 053:9ccccccc9ccccccc00000000bbbbbbbbbbbbbbbbbbbbbbbb8888888888888888
# 054:c0bbb888c0bbb88800bbb888bbbbb888bbbbb888bbbbb8888888888888888888
# 055:000444440c0444440c0444440c0444440c0444440c0444440c0000000c0cccca
# 056:44444444444444444444444444444444444444444444444404444444a0444444
# 059:4444444444444444444444444444444444444444444444444444444444444444
# 060:66bfeeee66bfeeed66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd
# 061:dddddddddddddddddddddeeeddddeeeedddeefffddeeffbbddeefbb6ddeefb66
# 062:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
# 063:dd55ffffdd55ffffdd55ffffdd55ffffdd55ffffdd55ffffdd55ffffdd55ffff
# 064:1133111111331333113313331133133311331331113311111113331111113333
# 065:1111331131113311313133111131331113313311111131111113311113331116
# 066:fffffffffeeeeeeffeeeeeeffeeeeeeffeeddeeffeeddeeffeeddeeffeeddeef
# 067:6666666666666666bbbbbbbbffffffffeeeeeeeeeeeeeeeedddddddddddddddd
# 068:fffffffffeeeeeeefeeeeeeefeeeddddfeeeddddfeeeeeeefeeeeeeeffffffff
# 069:ffffffffeeeeeeefeeeeeeefddddeeefddddeeefeeeeeeefeeeeeeefffffffff
# 071:0c0cccca0c0aaaaa0c0000000c0ccccc0c0ccccc0c0bbbbb0c0bbbbb0c000000
# 072:aa044444aa04444400000000ccccccccccccccccbbbbbbbbbbbbbbbb00000000
# 073:444444444444444400000000ccccccccccccccccbbbbbbbbbbbbbbbb00000000
# 074:444444444444444400000000ccccccccccccccccbbbbbbbbbbbbbbbb00000000
# 075:44444000444440c0000000c0bbbbb0c0bbbbb0c0bbbbb0c0bbbbb0c0000000c0
# 076:66666666000066660550066600550066600550006600555066605b55666055bb
# 077:66666666666600006660055066005500000550060555006655b50666bb550666
# 078:dddddddddddddddd5555555555555555ffffffffffffffffffffffffffffffff
# 079:ffff55ddffff55ddffff55ddffff55ddffff55ddffff55ddffff55ddffff55dd
# 080:6111333366111333661113336661133366611333666611336666613366666111
# 081:3331111633311166331116663311166631116666311166663116666611666666
# 082:feeddeeffeeddeeffeeddeeffeeddeeffeeeeeeffeeeeeeffeeeeeefffffffff
# 083:ddddddddddddddddeeeeeeeeeeeeeeeeffffffffbbbbbbbb6666666666666666
# 084:66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd
# 085:ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66
# 087:0c0ccccc00000000011111110111111100000000409044444090444440004444
# 088:cccccccc00000000111111111111111100000000444444444444444444444444
# 089:cccccccc00000000111111111111111100000000444444444444444444444444
# 090:cccccccc00000000111111111111111100000000444444444444444444444444
# 091:ccccc0c000000000111111101111111000000000444409044444090444440004
# 092:666005556666005b666660556666605b666660556666605b6666605566666055
# 093:5550066655006666b506666655066666b506666655066666b506666655066666
# 094:eeeeeeeeebbbbbbeebccbbbeebbccbbeebbbccbeebbbbcbeebbbbbbeeeeeeeee
# 095:ffffffffffffffffffffffffffffffff5555555555555555dddddddddddddddd
# 096:6666666666666666bbbbbbbbbbbbbbbb00000000000000000000000000000000
# 097:6666666666666666bbbbbbbbbbbbbbbb00000000000000000000000000000000
# 098:6666666666666666bbbbbbbbbbbbbbbb00000000000000000000000000000000
# 099:bbbbbbbbbbbbbbbbbb000000bb000000bb000000bb0000ddbb0000ddbb0000dd
# 100:bbbbbbbbbbbbbbbb000000bb000000bb000000bbdd0000bbddd000bbddd000bb
# 108:dd888888dd888888dd888888dd888888dd888888dd888888dd888888dd888888
# 109:888888888888888888888888dddddddddddddddddddddddd8888888888888888
# 110:88888888888888888888888888888888ccccccccbbbbbbbbbbbbbbbbcccccccc
# 111:dddddddddddddddddd555555dd555555dd55ffffdd55ffffdd55ffffdd55ffff
# 115:bb000dddbb000dddbb000dddbb00ddddbb000dddbb000dddbb000dddbb0000dd
# 116:ddd000bbdddd00bbdddd00bbdddd00bbddd000bbddd000bbddd000bbddd000bb
# 127:dddddddddddddddd555555dd555555ddffff55ddffff55ddffff55ddffff55dd
# 128:00000000000000000000000000000000bbbbbbbbbbbbbbbb6666666666666666
# 129:00000000000000000000000000000000bbbbbbbbbbbbbbbb6666666666666666
# 130:00000000000000000000000000000000bbbbbbbbbbbbbbbb6666666666666666
# 131:bb0000ddbb000000bb000000bb000000bb000000bb000000bbbbbbbbbbbbbbbb
# 132:dd0000bbdd0000bb000000bb000000bb000000bb000000bbbbbbbbbbbbbbbbbb
# 144:88888888888d888888d5d8888d555d88dd555dd8dd5b5dd8dd555dd8ddddddd8
# </TILES>

# <SPRITES>
# 000:000005060000f65f0000f4440000444400004ff400004444000044440000fccf
# 001:5000000065f00000444f000044440000ff4400004444000044440000cccf0000
# 002:000000050000ff560000f4440000444400004ff400004444000044440000fccf
# 003:00560000f5600000444f000044440000ff4400004444000044440000cccf0000
# 004:0000000000000ddd0000dddd0000dddd0000ddd50000dd5d0000dddd000000dd
# 005:00000000ddd00000d5dd00005ddd0000dddd0000dddd0000dddd0000ddd00000
# 006:0000000000000ddd0000ddd50000dddd0000dddd0000dddd0000dddd000000dd
# 007:00000000ddd00000dddd00005ddd0000d5dd0000dd5d0000dddd0000ddd00000
# 008:0000000000000000004440000044440000444000000000000000000000000000
# 009:0000000000000000000444000044440000044400000000000000000000000000
# 010:000000000000000000eeeee000eeeee000ee0e0000eee00000ee000000000000
# 016:000ffccf000ffccf000ffccf000ffccf0004ffff0000ff000000ff00000fff00
# 017:cccf0000cccf0000cccf0000cccf0000ffff000000ff000000ff00000fff0000
# 018:0000fccf0000fccf0000fccf0000fccf0000ffff0000ff000000ff000000fff0
# 019:cccff000cccff000cccff000cccff000ffff400000ff000000ff000000fff000
# 020:00000ddd000ddd5d0005dddd000ddd5d000ddddd0000dd000000dd00000ddd00
# 021:dddd0000d5dd0000dddd0000d5dd0000dddd000000dd000000dd00000ddd0000
# 022:00000ddd0000dd5d0000dddd0000dd5d0000dddd0000dd000000dd000000ddd0
# 023:dddd0000d5ddd000dddd5000d5ddd000ddddd00000dd000000dd000000ddd000
# </SPRITES>

# <MAP>
# 000:121212121212121212121212121212121212121212121245551212121212121212121212124555121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212124555121212124555121212121245551212121212455512121212124555121212121212121212121212121212121212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 001:121212121212121212121212121212121212121212121245551212121212121212121212124555121212121212121212121204140414041404140414041404140414041412121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212124555121212124555121212121245551212121212455512121212124555121212121212121212121212121212121212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 002:707070707070707070700414041404140414041412127045557012127070701212121212124555121212121212121212041405150515051505150515051505150515051570701212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212124555121212124555121212121245551212121212455512121212124555121212121212121212121212121212121212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 003:707070707070708070700515051505150515051512127045557012127070707070121212124555121212121212120414051570707070707070707070707070707070707070707012121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212124555707070704555707070707045557070707070455570707070704555707070707070707004140414041404140414041404141212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 004:061606163646707070707070707070707070707012127044547012127070807070707012124555120414041404140515707070707070707070707070707070707070707070707070121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212704555707070704555707070707045557070707070455570707070704555707070707070707005150515051505150515051505151212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 005:071707173747707070807070707070707070707012127070807012127070707070707070704555700515051505157070707070c2d234343434343434343434343434022270707070707070707070041404140414041404140414121212121212121212121212121212121212121212121212121212121212121270704555707070704555707070707045557070707070455570707070704555707070707070707070707070707070707070707070703646261626000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 006:081808183848707070707070708070707070707004147070707004147070707070807070704454707070707070707070707070c3d335353535353535353535353535032370707070707070707070051505150515051505150515701212121212121212121212121212121212121212121212121212121212127070704555707070704555707070707045557070707070455570707070704555707070707070707070707070707070707070707070703747271727000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 007:707070707070707070707070707070708070707005157080707005157080707070707070707070707070707070707070707070455570707070707070707070707070455570121212707070707070707070707070707070707070701212121212121212121212121212121212121212121212121212121212707070704454707070704454707070707044547070707070445470707070704454707070707070707070707070707070707070707070703848281828000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 008:707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070243434718170707080707070707070807070455570707070707070707070707070707070707070707070707012120414121212121212121212121212121212121212121212127070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070701212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 009:243434343434343434022270707070707070707070707070707070707070707070707070707070707070704454707070253535728270707070707070707070707070455570707070701212127070707070707070707070707070707070700515707070701212121212121212121212121212121212707070707070707080707070708070707070707080707070707070807070707070708070707070707070707070707070707070707070707012121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 010:253535353535353535032370707070707070702434342470802434342470707070707070707070707070704555707070707070708070707070707080707070707070455570707070707070707070707070707070707070707070707070707070707070707012041412120414121204141212041412707070707070707070707070707070707070707070707070707070708070707070707070707070707070707070707070707070707070121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 011:121212121212121212455512127070707070702535352570702535352570707070707070704454707070704555121270707070707070707070707070707070708070455570707070707070707012121270707070707070707070707070707070707070707070051570700515707005157070051570707070707070708070707070707070807070707070708070707070707070707070708070807070707070707070707070707070701212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 012:1212121212121212124555121212127070707070707070807070707070707070707012121245557070707045557070701212707012127080121270701212127070704555707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707080707070707070807070707070807070708070707070807070707070707070707070701212c4d41212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 013:1212121212121212124555121270707070707091a191a191a191a191a1707070701212121245559191919145557070707070708070707070708070707070707070704555707070707070707070707070701212127070707070707070121270701212707070707070707070707070707070707070707070707070707070708070707070707070707070707070707070707070707070707070707070707070707070121270701212c5d51212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 014:121212121212121212455512121212121212121212121212121212121212121212121212124555c0c0c0c0455570707070707070707070707070707070807070807045551212707070707070707070707070707070707070707012c4d470c4d470c4d470707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707012121212c4d4121212121212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 015:121212121212121212445412121212121212121212121212121212121212121212121212124555c0c0c0c0455591a191a191a191a191a191a191a191a191a191a19145551212127070707070707070707070707070707070701212c5d570c5d570c5d57070243434343434343434343434343434247070707091a191a191a191a191a191a191a191a191a191a191a191a191a191a191a191a170707070121212121212c5d5121212121212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 016:121212121212121212121212121212121212121212121212121212121212121212121212124555c0c0c0c04555c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c045551212121212121212121212121212121212121212121212121212121212121212122535353535353535353535353535352512121212c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0121212121212121212121212121212121212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 017:00000000000000d0d0d0d0d0f0f0f0f0f0d0d0d0d0d0d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 018:00f0f0f0f0f000d0d0d0d0d0f0f0e0f0f0d0d0d0d0d0d000f0f0f0f0f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 019:00f0c0c0c0f000d0d0d0d0d0f0e0e0e0f0d0d0d0d0d0d000f0c0c0c0f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 020:00f0f0f0f0f000d0d0d0d0d0f0f0e0f0f0d0d0d0d0d0d000f0f0f0f0f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 021:000000f0000000d0d0d0d0d0f0f0f0f0f0d0d0d0d0d0d0000000f0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 022:d0d000f0f000d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d000f0f000d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 023:d0d00000f000d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d000f00000d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 024:d0d0d0000000d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0000000d0d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 025:d0d0d0d0d0d0d0d0d0d0d0d07383d0d0b3d0d0d0d0d0d0d0d0d0d0d0d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 026:d0d0d0d0d0d0d0d0d0d0d0d0748494a4b4d0d0d0d0d0d0d0d0d0d0d0d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 027:d0d0d0d0d0d0d0d0d0d0d0d0758595a5b5d0d0d0d0d0d0d0d0d0d0d0d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 028:d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 029:30405060d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 030:31415161d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0b0b0b0b0b0b0d0d0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 031:32425262d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0b0b0b0e0e0c0c0b0b0b0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 032:33435363d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0b0b0b0e0e0c0c0b0b0b0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 033:12121212121212121212121212121212121212b0b0b0b0b0b0b0b0b0b0d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 034:100110101010101010101010101010101010100110101010101010101010101010101010101010101010101010011010101010101010101010011010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 035:101010101001101010101010101010101010101010101010101010101010011010101001101010100110101010101010101001101010101010101001101010101010011010011010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 036:e2e210101010101010101010101001101010101010101001101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 037:e2e2d1101010101001101010101010101010011010101010101010011010101001101010101010101010101010101010101010101010101010101010101010101010101010101010101010011010101010011010101001101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 038:e2f210101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010e6e6e6e6e6e6e6e6101010e6e6e6e6e6e6e6101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 039:e2f210011010101010101010011010101010101010101010011010101010101010101010101010101010101010101010101010101010f6e4e4e4e4e4e4f7101001f6e4e4e4e4e4f7101010101010101010101010011010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 040:e2e210100909101010101010101010101010101010101010101010101010101010101010101010e6e6e6e6e6e6e6e6e6101010100110f3e3e3e3e3e3e3f4101010f3e3e3e3e3e3f4101010101009101010101010101010100110101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 041:e2e2e2e2e2e2e21010101010101010101010101010101010101010101010101010101010101010f6e4e4e4e4e4e4e4f7101010101010f3e3e5e3e3e5e3f4011010f3e3e5e3e5e3f4101010e1e1e1e1e110101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 042:e23040506010101010101010101010101010101010101010101010101010100909101010101010f3e3e3e3e3e3e3e3f4d6d610101010f3e3e5e3e3e5e3f4101010f3e3e5e3e5e3f4101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 043:e231415161101010101010101010101010101010101010101010101010e1e1e1e1e1e1e1101010f3e3e5e5e3e5e5e3f4101010101010f3e3e3e3e3e3e3f4101010f3e3e5e3e5e3f4100110101010011010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 044:e23242526210101010101010090910101010101010101010101010101010100110101010101010f3e3e3e3e3e3e3e3f4101010101010f3e3e3e3e3e3e3f4100110f3e3e3e3e3e3f4101010101010101010090910101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 045:e2334353631010101010e1e1e1e1e1e11010101010090910101010101010101010100110101010f3e3e3e3e3e3e3e3f4d6d610101010f3e3e5e3e3e5e3f4101010f3e3e3e3e3e3f4101010011010101010e1e1e1e1e1e1101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 046:e2e2e2e2e2e2e2101010101010101010101010e1e1e1e1e1e1e110101010101010101010101010f3e3e5e5e3e5e5e3f4101010101010f3e3e5e3e3e5e3f4101010f3e3e5e3e5e3f4101010101010101010101001101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 047:e2f210101010101010101010100110101010101010101010101010101010101010101010101010f3e3e3e3e3e3e3e3f4100110101010f3e3e5e3e3e5e3f4101010f3e3e5e3e5e3f4101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 048:e2f210101001101010101010101010101010101010100110101012445412121010101010101010f3e3e3e3e3e3e3e3f4101010101010f3e3e3e3e3e3e3f4101010f3e3e3e3e3e3f4101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 049:e2e210101010100909090910101010090909090910101010101212455512121210101010101010f3e3e3e3e3e3e3e3f4101009090910f3e3e3e3e3e3e3f4090909f3e3e3e3e3e3f4090910101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 050:121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </MAP>

# <WAVES>
# 000:00000000ffffffff00000000ffffffff
# 001:0123456789abcdeffedcba9876543210
# 002:0123456789abcdef0123456789abcdef
# </WAVES>

# <SFX>
# 000:01000100010001000100410041004100410071007100710071007100b100d100e100f100f100f100f100f100f100f100f100f100f100f100f100f100364000000000
# 001:020502032202520072009200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f200f20030a000000000
# 002:0000000000000000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000f000008000000000
# 005:0100110021002100310031004100510051006100610071008100810091009100a100b100c100c100d100e100e100e100e100f100f100f100f10001002e9000000000
# 010:010011001100110021003100410051006100710081008100810091009100a100a100a100b100b100c100d100d100e100e100f100f100f100f100f1002e2000000000
# </SFX>

# <PATTERNS>
# 000:100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </PATTERNS>

# <TRACKS>
# 000:100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </TRACKS>

# <PALETTE>
# 000:1c1c1c895530ee1c18ef7d57ffcd75e214da20d60025717929366f3b5dc941a6f600f2fff4f4f494b0c2566c86333c57
# </PALETTE>

