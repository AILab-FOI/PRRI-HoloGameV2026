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
        
class TeleportTrigger(Collidable):
    def __init__(self, x, y, w, h, teleportToX, teleportToY, levelIndex, owner = None):
        Collidable.__init__(self, x, y, w, h)

        self.owner = owner
        self.levelIndex = levelIndex
        
        self.teleportToX = teleportToX
        self.teleportToY = teleportToY
        
    def Teleport(self):
        global activeLevelIndex
        activeLevelIndex = self.levelIndex
        activeLevel = levels[activeLevelIndex]
        activeLevel.LoadLevel(self.teleportToX, self.teleportToY)

# --- HELPER ---
def move_towards(a, b, v):
    if a < b:
        return min(a + v, b)
    else:
        return max(a - v, b)

tile_damage_type = {
    25: "poison",
    26: "poison",
    144: "spike",
    14: "instant"
}

# --- PLAYER ---
class Player:
    def __init__(self):
        self.x = 600
        self.y = 81
    
        self.width = 14
        self.height = 14

        self.hsp = 0
        self.vsp = 0
        
        self.on_ground = False
        self.coyote_timer = 0
        self.coyote_time_max = 2

        self.jump_buffer = 0
        self.jump_buffer_max = 10

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
        self.maxHealth = self.health
        self.dead = False
        
        self.iframeTimer = 0
        self.iframeTime = 90
        self.facing = 1   # 1 = right, -1 = left
        
        self.hitbox = Collidable(self.x, self.y, self.width, self.height)
        
        self.gun = None

        self.hasGun = False
        self.hasKatana = False

        self.activeWeapon = "none"

        self.hasImmunity = False
        self.max_jumps = 1

        self.hasDash = False
        
        self.pausePlayer = False

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
        tile_x = int((self.x + self.width / 2) / tile_size)
        tile_y = int((self.y + self.height) / tile_size)

        tile = mget(tile_x, tile_y + activeLevelIndex * 17)
        print(str(tile),10,20,12)

        if tile in tile_damage_type and self.iframeTimer <= 0:
            dmg_type = tile_damage_type[tile]
            if dmg_type == "poison" and self.hasImmunity:
                return False
            self.health -= 100
            self.iframeTimer = self.iframeTime
            if self.health <= 0:
                self.dead = True

        for d in damageTriggers:
            if d.check(self.hitbox) and self.iframeTimer <= 0:
                self.health -= d.damage
                self.iframeTimer = self.iframeTime
                if self.health < 1:
                    self.dead = True
                sfx(17, "C#2", 15)
                return True
        
        return False

    def check_teleport_triggers(self, teleportTriggers):
        for t in teleportTriggers:
            if t.check(self.hitbox):
                t.Teleport()
                
                return True
        
        return False

    def update(self, colliders, damageTriggers):
        if (self.dead or self.pausePlayer):
            return
        
        healthRectColor = 0
        healthRectWidth = int(40 * ((self.health / self.maxHealth)))
        
        if self.health > 75:
            healthRectColor = 7
        if self.health <= 75 and self.health >= 50:
            healthRectColor = 3
        if self.health <= 50 and self.health > 25:
            healthRectColor = 3
        if player.health <= 25:
            healthRectColor = 2
        
        rect(10, 10, healthRectWidth, 6, healthRectColor)
        
        # LEFT / RIGHT
        self.on_ground = self.check_collision(0, 1, colliders)

        if self.on_ground:
            self.coyote_timer = self.coyote_time_max
            self.jumps_left = self.max_jumps
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        # DEBUG
        #print("ground: " + str(self.on_ground), 6, 2, 12)
        #print("coyote: " + str(self.coyote_timer), 6, 10, 11)
        #print("buffer: " + str(self.jump_buffer), 6, 18, 10)
        #print("jumps: " + str(self.jumps_left), 6, 26, 9)
        #print("dash cd: " + str(self.dash_cooldown), 6, 34, 8)
        
        #if key(5):
            #sfx(2)
            
        #print("AD fsadfamove | Space jump | F shoot | E weapon | R restart ")
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

        if self.hasDash:

            if keyp(64) and not self.is_dashing and self.dash_cooldown <= 0:

                self.is_dashing = True
                self.dash_timer = self.dash_time_max
                self.dash_cooldown = self.dash_cooldown_max

                sfx(22, "G-4", 10)


        # SWITCH WEAPONS
        if keyp(6):
            if self.hasGun and self.hasKatana:
                if self.activeWeapon == "gun":
                    self.activeWeapon = "katana"
                else:
                    self.activeWeapon = "gun" 

        # JUMP INPUT
        if keyp(23):
            self.jump_buffer = 12
            sfx(16, "C-5", 5)

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
                    sfx(16, "C-5", 5)
                    #print("GROUND JUMP", 2, 58, 9)

                # drugi jump u zraku
                elif not self.on_ground and self.jumps_left > 0:
                    self.vsp = -4
                    self.jump_buffer = 0
                    self.jumps_left -= 1
                    sfx(16, "C-5", 5)
                    #print("DOUBLE JUMP", 2, 66, 8)

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
        self.check_teleport_triggers(teleportTriggersGlobal)
        
        self.iframeTimer -= 1
        if (self.iframeTimer <= 0):
            self.iframeTimer = 0

        if self.is_dashing:

            self.dash_timer -= 1

            if self.dash_timer <= 0:
                self.is_dashing = False

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

    def draw(self):
        if not self.dead:
            if self.facing == 1:
                spr(256, int(self.x -cam_x), int(self.y -cam_y), 0, 1, 0, 0, 2, 2)
            else:
                spr(256,int(self.x -cam_x), int(self.y -cam_y), 0, 1, 1, 0, 2, 2)
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
            sfx(32, "C-5", 5)


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
    
    def draw(self):
        if self.owner.dead:
            return

        x = int(self.x - cam_x)
        y = int(self.y - cam_y)

        # 🗡️ uvijek crtamo osnovnu katanu
        # 🗡️ normalna ili spuštena katana
        if self.attackTimer > 0:
            katana_sprite = 345
        else:
            katana_sprite = 344

        if self.owner.facing == 1:
            spr(katana_sprite, x - 1, y, 0, 1, 0, 0, 1, 1)
        else:
            spr(katana_sprite, x + 3, y, 0, 1, 1, 0, 1, 1)

        # 🔥 SLASH dok traje attack
        if self.attackTimer > 0:
            if self.owner.facing == 1:
                spr(346, x + 7, y, 0)
            else:
                spr(346, x - 5, y, 0, 1, 1)

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
        projectile = Projectile(int(self.owner.gun.x), int(self.owner.gun.y), 4 * sizeMultiplier, 4 * sizeMultiplier, int(self.damage) * damageMultiplier, playerDamageTriggers, 2.6, int(self.owner.facing), -1, True, True, 1, True)
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
    def __init__(self, x, y, width, height, damage, damageTriggers, hsp = 2, facing = 1, duration = -1, checkCollision = True, drawSelf = True, multiplier = 1, canBreakTiles = False):
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
        
        self.canBreakTiles = canBreakTiles

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
        
        def checkBreakableTiles():
            tile_x = int((self.x + self.width / 2) / tile_size)
            tile_y = int((self.y + self.height) / tile_size)

            tile = mget(tile_x, tile_y + activeLevelIndex * 17)
            
            for b in breakable_tile_indexes:
                if (b.tileID == tile):
                    mset(tile_x, tile_y + activeLevelIndex * 17, b.brokenTileID)
                    return True
            
            return False
        
        def checkColliders():
            tile_x = int((self.x + self.width / 2) / tile_size)
            tile_y = int((self.y + self.height) / tile_size)

            tile = mget(tile_x, tile_y + activeLevelIndex * 17)
            
            if tile not in background_tile_indexes:
                self.destroy()
        
            for c in colliders:
                if c.check(self):
                    self.destroy()
                    return True
        
        if self.canBreakTiles:
            if (not checkBreakableTiles()):
                checkColliders()
        else:
            checkColliders()
        
        self.x -= dx
        self.y -= dy
    
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
        
        if (abs(self.x - player.x) > 240):
            self.destroy()
    
    def draw(self):  
        if not self.destroyed:
            rect(int(self.x - cam_x), int(self.y - cam_y), int(self.width), int(self.height), 4)

    def destroy(self):
        if self in projectiles:
            projectiles.remove(self)
        if self.contactDamageTrigger in enemyDamageTriggers:
            enemyDamageTriggers.remove(self.contactDamageTrigger)
        
        self.drawSelf = False
        self.destroyed = True

class BossProjectile:
    def __init__(self, x, y, dx):
        self.x = x
        self.y = y

        self.dx = dx
        self.dy = 0

        self.width = 8
        self.height = 8

        self.sprite = 265
        self.damage = 20

        self.dead = False

        self.damageTrigger = DamageTrigger(
            self.x,
            self.y,
            self.width,
            self.height,
            self.damage
        )

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
        if self.dead:
            return

        if self.check_collision(self.dx, self.dy, colliders):
            self.destroy()
            return

        self.x += self.dx
        self.y += self.dy

        self.damageTrigger.x = self.x
        self.damageTrigger.y = self.y

    def draw(self):
        if not self.dead:
            spr(
                self.sprite,
                int(self.x - cam_x),
                int(self.y - cam_y),
                0
            )

    def destroy(self):
        self.dead = True

        if self.damageTrigger in enemyDamageTriggers:
            enemyDamageTriggers.remove(self.damageTrigger)

        if self in enemyProjectiles:
            enemyProjectiles.remove(self)

class PowerUp:
    def __init__(self, x, y, sprite_id, power_type):
        self.x = x
        self.y = y

        self.width = 8
        self.height = 8

        self.sprites = [sprite_id, sprite_id+1, sprite_id+2] 
        self.anim_timer = 0
        self.anim_speed = 20   # 20 frameova (TIC-80 radi na 60 FPS)
        self.anim_index = 0
        self.power_type = power_type

        self.collected = False

    def check_collision_with_player(self):
        return self.x < player.x + player.width and \
               self.x + self.width > player.x and \
               self.y < player.y + player.height and \
               self.y + self.height > player.y

    def apply_power(self):
        # TRAJNI powerup
        if self.power_type == "poison_immunity":
            player.hasImmunity = True

        elif self.power_type == "gun":
            player.hasGun = True
            player.activeWeapon = "gun"

        elif self.power_type == "katana":
            player.hasKatana = True
            player.activeWeapon = "katana"

        elif self.power_type == "heal":
            player.health = min(player.health + 25, 100)

        elif self.power_type == "double_jump":
            player.max_jumps = 2
        
        elif self.power_type == "dash":
            player.hasDash = True

        elif self.power_type == "health_up":
            player.health = min(player.health + 50, player.maxHealth)

    def update(self):
        self.anim_timer += 1

        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_index += 1
            
            if self.anim_index >= len(self.sprites):
                self.anim_index = 0
        if self.collected:
            return

        if self.check_collision_with_player():
            self.apply_power()
            self.collected = True

    def draw(self):
        if not self.collected:
            spr(self.sprites[self.anim_index], int(self.x - cam_x), int(self.y - cam_y))

class NPC:
    def __init__(self, x, y, sprite_id, dialogue):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.sprite_id = sprite_id
        self.dialogue = dialogue
        self.canTalk = True

    def is_player_near(self):
        return abs(player.x - self.x) < 30 and abs(player.y - self.y) < 20

    def update(self):
        if self.is_player_near():
            print("PRESS R", int(self.x - cam_x), int(self.y - cam_y - 10), 12)

            if keyp(18) and not dialogueManager.active:
                dialogueManager.start(self.dialogue)

    def draw(self):
        spr(self.sprite_id, int(self.x - cam_x), int(self.y - cam_y), 0, 1, 0, 0, 2, 2)

