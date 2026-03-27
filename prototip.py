import sys, pygame, random

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

izlaz = False

#inicijalizacija elemenata
character_right = pygame.image.load("character_right.png").convert_alpha()
character_right = pygame.transform.scale(character_right, (42, 84))
characterrect = character_right.get_rect()

character_left = pygame.image.load("character_left.png").convert_alpha()
character_left = pygame.transform.scale(character_left, (42, 84))

character = character_right

block = pygame.image.load("block.png").convert()
block = pygame.transform.scale(block, (32, 32))

katana_right = pygame.image.load("katana_neon_right.png").convert_alpha()
katana_right = pygame.transform.scale(katana_right, (48, 48))
katanarect = katana_right.get_rect()

#pozadina (rucno napravljen GIF)
frame_normal = pygame.image.load("background - glitch.png").convert()
frame_normal = pygame.transform.scale(frame_normal, (1200, 900))

glitch_frame1 = pygame.image.load("background - glitch_frame2.png").convert()
glitch_frame1 = pygame.transform.scale(glitch_frame1, (1200, 900))

glitch_frame2 = pygame.image.load("background - glitch_frame3.png").convert()
glitch_frame2 = pygame.transform.scale(glitch_frame2, (1200, 900))

glitch_frames=[glitch_frame1, glitch_frame2]

glitching = False
glitch_frame = 0
glitch_timer = 0

time_since_last_glitch = 0
next_glitch_time = random.randint(2000, 6000)

backgroundrect=frame_normal.get_rect()

backgroundrect.center = (450, 300)
characterrect.midbottom = (50, 400)
katanarect.midbottom = (600, 600)

#blokovi
blocks=[]

block1=block.get_rect()
block1.midbottom=(200, 600)

block2=block.get_rect()
block2.midbottom=(300, 560)

block3=block.get_rect()
block3.midbottom=(400, 500)

blocks.append(block1)
blocks.append(block2)
blocks.append(block3)

#fizika
speed = 3
y_speed = 0
gravity = 0.5
jump_strength = -10
on_ground = False

#kamera
camera_x = 0
camera_y = 0

#veličina svijeta
world_width = frame_normal.get_width()
world_height = frame_normal.get_height()

#okrugli ekran (maska)
game_surface = pygame.Surface((600, 600), pygame.SRCALPHA)
mask = pygame.Surface((600, 600), pygame.SRCALPHA)
pygame.draw.circle(mask, (255,255,255), (300,300), 300)

#igra
while not izlaz:
    dt = clock.tick(60)
    
    #hotkeys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            izlaz = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

    #kretnje lijevo, desno
    keys = pygame.key.get_pressed()

    dx = 0

    if keys[pygame.K_RIGHT]:
        dx = speed
        character = character_right

    if keys[pygame.K_LEFT]:
        dx = -speed
        character = character_left

    characterrect.x += dx

    for b in blocks:
        if characterrect.colliderect(b):
            if dx > 0:
                characterrect.right = b.left
            if dx < 0:
                characterrect.left = b.right

    #character u granicama svijeta
    if characterrect.left < 0:
        characterrect.left = 0
    if characterrect.right > world_width:
        characterrect.right = world_width

    #skakanje
    if keys[pygame.K_SPACE] and on_ground:
        y_speed = jump_strength

    y_speed += gravity
    characterrect.y += y_speed

    on_ground = False

    for b in blocks:
        if characterrect.colliderect(b):
            if y_speed > 0:
                characterrect.bottom = b.top
                y_speed = 0
                on_ground = True

            elif y_speed < 0:
                characterrect.top = b.bottom
                y_speed = 0

    #pod (NE background)
    if characterrect.bottom >= 600:
        characterrect.bottom = 600
        y_speed = 0
        on_ground = True

    #kretnja kamere
    target_x = characterrect.centerx - 300
    target_y = characterrect.centery - 350

    camera_x += (target_x - camera_x) * 0.1
    camera_y += (target_y - camera_y) * 0.1

    #ograničenje kamere
    camera_x = max(0, min(camera_x, world_width - 600))
    camera_y = max(0, min(camera_y, world_height - 600))

    #logika GIF-a
    time_since_last_glitch+=dt
    if not glitching and time_since_last_glitch >= next_glitch_time:
        glitching = True
        glitch_timer=0
        glitch_frame=0

    if glitching:
        glitch_timer+=dt

        if glitch_timer>50:
            glitch_timer=0
            glitch_frame+=1

            if glitch_frame >= len(glitch_frames):
                glitch_frame=0

        if time_since_last_glitch >= next_glitch_time + 200:
            glitching=False
            time_since_last_glitch=0
            next_glitch_time=random.randint(2000, 6000)
    
    #crtanje (na game surface)
    game_surface.fill((0,0,0))

    if glitching:
        game_surface.blit(glitch_frames[glitch_frame], (-camera_x, -camera_y))
    else:
        game_surface.blit(frame_normal, (-camera_x, -camera_y))

    for b in blocks:
        game_surface.blit(block, (b.x - camera_x, b.y - camera_y))

    game_surface.blit(character, (characterrect.x - camera_x, characterrect.y - camera_y))

    game_surface.blit(katana_right, (katanarect.x - camera_x, katanarect.y - camera_y))
    
    #primjena kružne maske
    game_surface.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

    screen.fill((0,0,0))
    screen.blit(game_surface, (0,0))

    pygame.display.flip()

pygame.quit()
sys.exit()
