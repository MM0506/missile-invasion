import pygame
import random
import os
import math
from itertools import combinations
import pygame.mixer

# Initialize Pygame
pygame.init()

# Initialize the sound mixer
pygame.mixer.init(44100, -16, 2, 2048)  # Initialize with specific settings

# Set up the game window
WIDTH = 1600
HEIGHT = 1000
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aircraft Dodge Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 40)  # Dark blue for space background

# Initialize sound variables
SOUNDS_LOADED = False
MUSIC_LOADED = False

# Sound settings
SOUND_VOLUME = 0.8  # Increased from 0.4 to 0.8 for louder effects

# Add after other constants
TITLE_FONT_SIZE = 128
MENU_FONT_SIZE = 64
GAME_TITLE = "Missile Invasion"
game_started = False  # Add this with other game settings

def load_game_sound(filename):
    try:
        sound_path = os.path.join('assets', filename)
        if os.path.exists(sound_path):
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(SOUND_VOLUME)
            return sound
        else:
            print(f"Sound file not found: {sound_path}")
            return None
    except Exception as e:
        print(f"Error loading sound {filename}: {e}")
        return None

# Load sounds
try:
    # Initialize mixer with specific settings
    pygame.mixer.init(44100, -16, 2, 2048)
    
    # Background music - keep quieter
    music_path = os.path.join('assets', 'background_music.mp3')
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.2)  # Reduced from 0.3 to 0.2
        MUSIC_LOADED = True
        print("Music loaded successfully!")
    else:
        print("Music file not found")
        MUSIC_LOADED = False
    
    # Load sound effects with higher volumes
    explosion_sound = load_game_sound('explosion.wav')
    explosion_sound.set_volume(0.8)  # Increased from 0.4 to 0.8
    
    missile_sound = load_game_sound('missile.wav')
    missile_sound.set_volume(0.3)  # Slightly increased but still quieter than explosion
    
    level_up_sound = load_game_sound('levelup.wav')
    level_up_sound.set_volume(0.6)  # Moderate volume
    
    SOUNDS_LOADED = all([explosion_sound, level_up_sound, missile_sound])
    if SOUNDS_LOADED:
        print("All sounds loaded successfully!")
    else:
        print("Some sounds failed to load")
        
except Exception as e:
    print(f"Error initializing sound system: {e}")
    SOUNDS_LOADED = False
    MUSIC_LOADED = False

def play_sound(sound):
    """Helper function to play sounds safely"""
    if SOUNDS_LOADED and sound:
        try:
            sound.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

def play_music():
    """Helper function to play background music"""
    if MUSIC_LOADED:
        try:
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error playing music: {e}")

# Load and scale images
def load_image(name, size):
    try:
        # Update path to look in assets folder
        image_path = os.path.join('assets', name)
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading image: {name}")
        print(f"Error details: {e}")
        # Create a surface with color as fallback
        surface = pygame.Surface(size)
        surface.fill((0, 255, 0))  # Green color as fallback
        return surface

# Player settings
player_width = 100
player_height = 80
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 40
player_speed = 10
player_base_y = player_y  # Store the base y position

# Load images
player_img = load_image("aircraft.png", (player_width, player_height))
background_img = load_image("space_bg.png", (WIDTH, HEIGHT))

# Bullet settings
bullet_width = 20
bullet_height = 40
bullet_base_speed = 5  # Reduced from 11 to 5
bullet_speed = bullet_base_speed
bullets = []

# Game settings
clock = pygame.time.Clock()
score = 0
game_over = False
level = 1
missiles_per_wave = 1  # Initial number of missiles per spawn
MISSILES_INCREASE_RATE = 1  # How many additional missiles per level
EXPLOSION_DURATION = 60  # Number of frames to show explosion
explosion_timer = 0
show_game_over = False  # Separate from game_over flag

# Star settings for background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.brightness = random.random()
        self.speed = random.random() * 0.1

    def update(self):
        self.brightness += self.speed
        if self.brightness > 1:
            self.brightness = 1
            self.speed = -self.speed
        elif self.brightness < 0.2:
            self.brightness = 0.2
            self.speed = -self.speed
        
    def draw(self, surface):
        brightness = int(255 * self.brightness)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

