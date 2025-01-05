import pygame
import random
import math
import asyncio
import platform

class Aircraft:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.speed = 5
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def move(self, dx, dy):
        self.x = max(0, min(800 - self.width, self.x + dx))
        self.y = max(100, min(600 - self.height - 20, self.y + dy))
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        # Colors
        GREEN = (100, 255, 0)
        DARK_GREEN = (50, 180, 0)
        DARKER_GREEN = (30, 130, 0)
        YELLOW = (255, 255, 0)
        WHITE = (255, 255, 255)
        
        # Main body
        body_width = self.width * 0.6
        body_x = self.x + (self.width - body_width) // 2
        
        # Draw main body
        body_points = [
            (body_x + body_width*0.5, self.y),  # top point
            (body_x + body_width, self.y + self.height*0.3),  # right top
            (body_x + body_width, self.y + self.height*0.7),  # right bottom
            (body_x + body_width*0.5, self.y + self.height),  # bottom point
            (body_x, self.y + self.height*0.7),  # left bottom
            (body_x, self.y + self.height*0.3),  # left top
        ]
        
        # Draw body shadow
        shadow_points = [(p[0], p[1] + 2) for p in body_points]
        pygame.draw.polygon(surface, DARKER_GREEN, shadow_points)
        
        # Main body
        pygame.draw.polygon(surface, GREEN, body_points)
        pygame.draw.polygon(surface, DARK_GREEN, body_points, 2)
        
        # Draw rotors
        rotor_radius = self.width * 0.25
        left_rotor = (self.x + self.width*0.2, self.y + self.height*0.5)
        right_rotor = (self.x + self.width*0.8, self.y + self.height*0.5)
        
        for center in [left_rotor, right_rotor]:
            pygame.draw.circle(surface, GREEN, (int(center[0]), int(center[1])), int(rotor_radius))
            pygame.draw.circle(surface, DARK_GREEN, (int(center[0]), int(center[1])), int(rotor_radius), 2)
            pygame.draw.circle(surface, DARK_GREEN, (int(center[0]), int(center[1])), int(rotor_radius*0.7))
            pygame.draw.circle(surface, YELLOW, (int(center[0]), int(center[1])), int(rotor_radius*0.2))
            pygame.draw.circle(surface, WHITE, (int(center[0]), int(center[1])), int(rotor_radius*0.1))

class Missile:
    def __init__(self, x, speed):
        self.x = x
        self.y = -40
        self.width = 20
        self.height = 40
        self.speed = speed
        self.flame_timer = 0
        self.rect = pygame.Rect(x, -40, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        self.flame_timer += 0.2

    def draw(self, surface):
        ORANGE = (255, 140, 0)
        GRAY = (128, 128, 128)
        YELLOW = (255, 255, 0)
        
        # Draw missile body
        pygame.draw.rect(surface, GRAY, 
                        (self.x + self.width*0.2, self.y + self.height*0.4, 
                         self.width*0.6, self.height*0.4))
        
        # Draw missile nose
        nose_points = [
            (self.x + self.width/2, self.y + self.height),
            (self.x + self.width, self.y + self.height*0.8),
            (self.x, self.y + self.height*0.8)
        ]
        pygame.draw.polygon(surface, ORANGE, nose_points)
        
        # Draw flame
        flame_height = abs(math.sin(self.flame_timer)) * 20
        flame_points = [
            (self.x + self.width/2, self.y),
            (self.x, self.y + self.height*0.2 + flame_height),
            (self.x + self.width, self.y + self.height*0.2 + flame_height)
        ]
        pygame.draw.polygon(surface, YELLOW, flame_points)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 40
        self.growth_rate = 2
        self.alpha = 255
        self.fade_rate = 8
        self.particles = []
        self.done = False
        
        # Create explosion particles
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.randint(2, 4),
                'alpha': 255
            })

    def update(self):
        # Update main explosion
        if self.radius < self.max_radius:
            self.radius += self.growth_rate
        self.alpha = max(0, self.alpha - self.fade_rate)
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] = max(0, particle['alpha'] - self.fade_rate)
        
        # Check if explosion is complete
        if self.alpha <= 0 and all(p['alpha'] <= 0 for p in self.particles):
            self.done = True

    def draw(self, surface):
        # Draw main explosion circle
        if self.alpha > 0:
            explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (255, 165, 0, self.alpha), 
                             (self.radius, self.radius), self.radius)
            surface.blit(explosion_surface, (self.x - self.radius, self.y - self.radius))
        
        # Draw particles
        for particle in self.particles:
            if particle['alpha'] > 0:
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, (255, 100, 0, particle['alpha']),
                                 (particle['size'], particle['size']), particle['size'])
                surface.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))

