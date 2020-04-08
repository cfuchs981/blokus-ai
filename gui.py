# Import the pygame module
import pygame

# Initialize pygame
pygame.init()

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


# Define constants for the screen width and height
SCREEN_WIDTH = 840
SCREEN_HEIGHT = 840

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Fill the screen with white
screen.fill((255, 255, 255))

def render(board):
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                pygame.exit()
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            pygame.exit()
    
    y = 0
    for i in range(len(board)):   
        x = 0
        for j in range(len(board[i])):
            #print("The current element is " + str(board[i][j]))
            if(board[i][j] == 1):
                pygame.draw.rect(screen,(0, 0, 255), (x, y, 60, 60), 0)
            elif(board[i][j] == 2):
                pygame.draw.rect(screen, (0, 255, 0), (x, y, 60, 60), 0)
            x += 60
        y += 60    
    
    for i in range(60, 821, 60):
       pygame.draw.line(screen, (250,0,0), (i, 0), (i, 840), 2)
       pygame.draw.line(screen, (250,0,0), (0, i), (840, i), 2)
    
    # Update the display
    pygame.display.flip()
    
    