# Create stars list after game settings
stars = [Star() for _ in range(200)]  # Create 200 stars

# Add after the Star class
class Planet:
    def __init__(self):
        self.reset()
        # Start planets at random positions along the height
        self.y = random.randint(-200, 0)
        
    def reset(self):
        self.x = random.randint(100, WIDTH - 100)  # Random x position
        self.y = -random.randint(100, 300)  # Start above the screen
        self.size = random.randint(40, 60)  # Made planets bigger
        self.speed = random.uniform(0.2, 0.5)  # Even slower for bigger planets
        # Darker gray colors for background effect
        gray_value = random.randint(60, 100)  # Darker gray
        self.color = (gray_value, gray_value, gray_value)
        self.ring = True  # Always have rings
        self.ring_color = (min(gray_value + 10, 255),) * 3
        self.ring_angle = random.uniform(-0.2, 0.2)  # Slight random tilt to rings
        
    def update(self):
        self.y += self.speed  # Move downward
        if self.y > HEIGHT + self.size:  # Reset when planet goes below screen
            self.reset()
            
    def draw(self, surface):
        # Draw planet with slight transparency for background effect
        planet_surface = pygame.Surface((self.size * 5, self.size * 4), pygame.SRCALPHA)
        
        # Draw planet
        pygame.draw.circle(planet_surface, (*self.color, 180), 
                         (self.size * 2.5, self.size * 2), self.size)
        
        # Add subtle shading
        lighter_gray = (*self.color, 100)
        pygame.draw.circle(planet_surface, lighter_gray,
                         (self.size * 2.5 - self.size//4, self.size * 2 - self.size//4),
                         self.size//2)
        
        # Draw large ring with transparency
        ring_rect = pygame.Rect(0, self.size * 1.5, self.size * 5, self.size)
        
        # Draw multiple rings for more detail
        for i in range(3):
            ring_color = (*self.ring_color, 150 - i * 30)  # Decreasing transparency
            pygame.draw.ellipse(planet_surface, ring_color, ring_rect.inflate(-i * 10, -i * 2), 2)
        
        # Rotate the surface slightly for ring tilt effect
        rotated_surface = pygame.transform.rotate(planet_surface, self.ring_angle * 30)
        
        # Calculate new position after rotation
        new_rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surface, new_rect)

# Keep just one planet
planets = [Planet() for _ in range(1)]

# Update bullet settings
class Bullet:
    def __init__(self, x):
        self.x = x
        self.y = -bullet_height
        self.width = bullet_width
        self.height = bullet_height
        self.rect = pygame.Rect(x, -bullet_height, bullet_width, bullet_height)
        self.flame_timer = 0
        # Reduce initial horizontal movement
        self.x_speed = random.uniform(-1, 1)  # Reduced from (-2, 2) to (-1, 1)
        self.destroyed = False  # Add this flag
        
    def update(self):
        self.y += bullet_speed
        self.x += self.x_speed  # Add horizontal movement
        # Keep missile within screen bounds
        if self.x < 0 or self.x > WIDTH - self.width:
            self.x_speed = -self.x_speed
        self.rect.x = self.x
        self.rect.y = self.y
        self.flame_timer += 0.2
        
    def draw(self, surface):
        # Colors for missile
        ORANGE = (255, 140, 0)
        GRAY = (128, 128, 128)
        YELLOW = (255, 255, 0)
        BRIGHT_YELLOW = (255, 255, 150)
        
        # Create surface for missile with transparency - Make much taller for longer flames
        missile_surface = pygame.Surface((self.width, self.height * 4), pygame.SRCALPHA)
        
        # Draw missile body (gray parts) - Reversed order
        body_height = self.height * 0.6
        pygame.draw.rect(missile_surface, GRAY, 
                        (0, self.height*0.4, self.width, body_height*0.4))
        pygame.draw.rect(missile_surface, GRAY, 
                        (0, self.height*0.2, self.width, body_height*0.4))
        
        # Draw missile nose (orange)
        nose_points = [
            (self.width/2, self.height),
            (self.width, self.height*0.8),
            (0, self.height*0.8)
        ]
        pygame.draw.polygon(missile_surface, ORANGE, nose_points)
        
        # Enhanced flame effect with much bigger animation
        flame_height = self.height * 2.5  # Much longer flames
        flame_offset = abs(math.sin(self.flame_timer)) * 12  # Increased flame movement
        
        # Draw multiple flame layers with wider spread
        flame_colors = [
            (BRIGHT_YELLOW + (255,)),    # Inner bright yellow flame
            (YELLOW + (220,)),           # Middle yellow flame
            (ORANGE + (180,)),           # Outer orange flame
            ((255, 50, 0, 150)),         # Red outer glow
            ((255, 30, 0, 100)),         # Extra outer glow
            ((255, 20, 0, 80))           # Final outer glow
        ]
        
        for i, color in enumerate(flame_colors):
            spread = i * 6  # Increased spread between flame layers
            flame_points = [
                (self.width/2, 0 - flame_offset + i*12),         # Top point (flame tip)
                (0 - spread, self.height*0.2 + spread*0.8),      # Left point (wider)
                (self.width + spread, self.height*0.2 + spread*0.8)  # Right point (wider)
            ]
            pygame.draw.polygon(missile_surface, color, flame_points)
            
            # Add extra flame details
            if i < 4:  # More inner flames
                # Add flickering inner flames
                inner_flame_points = [
                    (self.width/2, flame_height*0.15 - flame_offset + i*8),
                    (self.width/2 - 6 + i, self.height*0.1),
                    (self.width/2 + 6 - i, self.height*0.1)
                ]
                pygame.draw.polygon(missile_surface, BRIGHT_YELLOW + (200,), inner_flame_points)
        
        # Add more flame particles with longer trail
        for _ in range(8):  # More particles
            particle_x = self.width/2 + random.uniform(-10, 10)  # Wider spread
            particle_y = random.uniform(-flame_height*0.6, flame_height*0.3)  # Longer range
            particle_size = random.uniform(2, 5)  # Bigger particles
            pygame.draw.circle(missile_surface, BRIGHT_YELLOW + (150,),
                             (particle_x, particle_y), particle_size)
        
        # Adjust position for longer flames
        surface.blit(missile_surface, (self.x, self.y - self.height*1.5))

    def check_collision(self, other):
        # Check if two missiles collide
        return (not self.destroyed and not other.destroyed and 
                self.rect.colliderect(other.rect))

# Update spawn_bullet function
def spawn_bullet():
    x = random.randint(0, WIDTH - bullet_width)
    bullets.append(Bullet(x))

def draw_aircraft(surface, x, y, width, height):
    # Enhanced color palette
    GREEN = (100, 255, 0)
    DARK_GREEN = (50, 180, 0)
    DARKER_GREEN = (30, 130, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 50, 50)
    WHITE = (255, 255, 255)
    GRAY = (80, 80, 80)
    
    # Main body - center section
    body_width = width * 0.6
    body_x = x + (width - body_width) // 2
    
    # Draw main body
    body_points = [
        (body_x + body_width*0.5, y),  # top point
        (body_x + body_width, y + height*0.3),  # right top
        (body_x + body_width, y + height*0.7),  # right bottom
        (body_x + body_width*0.5, y + height),  # bottom point
        (body_x, y + height*0.7),  # left bottom
        (body_x, y + height*0.3),  # left top
    ]
    
    # Draw body shadow
    shadow_points = [(p[0], p[1] + 5) for p in body_points]
    pygame.draw.polygon(surface, DARKER_GREEN, shadow_points)
    
    # Main body
    pygame.draw.polygon(surface, GREEN, body_points)
    pygame.draw.polygon(surface, DARK_GREEN, body_points, 2)
    
    # Draw rotors (large circles on sides)
    rotor_radius = width * 0.25
    left_rotor_center = (x + width*0.2, y + height*0.5)
    right_rotor_center = (x + width*0.8, y + height*0.5)
    
    # Draw rotor circles
    for rotor_center in [left_rotor_center, right_rotor_center]:
        # Outer circle
        pygame.draw.circle(surface, GREEN, (int(rotor_center[0]), int(rotor_center[1])), int(rotor_radius))
        pygame.draw.circle(surface, DARK_GREEN, (int(rotor_center[0]), int(rotor_center[1])), int(rotor_radius), 2)
        
        # Inner circle
        pygame.draw.circle(surface, DARK_GREEN, (int(rotor_center[0]), int(rotor_center[1])), int(rotor_radius*0.7))
        
        # Draw star in center of rotor
        pygame.draw.circle(surface, YELLOW, (int(rotor_center[0]), int(rotor_center[1])), int(rotor_radius*0.2))
        pygame.draw.circle(surface, WHITE, (int(rotor_center[0]), int(rotor_center[1])), int(rotor_radius*0.1))
    
    # Draw connecting arms
    arm_width = width * 0.1
    left_arm_points = [
        (body_x, y + height*0.4),
        (x + width*0.2 - rotor_radius*0.3, y + height*0.4),
        (x + width*0.2 - rotor_radius*0.3, y + height*0.6),
        (body_x, y + height*0.6)
    ]
    
    right_arm_points = [
        (body_x + body_width, y + height*0.4),
        (x + width*0.8 + rotor_radius*0.3, y + height*0.4),
        (x + width*0.8 + rotor_radius*0.3, y + height*0.6),
        (body_x + body_width, y + height*0.6)
    ]
    
    # Draw arms
    pygame.draw.polygon(surface, GREEN, left_arm_points)
    pygame.draw.polygon(surface, GREEN, right_arm_points)
    pygame.draw.polygon(surface, DARK_GREEN, left_arm_points, 2)
    pygame.draw.polygon(surface, DARK_GREEN, right_arm_points, 2)
    
    # Shield emblem in center
    shield_x = body_x + body_width*0.3
    shield_y = y + height*0.35
    shield_width = body_width*0.4
    shield_height = height*0.3
    
    # Draw shield
    shield_points = [
        (shield_x + shield_width*0.5, shield_y),
        (shield_x + shield_width, shield_y + shield_height*0.5),
        (shield_x + shield_width*0.5, shield_y + shield_height),
        (shield_x, shield_y + shield_height*0.5),
    ]
    pygame.draw.polygon(surface, RED, shield_points)
    pygame.draw.polygon(surface, WHITE, shield_points, 2)
    
    # Add cross to shield
    cross_x = shield_x + shield_width*0.25
    cross_y = shield_y + shield_height*0.25
    pygame.draw.line(surface, WHITE, 
                    (cross_x, cross_y), 
                    (cross_x + shield_width*0.5, cross_y + shield_height*0.5), 2)
    pygame.draw.line(surface, WHITE, 
                    (cross_x + shield_width*0.5, cross_y), 
                    (cross_x, cross_y + shield_height*0.5), 2)

# Add explosion effect class
class Explosion:
    def __init__(self, x, y, is_player=False, is_aircraft=False, delay=0):
        self.x = x
        self.y = y
        self.delay = delay
        # Special explosion for aircraft
        if is_aircraft:
            self.radius = 15
            self.max_radius = 150
            self.growth_rate = 3
            self.fade = 255
            self.fade_rate = 5  # Increased fade rate
        else:
            self.radius = 8
            self.max_radius = 60
            self.growth_rate = 2
            self.fade = 255
            self.fade_rate = 8  # Increased fade rate
        
    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return True
            
        # Always update radius and fade
        if self.radius < self.max_radius:
            self.radius += self.growth_rate
        
        # Always decrease fade value
        self.fade -= self.fade_rate
        
        # Return False when completely faded
        return self.fade > 0
        
    def draw(self, surface):
        if self.fade <= 0:  # Don't draw if completely faded
            return
            
        # Calculate alpha for the entire explosion
        alpha = max(0, min(255, self.fade))
        
        # Draw multiple circles for explosion effect
        for r in range(int(self.radius), max(0, int(self.radius - 20)), -2):
            if r > 0:
                # Calculate color with fade
                if self.max_radius > 60:  # Aircraft explosion
                    red = 255
                    green = min(255, int(100 + r * 3 * (self.fade/255)))
                    blue = 0
                else:  # Regular explosion
                    red = 255
                    green = min(255, int(80 + r * 2 * (self.fade/255)))
                    blue = 0
                
                # Apply fade to alpha
                current_alpha = int(alpha * (1 - (r / self.max_radius)))
                color = (red, green, blue, current_alpha)
                
                pygame.draw.circle(surface, color, 
                                (int(self.x), int(self.y)), r)

# Add explosions list to game settings
explosions = []

def draw_start_screen(surface):
    # Create gradient background
    for i in range(HEIGHT):
        color = (0, 0, max(0, min(40 + i * 0.02, 60)))  # Darker to lighter blue
        pygame.draw.line(surface, color, (0, i), (WIDTH, i))
    
    # Draw stars in background
    for star in stars:
        star.update()
        star.draw(surface)
    
    # Draw title
    title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
    menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    
    # Draw game title with glow effect
    title_text = title_font.render(GAME_TITLE, True, (255, 255, 0))  # Yellow text
    title_glow = title_font.render(GAME_TITLE, True, (255, 128, 0))  # Orange glow
    
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    glow_rect = title_glow.get_rect(center=(WIDTH//2 + 2, HEIGHT//3 + 2))
    
    # Draw decorative missiles on sides of title
    missile_width = 40
    missile_height = 80
    missile_spacing = 30  # Space between missile and text
    
    def draw_decorative_missile(x, y, flip=False):
        # Colors for missile (match game missile colors)
        ORANGE = (255, 140, 0)
        GRAY = (128, 128, 128)
        YELLOW = (255, 255, 0)
        BRIGHT_YELLOW = (255, 255, 150)
        
        # Create missile surface with transparency
        missile = pygame.Surface((missile_width, missile_height * 3), pygame.SRCALPHA)
        
        # Draw missile body (gray parts)
        body_height = missile_height * 0.6
        pygame.draw.rect(missile, GRAY, 
                        (missile_width*0.2, missile_height*0.4, 
                         missile_width*0.6, body_height*0.4))
        pygame.draw.rect(missile, GRAY, 
                        (missile_width*0.2, missile_height*0.2, 
                         missile_width*0.6, body_height*0.4))
        
        # Draw missile nose (orange)
        nose_points = [
            (missile_width/2, missile_height),
            (missile_width, missile_height*0.8),
            (0, missile_height*0.8)
        ]
        pygame.draw.polygon(missile, ORANGE, nose_points)
        
        # Enhanced flame effect
        flame_height = missile_height * 2
        flame_offset = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 12
        
        # Draw multiple flame layers
        flame_colors = [
            (BRIGHT_YELLOW + (255,)),
            (YELLOW + (220,)),
            (ORANGE + (180,)),
            ((255, 50, 0, 150)),
            ((255, 30, 0, 100))
        ]
        
        for i, color in enumerate(flame_colors):
            spread = i * 6
            flame_points = [
                (missile_width/2, 0 - flame_offset + i*12),
                (0 - spread, missile_height*0.2 + spread*0.8),
                (missile_width + spread, missile_height*0.2 + spread*0.8)
            ]
            pygame.draw.polygon(missile, color, flame_points)
            
            # Add inner flames
            if i < 3:
                inner_flame_points = [
                    (missile_width/2, flame_height*0.15 - flame_offset + i*8),
                    (missile_width/2 - 6 + i, missile_height*0.1),
                    (missile_width/2 + 6 - i, missile_height*0.1)
                ]
                pygame.draw.polygon(missile, BRIGHT_YELLOW + (200,), inner_flame_points)
        
        # Add flame particles
        for _ in range(6):
            particle_x = missile_width/2 + random.uniform(-10, 10)
            particle_y = random.uniform(-flame_height*0.6, flame_height*0.3)
            particle_size = random.uniform(2, 4)
            pygame.draw.circle(missile, BRIGHT_YELLOW + (150,),
                             (particle_x, particle_y), particle_size)
        
        # Rotate missile if needed
        if flip:
            missile = pygame.transform.rotate(missile, 180)
        
        # Add pulsing effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        missile.set_alpha(200 + int(55 * pulse))
        
        # Draw missile at position
        surface.blit(missile, (x - missile_width/2, y - missile_height*1.5))
    
    # Draw missiles on both sides
    left_missile_x = title_rect.left - missile_spacing - missile_width/2
    right_missile_x = title_rect.right + missile_spacing + missile_width/2
    missile_y = title_rect.centery
    
    draw_decorative_missile(left_missile_x, missile_y)
    draw_decorative_missile(right_missile_x, missile_y, flip=True)
    
    # Draw title over missiles
    surface.blit(title_glow, glow_rect)
    surface.blit(title_text, title_rect)
    
    # Draw "Press SPACE to start" with pulsing effect
    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5  # Pulsing value between 0 and 1
    alpha = int(255 * pulse)
    
    start_text = menu_font.render("Press SPACE to start", True, (255, 255, 255))
    start_surface = pygame.Surface(start_text.get_size(), pygame.SRCALPHA)
    start_surface.fill((255, 255, 255, alpha))
    start_text.blit(start_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT*2//3))
    surface.blit(start_text, start_rect)
    
    # Draw controls info
    controls_text = menu_font.render("Arrow keys to move", True, (200, 200, 200))
    controls_rect = controls_text.get_rect(center=(WIDTH//2, HEIGHT*4//5))
    surface.blit(controls_text, controls_rect)

# Update main function
def main():
    global player_x, player_y, score, game_over, bullet_speed, level, missiles_per_wave, explosion_timer, show_game_over, game_started
    
    player = pygame.Rect(player_x, player_y, player_width, player_height)
    bullet_timer = 0
    last_speed_increase = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle start screen input
            if not game_started:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_started = True
                    play_music()  # Start music when game starts
                    continue
            
            # Handle game over restart
            if event.type == pygame.KEYDOWN and show_game_over:
                if event.key == pygame.K_r:
                    # Reset game
                    game_over = False
                    show_game_over = False
                    game_started = False  # Return to start screen
                    explosion_timer = 0
                    score = 0
                    level = 1
                    missiles_per_wave = 1
                    bullet_speed = bullet_base_speed
                    bullets.clear()
                    explosions.clear()
                    player_x = WIDTH // 2 - player_width // 2
                    player_y = player_base_y
        
        # Draw start screen if game hasn't started
        if not game_started:
            draw_start_screen(window)
            pygame.display.flip()
            clock.tick(60)
            continue
            
        # Move player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed
        # Add forward/backward movement
        if keys[pygame.K_UP] and player_y > 100:  # Limit how high the aircraft can go
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_height - 20:
            player_y += player_speed
        
        # Update player position
        player.x = player_x
        player.y = player_y  # Update y position
        
        # Level and speed increase
        if score > 0 and score % 30 == 0 and score != last_speed_increase:
            bullet_speed += 0.5
            level += 1
            missiles_per_wave += MISSILES_INCREASE_RATE
            last_speed_increase = score
            play_sound(level_up_sound)  # Play level up sound
            print(f"Level {level}! Speed: {bullet_speed:.1f}, Missiles: {missiles_per_wave}")
        
        # Spawn multiple bullets with spacing
        bullet_timer += 1
        if bullet_timer >= 30:  # Spawn bullet every 30 frames
            # Spawn missiles with some spacing between them
            for i in range(missiles_per_wave):
                x = random.randint(0, WIDTH - bullet_width)
                bullets.append(Bullet(x))
                try:
                    missile_sound.play()
                except:
                    pass
            bullet_timer = 0
        
        # Check missile collisions
        for b1, b2 in combinations(bullets, 2):
            if b1.check_collision(b2):
                # Create explosion at collision point
                explosion_x = (b1.x + b2.x) / 2
                explosion_y = (b1.y + b2.y) / 2
                explosions.append(Explosion(explosion_x, explosion_y))
                b1.destroyed = True
                b2.destroyed = True
                play_sound(explosion_sound)  # Play explosion sound
        
        # Remove destroyed missiles
        bullets[:] = [b for b in bullets if not b.destroyed]
        
        # Update and remove finished explosions
        explosions[:] = [exp for exp in explosions if exp.update()]
        
        # Update remaining bullets
        for bullet in bullets[:]:
            bullet.update()
            # Only count score if game is not over
            if bullet.y > HEIGHT and not game_over:
                bullets.remove(bullet)
                score += 1
            elif bullet.y > HEIGHT:
                bullets.remove(bullet)  # Still remove bullets that go off screen
            
            # Update player collision to create explosion
            if bullet.rect.colliderect(player):
                # Create chain reaction explosions
                explosion_points = [
                    # Center explosions
                    (player.x + player_width/2, player.y + player_height/2, 0),
                    # Rotor explosions
                    (player.x + player_width*0.2, player.y + player_height*0.5, 5),
                    (player.x + player_width*0.8, player.y + player_height*0.5, 5),
                    # Wing explosions
                    (player.x + player_width*0.3, player.y + player_height*0.3, 10),
                    (player.x + player_width*0.7, player.y + player_height*0.3, 10),
                    # Body explosions
                    (player.x + player_width*0.4, player.y + player_height*0.6, 15),
                    (player.x + player_width*0.6, player.y + player_height*0.6, 15),
                    # Final explosions
                    (player.x + player_width*0.5, player.y, 20),
                    (player.x + player_width*0.5, player.y + player_height, 20),
                    # Additional random explosions
                    (player.x + random.uniform(0, player_width), 
                     player.y + random.uniform(0, player_height), 25),
                    (player.x + random.uniform(0, player_width), 
                     player.y + random.uniform(0, player_height), 30),
                ]
                
                # Create delayed chain reaction explosions
                for ex_x, ex_y, delay in explosion_points:
                    if random.random() < 0.7:  # 70% chance for each explosion
                        explosions.append(Explosion(ex_x, ex_y, is_aircraft=True, delay=delay))
                
                # Create missile explosion
                explosions.append(Explosion(bullet.x + bullet_width/2, 
                                         bullet.y + bullet_height/2))
                
                bullet.destroyed = True
                game_over = True
                explosion_timer = EXPLOSION_DURATION + 40  # Longer duration for chain reaction
                play_sound(explosion_sound)  # Play explosion sound
        
        # Handle explosion timer
        if game_over and explosion_timer > 0:
            explosion_timer -= 1
            if explosion_timer <= 0:
                show_game_over = True
        
        # Draw everything
        window.fill(BACKGROUND_COLOR)  # Use the defined background color
        
        # Update and draw stars
        for star in stars:
            star.update()
            star.draw(window)
            
        # Update and draw planets
        for planet in planets:
            planet.update()
            planet.draw(window)
        
        # Draw player (aircraft) only if not game over
        if not game_over:
            draw_aircraft(window, player.x, player.y, player_width, player_height)
        
        # Draw explosions
        for explosion in explosions:
            explosion.draw(window)
        
        # Draw remaining bullets
        for bullet in bullets:
            bullet.draw(window)
        
        # Draw score
        font = pygame.font.Font(None, 48)  # Increased font size
        score_text = font.render(f"Score: {score}", True, WHITE)
        window.blit(score_text, (20, 20))
        
        # Level
        level_text = font.render(f"Level: {level}", True, WHITE)
        window.blit(level_text, (20, 70))
        
        # Speed
        speed_text = font.render(f"Speed: {bullet_speed:.1f}", True, WHITE)
        window.blit(speed_text, (20, 120))
        
        # Missiles per wave
        missile_text = font.render(f"Missiles: {missiles_per_wave}", True, WHITE)
        window.blit(missile_text, (20, 170))
        
        # Draw game over screen only after explosion finishes
        if show_game_over:
            game_over_text = font.render("Game Over! Press R to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            window.blit(game_over_text, text_rect)
        
        # Stop music when game over
        if game_over and not show_game_over:
            try:
                pygame.mixer.music.fadeout(2000)  # Fade out over 2 seconds
            except:
                pass
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