class Planet:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.ring_angle = random.uniform(-math.pi/6, math.pi/6)  # Slight ring tilt
        # Gray color scheme
        self.base_color = (
            random.randint(150, 180),  # Gray base
            random.randint(150, 180),
            random.randint(150, 180)
        )
        # Darker gray for surface details
        self.detail_color = (
            max(self.base_color[0] - 40, 0),
            max(self.base_color[1] - 40, 0),
            max(self.base_color[2] - 40, 0)
        )
        self.speed = random.uniform(0.2, 0.4)  # Even slower movement
        # Surface detail positions
        self.surface_details = []
        for _ in range(4):  # Add 4 surface details
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(0.2, 0.8) * size
            self.surface_details.append({
                'angle': angle,
                'dist': dist,
                'size': random.uniform(0.15, 0.3) * size
            })

    def update(self):
        self.y += self.speed  # Move from top to bottom
        if self.y - self.size > 600:  # Reset position when off screen
            self.y = -self.size * 2
            self.x = random.randint(self.size, 800 - self.size)

    def draw(self, surface):
        # Draw planet glow
        glow_radius = self.size + 6
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.base_color, 30), 
                         (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, 
                    (int(self.x) - glow_radius, int(self.y) - glow_radius))
        
        # Draw base planet
        pygame.draw.circle(surface, self.base_color, (int(self.x), int(self.y)), self.size)
        
        # Draw surface details (craters/spots)
        for detail in self.surface_details:
            detail_x = self.x + math.cos(detail['angle']) * detail['dist']
            detail_y = self.y + math.sin(detail['angle']) * detail['dist']
            pygame.draw.circle(surface, self.detail_color, 
                             (int(detail_x), int(detail_y)), 
                             int(detail['size']))
        
        # Draw ring
        ring_surface = pygame.Surface((self.size * 4, self.size * 2), pygame.SRCALPHA)
        # Draw main ring
        pygame.draw.ellipse(ring_surface, (*self.base_color, 120), 
                          (0, self.size//2, self.size * 4, self.size))
        # Draw ring shadow
        pygame.draw.ellipse(ring_surface, (*self.detail_color, 80), 
                          (self.size//2, self.size//2 + 2, self.size * 3, self.size//2))
        
        rotated_ring = pygame.transform.rotate(ring_surface, math.degrees(self.ring_angle))
        surface.blit(rotated_ring, 
                    (self.x - rotated_ring.get_width()//2,
                     self.y - rotated_ring.get_height()//2))

async def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    
    # Load sounds with correct web paths
    sounds = {}
    try:
        # Load background music
        pygame.mixer.music.load("assets/background_music.mp3")
        pygame.mixer.music.set_volume(0.3)
        
        # Load sound effects
        sounds["missile"] = pygame.mixer.Sound("assets/missile.wav")
        sounds["explosion"] = pygame.mixer.Sound("assets/explosion.wav")
        sounds["levelup"] = pygame.mixer.Sound("assets/levelup.wav")
        
        # Set sound volumes
        sounds["missile"].set_volume(0.4)
        sounds["explosion"].set_volume(0.6)
        sounds["levelup"].set_volume(0.5)
        
        # Start background music
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error loading sounds: {e}")
        sounds = {}
    
    # Set up display
    WIDTH = 800
    HEIGHT = 600
    canvas = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Missile Invasion")
    
    # Colors
    WHITE = (255, 255, 255)
    BACKGROUND_COLOR = (0, 0, 40)
    
    # Game objects
    stars = []
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        stars.append({"x": x, "y": y, "size": size})
    
    # Game state
    game_started = False
    game_over = False
    score = 0
    level = 1
    missile_speed = 5
    missiles_per_wave = 1
    last_level_up = 0
    
    # Create player
    player = Aircraft(WIDTH//2 - 25, HEIGHT - 60)
    missiles = []
    missile_timer = 0
    
    # Add explosions list to game state
    explosions = []
    
    # Create just one planet
    planets = []
    x = random.randint(100, WIDTH-100)
    y = random.randint(-200, -100)  # Start above the screen
    size = random.randint(25, 35)  # Slightly larger size
    planets.append(Planet(x, y, size))
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_started:
                    game_started = True
                elif event.key == pygame.K_r and game_over:
                    # Reset game
                    game_started = False
                    game_over = False
                    score = 0
                    level = 1
                    missile_speed = 5
                    missiles_per_wave = 1
                    last_level_up = 0
                    missiles.clear()
                    player = Aircraft(WIDTH//2 - 25, HEIGHT - 60)
                    # Restart background music
                    try:
                        pygame.mixer.music.play(-1)
                    except:
                        pass
        
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Clear screen
        canvas.fill(BACKGROUND_COLOR)
        
        # Draw stars
        for star in stars:
            pygame.draw.circle(canvas, WHITE, (star["x"], star["y"]), star["size"])
        
        # Update and draw planets
        for planet in planets:
            planet.update()
            planet.draw(canvas)
        
        if not game_started:
            # Draw title screen
            font = pygame.font.Font(None, 74)
            title = font.render("Missile Invasion", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
            canvas.blit(title, title_rect)
            
            font = pygame.font.Font(None, 36)
            text = font.render("Press SPACE to start", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            canvas.blit(text, text_rect)
            
            # Draw controls info
            controls_text = font.render("Arrow keys to move", True, (200, 200, 200))
            controls_rect = controls_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            canvas.blit(controls_text, controls_rect)
        else:
            if not game_over:
                # Move player
                dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player.speed
                dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * player.speed
                player.move(dx, dy)
                
                # Spawn missiles
                missile_timer += 1
                if missile_timer >= max(20, 60 - level * 2):  # Spawn rate increases with level
                    for _ in range(missiles_per_wave):
                        missiles.append(Missile(random.randint(0, WIDTH - 20), missile_speed))
                        try:
                            if "missile" in sounds:
                                sounds["missile"].play()
                        except:
                            pass
                    missile_timer = 0
                
                # Update and check missiles
                for missile in missiles[:]:
                    missile.update()
                    if missile.y > HEIGHT:
                        missiles.remove(missile)
                        score += 1
                        # Level up every 30 points
                        if score > 0 and score % 30 == 0 and score != last_level_up:
                            level += 1
                            missile_speed += 0.5
                            if level % 2 == 0:  # Increase missiles every 2 levels
                                missiles_per_wave += 1
                            last_level_up = score
                            try:
                                if "levelup" in sounds:
                                    sounds["levelup"].play()
                            except:
                                pass
                    elif missile.rect.colliderect(player.rect):
                        game_over = True
                        # Create explosion at collision point
                        explosions.append(Explosion(missile.x + missile.width/2, missile.y + missile.height/2))
                        explosions.append(Explosion(player.x + player.width/2, player.y + player.height/2))
                        # Remove the missile that caused the collision
                        missiles.remove(missile)
                        try:
                            if "explosion" in sounds:
                                sounds["explosion"].play()
                            pygame.mixer.music.stop()
                        except:
                            pass
            
            # Update and draw explosions
            for explosion in explosions[:]:
                explosion.update()
                explosion.draw(canvas)
                if explosion.done:
                    explosions.remove(explosion)
            
            # Draw game objects
            if not game_over:
                player.draw(canvas)
            for missile in missiles:
                missile.draw(canvas)
            
            # Draw game info
            font = pygame.font.Font(None, 36)
            # Score
            score_text = font.render(f"Score: {score}", True, WHITE)
            canvas.blit(score_text, (10, 10))
            # Level
            level_text = font.render(f"Level: {level}", True, WHITE)
            canvas.blit(level_text, (10, 50))
            # Speed
            speed_text = font.render(f"Speed: {missile_speed:.1f}", True, WHITE)
            canvas.blit(speed_text, (10, 90))
            # Missiles per wave
            missile_text = font.render(f"Missiles: {missiles_per_wave}", True, WHITE)
            canvas.blit(missile_text, (10, 130))
            
            # Draw game over screen
            if game_over:
                font = pygame.font.Font(None, 74)
                text = font.render("Game Over!", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
                canvas.blit(text, text_rect)
                
                font = pygame.font.Font(None, 36)
                text = font.render("Press R to restart", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
                canvas.blit(text, text_rect)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main()) 