# --- ENEMIES ---
class Enemy:
    def __init__(self, x, y):
        self.attackTimer = 0

        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.dx = -1
        self.sprite = 260

        self.hsp = 0
        self.vsp = 0

        self.facing = 1   # 1 = right, -1 = left
        self.health = 100
        self.dead = False
        
        self.iframe = 0
        self.iframeMax = 10

        self.contactDamageTrigger = DamageTrigger(self.x, self.y, self.width, self.height, 25)
        
        self.startingPosX = x
        self.startingPosY = y

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
                    sfx(21, "B-3", 12)
                if self.health < 1:
                    self.dead = True
                    self.destroy()
                if d.owner is not None and not d.owner.destroyed:
                    d.owner.destroy()
                return True
    
        return False

    def update(self, colliders, damageTriggers):
        if (self.dead): return
        
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
                spr(self.sprite, int(self.x - cam_x), int(self.y - cam_y), 0, 1, 0, 0, 2, 2)
            else:
                spr(self.sprite, int(self.x - cam_x), int(self.y - cam_y), 0, 1, 1, 0, 2, 2)
            # DEBUG: body hitbox
            rectb(
                int(self.x - cam_x),
                int(self.y - cam_y),
                self.width,
                self.height,
                2
            )

            # DEBUG: damage hitbox
            rectb(
                int(self.contactDamageTrigger.x - cam_x),
                int(self.contactDamageTrigger.y - cam_y),
                self.contactDamageTrigger.width,
                self.contactDamageTrigger.height,
                3
            )

    def TakeDamage(self, damage, removeInt):
        self.health = self.health - damage
        if self.health < 1:
            self.dead = True
            
    def destroy(self):
        if self.contactDamageTrigger in playerDamageTriggers:
            playerDamageTriggers.remove(self.contactDamageTrigger)
        if self in enemiesGlobal:
            enemiesGlobal.remove(self)

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

