import os # Provides functions to interact with the operating system, like file and directory management.
import random
import math
import pygame

"""
listdir and isfile: These are from the os module, 
used to get file lists from directories and check if a file exists.
"""

from os import listdir
from os.path import isfile,join
# to initialize the pygame module
pygame.init()
# to step the caption at the  top of the window
pygame.display.set_caption("Plateformer")




# definig few global variable
#BG_COLOR = (255 , 255 ,255) # As of know we are using white background
# Set the screen mode to fullscreen, adjusting to the screen size
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
window = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

WIDTH, HEIGHT = 1000 , 800 # U might have to alter this as per ur display size
FPS = 60 # frame per second
PlAYER_VEL = 5 # Speed with which my character moves 
#window = pygame.display.set_mode((WIDTH,HEIGHT)) # This create the game window
# --- Procedural Generation Functions ---
def generate_platforms(start_x, count=5, min_gap=100, max_gap=300, height_levels=None):
    """Generate platforms starting from start_x position"""
    if height_levels is None:
        height_levels = [100, 150, 200]  # Default height options
    
    platforms = []
    current_x = start_x
    
    for _ in range(count):
        gap = random.randint(min_gap, max_gap)
        height = random.choice(height_levels)
        platforms.append(Block(current_x + gap, HEIGHT - height, 96))
        current_x += gap
    
    return platforms

def validate_level(platforms, max_jump=300):
    """Ensure all platforms are reachable"""
    for i in range(1, len(platforms)):
        dx = platforms[i].rect.x - platforms[i-1].rect.x
        dy = platforms[i].rect.y - platforms[i-1].rect.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > max_jump:
            # Adjust unreachable platform
            platforms[i].rect.x = platforms[i-1].rect.x + random.randint(100, 250)
            platforms[i].rect.y = HEIGHT - random.choice([100, 150])
# --- Existing Helper Functions ---




def flip(sprites):
    return[pygame.transform.flip(sprite, True , False) for sprite in sprites]





