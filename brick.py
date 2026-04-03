# script: python

# --- PLAYER ---
player_x = 50
player_y = 50
player_h = 10
player_w = 10

hsp = 0 # horizontal speed
vsp = 0 # vertical speed

#block

box_x = 80 #pozicija na x koordinati
box_y = 80 #pozicija na y koordinati
box_h = 20 #visina
box_w = 20 #sirina

def collide(player_x, player_y, player_w, player_h, box_x, box_y, box_w, box_h):
    return player_x < box_x + box_w and player_x + player_w > box_x and player_y < box_y + box_h and player_y + player_h > box_y



def TIC():
    global player_x, player_y,player_h,player_w,box_x,box_y,box_h,box_w ,hsp, vsp

    cls(0)

    # --- INPUT ---
    if key(1):   # left
        hsp = -3
    elif key(4): # right
        hsp = 3
    else:
        hsp = 0

    # --- JUMP ---
    if key(23):  # space
        vsp = -3

    # --- GRAVITY ---
    vsp += 0.2

    # --- MOVE ---
    player_x += hsp
    player_y += vsp
    
    if collide(player_x, player_y, player_w, player_h, box_x, box_y, box_w, box_h):
        player_x -= hsp
        if key(1):   # left
            player_x -= hsp
        elif key(4): # right
            player_x += hsp
        else:
            vsp = 0

    if collide(player_x, player_y, player_w, player_h, box_x, box_y, box_w, box_h):
        player_y -= vsp
        vsp = 0

    # --- FLOOR ---
    if player_y > 100:
        player_y = 100
        vsp = 0

    # --- DRAW PLAYER ---
    rect(int(player_x), int(player_y), int(player_h), int(player_w), 11)

    # --- DRAW FLOOR ---
    rect(0, 110, 240, 10,12)
    
    rect(int(box_x),int(box_y),int(box_w) ,int(box_h),1)
    
    if collide(player_x, player_y, player_w, player_h, box_x, box_y, box_w, box_h):
        print("HIT!", 10, 10, 12)
        
    