class ScreenTransition():
    def __init__(self):
        self.transitionFrameDelay = 1
        self.transitionPeakDelay = 15
        
        self.transitionTimer = 0
        
        self.transitionSlideFrameAmount = 30
        self.transitionSlideFrameCounter = 0
        
        self.isDoingTransition = False
        self.reverse = False
        
        self.firstSlideComplete = False
        
        self.i = 0
        self.xPos = 0
    
    def update(self):
        if (self.isDoingTransition):
            self.transitionTimer += 1
            
            motion = int(256 / self.transitionSlideFrameAmount)
            
            #spr(0, cam_x - (256 - motion * self.i), cam_y, 0, 2 * self.i, 0, 0, 1, 1)
            #spr(0, cam_x + (256 - 4 * motion * self.i), cam_y, 0, 10 * self.i, 0, 0, 1, 1)
            
            self.xPos = cam_x - 128
            self.xPos = self.clampPosition(self.xPos, 0, 0)
            
            if (not self.reverse): 
                rect(self.xPos, cam_y, self.xPos - (64 - 2 * motion * self.i), 200, 0)
            else:
                rect(self.xPos, cam_y, ((2 * motion * self.i)), 200, 0)
            
            if self.transitionTimer > self.transitionPeakDelay and (self.transitionSlideFrameCounter >= self.transitionSlideFrameAmount) and not self.reverse:
                self.reverse = True
                self.transitionTimer = 0
                self.transitionSlideFrameCounter = 0
                self.firstSlideComplete = True
            
            if (self.transitionTimer > self.transitionFrameDelay) and (self.transitionSlideFrameCounter < self.transitionSlideFrameAmount) and not self.reverse:
                self.i += 1
                self.transitionTimer = 0
                self.transitionSlideFrameCounter += 1
            elif (self.transitionTimer > self.transitionFrameDelay) and (self.transitionSlideFrameCounter < self.transitionSlideFrameAmount) and self.reverse:
                self.i -= 1
                self.transitionTimer = 0
                self.transitionSlideFrameCounter += 1
            elif (self.transitionTimer > self.transitionFrameDelay) and (self.transitionSlideFrameCounter >= self.transitionSlideFrameAmount) and self.reverse:
                #spr(0, cam_x - (256 - motion * self.i), cam_y, 0, 0, 0, 0, 1, 1)
                self.firstSlideComplete = False
                self.isDoingTransition = False
                self.i = 0
    
    def doTransition(self):
        self.i = 0
        self.transitionTimer = 0
        self.transitionSlideFrameCounter = 0
        self.isDoingTransition = True
        self.reverse = False
        self.firstSlideComplete = False
        
    def clampPosition(self, n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n
    

class Level:
    def __init__(self, x, y, sizeX, sizeY, mapX, mapY, enemiesList, teleportTriggersList, powerupsList,npcsList):
        self.startX = x
        self.startY = y

        self.sizeX = sizeX
        self.sizeY = sizeY
        
        self.mapX = mapX
        self.mapY = mapY
        
        self.enemiesList = enemiesList
        self.teleportTriggersList = teleportTriggersList
        self.powerupsList = powerupsList
        self.npcsList=npcsList
        
        self.isLoadingLevel = False
        
        self.playerLocationX = 0
        self.playerLocationY = 0
    
    def Update(self):
        if (self.isLoadingLevel):
            player.pausePlayer = True
            global screenTransition
            if ((screenTransition.firstSlideComplete and screenTransition.isDoingTransition) or not screenTransition.isDoingTransition):
                global activeLevelMapX
                activeLevelMapX = self.mapX

                global activeLevelMapY
                activeLevelMapY = self.mapY

                global activeLevelSizeX
                activeLevelSizeX = self.sizeX

                global activeLevelSizeY
                activeLevelSizeY = self.sizeY

                global player
                player.pausePlayer = True
                player.x = self.playerLocationX
                player.y = self.playerLocationY
                player.hsp = 0
                player.vsp = 0

                # očisti stare powerupe
                for p in powerupsGlobal[:]:
                    powerupsGlobal.remove(p)

                # dodaj powerupe iz ovog levela
                for p in self.powerupsList:
                    powerupsGlobal.append(p)
                
                for e in enemiesGlobal[:]:
                    #e.dead = False
                    enemiesGlobal.remove(e)
                for n in npcsGlobal[:]:
                    npcsGlobal.remove(n)
                
                for n in self.npcsList:
                    npcsGlobal.append(n)

                for t in teleportTriggersGlobal:
                    if t in teleportTriggersGlobal:
                        teleportTriggersGlobal.remove(t)

                for t in self.teleportTriggersList:
                    teleportTriggersGlobal.append(t)

                if (not screenTransition.isDoingTransition): 
                    player.pausePlayer = False

                    for e in self.enemiesList:
                        e.x = e.startingPosX
                        e.y = e.startingPosY
                        enemiesGlobal.append(e)
                    
                    global playerDamageTriggers
                    playerDamageTriggers = []

                    for e in enemiesGlobal:
                        playerDamageTriggers.append(e.contactDamageTrigger)
                    
                    self.isLoadingLevel = False
    
    def LoadLevel(self, teleportX, teleportY):
        self.playerLocationX = teleportX
        self.playerLocationY = teleportY
        
        global screenTransition
        screenTransition.doTransition()
        self.isLoadingLevel = True

class SmallEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.health = 30
        self.width = 12
        self.height = 12
        self.dx = -1.5

        self.iframe = 0
        self.iframeMax = 8

        self.sprite = 267

        # Smaller contact/damage hitbox
        self.contactDamageTrigger = DamageTrigger(
            self.x,
            self.y,
            self.width,
            self.height,
            10
        )
        
      
        rectb(
                int(self.x - cam_x),
                int(self.y - cam_y),
                self.width,
                self.height,
                4
            )

            # SmallEnemy damage hitbox
        rectb(
                int(self.contactDamageTrigger.x - cam_x),
                int(self.contactDamageTrigger.y - cam_y),
                self.contactDamageTrigger.width,
                self.contactDamageTrigger.height,
                3
            )
class StaticEnemy(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y)

        self.dx = 0
        self.hsp = 0

        self.sprite = 262

        self.contactDamageTrigger.damage = 15

    def update(self, colliders, damageTriggers):
        if self.dead:
            return

        # GRAVITY
        if not self.check_collision(0, self.vsp + 1, colliders):
            self.vsp += 0.25
        else:
            self.vsp = 0

        # COLLISION Y
        if self.check_collision(0, self.vsp, colliders):
            self.vsp = 0

        # MOVE ONLY VERTICALLY
        self.y += self.vsp

        if self.attackTimer > 0:
            self.attackTimer -= 1

        if self.iframe > 0:
            self.iframe -= 1

        self.check_damage_trigger(damageTriggers)

        self.contactDamageTrigger.x = self.x
        self.contactDamageTrigger.y = self.y

class BigEnemy(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y)

        self.health = 200
        self.sprite = 269

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.width = 32
        self.height = 32

        self.sprite = 323

        self.health = 500

        self.dx = 1
        self.speed = 1

        self.attackCooldown = 90
        self.attackTimer = 0

        self.contactDamageTrigger = DamageTrigger(
            self.x,
            self.y,
            self.width,
            self.height,
            40
        )

    def shoot(self):
        proj = BossProjectile(
            self.x + 12,
            self.y + 12,
            self.facing
        )

        BossProjectiles.append(proj)
        enemyDamageTriggers.append(proj.damageTrigger)

        sfx(10, "C-4", 15)

    def update(self, colliders, damageTriggers):
        if self.dead:
            return

        # MOVEMENT
        self.x += self.dx * self.speed

        if self.check_collision(4 * self.dx, 0, colliders):
            self.dx = -self.dx
            self.facing *= -1

        # SHOOT TIMER
        if self.attackTimer > 0:
            self.attackTimer -= 1
        else:
            self.shoot()
            self.attackTimer = self.attackCooldown

        # GRAVITY
        if not self.check_collision(0, self.vsp + 1, colliders):
            self.vsp += 0.25
        else:
            self.vsp = 0

        # Y COLLISION
        if self.check_collision(0, self.vsp, colliders):
            self.vsp = 0

        self.y += self.vsp

        # DAMAGE
        self.check_damage_trigger(damageTriggers)

        if self.iframe > 0:
            self.iframe -= 1

        self.contactDamageTrigger.x = self.x
        self.contactDamageTrigger.y = self.y

    def draw(self):
        if not self.dead:
            spr(self.sprite, int(self.x - cam_x), int(self.y - cam_y), 0, 1, int(self.facing == -1), 0, 4, 4)


class BountyHunter(BossEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.sprite = 290

#class WaterDropper():
   # def __init__(self, x, y, water_tile_id, stopping_tile_id, delay, restartDelay = 0, startingDelay = 0):
    #    self.x = x
    #    self.y = y
    #    self.startingY = y
    #    self.tile_id = water_tile_id
    #    self.stopping_tile_id = stopping_tile_id
    #    
    #    self.delay = delay
    #    self.restartDelay = restartDelay
    #    
    #    self.timer = 0
    #    self.restartTimer = startingDelay
    #    
    #    self.prev_tile_id = self.y + 1
    
    #def update(self):
    #    if (self.restartTimer > 0):
    #        self.restartTimer -= 1
    #        return
        
    #    self.timer += 1
    #    if self.timer > self.delay:
    #        nextTile = mget(self.x, (self.y))
    #        self.prev_tile_id = mget(self.x, (self.y))
    #        if (nextTile != self.stopping_tile_id):
    #            mset(self.x, self.y, self.tile_id)
    #            if (self.y != self.startingY): mset(self.x, self.y - 1, self.prev_tile_id)
    #            self.y += 1
    #        else:
    #            self.prev_tile_id = mget(self.x, (self.y - 2))
    #            mset(self.x, self.y - 1, self.prev_tile_id)
    #            self.y = self.startingY
    #            self.restartTimer = self.restartDelay

    #        self.timer = 0

class BreakableTile():
    def __init__(self, tileID, brokenTileID):
        self.tileID = tileID
        self.brokenTileID = brokenTileID

# --- DIALOGUES ---
class DialogueManager:
    def __init__(self):
        self.active = False
        self.lines = []
        self.index = 0
        self.just_started = False

    def start(self, lines):
        self.active = True
        self.lines = lines
        self.index = 0
        self.just_started = True

        player.pausePlayer = True

    def update(self):
        if not self.active:
            return

        if self.just_started:
            self.just_started = False
            return

        if keyp(18):
            self.index += 1

            if self.index >= len(self.lines):
                self.active = False
                player.pausePlayer = False

    def draw(self):
        if not self.active:
            return

        rect(10, 92, 220, 34, 0)
        rectb(10, 92, 220, 34, 12)

        print(self.lines[self.index], 18, 102, 12)
        print("PRESS R", 170, 116, 10)

# --- INIT ---
player = Player()
gun = RangedWeapon(player, 30, 25)
katana = Katana(player, 60, 25)

tile_size = 8

playerDamageTriggers = []
enemyDamageTriggers = []
powerupsGlobal = []
npcsGlobal = []

projectiles = []
BossProjectiles = []
enemyProjectiles = []
    
background_tile_indexes = [
    1, 3, 4, 5, 6, 7, 8, 14, 15, 16, 19, 20, 21, 22, 25, 26, 29, 35, 36, 37, 38, 51, 52, 53, 54, 55, 56, 71, 72, 73, 74, 75, 87, 88, 89, 90, 91, 99, 100, 104, 105, 115, 116, 117, 118, 121, 122, 123, 124, 125, 131, 132, 133, 134, 137, 138, 139, 140, 141, 144, 145, 146, 147, 148, 149, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 163, 164, 165, 168, 169, 170, 171, 172, 173, 174, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 187, 188, 192, 193, 194, 198, 199, 200, 201, 204, 205, 208, 209, 210
]

breakable_tile_indexes = {
    BreakableTile(102, 187)
}

enemiesLevel1 = []
enemiesLevel2 = []
enemiesLevel3 = []
enemiesGlobal = []

teleportTriggersGlobal = []

screenTransition = ScreenTransition()
dialogueManager = DialogueManager()
#waterDroppers = [
#       WaterDropper(23, 5, 8, 25, 5, 0, 0),
#      WaterDropper(24, 5, 8, 26, 5, 0, 8),
#      WaterDropper(23, 5, 8, 25, 5, 0, 16),
#        WaterDropper(24, 5, 8, 26, 5, 0, 24),
#        WaterDropper(23, 5, 8, 25, 5, 0, 32),
#        WaterDropper(24, 5, 8, 26, 5, 0, 40),
#        WaterDropper(52, 9, 8, 33, 5, 60, 0),
#        WaterDropper(124, 8, 8, 26, 5, 0, 5),
#        WaterDropper(125, 8, 8, 25, 5, 0, 25),
#        WaterDropper(130, 8, 8, 26, 5, 0, 5),
#        WaterDropper(131, 8, 8, 25, 5, 0, 25),
#        WaterDropper(137, 8, 8, 25, 5, 0, 5),
#        WaterDropper(138, 8, 8, 26, 5, 0, 25),
#        WaterDropper(144, 8, 8, 26, 5, 0, 5),
#        WaterDropper(145, 8, 8, 25, 5, 0, 25),
#        WaterDropper(151, 8, 8, 25, 5, 0, 5),
#        WaterDropper(152, 8, 8, 26, 5, 0, 25),
#    ]

def game_setup():
    global player, gun, katana
    global enemiesGlobal
    global enemiesLevel1, enemiesLevel2, enemiesLevel3
    global playerDamageTriggers
    global teleportTriggersGlobal
    global teleportTriggersLevel1, teleportTriggersLevel2, teleportTriggersLevel3
    global levels
    global activeLevelIndex
    global activeLevelMapX, activeLevelMapY
    global activeLevelSizeX, activeLevelSizeY
    global activeLevel
    global screenTransition
    global waterDroppers
    global BossProjectiles
    BossProjectiles = []

    player = Player()
    npcsGlobal = []

    gun = RangedWeapon(player, 30, 25)
    katana = Katana(player, 60, 25)

    powerupsLevel1 = [
        PowerUp(61 * tile_size, 10 * tile_size, 328, "double_jump"),
        PowerUp(166 * tile_size, 8 * tile_size, 280, "gun")
    ]

    powerupsLevel2 = [
        PowerUp(107 * tile_size, 9 * tile_size, 341, "katana")
    ]

    powerupsLevel3 = [
        PowerUp(63 * tile_size, 6 * tile_size, 331, "dash"),
        PowerUp(3 * tile_size, 5 * tile_size, 325, "poison_immunity"),
        PowerUp(102 * tile_size, 0 * tile_size, 352, "health_up")
    ]

    npcsLevel1 = []
    npcsLevel2 = []
    npcsLevel3 = []

    # NPC dijalozi
    npc_doc = NPC(892, 81, 288, [
        "I need to scan you for your ID.",
        "Scanning...",
        "Huh... no ID.",
        "Let me try again.",
        "...",
        "Government gear still",
        "doesn't work in 2058.",
        "...",
        "Sir, stay right there.",
        "I'm calling the Entity Enforcers.",
        "They'll handle you.",
        "Sir, put the weapon down.",
        "Unknown entity in the hospital.",
        "INITIATE PROTOCOL X!!!",
        "I REPEAT, INITIATE PROTOCOL X!"
    ])

    npc_veso = NPC(520, 81, 298, [
        "Woah!!!",
        "You just woke up broo!",
        "That's crazy brooo!",
        "Hi, I'm Dank btw!",
        "Those back-alley docs gave me some",
        "crazy eye infection.",
        "Should've gone to a real doc.",
        "Controls:",
        "Arrows - move",
        "A - jump",
        "B - combat",
        "see you around broo!!"

    ])

    npc_jinx = NPC(286, 112, 294, [
    "01101000 01100101 01111001",
    "...",
    "wait... translating",
    "So it's really you.",
    "The guy from the billboard.",
    "Snark...",
    "You survived being Protocol X-ed.",
    "Most don't last a week.",
    "Impressive.",
    "See you around, chum."
])

    

    npcsLevel2.append(npc_doc)
    npcsLevel2.append(npc_veso)
    
    npcsLevel3.append(npc_jinx)

    Level1Y = 0
    Level2Y = 17
    Level3Y = 34
    Level4Y = 51
    Level5Y = 68
    Level6Y = 85

    enemiesLevel1 = []
    enemiesLevel1.append(Enemy(19 * tile_size, (12 - Level1Y) * tile_size))
    
   # enemiesLevel1.append(BountyHunter(224 * tile_size, (10 - Level1Y) * tile_size))

    enemiesLevel2 = []
    #enemiesLevel2.append(SmallEnemy(161 * tile_size, (29 - Level2Y) * tile_size))

    enemiesLevel3 = []
    enemiesLevel3.append(Enemy(208 * tile_size, (47 - Level3Y) * tile_size))
    enemiesLevel3.append(StaticEnemy(58 * tile_size, (37 - Level3Y) * tile_size))
    enemiesLevel3.append(StaticEnemy(67 * tile_size, (37 - Level3Y) * tile_size))

    enemiesLevel4 = []
    enemiesLevel4.append(BigEnemy(30 * tile_size, (63 - Level4Y) * tile_size))
    enemiesLevel4.append(BigEnemy(55 * tile_size, (63 - Level4Y) * tile_size))
    enemiesLevel4.append(BigEnemy(100 * tile_size, (63 - Level4Y) * tile_size))
    enemiesLevel4.append(BigEnemy(150 * tile_size, (63 - Level4Y) * tile_size))
    enemiesLevel4.append(BossEnemy(220 * tile_size, (63 - Level4Y) * tile_size))

    enemiesGlobal = []

    playerDamageTriggers = []

    teleportTriggersLevel1 = [
        TeleportTrigger(4 * tile_size, 16 * 2, 2 * tile_size, 3 * tile_size, 5 * tile_size, 26 * 2, 1),
        TeleportTrigger(1400,49, 2 * tile_size, 3 * tile_size,218, 97 , 2) #kanal cijev za grad kraj levela
    ]

    teleportTriggersLevel2 = [
        TeleportTrigger(176 * tile_size, 31 * 2, 4 * tile_size, 4 * tile_size, 6 * tile_size, 38 * 2, 2),
        TeleportTrigger(1 * tile_size, 52 * 2, 3 * tile_size, 2 * tile_size, 8 * tile_size, 5 * tile_size, 0)
    ]

    teleportTriggersLevel3 = [
        TeleportTrigger(1 * tile_size, 34 * 2, 3 * tile_size, 4 * tile_size, 174 * tile_size, 34 * 2, 1),
        TeleportTrigger(1710, 113, tile_size, tile_size, 37, 90, 3),
    ]

    teleportTriggersLevel4 = [
        TeleportTrigger(584, 105, tile_size, tile_size, 38, 105, 5),
        TeleportTrigger(1060, 105, tile_size, tile_size, 25, 60, 4),
        TeleportTrigger(8, 105, tile_size, tile_size, 1645, 105, 2)
    ]

    teleportTriggersLevel5 = [
        TeleportTrigger(14, 65, tile_size, tile_size, 1030, 105, 3)
    ]

    teleportTriggersLevel6 = [
        TeleportTrigger(12, 105, tile_size, tile_size, 566, 105, 3)
    ]

    teleportTriggersGlobal = []

    levels = [
        Level(8 * tile_size, 7 * tile_size, 240, 17, 0, 0, enemiesLevel1, teleportTriggersLevel1, powerupsLevel1, npcsLevel1),
        Level(75 * tile_size, 26 * 2, 180, 17, 0, 17, enemiesLevel2, teleportTriggersLevel2, powerupsLevel2, npcsLevel2),
        Level(1600, 70, 240, 17, 0, 34, enemiesLevel3, teleportTriggersLevel3, powerupsLevel3, npcsLevel3),
        Level(8, 90, 240, 17, 0, 51, enemiesLevel4, teleportTriggersLevel4, [], []),
        Level(8, 90, 240, 17, 0, 68, enemiesLevel3, teleportTriggersLevel5, [], []),
        Level(8, 90, 60, 17, 0, 85, enemiesLevel3, teleportTriggersLevel6, [], [])
    ]

    activeLevelIndex = 1

    activeLevelMapX = 0
    activeLevelMapY = 0

    activeLevelSizeX = 0
    activeLevelSizeY = 0

    activeLevel = levels[activeLevelIndex]

    activeLevel.LoadLevel(activeLevel.startX, activeLevel.startY)
    screenTransition = ScreenTransition()

def update_camera():
    global cam_x, cam_y, cam_maxX, cam_maxY

    cam_x = 0
    cam_y = 0
    
    cam_maxX = (activeLevelSizeX * tile_size) - 240
    cam_maxY = -1

    cam_x = int(player.x -120)
    cam_y = int(player.y)

    if cam_x < 0:
        cam_x = 0
    if cam_y < 0:
        cam_y = 0
    
    if cam_x > cam_maxX:
        cam_x = cam_maxX
    if cam_y > cam_maxY:
        cam_y = cam_maxY

game_setup()
music(3)

# --- MAIN LOOP ---
def TIC():
    cls(0)
    update_camera()
    map(activeLevelMapX, activeLevelMapY, activeLevelSizeX, activeLevelSizeY, -cam_x, -cam_y)
    print("x: " + str(int(player.x)), 2, 2, 12)
    print("y: " + str(int(player.y)), 2, 10, 12)
    collidables = TileCollisions([player, enemiesGlobal], activeLevelIndex, 17)

    player.update(collidables, playerDamageTriggers)
    # ACTIVE WEAPON
    if player.activeWeapon == "gun":
        player.gun = gun
        gun.update()

    elif player.activeWeapon == "katana":
        player.gun = katana
        katana.update()

    for e in enemiesGlobal[:]:
        e.update(collidables, enemyDamageTriggers)

    player.draw()

    if player.activeWeapon == "gun":
        gun.draw()

    elif player.activeWeapon == "katana":
        katana.draw()

    for e in enemiesGlobal:   
        e.draw()

    for npc in npcsGlobal:
        npc.update()
        npc.draw()
    
    for pr in projectiles:
        pr.update(collidables)

    for bp in BossProjectiles[:]:
        bp.update(collidables)
        bp.draw()

    for l in levels:
        l.Update()
        
    screenTransition.update()

    for p in powerupsGlobal:
        p.update()

    for p in powerupsGlobal:
        p.draw()

   # for w in waterDroppers:
       # w.update()
    for npc in npcsGlobal:
        npc.update()
        npc.draw()
    dialogueManager.update()
    dialogueManager.draw()
    # death
    if player.dead:
        rect(0,0,240,136,12)
        rectb(50,32,140,65,8)
        rectb(52,34,136,61,12)
        line(63,48,173,48,8)
        print("GAME OVER",90,57,8)
        line(63,72,173,72,8)
        

        if time() // 500 % 2 == 0:
            print("Press R to restart", 66, 78, 8)

        music()
								
        if keyp(18):
            game_setup()
            music(3)
        return

# <TILES>
# 001:8888888888888888888888888888888888888888888888888888888888888888
# 002:7777777777777777777777777777777777777777777777777777777777777777
# 003:88888888888888888888888888888888888bbbbb888bbbbb888bbbbb888bbb00
# 004:88888888888888888888888888888888bbbbbbbbbbbbbbbbbbbbbbbb00000000
# 005:88888888888888888888888888888888bbbbbbbbbbbbbbbbbbbbbbbb00000000
# 006:88888888888888888888888888888888bbbbb888bbbbb888bbbbb88800bbb888
# 007:6666666666666666666666666666666666666666666666666666666666666666
# 008:666b666666bbb6666bcbbb666bbbbb666bbbbb6666bbb6666666666666666666
# 009:44444444454444b445544bb444555b44444b554444bb45544bb4445444444444
# 011:1111111111111111111111111111111111111111111111111111111111111111
# 012:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# 013:4444444444444444444444444444444444444444444444444444444444444444
# 014:2222222222222222222222222222222222222222222222222222222222222222
# 015:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
# 016:888888888888888888b88b88888bb88888bbbb88888bb88888b88b8888888888
# 017:7777777777777777777777777777777777777777777777777777777777777777
# 019:888bbb0d888bbb0d888bbb0d888bbb0d888bbb0d888bbb0d888bbb0c888bbb0c
# 020:ddddddd9dd2dddd9d222ddd9dd2dddd9ddddddd9ddddddddcccccccccccccccc
# 021:9ddddddd9ddddd2d9dddd22299dddd2d99dddddd99dddddd99cccccc99cccccc
# 022:d0bbb888d0bbb888d0bbb888d0bbb888d0bbb888d0bbb888c0bbb888c0bbb888
# 023:66bfeedd6bbfeeddbbffeeddfffeedddeeeeddddeeeddddddddddddddddddddd
# 024:ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66deeefb66eeeefb66
# 025:6666666666666666cccccccc5555555555555555555555555555555555555555
# 026:6666666666666666cccccccc5555555555555555555555555555555555555555
# 027:dddddddddddddccddddddccddddddddddddddddddddddddddddddddddddddddd
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
# 041:66bfeedd66bfeeed66bfefbe66bffb2b66bfb262662b26666662666666666666
# 042:ddeefb66ddeefb66deeefb66deeffb66fffbfb66bfb2bb662b262b6662666266
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
# 055:000888880c0888880c0888880c0888880c0888880c0888880c0000000c0cccca
# 056:88888888888888888888888888888888888888888888888808888888a0888888
# 060:66bfeeee66bfeeed66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd
# 061:dddddddddddddddddddddeeeddddeeeedddeefffddeeffbbddeefbb6ddeefb66
# 062:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
# 063:cb5fffffcb5fffffcb5fffffcb5fffffcb5fffffcb5fffffcb5fffffcb5fffff
# 064:1133111111331333113313331133133311331331113311111113331111113333
# 065:1111331131113311313133111131331113313311111131111113311113331116
# 066:fffffffffeeeeeeffeeeeeeffeeeeeeffeeddeeffeeddeeffeeddeeffeeddeef
# 067:6666666666666666bbbbbbbbffffffffeeeeeeeeeeeeeeeedddddddddddddddd
# 068:fffffffffeeeeeeefeeeeeeefeeeddddfeeeddddfeeeeeeefeeeeeeeffffffff
# 069:ffffffffeeeeeeefeeeeeeefddddeeefddddeeefeeeeeeefeeeeeeefffffffff
# 070:cc1111cccc1111cccc1111cccc1111cccc1111cccc1111cccc1111cccc1111cc
# 071:0c0cccca0c0aaaaa0c0000000c0ccccc0c0ccccc0c0bbbbb0c0bbbbb0c000000
# 072:aa088888aa08888800000000ccccccccccccccccbbbbbbbbbbbbbbbb00000000
# 073:888888888888888800000000ccccccccccccccccbbbbbbbbbbbbbbbb00000000
# 074:888888888888888800000000ccccccccccccccccbbbbbbbbbbbbbbbb00000000
# 075:88888000888880c0000000c0bbbbb0c0bbbbb0c0bbbbb0c0bbbbb0c0000000c0
# 076:66666666000066660550066600550066600550006600555066605b55666055bb
# 077:66666666666600006660055066005500000550060555006655b50666bb550666
# 078:ccccccccbbbbbbbb55555555ffffffffffffffffffffffffffffffffffffffff
# 079:fffff5bcfffff5bcfffff5bcfffff5bcfffff5bcfffff5bcfffff5bcfffff5bc
# 080:6111333366111333661113336661133366611333666611336666613366666111
# 081:3331111633311166331116663311166631116666311166663116666611666666
# 082:feeddeeffeeddeeffeeddeeffeeddeeffeeeeeeffeeeeeeffeeeeeefffffffff
# 083:ddddddddddddddddeeeeeeeeeeeeeeeeffffffffbbbbbbbb6666666666666666
# 084:66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd66bfeedd
# 085:ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66ddeefb66
# 086:cccccccccccccccccccccccccccccccccccccccccc2222cccc2222cccc2222cc
# 087:0c0ccccc00000000011111110111111100000000809088888090888880008888
# 088:cccccccc00000000111111111111111100000000888888888888888888888888
# 089:cccccccc00000000111111111111111100000000888888888888888888888888
# 090:cccccccc00000000111111111111111100000000888888888888888888888888
# 091:ccccc0c000000000111111101111111000000000888809088888090888880008
# 092:666005556666005b666660556666605b666660556666605b6666605566666055
# 093:5550066655006666b506666655066666b506666655066666b506666655066666
# 094:eeeeeeeeebbbbbbeebccbbbeebbccbbeebbbccbeebbbbcbeebbbbbbeeeeeeeee
# 095:ffffffffffffffffffffffffffffffff5555555555555555dddddddddddddddd
# 096:6666666666666666bbbbbbbbbbbbbbbb00000000000000000000000000000000
# 097:6666666666666666bbbbbbbbbbbbbbbb00000000000000000000000000000000
# 098:6666666666666666bbbbbbbbbbbbbbbb00000000000000000000000000000000
# 099:bbbbbbbbbbbbbbbbbb000000bb000000bb000000bb0000ddbb0000ddbb0000dd
# 100:bbbbbbbbbbbbbbbb000000bb000000bb000000bbdd0000bbddd000bbddd000bb
# 101:ccc5cccccc555cccc5c555ccc55555ccc55555cccc555dcccccccccccccccccc
# 102:eeeeeeeeeffffffeef7777feef7667feef7667feef7777feeffffffeeeeeeeee
# 103:eeeeeeeeeffffffeef7777feef7667feef7667feef7777feeffffffeeeeeeeee
# 104:666666666777777667ffff7667feef7667feef7667ffff766777777666666666
# 105:ccccccccccccccccccddddccccdccdccccdccdccccddddcccccccccccccccccc
# 106:fffffffffeeeeeeffeddddeffedccdeffedccdeffeddddeffeeeeeefffffffff
# 107:dddddddddddddddddd0000dddd0000dddd0000dddd0000dddddddddddddddddd
# 108:dd888888dd888888dd888888dd888888dd888888dd888888dd888888dd888888
# 109:888888888888888888888888dddddddddddddddddddddddd8888888888888888
# 110:88888888888888888888888888888888ccccccccbbbbbbbbbbbbbbbbcccccccc
# 111:cccccccccbbbbbbbcb555555cb5fffffcbff555fcb5fffffbbbbffffcb5fffff
# 115:bb000dddbb000dddbb000dddbb00ddddbb000dddbb000dddbb000dddbb0000dd
# 116:ddd000bbdddd00bbdddd00bbdddd00bbddd000bbddd000bbddd000bbddd000bb
# 117:ccccccccccccccccccccccccccccceeecccccdeecccccdedccccceedccccceed
# 118:cccccccccccccccccccccccceeeecccceeeeccccdddeccccdddeccccdddecccc
# 119:000000000000000000000000000dd000000d6000000dd0000000000000000000
# 120:cccccccccbbbbbbccbccccbccbcbbcbccbcbbcbccbccccbccbbbbbbccccccccc
# 121:88888888888ccccc8cccbbbb8cbbbb5b8cb55bbb8ccbbb5b88ccbbbb888ccccc
# 122:88888888cccccc88bbbbbc885bb5bc88bbbbbc885b5bbc88bbbbcc88cbccc888
# 123:8858888888858888885888888885888888588888888588888858888888858888
# 124:88b88888888b888888b88888888b888888b88888888b888888b88888888b8888
# 125:888888888b8888b888b88888888b888888888888888888888bb88b88888888b8
# 126:4444444444444444444444444444444444444444444444444444444444444444
# 127:ccccccccbbbbbbbc555fbbbbfffffb5cfffffb5cfff555fcfffffb5cfffffb5c
# 128:00000000000000000000000000000000bbbbbbbbbbbbbbbb6666666666666666
# 129:00000000000000000000000000000000bbbbbbbbbbbbbbbb6666666666666666
# 130:00000000000000000000000000000000bbbbbbbbbbbbbbbb6666666666666666
# 131:bb0000ddbb000000bb000000bb000000bb000000bb000000bbbbbbbbbbbbbbbb
# 132:dd0000bbdd0000bb000000bb000000bb000000bb000000bbbbbbbbbbbbbbbbbb
# 133:ccccceeeccccceeeccccceeeccccceeecccccdeecccccdeeccccceeeccccceee
# 134:eeeecccceeeeccccedddcccceeeecccceeeecccceeeecccceeeecccceeeecccc
# 137:8888888588888885888885558888555888855888888588888885558888888888
# 138:ccc8888888888888588888885588888885588888885888888855888888888888
# 139:8858888888858888885888888885888888588888888588888858888888858888
# 140:88b88888888b888888b88888888b888888b88888888b888888b88888888b8888
# 141:8888888885888558885888888885888885888888888888888885888588588888
# 142:5555555555555555555555555555555555555555555555555555555555555555
# 143:6666666666666666666666666666666666666666666666666666666666666666
# 144:88888888888d888888d5d8888d555d88dd555dd8dd5b5dd8dd555dd8ddddddd8
# 145:555555555ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccb
# 146:55555555ccccccccccccccccccccccccccccccccccccccccccccccccbbbbbbbb
# 147:55555555cccccccbcccccccbcccccccbcccccccbccbbbbcccccccccbc5555ccb
# 148:55555555cccccccbccbbbbcccccccccbcccccccbcccccccbcccccccbbbbbbbbb
# 149:5cccccc55ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccb
# 150:8888888888888888888888888888888888888888888888888888888888888888
# 151:8888888888888888888888888888888888888888888888888888888888888888
# 152:bbbbbbbbbbbbbbbbbb000000bb000000bb000000bb0000ddbb000dddbb000ddd
# 153:bbbbbbbbbbbbbbbb00000000000000000ddd0000dddddddddddddddddddddddd
# 154:bbbbbbbbbbbbbbbb000000bb000000bb000000bb000000bbdd0000bbdd0000bb
# 155:888b8888888bb8888888bb8888888bb8888888bb8888888b8888888888888888
# 156:8888888888888888888888888888888888888888b8888888bb8888888bb88888
# 157:88bb8888888bb88d8888bddd8888dddd888ddddd88dddddd8ddddddd8ddddbdd
# 158:8ddd8888dddddd88dddddd88ddbddd88dbbbdd88ddbddd88dddddd88dddddd88
# 159:2222222222222222222222222222222222222222222222222222222222222222
# 160:cccccccbcccccccbcccccccbcccccccbcccccccbcccccccbcccccccbbbbbbbbb
# 161:5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb
# 163:5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb5ccccccb
# 164:5cccbbbc5ccccccbcc555ccb5ccccccb5ccccccb5ccccccb5ccccccb5bbbbbbb
# 165:5ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccb
# 166:8888888888888888888888888888888888888888888888888888888888888888
# 167:8888888888888888888888888888888888888888888888888888888888888888
# 168:bb000dddbb000dddbb000000bb000000bb000000bb000000bbbbbbbbbbbbbbbb
# 169:ddddddddddddddddddddddd0000d00000000000000000000bbbbbbbbbbbbbbbb
# 170:d00000bbd00000bb000000bb000000bb000000bb000000bbbbbbbbbbbbbbbbbb
# 171:8888888888888888888888888888888888888888888888888888888888888888
# 172:88bb8888888bb8888888bb8888888bb8888888bb8888888b8888888888888888
# 173:8dddbbbd8ddddbdd888ddddd888888dd88888888888888888888888888888888
# 174:dddddd88dddddd88dddddd88dddddd88888dd888888888888888888888888888
# 176:55555555cccccccccccccccccccccccccccccccccccccccccccccccccccccccb
# 177:5ccccccb5ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5ccccccc5bbbbbbb
# 178:55555555ccccccccccccccccccccccccccccccccccccccccccccccccbbbbbbbb
# 179:c5555ccbcccccccbcccccccbcccccccbcccccccbccbbbbcccccccccbbbbbbbbb
# 180:5ccccccb5ccccccc5ccccccc5ccccccc5ccccccccc555ccc5ccccccc5ccccccc
# 181:5555555b5ccccccbcc555ccb5ccccccb5ccccccb5ccbbbcc5ccccccb5bbbbbbb
# 182:88888888888888dd888888dd88888ddd88888ddb88888dbb8888dddb8888dddd
# 183:888888bbdd888bbbddd8bb88ddddb888ddddd888bddddd88dddddd88ddddddd8
# 184:888888888888888888888888888888888888888888888888888888888888888b
# 185:888888bb88888bb88888bb88888bb88888bb88888bb88888bb888888b8888888
# 186:3333333333333333333333333333333333333333333333333333333333333333
# 187:6666666666666666667776666666766666667666666676666666777666666666
# 188:6666666666666626667776266666762662667626626676666266777666666666
# 189:ccccccccc2ccccccc2dddd2cc2dccd2cc2dccd2cccdddd2ccccccc2ccccccccc
# 190:fffff5bdfffff5bdffbbbffdfffff5bdfffff5bdfffff5bd555ffffdfffff5bd
# 191:cb5fffffcb5fffffcb5fffffcfbbbbffcb5fffffcb5fffffcbff555fcb5fffff
# 192:880000088055555005555555000000000bbbbbbb80bbbbbb8800000088888888
# 193:80000008055555505555555500000000bbbbbbbbbbbbbbbb00000000880dd088
# 194:80000088055555085555555000000000bbbbbbb0bbbbbb080000008888888888
# 195:66bb000066bb000066bb000066bb000066bb000066bb000066bb000066bb0000
# 196:0000bb660000bb660000bb660000bb660000bb660000bb660000bb660000bb66
# 198:8888dddd8888dddd8888dddd888ddddd888ddddd8888dddd8888888888888888
# 199:ddddddd8dddbddddddbbbddddddbddddddddddd8ddddddd88888888888888888
# 200:888888bb88888bb88888bb88888bb88888bb88888bb88888bb888888b8888888
# 201:8888888888888888888888888888888888888888888888888888888888888888
# 202:fffffffffffffffffffffffffffffffffffffffffffffffff555555fffffffff
# 203:ffffffffffffffffffffffffffbbbbbbffffffffffffffffffffffffffffffff
# 204:cb5fffffcb5fffffcb5fffffcb5fffffcb5fffffcb5fffffcb5fffffcb5fffff
# 205:fffff5bcfffff5bcfffff5bcfffff5bcfffff5bcfffff5bcfffff5bcfffff5bc
# 208:8888888888888888888888808888800088880ddd8880ddd28880002288888882
# 209:80dddd080dddddd0dddddddd00000000dddddddddddddddd2000000288888888
# 210:88888888888888880888888800088888ddd088882ddd08882200088828888888
# 211:66bb00006bbb0000bbbb0000bbb0000000000000000000000000000000000000
# 212:0000bb660000bb660000bb66000bbb66bbbbbb66bbbbb6666666666666666666
# 213:ccbb0000ccbb0000ccbb0000ccbb0000ccbb0000ccbb0000ccbb0000ccbb0000
# 214:0000bbcc0000bbcc0000bbcc0000bbcc0000bbcc0000bbcc0000bbcc0000bbcc
# </TILES>

# <SPRITES>
# 000:0000000500000f570000f33300003333000033ff00003333000033330000fccc
# 001:70500000f57f0000333f0000333300003ff300003333000033330000fccf0000
# 004:0000000000000ddd0000dd5d0000ddd50000dddd0000dddd0000dddd00000ddd
# 005:00000000ddd00000dddd0000dddd00005ddd0000d5dd0000dddd0000dd000000
# 006:0000000000000999000099990000999900009992000099290000999900000099
# 007:0000000099900000929900002999000099990000999900009999000099900000
# 008:0000000000000000003330000033330000333000000000000000000000000000
# 009:0000000000000000000333000033330000033300000000000000000000000000
# 010:000000000000000000eeeee000eeeee000ee0e0000eee00000ee000000000000
# 011:0000000000000888000088880000888800008885000088580000888800000088
# 012:0000000088800000858800005888000088880000888800008888000088800000
# 013:000000000000099900009999000099990000999b000099b90000999900000099
# 014:00000000999000009b990000b999000099990000999900009999000099900000
# 016:0000fccc0000fccc0000fccc0000fccc0000ffff0000ff000000ff000000fff0
# 017:fccff000fccff000fccff000fccff000ffff300000ff000000ff000000fff000
# 020:0000dddd0000dd5d0000dddd0000dd5d0000dddd0000dd000000dd000000ddd0
# 021:ddd00000d5ddd000dddd5000d5ddd000ddddd00000dd000000dd000000ddd000
# 022:0000099900099929000299990009992900099999000099000000990000099900
# 023:9999000092990000999900009299000099990000009900000099000009990000
# 024:666666666666666666eeeee666eeeee666ee6e6666eee66666ee666666666666
# 025:6636666663336666663eeee666eeeee666ee6e6666eee66666ee666666666666
# 026:6636666663336666663eeee666eeeee666ee6e6666eee63666ee633366666636
# 027:0000088800088858000588880008885800088888000088000000880000088800
# 028:8888000085880000888800008588000088880000008800000088000008880000
# 029:00000999000999b9000b9999000999b900099999000099000000990000099900
# 030:999900009b990000999900009b99000099990000009900000099000009990000
# 032:00000000000003330000d3330000d3330000330300003333000033330000ccbb
# 033:0000000033300000333d0000333d0000303300003333000033330000bbcc0000
# 034:0000000000000000000006660000665600006657000666770066667700000003
# 035:0000000000000000666600006222000077270000772700007777000033300000
# 036:aaaaa000aaaa0033aaa03333aaa0f663aaaa3333aaaa0000aaaa0004aaaaaa00
# 037:000aaaaa3330aaaa33330aaa35330aaa3333aaaa0000aaaa4000aaaa000aaaaa
# 038:000099990009955900093933000935b300093933000033330000333500000033
# 039:5990000095999000339999003b39590033395900333959005339590033395900
# 040:000005550005556600055333000533f300003333000033330000333f00000333
# 041:6660000055660000333660003f3360003333000033330000f333000033300000
# 042:000000000000000000000fff0000f3330000f3f3000003330000033f00000033
# 043:0000000000000000ffff0000333ff0003533000032330000f333000033300000
# 048:000cc2bb000cccbb000cccbb000cccbb0003cfff0000cf000000ff00000fff00
# 049:bbcc0000bbcc0000bbcc0000bbcc0000fff3000000fc000000ff00000fff0000
# 050:0000e272000ee777000ee7770000e7770000007700000ff000000ff000000fff
# 051:77227000227770007777700077777000777000000ff000000ff000000fff0000
# 052:aaaa8009aaa30009aaa22009aaa32009aaa33009aaaaa880aaaaa88aaaaa000a
# 053:9003aaaa9002aaaa9002aaaa9003aaaa9003aaaa0000aaaaaa00aaaaa000aaaa
# 054:00000fea000fffea000fffea00044fea000ddfea0000099900000f900000fff0
# 055:aeff5900aeff9900aeff9900aef40900aefd09009999090000f900000fff0000
# 056:0000fff3000ffffd000eeff600033ffd00033ffd00000eee00000fd00000fff0
# 057:3fff0000dffff000dffff0006ff33000dff33000eeee000000fd00000fff0000
# 058:000002220000f2220000f2220000f22200004222000000aa000000aa000000ff
# 059:f2220000f2c2f000f222f000f222f000f22230009aa000009aa000009ff00000
# 060:0000002e0000023d000023d000023d000023d00000fd00000f000000f0000000
# 061:000000000000a8b00099a8b0589fa8b05899a8b00099a8b00000a8b000000000
# 064:0000000c000000cc00000ccb0000ccbb000ccbb200ccbb220ccbbb220cbbbbb2
# 065:c0000000cc000000bcc00000bbcc00002bbcc00022bbcc0022bbbcc02bbbbbc0
# 067:0000000000000ccc0000cccc0000ccff0000cccc0000cccc0000cccc00000ccc
# 068:00000000ccc00000cccc0000fffc0000fccc0000fccc0000cccc0000cc000000
# 069:88cccc88888cc88888cccc888cc88cc88c4444c88c4444c88cc44cc888cccc88
# 070:83cccc88333cc88883cccc888cc88cc88c4444c88c4444c88cc44cc888cccc88
# 071:83cccc88333cc88883cccc888cc88cc88c4444c88c4444388cc4433388cccc38
# 072:666bb66666bbbb666bb66bb6bb6666bb666bb66666bbbb666bb66bb6bb6666bb
# 073:636bb666333bbb6663b66bb6bb6666bb666bb66666bbbb666bb66bb6bb6666bb
# 074:636bb666333bbb6663b66bb6bb6666bb666bb66666bbbb366bb66333bb66663b
# 075:a888a888aa88aa888aa88aa888aa88aa88aa88aa8aa88aa8aa88aa88a888a888
# 076:a388a8883338aa8883a88aa888aa88aa88aa88aa8aa88aa8aa88aa88a888a888
# 077:a388a8883338aa8883a88aa888aa88aa88aa88aa8aa88a38aa88a333a888a838
# 080:0cbbbbbb0cbbbbcc0cccccc000c0000000000000000000000000000000000000
# 081:bbbbbbc0ccbbbbc00cccccc000000c0000000000000000000000000000000000
# 083:0000dcfc0000dccf0000dcfc0000dccf0000dcfc0000ff000000cc000000ccc0
# 084:ccf00000cfcdd000ccfdd000cfcff000ccfdd00000ff000000cc000000ccc000
# 085:8838889e833389bd88389bd88889bd88889bd88888fd88888f888888f8888888
# 086:8838889e833389bd88389bd88889bd88889bd88888fd83888f883338f8888388
# 087:8888889e888889bd88889bd88889bd88889bd88888fd88888f888888f8888888
# 088:0000009e000009bd00009bd00009bd00009bd00000fd00000f000000f0000000
# 089:f00000000f00000000f9000000db9000000db9000000db9000000db9000000de
# 090:0d0000000dd0000000dd000000dd000000dd00000ddd0000ddd00000dd000000
# 096:8777777787ccccc787cc2cc787c222c787cc2cc787ccccc78777777788888888
# 097:873777778333ccc7873c2cc787c222c787cc2cc787ccccc78777777788888888
# 098:873777778333ccc7873c2cc787c222c787cc2c3787ccc3338777773788888888
# 099:0000000000000000333000003033333033300300000000000000000000000000
# 102:0000000000cccccc00cccccccccccccccccccfffcccccfffcccccccccccccccc
# 103:00000000ccccccc0ccccccc0ccccccccffffffccffffffccfffcccccfffccccc
# 104:000000000000000000000000c0000000c0000000c0000000c0000000c0000000
# 118:cccccccccccccccccccccccc00cccccc0000cccc0000ccccddcccffcddcccffc
# 119:fffcccccfffcccccfffcccccccccccc0ccccc000ccccc000cccccff0cccccff0
# 120:c0000000c0000000c00000000000000000000000000000000000000000000000
# 134:ddcccccfddcccccfddcccffcddcccffcddcccccfddcccccfddcccffcddcccffc
# 135:fccffccdfccffccdcccccffdcccccffdfccffccffccffccfcccccffdcccccffd
# 136:ddd00000ddd00000ddd00000ddd00000fff00000fff00000ddd00000ddd00000
# 150:ffff0000ffff0000cccc0000cccc0000cccccc00cccccc00cccccc0000000000
# 151:00000fff00000fff00000ccc00000ccc00000ccc00000ccc00000ccc00000000
# 152:f0000000f0000000c0000000c0000000ccc00000ccc00000ccc0000000000000
# </SPRITES>

# <MAP>
# 000:12121212121212121212121212121212121212124555121212124555121212121212121212455512121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121245551212455512124555121245551212121212121212455512121212455512121212124555121212121245551212121212121212121212121212121212121212121212121212121212121212123c174c86868686868686868686868686868686868686868686868686868686868686868686868686868686868686868686868686868686868686868686
# 001:12121212121212121212121212121212121212124555121212124555121212121212121212455512121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121245551212455512124555121245551212121212121212455512121212455512121212124555121212121245551212121212121212121212121212121212121212121212121212121212121212123c174c76767676767676bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb767676
# 002:12707070707070707070707070707070707070704555701212704555707070121212121212455512121212121212121270707070707070707070707070707070707070707070707012121212121212121212121212121212121212121212121212121212121245551212455512124555121245551212121212121212455512121212455512121212124555121212121245551212121212121212121212121212121212121212121212121212121212121212123c174c76767676767676bbbbbbbbbbbbf9f9f9f9bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb767676
# 003:12707070707070707070707070707070707070704555701212704555707070707012121212455512121212121212707070707070707070707070707070707070707070707070707070121212121212121212121212121212121212121212121212121212121245551212455512124555121245551212121212121212455570707070455570707070704555707070707045557070707070707070707070707070707070707070707070707070707070707012123c174c76767676767676bbcbbbbbbbf9bbbbbbbbf9bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbcbcbbbbbbbcbcbbbbbbbbbbbbbbbbbbbbb767676
# 004:06160616364670707070707070707070707070704555704454704555707070707070701212455512707070707070707070707070707070707070707070707070707070707070707070701212121212121212121212121212121212121212121212121212121245551212455512124555121245551212121212121270455570707070455570707070704555707070707045557070707070707070707070707070707070707070707070707070707070707012123c174c76767676767676bbbbbbbbf9bb12121212f9f9bbbbbbbbbbbbcbcbbbcbcbcbbbcbcbbbcbcbbbcbbbcbbbcbbbbbcbbbcbbbbbcbbbbbbbbb767676
# 005:07170717374770707070707070707070707070704555707070704555707070707070707070455570707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707012121212121212121212121245551212455512124555121245551212121212127070455570707070455570707070704555707070707045557070707070707070707070707070707070707070707070707070707070364626163d174c76767676767676bbbbbbf9bbd0121212f9d0bbf9bbbbbbbbbbcbbbbbcbbbcbbbcbbbbbcbbbbbcbbbcbbbcbbbbbcbbbcbcbcbcbbbbbbbbb767676
# 006:081808183848707070707070707070707070707092a27070707092a27070707070707070704454707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070701212121212121212121212455512124555121245551212455512121212127070704555707070704555707070707045557070707070455570707070707070707070707070707070707070707070707070707070703747271727004c76767676767676bbbbbbf9bb12d012f9d012bbf9bbbbbbbbbbcbcbbbcbcbcbbbcbcbbbcbcbbbcbbbcbbbcbbbbbcbbbcbbbbbcbbbbbbbbb767676
# 007:127070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070702434343434343434343434343434022270707070707070707070707070707070707070707070701212121212121212121212455512124555121245551212455512121212707070704454707070704454707070707044547070707070445470707070707070707070707070707070707070707070707070707070703848281828184d70707070707070bbbbbbf9bb1212f9d01212bbf9bbbbbbbbbbcbbbbbcbcbbbbbcbbbbbcbbbbbcbbbcbbbcbbbbbcbbbcbbbbbcbbbbbbbbb767676
# 008:127070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707012122535353535353535353535353535032370707070707070707070707070707070707070707070707012127070121212121212455512124555121245551212455512127070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070121212121212121212707070707070707070bbbbbbbbf9bbf9121212bbf9bbbbbbbbbbbbcbbbbbcbbbcbbbcbcbbbcbcbbbcbcbbbbbbbcbcbbbbbcbbbbbcbcbbbbbbb767676
# 009:243434343434343434022270707070707070707070707070707070707070707070707070707070707070704454707070707070707070707070707070707070707070455570707070707070707070707070707070707070707070707070707070707070701212455512124555121245551212455512707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070701212707070707070707070707070707070707070707070bbbbcbbbf9f9bb1212bbf9bbbbbbbbbbbbbbbbcbbbbbbbbbbbbbbbbbbbcbbbbbcbbbbbbbbbcbbbbbbbcbbbbbcbbbcbbb767676
# 010:253535353535353535032370707070707070707012121212121212127070707070707070707070707070704555707070707070707070707070707070707070707070455570701212121270707070707070707070707070707070707070707070707070707012455512124555121245551212455512707070707070707070707070707070707070707070707070707070707070707070707070707070707070707012127070707070707070707070707070707070707070707070707070bbbbbbbbbbbbf9f9f9f9bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbcbbbbbbbbbcbbbbbbbbbbbbbbbbbbbbb767676
# 011:12121212121212121245557070707070707070707070707070707070707070707070707070445470707070455570707070707070707070707070707070707070707045557070707070707070707070707070707070707070707070707070707070707070707092a2707092a2707092a2707092a270707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070bbbbbbbbbbbbcbbbbbbbbbcbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb767676
# 012:121212121212121212455570707070707070707070707070707070707070707070701212124555707070704555707070707070707070707070707070707070707070455570707070707070701212121270707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070701212707070707070707070707070707070707070707070707070707070707070bbbbbbbbbbbbcbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb767676
# 013:121212121212121212455570707070707070707070707070707070707070707070121212124555919191914555707070a6a6a670707070a670707070a6a6a6a6a6a645557070707070707070707070707070707070707070707012121291919112121270707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070701212121212a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 014:121212121212121212455512121212121212121212121212121212121212121212121212124555e8e8e8e84555707070a6a6a670707070a670707070a6a6a6a6a67045557070707070707070707070707070707070707070701212e8e8e8e8e8e8e81212707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707012121212121212e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 015:121212121212121212445412121212121212121212121212121212121212121212121212124555e8e8e8e8455591a191a6a6a691a191a1a6a191a191a191a191a191455570707070707070707070707070707070707070701212e8e8e8e8e8e8e8e8e81212243434343434343434343434343434247070707012a1919191a191a1919191a191a191a191919191919191919191a6a6a6a6a6a612121212121212e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 016:121212121212121212121212121212121212121212121212121212121212121212121212124555e8e8e8e84555e8e8e8a6a6a6e8e8e8e8a6e8e8e8e8e8e8e8e8e8e84555121212121212121212121212121212121212121212121212121212121212121212253535353535353535353535353535251212121212e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8a6a6a6a6a6a612121212121212e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 017:878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787f0f0f0f0f0f0f0f087878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 018:878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787f0f0f0f9f9f0f0f087878787878787878787878787871929292929292929292929292929292929292929292929398787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 019:87d7b71010b71010b71010b71010b71010b710d7b71010b71010b71087878787101010b9c9101010108787878787878787878710101010108b9b87878787b710b710b710b710b710f0f0f0f9f9f0f0f010b7b7b7b7b7b7b78787878787871a8b9bb710b710b7108b9b10b710b7b9c9b710b7b78b9b3a8787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 020:8710b81010b81010b81010b81010b81010b81010b81010b81010b81087878787101010bacac910d710d7878787878787878710101010108b9b9c87878787b810b810b810b810b810f0f9f9f9f9f9f9f010b8b8b8b8b8b8b88787878787871a8c9cb710b710b7108c9c10b710b7bacab710b7108c9c3a87871010101010101010101010101010101010101010101010101010101010101010b7101010b71010c71010c71010c71010b71087878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 021:8710b710d7b71010b7d71010d8101010d7101010b71010b71010b710878787871010101010cac91010101087878787878710d71010108b9b9c1087878787b710b710b710b710b710f0f9f9f9f9f9f9f010b7b7b7b7b7b7b787878787c7c71ab9c910108b9b10b9c9c7108b9b1010c78b9bb7b9c9b73a10c71929294910192929293910192929391019292929391019292929391010101010b8101010b81010c81010c81010c81010b81087878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 022:8710b81010b71010b81010101010101010101010b81010b71010b8108787878797a797a710bad9e9101010108787878710101010106b7b9c10108787878710101010101010101010f0f0f0f9f9f0f0f0101010101010101087878787c7c71abaca10b78c9c10bacac7108c9c10b7c78c9c10bacab73a10c71a101010101a1010103a101a10103a101a1010103a101a1010103a1010101010b71010d8b710d7c71010c7d710c71010b71010108787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 023:8710b71010b710101010101010d7101010101010101010b81010b7108787878798a898a81010daea10d8101097a797a7d710d7d8106c7c1010108787878710101010101010101010f0f0f0f9f9f0f0f0101010101010101087878787c8c81a10c810b7c81010c810c810c810c8b7c810c810c8b7b73a10c81a101010104b0b2b2b3b101a10103a104b0b29293b104b0b29293b1010101010b8101010b81010c8d810c81010c810d8b81010101010878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 024:8710b81010b810101010101010878787871010101010d8101010b7108787878787878787871010101010101098a898a8101010101010101010108787878710101010101010101010f0f0f0f0f0f0f0f010101010101010108787878710101b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b3b101059294910105a0a101010101a10103a105a0a101010105a0a1010101010101010b7101010b7d710c71010c71010c71010b7d810101010101030405060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 025:8710b710101010101010d7878787878787878710d71010101010b810871010871010101010d710d71010101087878787101010101010d710101087101087101010101010101010101010101010101010101010101010101087101087101010101010101010101010101010101010101010d81010101010101a101010101a105b1010101a10103a101a105b1010101a105b10101010101010b8101010b81010c8d810c8d710c81010b81010d810d8101031415161000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 026:87d7b81010101010108787878787878787878787871010d7101010101010101010d810101010101010101010d710101010d7101010101010d710101010101010101010101010101010738310101010101010101010101010101010101010d8101010101010101010101010101010101010101010101010101a101010101a10105b10101a10103a101a10105b10101a10105b101010101010101010d710d710101010101010101010101010101010101032425262000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 027:871010101010d7878787878787878787878787878787871010101010d7101010101010101010d80c1c2c10101010101010100c1c2c10101010101010101010101010101097a7101010748494a4b410101097a7101010101010101010101010101010100c1c2c1010d8100c1c2c101010100c1c2c101010101b2b2b49104a1010105b101b2b2b3b104a1010105b104a1010105b101010101010101010101010101010101010101010101010101010d81033435363000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 028:8710101010108787878787878787878787878787878787878710101010101010d71010101010100d1d2d10101010101010100d1d2d10101010101010101010101010101098a8101010758595a5b510101098a8101010101010101010101010101010100d1d2d101010100d1d2d101010100d1d2d1010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010d810101010101010101087878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 029:87101010108787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878710101097a710101097a710101097a710101097a710101087878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 030:878999a9878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878710101098a810101098a810101098a810101098a810878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 031:878a9aaa8787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 032:875d006d8787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 033:875d006d8787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787878787000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 034:1001101010101010101010101010101010101001101010101010101010101010101010101010101010101010100110101010101010101010100110101010101010101010101010101010101010101010101010101010101010100110101010101010101010101010101010101010101010101010101010101010101010100110101010101001011010101010101010101010101010100110101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010f3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3
# 035:10101010100110101010101010101010101010101010101010101010101001101010100110101010011010101010101010100110101010101010100110101010101001101001101010101010101010101010101010100110101010101010010110101010e4e4e4e4e4e4e4e4e4e4101010101010101010101010101010101010101010101010101010101010100110101010101010101010101001101001011010101010100110101010101010101010011010011010101010101010101010101010101010101010101010101010101010101010101010fbe3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3
# 036:e2e210101010101010101010101001101010101010101001101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101001101010101010f310f9f9e0e0e0e0e0e010f41010101010101001101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010100110101010101010101010101010f3e5e5bce3e3f2f2f2f2f2f2e3f2f2f2f2f2e3e3e3e3e3e3e3
# 037:e2e2d1101010101001101010101010101010011010101010101010011010101001101010101010101010101010101010101010101010101010101010101010101010101010101010101010011010101010011010101001101010101001101010101010f3f9f970f8e870f8e8f9e0f41010101010101010121212121212121212121212121212121212121212121212121212121010011010101010101212121212121212121212121212121212121212121010101010101010101010101010101010101010101010100110101010101010011010101010f3e5e5e3ace3f2f2f2f2f2f2e3f2f2e3acf2f2e3e3e3e3e3e3
# 038:e2f210101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101001101010fbf90000e80000e8f9abe0f4101010011010101012e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e31210101010101010101012e3e3e3e3e3e3e3acbce3e3e3e3e3e3e3e3e3e3121010101010101010011010101010101010011010101010101010101010101010101010101001f3e5e5e3e3e3f2f2e3e3f2f2e3f2f2bce3f2f2e3e3e3e3e3e3
# 039:e2f210011010101010101010011010101010101010101010011010101010101010101010101010101010101010101010101010101010f6e4e4e4e4e4e4f7101001f6e4e4e4e4e4f7101010101010101010101010011010101010101001101010101010f3f9abababababf9ababe0eb101010101010101012e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e31210101010101010101012e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3121010101010101010101010101010101010101010101010101010100110101010101010101010fbe5e5e3e3e3f2f2bcacf2f2e3f2f2bcacf2f2e3e3e3e3e3e3
# 040:e2e210101009101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010100110f3e3e3e3e3e3e3f4101010f3e3e3e3e3e3f4101010101009101010101010101010100110101010101010101010f3f9ababababf9abababe0f4101010101010121212e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2acbcf2f2e3e3f2f2e3e31210101010101010101012e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3121010011010101010101010101010101010101010101010101010101010101010101010101010fbe5e5e3bcacf2f2e3e3f2f2e3f2f2e3e3f2f2e3e3e3e3e3e3
# 041:e2e2e2e2e2e2e21010101010101010101010101010101010101010101010101010101010101010f6e4e4e4e4e4e4e4f7101010101010f3e3e5e3e3e5e3f4011010f3e3e5e3e5e3f4101010e1e1e1e1e110101010101010101010100101101010101010f3f9ab00f1f900f1ababe0f4101010101010101012e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e31209090909090909090912e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3121010101010101010101010101010101010101010101010101010101010101010101010101010f3e5e5e3e3e3f2f2f2f2f2f2e3f2f2e3e3f2f2e3e3e3e3e3e3
# 042:e23040506010101010101010101010101010101010101010101010101010100909101010101010f3e3e3e3e3e3e3e3f4d6d610101010fbe3e5e3e3e5e3f4101010f3e3e5e3e5e3eb101010101010101010101010100101101010101010101010101010ebf9ababf9abababababe0f4101010101010101012e3e3ace3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e31209090909090909090912e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3121010101010101010101010101010011010101010011010101010101001101010101010101010f3e5e5bcace3f2f2f2f2f2f2e3f2f2f2f2f2e3e3e3e3e3e3e3
# 043:e231415161101010101010101010101010101010101010101010101010e1e1e1e1e1e1e1101010f3e3e5e5e3e5e5e3eb101010101010f3e3e3e3e3e3e3f4101010f3e3e5e3e5e3f4100110101010011010101010101010101010101010101010101010f3f9abf9ababababababe0fb101010100110101012e3e3e3bce3e3e3e3e3e3e3e3acbce3e3e3e3e3e3e3e3bcace3e31209090909090909090912e3e3e3e3e3e3e3e3e3e3e3bcace3e3e3e3e3e3121010101010101010101010101010101010101010101010101010101010101010101010101010f3e5e5e3e3e3f2f2bcacf2f2e3f2f2e3e3f2f2e3e3e3e3e3e3
# 044:e23242526210101010101010090910101010101010101010101010101010100110101010101010f3e3e3e3e3e3e3e3f4101010101010f3e3e3e3e3e3e3eb100110f3e3e3e3e3e3f4101010101010101010090910101010101010101010101010101010fbf9e0ababababababe0e0f4e3e310101010101012e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e31209090909090909090912e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3121010101010101010101010101010101010101010101010101010101010101010101010101010fbe5e5e3e3e3f2f2e3e3f2f2e3f2f2e3bcf2f2e3e3e3e3e3e3
# 045:e2334353631010101010e1e1e1e1e1e11010101010090910101010101010101010100110101010fbe3e3e3e3e3e3e3f4d6d610101010fbe3e5e3e3e5e3f4101010fbe3e3e3e3e3f4101010011010101010e1e1e1e1e1e1101010101010101010101010f310f9e0e0e0e0e0e0e010f4101010101010101012e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e31209090909090909090912e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3121010101010101010100110101010101010101010101010101010101010101010100110011010f3e5e5e3e3e3f2f2ace3f2f2e3f2f2ace3f2f2e3e3e3e3e3e3
# 046:e2e2e2e2e2e2e2101010101010101010101010e1e1e1e1e1e1e110101010101010101010101010f3e3e5e5e3e5e5e3eb101010101010f3e3e5e3e3e5e3f4101010f3e3e5e3e5e3eb10101010101010101010100110101010101010101010101010101010e4e4e4e4e4e4e4e4e4e410101010101010101212e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e3f2f2e3e31209090909090909090912e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3f2f2e3121010101010101010101010101010101010101010101010101010101010101010101010101010fbe5e5e3e3e3f2f2e3bcf2f2e3f2f2e3e3f2f2e3e3e3e3e3e3
# 047:e2f210101010101010101010100110101010101010101010101010101010101010101010101010f3e3e3e3e3e3e3e3f4100110101010f3e3e5e3e3e5e3eb101010f3e3e5e3e5e3f41010101010101010101010101010101010101010101010101010101010101010ccdc1010101010101010101010101012e3e3e3e3e3bcace3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e31209090909090909090912e3e3acbce3e3e3e3e3e3e3e3e3e3e3e3e3e3e31210101010101010101010101010101010101010101010101010101010101010101010101010f4e3e5e5e5e5e3f2f2e3e3f2f2e3f2f2e3e3f2f2e3e3e3e3e3e3
# 048:e2f210101001101010101010101010101010101010100110101012445412121010101010101010f3e3e3e3e3e3e3e3f4101010101010f3e3e3e3e3e3e3f4101010fbe3e3e3e3e3f41010101010101010101010101010101010101010101010101010101010101010ccdc1010101010101010101010101012e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3ace3e3e3e3e3e3e3e3e31209090909090909090912e3e3e3e3ace3e3e3e3e3e3e3e3bcace3e3e3e312101010101010101010101010101010101010e1e1e1e1e1e110101010101010101010101010f4e3e5e5e5e5e3f2f2acbcf2f2e3f2f2f2f2f2e3e3e3e3e3e3e3
# 049:e2e210101010100909090910101010090909090910101010101212455512121210101010101010f3e3e3e3e3e3e3e3f4101009090910fbe3e3e3e3e3e3f4090909f3e3e3e3e3e3f40909090909090909090909090909090909090909090909091010101010101010ccdc1010101010101010100910101012e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3bce3e3e3e3e3e3e3e3e3e31209090909090909090912e3e3e3e3e3bce3e3e3e3e3e3e3e3e3e3e3e3e31209090909090909090909090909090909090910101010101010101010101010101010101010f4e3e3e3bcace3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3
# 050:121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212
# 051:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a67676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 052:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a67676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 053:9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696b19696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696b19696969696969696969696969696969696969696969696b1969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 054:969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696b1b1969696b19696969696969696969696969696969696b1b1969696969696969696969696b1b19696969696969696969696969696969696969696b196969696969696969696969696969696b1b19696969696b1969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 055:96969696969696969696969696969696969696969696969696969696969696969696969696961929292929292929292929292949b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b11929292929292929292929292949b19696969696969696969696969696969696969696b196969696969696969696969696969696b119292929292929292929292929499696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 056:96969696969696969696969696969696969696969696969696969696969696969696969696961a5a000000000000000000005a3ab1969696969696969696969696969696969696969696b11a5a000000000000000000005a3ab1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b11a5a000000000000000000005a3a9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 057:96969696969696969696969696969696969696969696969696969696969696969696969696961a5a000000000000000000005a3a96969696969696969696969696969696969696969696961a5a000000000000000000005a3ab196969696969696969696969696969696969696969696969696969696969696969696969696b11a5a000000000000000000005a3a9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 058:96969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a96969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 059:96969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a1a5a5a5a3a96969696969696969696969696969696969696969696961a5a5a5a5a5a00005a1a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a1a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 060:96969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a96969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 061:96969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a96969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696961a5a5a5a5a5a00005a5a5a5a5a3a9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 062:96969696969696969696969696969696969696969696969696969696969696969696969696961b2b2b2b2b2b2b2b2b2b2b2b2b3b96969696969696969696969696969696969696969696961b2b2b2b2b2b2b2b2b2b2b2b2b3b9696969696969696969696969696969696969696969696969696969696969696969696969696961b2b2b2b2b2b2b2b2b2b2b2b2b3b9696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696967676768686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 063:969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696968686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 064:965767969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696965767969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969657679696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696968686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 065:965868969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696965868969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969658689696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696968686868686868686868686868686868686868686868686868686868686868686868686868686868686868686867676
# 066:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a67676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 067:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a67676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676
# 068:000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000760000
# 069:00a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 070:00a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 071:00969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 072:00969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a68686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 073:00969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a68686868686868686868686860000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 074:00969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a68686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 075:00969696969696969696969696969696969696969696969696969696969696a6969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696a6a6969696969696969696969696969696969696969696969696969696969696965767a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a68686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 076:005767969696969696969696969696969696969696969696969696969696a6a696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696a6969696e0e0e0969696969696969696969696969696969696969696969696969696969696965868a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a68686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 077:0058689696969696969696969696969696969696969696969696969696a6a6a69696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696e0e0e0e0e0e096969696a69696969696a69696969696a6969696969696969696969696a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a68686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 078:00a6a6a6a69696969696969696969696969696969696969696969696a6a6a6a6969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696969696e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0e0e0a6e0e0e0e0e0a6969696969696969696969696969696968686868686868686868686868686868686868686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 079:009696969696969696969696969696969696969696969696969696a6a6a6a6a6969696969696969696a6a6a6a6a6a69696969696969696969696969696969696969696969696969696969696a6969696e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0e0e0a6e0e0e0e0e0a6969696969696969696969696969696968686868686868686868686868686868686868686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 080:00969696969696a6a6a6a6969696969696969696969696969696a6a6a6a6a6a6e0e0e0e0e0e0e0e0e0a6a6a6a6a6a696969696969696969696969696969696969696969696969696969696969696e0e0e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0e0e0a6e0e0e0e0e0a6969696a696969696a696969696969696868686868686868686868686868686868686868686868686868686a6a6a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 081:00e0e0e0e0e0e0e0e0e0e0e0e0e0a6969696a6969696a6a6a6a6a6a6a6a6a6a6e0e0e0e0e0e0e0e0a6a6a6a6a6a6a6a696969696969696969696a696969696969696969696969696969696e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0e0e0a6e0e0e0e0e0a6969696a696969696a6969696969696968686868686868686868686868686868686868686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 082:00e0e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0a6e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0a6a6a6a6a6a6a6a6a6a69696969696969696969696969696969696969696969696a69696e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0e0e0a6e0e0e0e0e0a6969696a696969696a6969696969696968686868686868686868686868686868686868686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 083:00e0e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0a6e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0a6a6a6a6a6a6a6a6a6a6a6a6e0e0e0e0e0e0a6e0e0e0e0e0e0e0e0a6a6a6e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0a6e0e0e0e0e0a6e0e0e0e0e0a6e0e0e0a6e0e0e0e0a6969696969696968686868686868686868686868686868686868686868686868686868686a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 084:00a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 085:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 086:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 087:969696969696969696969696969696969696969696969696969696969696a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 088:969696963a2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b3a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 089:969696963af0f0f000000000005a000000000000005a00000000f03a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 090:969696963af0f0f000000000005a000000000000005a00000000f03a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 091:969696963af0f0f0f0f0f0f0f05af000000000f0f05af0f0f0f03a3a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 092:969696963a2b2b2b2b2b2b2b2b5a2b2b2b2b2b2b2b5a2b2b2b2b2b3a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 093:969696963af0f0f0f0f0f0f0f05af000000000f0f05af0f0f0f0f03a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 094:969696963af0f0f0f0f0f0f0f05af000000000f0f05af0f0f0f0f03a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 095:969696963af0f0f0f0f0f0f0f05af000000000f0f05af0f0f0f0f03a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 096:969696963a2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b3a5a96a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 097:969696969696969696969696969696969696969696969696969696969696a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 098:965767969696969696969696969696969696969696969696969696969696a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 099:965868969696969696969696969696969696969696969696969664969696a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 100:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 101:a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a6
# 134:000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 135:000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </MAP>

# <WAVES>
# 000:00000000ffffffff00000000ffffffff
# 001:0123456789abcdeffedcba9876543210
# 002:0123456789abcdef0123456789abcdef
# 003:66666655555555544443332222111000
# 004:000000888888444444cccccccc777777
# 005:bbbbb98776679aaa9644566666533333
# 006:111111111222233344577789aabccdee
# 007:00000000ffffffff00000000ffffffff
# 008:5678abbcccccccb98755555555667789
# 009:9abcdeffffedcba98765432222234567
# 010:468accddc85332223579bbccccca7655
# 011:7a37a77b988169d2c62b77f726660a9b
# 012:12452012355312345562112335431123
# 013:689abbccdddcba986543332222223345
# </WAVES>

# <SFX>
# 000:922d922d920d927f927f923fa2b492949281925da23da23da21da21da26fb26fb26fb24fb24fb2b3b2a3c2b3c291c281c200c200c200c200c200c200249009009f9f
# 001:923d923d921d926f926f924f92b492b49281926392639263924092409240924092409240924092409240924092409240924092409240924092409240441009000909
# 016:661066206630666066606600660066006600660066006600660066006600660066006600660066006600660066006600660066006600660066006600401000000000
# 017:0bf00bf00bf00bf01be02bd03bc05bb06ba07b808b70ab50cb40eb20fb004ba04b905b907b708b70ab50cb40eb20fb009b00ab40bb30cb20eb10fb001a1000000000
# 018:030003000300030003000300030003000300030003000300030003000300030003000300030003000300030003000300030003000300030003000300307000000000
# 021:0bf00bf00bf01be02be03bd04bc05ba07b809b50cb30fb000bf00be01be01bc02bb04b906b808b60cb40fb100bf00be01bd01bb03ba05b808b60cb30322000000000
# 022:0d000d000d100d200d300d500d500d700d900daf0dcf0ddf0dff0d000d000d000d000d000d000d000d000d000d000d000d000d000d000d000d000d00336000000000
# 032:1800181038303840585068606880789088a0a8b0a8c0b8d0c8e0e8f0f8f0f800080008000800080008000800080008000800080008000800080008004270000f0f03
# 052:9d1e9d3f9d4f9d509d529d529d529d429d319d309d2f9d1e9d0e9d0e9d0e9d0e9d109d209d219d329d329d529d529d519d509d409d409d3f9d2e9d1e405000000000
# 053:0c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c000c00000000000000
# 054:d803d813d812d821d82fd83ed84ed85ed85ed86fd860d870d882d883d894d8a4d8a4d8a4d8b4d8b3d8c2d8c1d8d0d8dfd8dfd8eed8eed8ffd8f0d8f24d7000000000
# 055:880088008800880088008800880088008800880088008800880088008800880088008800880088008800880088008800880088008800880088008800304000000000
# 056:6a006a006a006a006a006a006a006a006a006a006a006a006a007a007a007a007a008a008a009a009a009a00aa00aa00aa00ba00ba00ba00ca00ca00302000000000
# 057:060006000600060006000600060006000600060006000600060006000600060006000600060006000600060006000600060006000600060006000600000000000000
# 058:050005000500050005000500050005000500050005000500050005000500050005000500050005000500050005000500050005000500050005000500000000000000
# 059:040004000400040004000400040004000400040004000400040004000400040004000400040004000400040004000400040004000400040004000400000000000000
# 060:0300030003000300130013001300130023002300230023003300330033004300430053005300630063007300730083009300a300a300b300c300d300306000000000
# 061:020002000200020002000200020002000200020002000200020002000200020002000200020002000200020002000200020002000200020002000200000000000000
# 062:010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100000000000000
# 063:070007000700070007000700070007000700070007000700070007000700070007000700070007000700070007000700070007000700070007000700000000000000
# </SFX>

# <PATTERNS>
# 000:800877900877b00877800877f00877b00877600879f00877800879600879600879800879f00879600877b00879f00877b00b771008710000000000000000000000000000000008c10008c10008c10008c10008c1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 001:100881100881600885100881600885000881100881600885100881000000000000000000600885100881600885100881600b85000871000871000871000871000000000871000871000871000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 002:948ec50008610008c1a008c79008c5000861a008c70008619008c50008610008c1a008c79008c5000861a008c70003000008c1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 003:0000000000000000000008c1c339511008511008c1000000000000000000000891000891c33951100851100891000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 004:e00855c00855a00855c00855a00855800855a00855800855600855800855700855602c555cd9554bb9554a895546995548495542695344195341295114f951000851000851000851400883000000000000000000000881000000000000000000000881000000000000000000000881100881000000000000a00881000000000000000000000000000000000000000000000000000000000000000000000000100881000000000000006300000000000000000000000000000000000000000000
# 005:8008890000000000008aa9899aa9890008810000009aa9890000000000009aa989aaa989000000000000aaa989aaa9890000000000009aa989aaa9899aa989000881aaa989aaa9890008819aa9898aa989000881800b89000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 006:c00881000000000000000000b00883000000000000000000c00881000000000000000000b00883000000000000000000c00881000000000000000000b00883000000000000000000c00881000000000000000000b00883000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 007:028e51000851000851000851c00859b00859a00859b00859a00859b00859c00859d00859000851000851c00859d00859c00859d00859c00859000000001300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 008:600883500883600883100851600883000851100851000000600883000851100851000000600883000851100851000000000881600883600883100851000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </PATTERNS>

# <TRACKS>
# 000:180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a00040
# 001:301000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001
# 002:5000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff
# 003:6c1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020
# 004:842000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </TRACKS>

# <PALETTE>
# 000:1c1c1c895530ea1c18ef7d55aa1cffe214da003c0025717929366f3b5dc941a6f600f2fff4f4f494b0c2566c86333c57
# </PALETTE>

