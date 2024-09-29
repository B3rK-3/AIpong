import pygame as py
import random
import math

# Constants
SPEED = 10
SIDEHEIGHT = 100
TICKSPEED = 30
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)
BALLRADIUS = 10
RECTWIDTH = 10
PADDLE_SPEED = 15

class Pong:
    def __init__(self, w=640, h=480, visualize=True):
        self.w = w
        self.h = h
        self.visualize = visualize
        # init display
        if self.visualize:
            self.display = py.display.set_mode((self.w, self.h))
            py.display.set_caption('Pong')  # Corrected caption
        self.clock = py.time.Clock()
        self.reset()
        
    def reset(self):
        self.xDir = random.uniform(-1, 1)
        self.yDir = random.uniform(-0.45,0.45)
        # Normalize the direction vector
        magnitude = math.sqrt(self.xDir**2 + self.yDir**2)
        self.xDir /= magnitude
        self.yDir /= magnitude

        self.xy = (self.w // 2, self.h // 2)
        
        self.sideOne = [20, self.h // 2]
        self.sideTwo = [self.w - 20, self.h // 2]
        
        self.sideOneSpeed = 0  # Paddle speed
        self.sideTwoSpeed = 0  # Paddle speed
        self.gameOver = False
        
    def checkCollision(self):
        cUp = self.xy[1]-BALLRADIUS
        cBot = self.xy[1]+BALLRADIUS
        cLeft = self.xy[0]-BALLRADIUS
        cRight = self.xy[0]+BALLRADIUS
        
        # Collision with top or bottom wall
        if cBot >= self.h or cUp <= 0:
            self.yDir = -self.yDir
            
        if cRight >= self.w:
            self.gameOver = True
        elif cLeft <= 0:
            self.gameOver = True
            
        if cRight >= self.sideTwo[0]+RECTWIDTH//2:
            return
        elif cLeft <= self.sideOne[0]-RECTWIDTH//2:
            return
        
        # Collision with paddles
        if cRight >= self.sideTwo[0]-RECTWIDTH//2 and self.sideTwo[1]-SIDEHEIGHT//2 <= self.xy[1] <= self.sideTwo[1] + SIDEHEIGHT//2:
            self.xDir = -self.xDir
            self.yDir += self.sideTwoSpeed / 50  # Adjust the y-direction based on paddle speed

        if cLeft <= self.sideOne[0]+RECTWIDTH//2 and self.sideOne[1]-SIDEHEIGHT//2 <= self.xy[1] <= self.sideOne[1] + SIDEHEIGHT//2:
            self.xDir = -self.xDir
            self.yDir += self.sideOneSpeed / 50  # Adjust the y-direction based on paddle speed

    def move(self):
        self.xy = (self.xy[0]+SPEED*self.xDir, self.xy[1]+SPEED*self.yDir)
        self.sideTwo[1] = self.xy[1]
    
    def updateGame(self):
        self.display.fill(BLACK)
        py.draw.circle(self.display, RED, self.xy, BALLRADIUS)
        py.draw.rect(self.display, BLUE1, py.Rect(self.sideOne[0]-RECTWIDTH//2, self.sideOne[1]-SIDEHEIGHT//2, RECTWIDTH, SIDEHEIGHT))
        py.draw.rect(self.display, BLUE1, py.Rect(self.sideTwo[0]-RECTWIDTH//2, self.sideTwo[1]-SIDEHEIGHT//2, RECTWIDTH, SIDEHEIGHT))
        py.display.flip()
    
    def run_one_frame(self):
        # Get pressed keys for paddle movement
        keys = py.key.get_pressed()
        
        # Track previous positions to calculate speed
        previous_sideOne_pos = self.sideOne[1]
        previous_sideTwo_pos = self.sideTwo[1]
        
        # Paddle 1 movement (W and S keys)
        if keys[py.K_UP] and self.sideOne[1] - SIDEHEIGHT//2 > 0:
            self.sideOne[1] -= PADDLE_SPEED
        if keys[py.K_DOWN] and self.sideOne[1] + SIDEHEIGHT//2 < self.h:
            self.sideOne[1] += PADDLE_SPEED
        
        """# Paddle 2 movement (Up and Down arrow keys)
        if keys[py.K_UP] and self.sideTwo[1] - SIDEHEIGHT//2 > 0:
            self.sideTwo[1] -= PADDLE_SPEED
        if keys[py.K_DOWN] and self.sideTwo[1] + SIDEHEIGHT//2 < self.h:
            self.sideTwo[1] += PADDLE_SPEED"""

        # Calculate paddle speeds based on movement
        self.sideOneSpeed = self.sideOne[1] - previous_sideOne_pos
        """self.sideTwoSpeed = self.sideTwo[1] - previous_sideTwo_pos"""

        # Run game logic
        if not self.gameOver:
            self.move()
            self.checkCollision()
            if self.visualize:
                self.updateGame()
            self.clock.tick(TICKSPEED)
        
# Initialize pygame
py.init()

# Create the game object
game = Pong()

# Main loop, handle events, and run one frame at a time
running = True
while running:
    if game.gameOver:
        break
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
    
    # Run one frame of the game
    game.run_one_frame()

# Clean up pygame
py.quit()
