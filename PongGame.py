import pygame as py
import random
import math

# Initialize pygame
py.init()

font = py.font.SysFont('Roboto',25)

# Constants
MAX_SPEED = 20
BASE_SPEED = 15
SPEED_INCREASE_FACTOR = 0.5  # Adjusts how much the paddle's speed affects the ball
DECELERATION = 0.1           # Rate at which the ball slows down
SIDEHEIGHT = 100
TICKSPEED = 100
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
BALLRADIUS = 10
RECTWIDTH = 10
PADDLE_SPEED = 15


class Pong:
    def __init__(self, w=640, h=480, visualize=True):
        self.speedInc = 0
        self.score = 0
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
        # Randomly choose left or right direction
        direction = random.choice([-1, 1])
        # Define the minimum and maximum angles in radians
        min_angle = math.radians(15)
        max_angle = math.radians(50)  # Adjust as needed (up to 90 degrees)
        # Randomly choose an angle between min_angle and max_angle
        angle = random.uniform(min_angle, max_angle)
        # Randomly decide if the angle is positive or negative
        angle *= random.choice([-1, 1])
        # Set the initial speed
        speed = BASE_SPEED+self.speedInc
        # Set the velocity components
        self.xSpeed = direction * speed * math.cos(angle)
        self.ySpeed = speed * math.sin(angle)

        # Reset ball position
        self.xy = (self.w // 2, self.h // 2)
        
        self.sideOne = [20, self.h // 2]
        self.playerTop = self.sideOne[1]+SIDEHEIGHT//2
        self.playerBottom = self.sideOne[1]-SIDEHEIGHT//2
        self.playerRight = self.sideOne[0]+RECTWIDTH//2
        
        self.sideTwo = [self.w - 20, self.h // 2]
        
        self.sideOneSpeed = 0  # Paddle speed
        self.sideTwoSpeed = 0  # Paddle speed
        self.gameOver = False
        self.score = 0
        
    def checkCollision(self):
        reward = 0
        cUp = self.xy[1] - BALLRADIUS
        cBot = self.xy[1] + BALLRADIUS
        cLeft = self.xy[0] - BALLRADIUS
        cRight = self.xy[0] + BALLRADIUS

        # Collision with top or bottom wall
        if cBot >= self.h:
            self.ySpeed = -abs(self.ySpeed)
            self.xy = (self.xy[0], self.h - BALLRADIUS)
        if cUp <= 0:
            self.ySpeed = abs(self.ySpeed)
            self.xy = (self.xy[0], BALLRADIUS)

        # Ball out of bounds (Game Over conditions)
        if cLeft <= 0:
            self.gameOver = True
            return -1

        # Collision with sideOne (left paddle)
        if cLeft <= self.sideOne[0] + RECTWIDTH//2 and cRight >= self.sideOne[0] - RECTWIDTH//2:
            if self.sideOne[1] - SIDEHEIGHT//2 <= self.xy[1] <= self.sideOne[1] + SIDEHEIGHT//2:
                # Reverse xSpeed
                self.xSpeed = -self.xSpeed
                # Increase xSpeed based on paddle speed
                speed_increase = abs(self.sideOneSpeed) * SPEED_INCREASE_FACTOR
                self.xSpeed += speed_increase * (1 if self.xSpeed > 0 else -1)
                # Cap xSpeed to MAX_SPEED
                if abs(self.xSpeed) > MAX_SPEED:
                    self.xSpeed = MAX_SPEED * (1 if self.xSpeed > 0 else -1)
                # Adjust ball position to prevent sticking
                self.xy = (self.sideOne[0] + RECTWIDTH//2 + BALLRADIUS, self.xy[1])
                self.score+=1
                self.speedInc+=0.1
                reward+=1

        # Collision with sideTwo (right paddle)
        if cRight >= self.sideTwo[0] - RECTWIDTH//2 and cLeft <= self.sideTwo[0] + RECTWIDTH//2:
            if self.sideTwo[1] - SIDEHEIGHT//2 <= self.xy[1] <= self.sideTwo[1] + SIDEHEIGHT//2:
                # Reverse xSpeed
                self.xSpeed = -self.xSpeed
                # Adjust ball position to prevent sticking
                self.xy = (self.sideTwo[0] - RECTWIDTH//2 - BALLRADIUS, self.xy[1])
        return reward
                
    def move(self):
        # Update position
        self.xy = (
            self.xy[0] + self.xSpeed,
            self.xy[1] + self.ySpeed
        )
        # Decrease xSpeed incrementally until it reaches BASE_SPEED
        if abs(self.xSpeed) > BASE_SPEED+self.speedInc:
            speed_diff = abs(self.xSpeed) - BASE_SPEED
            deceleration = DECELERATION
            if speed_diff > deceleration:
                self.xSpeed -= deceleration * (1 if self.xSpeed > 0 else -1)
            else:
                self.xSpeed = (BASE_SPEED+self.speedInc) * (1 if self.xSpeed > 0 else -1)
        self.sideTwo[1] = self.xy[1]
        
        self.playerTop = self.sideOne[1]+SIDEHEIGHT//2
        self.playerBottom = self.sideOne[1]-SIDEHEIGHT//2
        self.playerRight = self.sideOne[0]+RECTWIDTH//2
    
    def updateGame(self):
        self.display.fill(BLACK)
        py.draw.circle(self.display, RED, self.xy, BALLRADIUS)
        py.draw.rect(self.display, BLUE1, py.Rect(self.sideOne[0]-RECTWIDTH//2, self.sideOne[1]-SIDEHEIGHT//2, RECTWIDTH, SIDEHEIGHT))
        py.draw.rect(self.display, BLUE1, py.Rect(self.sideTwo[0]-RECTWIDTH//2, self.sideTwo[1]-SIDEHEIGHT//2, RECTWIDTH, SIDEHEIGHT))
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [self.w//2, 0])
        py.display.flip()
    
    def run_one_frame(self, move):
        reward = 0.1
        # Get pressed keys for paddle movement
        keys = py.key.get_pressed()
        
        # Track previous positions to calculate speed
        previous_sideOne_pos = self.sideOne[1]
        previous_sideTwo_pos = self.sideTwo[1]
        
        # Paddle 1 movement (Up and Down arrow keys)
        if move[0] and self.sideOne[1] - SIDEHEIGHT//2 > 0:
            self.sideOne[1] -= PADDLE_SPEED
        elif move[1] and self.sideOne[1] + SIDEHEIGHT//2 < self.h:
            self.sideOne[1] += PADDLE_SPEED

        # Calculate paddle speeds based on movement
        self.sideOneSpeed = self.sideOne[1] - previous_sideOne_pos

        # Run game logic
        if not self.gameOver:
            self.move()
            reward = self.checkCollision()
            if self.score > 1000:
                print(self.score)
            if self.visualize:
                self.updateGame()
                self.clock.tick(TICKSPEED)
            return reward, self.gameOver, self.score
        else:
            return -10, True, self.score