def load_sprite_sheets(dir1,dir2,width,height,direction = False):# direction is used if we need to store multiple direction  here false set to enusre that u load only left or right side images like we flip the image if u passed this equal to true
    path = join("assets",dir1,dir2)
    images = [f for f in listdir(path) if isfile (join(path,f))]# this is going to load every single file which is inside of main directory
    # now we have files we are going to split them into individual images
    all_sprites = {}
    for image in images:
        # here we are loading the image ehich is one of thr file me just need to append the path
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()
        sprites =[]
        #here we know width of individual pic is let say 32 oixel so dividing the total by it give the no of images abstrcted from one single sprite sheet
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width , height), pygame.SRCALPHA, 32)
            # creating a rectangel which is going to tell us where in this sprite sheet from which we want an individual image and bullet it onto the surface
            # we are creating a surface thats the size of our desired individual animation frame and then
            #we are going to grab that animation from our main , main image we are going to draw it onto the surfcae and then we are going to kind of export that surface 
            rect = pygame.Rect(i*width , 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        if direction:
            all_sprites[image.replace(".png","") + "_right"] = sprites
            all_sprites[image.replace(".png","") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites
    return all_sprites





def get_block(size):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA, 32)
    # I have already done the calculation the terrain I want is at 96th pixel
    rect = pygame.Rect(96,0,size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)



#------------------------------------------------------------------------------------GAME CLASSES-------------------------------------------------

# Now as per above code we are drawing spreadsheet on a new surface at coordinate 0,0 which is my top left cornor but we are drawing the fram from sprite sheet that we want
#----------------------------------What is Sprite- Sprite helps for pixel perfect collison
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0 ,0)
    GRAVITY =1
    SPRITES =load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width , height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)# This to make your course simplier
        # Velocity in x and y direction
        self.x_vel = 0 
        self.y_vel = 0
        self.mask = None 
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        # ... existing code ...
        self.health = 100  # New health attribute
        self.invincible = False#----------------------------------------------CAN BE USED TO ADD POWER UP IN FUTURE OR SHIELD
        self.invincible_timer = 0
        self.sprite = self.SPRITES["idle_left"][0]
        self.mask = pygame.mask.from_surface(self.sprite)
    #-------------------------------Added due to enemy and health stuff
    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_timer = 30  # 0.5 seconds at 60 FPS
            self.make_hit()  # Your existing hit effect


    def jump(self):
        self.y_vel = -self.GRAVITY*8 # this factort defines how fast u jump
        self.animation_count = 0
        """as soon as i jump i get rid of any gravity i have already obtained 
        like i m on ground so some gravity is there which is keeping there on ground so if i jump i dont account for that gravity
        then i apply gravity after my jump
        so thats why i m setting fall_count = 0 , however this is only for 1st jump
        For second jump  we are going to time it based on like wehn player is jumping
        kie if u press K_UP very quickly i.e ur gravity is minimum at that time as i have set the count 0 then u will jump higher
        in comparison to when u will press K_UP when ur player is already at the peak of his first jump 
        as by the tume gravity would have come to play and will be higest"""
        self.jump_count +=1
        if self.jump_count ==1:
            self.fall_count = 0

    # In py the coordinate (0,0) is at top let cornor there for to move left and up we subtract and for down and right add
    def move(self , dx , dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True 
        self.hit_count =0

    def move_left(self , vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self , vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self,fps):
        self.y_vel += min(1,(self.fall_count/fps )* self.GRAVITY) # Not actually  gravity reaaly but bare with me and how is it working
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.hit_count +=1
        if self.hit_count >fps *2 :# you can pic any value u want
            self.hit = False
            self.hit_count = 0
            #------------------------ENEMY SE ADDED
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        self.fall_count +=1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        #all jump work is done after introducing jump
        if self.y_vel < 0 :
            if self.jump_count ==1:
                sprite_sheet = "jump"
            elif self.jump_count ==2:
                sprite_sheet ="double_jump"

            """this is beacsue gravity is being applied ewven on ground so setting it >0 will lead to giltiching between fall and jump state
            when the player have gone off the block and then have fallen down to the block
            now what is happen is when player hit the block i.e collide with it it is going to reset my gravity count and then player is kind of spawn to the top of the block
            so when player is on the top of block going to be slowly falling down to the block
            then wehn i hit the block its going to do the same thing its going to bring me to the top and rset mu grabity count 
            """             
        elif self.y_vel > self.GRAVITY*2: 
            sprite_sheet = "fall"
        if self.x_vel !=0 :
            sprite_sheet = "run"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        """some sprites are pushed little bit right some our little bit left or some thing like that but we need that to be fixed
        so we are constantly going to change the size of rectangle depending upon what we are getting"""
        self.rect= self.sprite.get_rect(topleft =(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        """mask is a mapping of all the pixels that exist in the Sprite so when ever we draw some thing on screen 
        basically what we are drawing is a rectangle but it mahe not have non transparent pixels so only part of recatngle is actually filled 
        so this mask tell us where actually pixels are there and helps in pixel perfect collisons
        as we can mask it with another mask and 
        make sure that we only say two objects are colliding only when there pixels are colliding and not when boxes are colliding"""
        

    def draw(self,win, offset_x):
        #pygame.draw.rect(win, self.COLOR,self.rect)
        #self.sprite = self.SPRITES["idle_" + self.direction][0] # how doee _ make a difference
        win.blit(self.sprite, (self.rect.x- offset_x, self.rect.y))

#--------------------------------------------------------------------------ENEMY-------------------------------
class Enemy(pygame.sprite.Sprite):
    """Relentless 2-State FSM: Patrol -> Chase (No Return)"""
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    
    def __init__(self, x, y):
        super().__init__()
        # sequence matters
        self.rect = pygame.Rect(x, y, 32, 32)
        self.direction = "left"
        self.name = "enemy" # to fix attribute error of no name
        self.sprite = self.SPRITES["run_" + self.direction][0]
        self.mask = pygame.mask.from_surface(self.sprite)

        self.state = "patrol"
        self.speed = 3
        self.patrol_range = 300
        self.start_x = x
        self.detection_range = 350  # Distance to spot player
        self.animation_count = 0
        self.attack_cooldown = 0
        self.attack_damage = 10
        
    def update(self, player):
        # Animation needs to set first
        sprite_sheet = "run_" + self.direction
        sprites = self.SPRITES[sprite_sheet]
        sprite_index = (self.animation_count // 5) % len(sprites)
        self.sprite = sprites[sprite_index]
        
        self.animation_count += 1
        
        # then do collision detection
        dist_x = abs(self.rect.x - player.rect.x)
        
        # State transitions
        if self.state == "patrol" and dist_x < self.detection_range:
            self.state = "chase"
        # Damage by enemy to player
        if (self.state == "chase" and 
            pygame.sprite.collide_mask(self, player) and 
            self.attack_cooldown <= 0):
            
            player.take_damage(self.attack_damage)
            self.attack_cooldown = 60  # 1 second cooldown at 60 FPS
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        # State actions
        if self.state == "patrol":
            if abs(self.rect.x - self.start_x) > self.patrol_range:
                self.direction = "right" if self.direction == "left" else "left"
            self.rect.x += self.speed if self.direction == "right" else -self.speed
            
        elif self.state == "chase":
            # Chase player indefinitely
            self.direction = "right" if player.rect.x > self.rect.x else "left"
            self.rect.x += self.speed * (1 if self.direction == "right" else -1)
            
        
        
    def attack(self, player):
        """Damage player when in range"""
        player.make_hit()  # Use your existing player hit method
        # Optional: Add attack animation here
# draw is new as it will flash red light on attacl
    def draw(self, win, offset_x):
        # Flash red when attacking
        if self.attack_cooldown > 55:  # First 5 frames after attacking
            temp_sprite = self.sprite.copy()
            temp_sprite.fill((255, 0, 0, 100), special_flags=pygame.BLEND_MULT)
            win.blit(temp_sprite, (self.rect.x - offset_x, self.rect.y))
        else:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):

    def __init__(self, x,y,width,height,name = None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self,win,offset_x):
        # before inclusion of offset win.blit(self.image, (self.rect.x, self.rect.y))
        win.blit(self.image, (self.rect.x- offset_x, self.rect.y))




class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y,size ,size)
        block = get_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)




class Fire(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire" , width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
    
    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect= self.image.get_rect(topleft =(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            # if u do it in player class it mess with double jump and hence we are constantly reseting the mask and animation count but since fire is static we made it smaller
            self.animation_count = 0


def get_full_background(name, screen_width, screen_height):
    """Loads a full-sized background image dynamically scaled to the screen size."""
    image = pygame.image.load(join("assets", "Background", name)).convert_alpha()
    full_bg = pygame.transform.scale(image, (screen_width, screen_height))
    return full_bg


def get_tiled_background(name, screen_width, screen_height, tile_size):
    """Loads a tiled background that repeats to cover the screen."""
    image = pygame.image.load(join("assets", "Background", name)).convert_alpha()
    tile_width, tile_height = image.get_width(), image.get_height()

    # Create a new surface with the exact dimensions of the screen
    tiled_bg = pygame.Surface((screen_width, screen_height))

    # Fill the surface with repeated tiles
    for y in range(0, screen_height, tile_height):
        for x in range(0, screen_width, tile_width):
            tiled_bg.blit(image, (x, y))

    return tiled_bg



def draw_health_bar(surface, x, y, current_health, max_health=100):
    """Draws a health bar with border and filling"""
    BAR_LENGTH = 200
    BAR_HEIGHT = 30
    fill = (current_health / max_health) * BAR_LENGTH
    
    # Background (empty part)
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    pygame.draw.rect(surface, (60, 60, 60), outline_rect)  # Gray background
    
    # Health fill (colored part)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    if current_health > 60:
        color = (0, 255, 0)  # Green when healthy
    elif current_health > 30:
        color = (255, 255, 0)  # Yellow when medium
    else:
        color = (255, 0, 0)  # Red when low
    
    pygame.draw.rect(surface, color, fill_rect)
    pygame.draw.rect(surface, (255, 255, 255), outline_rect, 2)  # White border
    
    try:
        font = pygame.font.Font("assets/fonts/Bangers-Regular.ttf", 25)  # Single font initialization
    except:
        font = pygame.font.SysFont("Arial", 20)  # Fallback font
    text = font.render(f"{int(current_health)}/{max_health}", True, (183, 255, 255))
    surface.blit(text, (x + BAR_LENGTH + 10, y + 5))


def draw(window, bg_image, player, objects, offset_x):
    """
    Draw everything on the screen:
    - Either a full-screen background or a tiled background
    - Objects and the player.
    """
    # 1. Draw background first
    window.blit(bg_image, (0, 0))
    
    # 2. Draw all game objects
    for obj in objects:
        obj.draw(window, offset_x)
    
    # 3. Draw player (above objects)
    player.draw(window, offset_x)
    
    # 4. Draw UI elements (top layer)
    draw_health_bar(window, 10, 10, player.health)
    
    pygame.display.update()



    """ 
    we will check for horizontal collison first only then we go for vertical collision
    this is all we need to do to check if two objects are colliding all this is so simple becasue if inherited the objects from sprite
    we are using rectangle as well as mask property
    since we have all ready handled the verticle collison now we need to make sure that program does not get condfuse between the vertivle and horizontal collision
    for that when collided horizontally we move off that block when collided
    """





def handle_verticle_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        # Skip if masks aren't ready (safety check)
        if not hasattr(player, 'mask') or not hasattr(obj, 'mask'):
            continue
            
        # Your original collision logic with added protection
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects



def collide(player,objects,dx):
    """ this check if palyer move in dirction it is moving will it collide horizontally 
    it does not matter whether they actually collide we need to place them back
    Now we are going to use this function to allow or disallow player to move to a particular block
    """
    player.move(dx , 0)# moving them a little bit
    player.update()# we update their mask and rectangle before we comare them actully
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            collided_object = obj
            break
    player.move(-dx,0)
    player.update()
    return collided_object





def handle_move(player,objects):
    """Jump is defined in main instead of here becasue if we put jump here let say space_bar is that key
    So if keep holdig the spacebar the player will keep on jumping
    Whereas if placed inside main u will have to realse the key and repress it to make it jump again 
    as it jumps only once if u press the key or keep holding it
    """
    keys = pygame.key.get_pressed()
    player.x_vel = 0 # if not set to 0 the player will keep on moving in the direction u pressed
    collide_left = collide(player,objects,-PlAYER_VEL*2) # thsi is a heck so there is little bt of time between collision and change of sprite animation
    collide_rightt = collide(player,objects,PlAYER_VEL*2)
    #movement
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PlAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_rightt:
        player.move_right(PlAYER_VEL)
    vertical_collide = handle_verticle_collision(player, objects, player.y_vel)
    to_check = [collide_left,collide_rightt, *vertical_collide]
    # Hazard detection
    for obj in objects:
        if not hasattr(obj, 'name'):
            continue
            
        # Fire collision
        if obj.name == "fire" and pygame.sprite.collide_mask(player, obj):
            player.take_damage(10)  # Fire damage
            player.make_hit()
            
        # Enemy collision
        elif obj.name == "enemy" and pygame.sprite.collide_mask(player, obj):
            if not player.invincible:
                player.take_damage(20)  # Enemy damage
                player.make_hit()
                # Knockback effect
                player.x_vel = -15 if player.direction == "right" else 15


#----------------------------------------------------------------------------------------MAIN GAME FUNCTION-------------------------------------------

def main(window):
    # Initialize game state
    clock = pygame.time.Clock()
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    window = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    # Game state variables
    game_over = False
    death_time = 0
    # UI elements
    font = pygame.font.Font("assets/fonts/Bangers-Regular.ttf", 50)
    # Background setup
    background_type = "full"
    if background_type == "full":
        background_image = get_full_background("forest.png", screen_width, screen_height)
    elif background_type == "tiled":
        tile_size = 64
        background_image = get_tiled_background("Blue.png", screen_width, screen_height, tile_size)
    # Game constants
    block_size = 96
    SCROLL_AREA_WIDTH = 200
    INITIAL_PLATFORMS = 15
    CLEANUP_DISTANCE = 1000
    
    def reset_game():
        """Reset all game objects"""
        nonlocal game_over, death_time
        player = Player(100, 100, 50, 50)
        floor = generate_platforms(0, INITIAL_PLATFORMS)
        validate_level(floor)
        # Create new instances of hazards
        fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
        fire.on()
        enemy = Enemy(300, HEIGHT - block_size - 64)
        objects = [*floor, Block(9, HEIGHT - block_size*2, block_size),
                Block(block_size*3, HEIGHT - block_size*4, block_size),
                fire, enemy]
        game_over = False
        death_time = 0
        return player, floor, objects, fire, enemy, 0  # offset_x starts at 0
    
    # FUnction to draw text at cemter
    def draw_centered_text(surface, text, font, y_offset=0, color=(255, 255, 255)):
        """Perfectly centers text on the surface with optional vertical offset"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(surface.get_width()//2, surface.get_height()//2 + y_offset))
        surface.blit(text_surface, text_rect)
        return text_rect  # Returns position in case you need it
    # Initial game setup
    player, floor, objects, fire, enemy, offset_x = reset_game()
    
    run = True
    while run:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if not game_over and event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if game_over and event.key == pygame.K_r:
                    player, floor, objects, fire, enemy, offset_x = reset_game()
        
        if not game_over:
            # Game logic
            player.loop(FPS)
            fire.loop()
            enemy.update(player)
            handle_move(player, objects)
            
            # Check for player falling off screen
            if player.rect.top > HEIGHT:
                player.health = 0
            
            # Check for death
            if player.health <= 0:
                game_over = True
                death_time = pygame.time.get_ticks()
            
            # Infinite platform generation
            if floor:
                last_platform = max(floor, key=lambda p: p.rect.x)
                if player.rect.right > offset_x + WIDTH - SCROLL_AREA_WIDTH:
                    new_platforms = generate_platforms(last_platform.rect.x, 5)
                    floor.extend(new_platforms)
                    objects.extend(new_platforms)
                    
                    # Clean up old platforms
                    objects = [obj for obj in objects if obj.rect.right > offset_x - CLEANUP_DISTANCE]
                    floor = [p for p in floor if p.rect.right > offset_x - CLEANUP_DISTANCE]
            
            # Scrolling logic
            if ((player.rect.right - offset_x >= WIDTH - SCROLL_AREA_WIDTH) and player.x_vel > 0) or ((player.rect.left - offset_x <= SCROLL_AREA_WIDTH) and player.x_vel < 0):
                offset_x += player.x_vel
        
        # Drawing
        window.fill((0, 0, 0))  # Clear screen
        
        # Draw background and game objects
        window.blit(background_image, (0, 0))
        for obj in objects:
            obj.draw(window, offset_x)
        player.draw(window, offset_x)
        
        # Draw health text
        # health_text = font.render(f"Health: {player.health}", True, (255, 255, 255))
        # window.blit(health_text, (50, 50))
        draw_health_bar(window, 20, 20, player.health)
        
        # Draw game over screen if needed
        if game_over:
            # Draw centered texts with 60px vertical spacing
            draw_centered_text(window, "GAME OVER", font, y_offset=-60, color=(255, 0, 0))
            draw_centered_text(window, "Press R to Restart",  font, y_offset=60, color=(255, 255, 255))
            # Auto-restart after 5 seconds (optional)
            if pygame.time.get_ticks() - death_time > 5000:
                player, floor, objects, fire, enemy, offset_x = reset_game()
        
        pygame.display.update()
    
    pygame.quit()
    quit()

if __name__=="__main__": # This is to enure that the main excutes onky if run directly and not if we import something from there
    main(window)
# limitation accespted peeche ka khatam ho ta jaa raha hai map as i m focosed generation
# 2 april implement fall logic and wfc lite