import sys, pygame, random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

izlaz = False

#inicijalizacija elemenata
character_right = pygame.image.load("character_right.png").convert_alpha()
character_right = pygame.transform.scale(character_right, (42, 84))
characterrect = character_right.get_rect()

character_left = pygame.image.load("character_left.png").convert_alpha()
character_left = pygame.transform.scale(character_left, (42, 84))

character = character_right

background = pygame.image.load("background - glitch.png").convert()
background = pygame.transform.scale(background, (1200, 900))
backgroundrect = background.get_rect()

block = pygame.image.load("block.png").convert()
block = pygame.transform.scale(block, (32, 32))

backgroundrect.center = (600, 450)
characterrect.midbottom = (50, 400)

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

#igra
while not izlaz:
    #hotkeys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            izlaz = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

    #kretnje
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and on_ground:
        y_speed = jump_strength

    #KAD
    #if keys[pygame.K_DOWN]:
     #   screen.blit(block, characterrect)
    #else:
     #   screen.blit(character, characterrect)

    if keys[pygame.K_RIGHT] and backgroundrect.right > 800:
        can_move=True
        for b in blocks:
            test_block = b.copy()
            test_block.x -= speed
            character=character_right

            if characterrect.colliderect(test_block):
                can_move=False
                break
            
        if can_move:
            backgroundrect.x -= speed / 5
            for b in blocks:
                b.x -= speed

    if keys[pygame.K_LEFT] and backgroundrect.left < 0:
        can_move=True
        for b in blocks:
            test_block = b.copy()
            test_block.x += speed
            character=character_left

            if characterrect.colliderect(test_block):
                can_move=False
                break

        if can_move:
            backgroundrect.x += speed / 5
            for b in blocks:
                b.x += speed
                
    #fizika (logika)
    y_speed += gravity
    characterrect.y += y_speed

    if characterrect.bottom >= 600:
        characterrect.bottom = 600
        y_speed = 0
        on_ground = True
    else:
        on_ground = False

    for b in blocks:
        if characterrect.colliderect(b) and y_speed > 0:
            characterrect.bottom = b.top
            y_speed = 0
            on_ground = True

        if characterrect.colliderect(b) and y_speed < 0:
            characterrect.top = b.bottom
            y_speed = 0

    #crtanje elemenata
    screen.blit(background, backgroundrect)
    screen.blit(character, characterrect)

    for b in blocks:
        screen.blit(block, b)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
