#Import relevant libraries
import pygame
from config import * 
import math
import random
import copy

# Define a class named Spritesheet
class Spritesheet:
    # Initialize the class with a file parameter
    def __init__(self, file):
        # Load the image file and convert it to the appropriate format
        self.sheet = pygame.image.load(file).convert()

    # Define a method to extract a sprite from the spritesheet
    def getSprite(self, x, y, width, height, ar):
        # Create a new surface with the specified width and height
        sprite = pygame.Surface([width, height])
        
        # Copy a portion of the spritesheet onto the new surface
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        
        # Scale the sprite using the provided aspect ratio
        sprite = pygame.transform.scale(sprite, ((TILE_SIZE * ar), (TILE_SIZE * ar)))
        
        # Set the color key to make the background transparent
        sprite.set_colorkey(BLACK)
        
        # Return the resulting sprite
        return sprite

# Define a class named Player that inherits from pygame.sprite.Sprite
class Player(pygame.sprite.Sprite):
    # Initialize the player with the game instance, initial x, and y coordinates
    def __init__(self, game, x, y):

        # Set the game instance and layer for sprite ordering
        self.game = game
        self._layer = PLAYER_LAYER

        # Call the constructor of the superclass (pygame.sprite.Sprite)
        self.groups = self.game.all_sprites 
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set the initial values for player attributes
        self.x_change = 0
        self.y_change = 0
        self.total_y_change = 0
        self.facing = 'down'
        self.animation_loop = 1

        # Calculate initial pixel coordinates based on TILE_SIZE
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = RENDER_SIZE
        self.height = RENDER_SIZE

        # Get the initial sprite image from the character_spritesheet
        self.image = self.game.character_spritesheet.getSprite(0, 0, self.width, self.height, PLAYER_RATIO)

        # Set the initial rectangle properties
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Apply offsets to the rectangle position
        self.rect.x += X_OFFSET
        self.rect.y += Y_OFFSET

        # Define animations for different directions
        self.down_animations = [self.game.character_spritesheet.getSprite(0, 0, self.width, self.height, PLAYER_RATIO),
                                self.game.character_spritesheet.getSprite(32, 0, self.width, self.height, PLAYER_RATIO),
                                self.game.character_spritesheet.getSprite(64, 0, self.width, self.height, PLAYER_RATIO)]

        self.up_animations = [self.game.character_spritesheet.getSprite(0, 32, self.width, self.height, PLAYER_RATIO),
                              self.game.character_spritesheet.getSprite(32, 32, self.width, self.height, PLAYER_RATIO),
                              self.game.character_spritesheet.getSprite(64, 32, self.width, self.height, PLAYER_RATIO)]

        self.left_animations = [self.game.character_spritesheet.getSprite(0, 96, self.width, self.height, PLAYER_RATIO),
                                self.game.character_spritesheet.getSprite(32, 96, self.width, self.height, PLAYER_RATIO),
                                self.game.character_spritesheet.getSprite(64, 96, self.width, self.height, PLAYER_RATIO)]

        self.right_animations = [self.game.character_spritesheet.getSprite(0, 64, self.width, self.height, PLAYER_RATIO),
                                 self.game.character_spritesheet.getSprite(32, 64, self.width, self.height, PLAYER_RATIO),
                                 self.game.character_spritesheet.getSprite(64, 64, self.width, self.height, PLAYER_RATIO)]

    # Check for collisions with blocks in the specified direction
    def collideBlocks(self, direction):
        if direction == 'x':
            # Check for collisions with blocks in the x-direction
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    # Adjust player position and other sprites when moving right
                    self.rect.x = hits[0].rect.left - self.rect.width
                    for sprite in self.game.all_sprites:
                        sprite.rect.x += PLAYER_SPEED
                if self.x_change < 0:
                    # Adjust player position and other sprites when moving left
                    for sprite in self.game.all_sprites:
                        sprite.rect.x -= PLAYER_SPEED
                    self.rect.x = hits[0].rect.right

        if direction == 'y':
            # Check for collisions with blocks in the y-direction
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    # Adjust player position and total_y_change when moving down
                    for sprite in self.game.all_sprites:
                        sprite.rect.y += PLAYER_SPEED
                    self.total_y_change -= PLAYER_SPEED
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    # Adjust player position and total_y_change when moving up
                    for sprite in self.game.all_sprites:
                        sprite.rect.y -= PLAYER_SPEED
                    self.total_y_change += PLAYER_SPEED
                    self.rect.y = hits[0].rect.bottom

    # Check for collisions with enemies and handle player elimination
    def collideEnemy(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            # Eliminate the player and end the game when colliding with enemies
            self.kill()
            self.game.playing = False
    # Define a method to handle animation of the player character
    def animate(self):
        # Check the facing direction and update the player's image accordingly
        if self.facing == 'down':
            if self.y_change == 0:
                # Set the default down-facing image when not moving vertically
                self.image = self.game.character_spritesheet.getSprite(0, 0, self.width, self.height, PLAYER_RATIO)
            else:
                # Set the animation based on the down_animations list
                self.image = self.down_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        if self.facing == 'up':
            if self.y_change == 0:
                # Set the default up-facing image when not moving vertically
                self.image = self.game.character_spritesheet.getSprite(0, 32, self.width, self.height, PLAYER_RATIO)
            else:
                # Set the animation based on the up_animations list
                self.image = self.up_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        if self.facing == 'left':
            if self.x_change == 0:
                # Set the default left-facing image when not moving horizontally
                self.image = self.game.character_spritesheet.getSprite(0, 96, self.width, self.height, PLAYER_RATIO)
            else:
                # Set the animation based on the left_animations list
                self.image = self.left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        if self.facing == 'right':
            if self.x_change == 0:
                # Set the default right-facing image when not moving horizontally
                self.image = self.game.character_spritesheet.getSprite(0, 64, self.width, self.height, PLAYER_RATIO)
            else:
                # Set the animation based on the right_animations list
                self.image = self.right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

    # Define a method to update the player's state
    def update(self):
        # Call various methods to handle player movement, enemy proximity, animation, and collision detection
        self.movement()
        self.enemyClose()
        self.animate()
        self.collideEnemy()
        self.rect.x += self.x_change
        self.collideBlocks('x')
        self.rect.y += self.y_change
        self.collideBlocks('y')
        self.passedFinnish()

        # Reset movement values for the next update
        self.x_change = 0
        self.y_change = 0
    # Define a method to check the proximity to an enemy and adjust volume accordingly
    def enemyClose(self):
        # Call the method to find the nearest enemy
        self.findEnemy()
        if self.enemy:
            # Calculate the Euclidean distance between player and enemy and adjust volume
            distance = math.sqrt((self.rect.x // TILE_SIZE - self.enemy.rect.x // TILE_SIZE) ** 2 +
                                (self.rect.y // TILE_SIZE - self.enemy.rect.y // TILE_SIZE) ** 2)
            self.adjustVolume(distance)

    # Define a method to adjust the volume of the enemy step sound based on distance
    def adjustVolume(self, distance):
        if distance > 9:
            # Set volume to 0 if the distance is more than 7 tiles
            self.game.enemy_step.set_volume(0)
        elif 6 <= distance <= 9:
            # Set volume to 0.2 if the distance is between 5 and 7 tiles (inclusive)
            self.game.enemy_step.set_volume(0.2)
        elif 4 <= distance < 6:
            # Set volume to 0.5 if the distance is between 3 and 5 tiles (exclusive)
            self.game.enemy_step.set_volume(0.5)
        elif distance < 4:
            # Set volume to 1 if the distance is less than 3 tiles
            self.game.enemy_step.set_volume(1)

    # Define a method to find the nearest enemy in the game
    def findEnemy(self):
        for sprite in self.game.all_sprites:
            if isinstance(sprite, Enemy):
                # Update the player's reference to the nearest enemy
                self.enemy = sprite

    # Define a method to check if the player has passed the finish line
    def passedFinnish(self):
        if (36 * TILE_SIZE) < self.total_y_change:
            # Set win flag to True and end the game if the player passed the finish line
            self.game.win = True
            with open(self.game.records, "a") as file:
                file.write(str(self.game.time_elapsed[0]) + ":" + str(self.game.time_elapsed[1]))
            self.game.playing = False
    # Define a method to handle player movement based on key inputs
    def movement(self):
        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Check if the 'A' key is pressed, adjust x_change and set facing direction
        if keys[pygame.K_a]:
            for sprite in self.game.all_sprites:
                sprite.rect.x += PLAYER_SPEED
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'

        # Check if the 'D' key is pressed, adjust x_change and set facing direction
        if keys[pygame.K_d]:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= PLAYER_SPEED
            self.x_change += PLAYER_SPEED
            self.facing = 'right'

        # Check if the 'W' key is pressed, adjust y_change and total_y_change, set facing direction
        if keys[pygame.K_w]:
            for sprite in self.game.all_sprites:
                sprite.rect.y += PLAYER_SPEED
            self.total_y_change -= PLAYER_SPEED
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'

        # Check if the 'S' key is pressed, adjust y_change and total_y_change, set facing direction
        if keys[pygame.K_s]:
            for sprite in self.game.all_sprites:
                sprite.rect.y -= PLAYER_SPEED
            self.total_y_change += PLAYER_SPEED
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

# Define a class named Block that inherits from pygame.sprite.Sprite
class Block(pygame.sprite.Sprite):
    # Initialize the Block with the game instance, x, and y coordinates
    def __init__(self, game, x, y):

        # Set the game instance, layer for sprite ordering, and groups for sprite management
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks

        # Call the constructor of the superclass (pygame.sprite.Sprite)
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Calculate initial pixel coordinates based on TILE_SIZE
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = RENDER_SIZE
        self.height = RENDER_SIZE

        # Get the initial sprite image from the wall_tile Spritesheet
        self.image = self.game.wall_tile.getSprite(0, 0, self.width, self.height, REGULAR_RATIO)

        # Set the initial rectangle properties
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Apply offsets to the rectangle position
        self.rect.x += X_OFFSET
        self.rect.y += Y_OFFSET

# Define a class named Enemy that inherits from pygame.sprite.Sprite
        
# Define a class for the Ground sprite in the game
class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Initialize the Ground sprite with references to the game and rendering layer
        self.game = game
        self._layer = GROUND_LAYER

        # Add the sprite to the 'all_sprites' group
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set the initial position and size of the Ground sprite
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = RENDER_SIZE
        self.height = RENDER_SIZE

        # Create the image for the Ground sprite using the game's floor_tile
        self.image = self.game.floor_tile.getSprite(0, 0, self.width, self.height, REGULAR_RATIO)

        # Set the rect attributes for collision detection and rendering
        self.rect = self.image.get_rect()
        self.rect.x = self.x 
        self.rect.y = self.y

        # Apply X and Y offsets to center the sprite on the game screen
        self.rect.x += X_OFFSET
        self.rect.y += Y_OFFSET

class Enemy(pygame.sprite.Sprite):
    # Initialize the Enemy with the game instance, x, and y coordinates
    def __init__(self, game, x, y):

        # Set the game instance, layer for sprite ordering, and groups for sprite management
        self.game = game
        self._layer = ENEMY_LAYER

        # Call the constructor of the superclass (pygame.sprite.Sprite)
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Initialize attributes for player tracking, position, size, and movement
        self.player = None
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = RENDER_SIZE
        self.height = RENDER_SIZE
        self.x_change = 0
        self.y_change = 0
        self.tick = 59
        self.animation_loop = 1
        self.facing = "down"
        self.facing_other = "up"
        self.first_time = True

        # Set the initial sprite image from the enemy_spritesheet
        self.image = self.game.enemy_spritesheet.getSprite(3, 2, self.width, self.height, REGULAR_RATIO)
        self.image.set_colorkey(BLACK)

        # Set the initial rectangle properties
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Apply offsets to the rectangle position
        self.rect.x += X_OFFSET
        self.rect.y += Y_OFFSET

        # Define animations for different directions
        self.down_animations = [self.game.enemy_spritesheet.getSprite(0, 0, self.width, self.height, REGULAR_RATIO),
                                self.game.enemy_spritesheet.getSprite(32, 0, self.width, self.height, REGULAR_RATIO),
                                self.game.enemy_spritesheet.getSprite(64, 0, self.width, self.height, REGULAR_RATIO)]

        self.up_animations = [self.game.enemy_spritesheet.getSprite(0, 32, self.width, self.height, REGULAR_RATIO),
                              self.game.enemy_spritesheet.getSprite(32, 32, self.width, self.height, REGULAR_RATIO),
                              self.game.enemy_spritesheet.getSprite(64, 32, self.width, self.height, REGULAR_RATIO)]

        self.right_animations = [self.game.enemy_spritesheet.getSprite(0, 96, self.width, self.height, REGULAR_RATIO),
                                 self.game.enemy_spritesheet.getSprite(32, 96, self.width, self.height, REGULAR_RATIO),
                                 self.game.enemy_spritesheet.getSprite(64, 96, self.width, self.height, REGULAR_RATIO)]

        self.left_animations = [self.game.enemy_spritesheet.getSprite(0, 64, self.width, self.height, REGULAR_RATIO),
                                self.game.enemy_spritesheet.getSprite(32, 64, self.width, self.height, REGULAR_RATIO),
                                self.game.enemy_spritesheet.getSprite(64, 64, self.width, self.height, REGULAR_RATIO)]

    # Define a method to update the enemy's state
    def update(self):
        self.movement()
        self.animate()
        self.rect.x += self.x_change
        self.collideBlocks('x')
        self.collideGround('x')
        self.rect.y += self.y_change
        self.collideBlocks('y')
        self.collideGround('y')

        # Reset movement values for the next update
        self.x_change = 0
        self.y_change = 0
    # Define a method to handle enemy movement
    def movement(self):
        # Call the method to determine the blocked view and choose a path
        self.blockedView()

    # Define a method to determine the blocked view and choose a path for enemy movement
    def blockedView(self):
        # Call the method to choose a path
        self.choosePath()

        # Check the chosen path and update the positions of sprites and the enemy accordingly
        if self.choice[1] == "left":
            self.rect.x -= ENEMY_SPEED
            self.facing = "left"
            self.facing_other = "right"
        elif self.choice[1] == "right":
            self.rect.x += ENEMY_SPEED
            self.facing = "right"
            self.facing_other = "left"
        elif self.choice[1] == "up":
            self.rect.y -= ENEMY_SPEED
            self.facing = "up"
            self.facing_other = "down"
        elif self.choice[1] == "down":
            self.rect.y += ENEMY_SPEED
            self.facing = "down"
            self.facing_other = "up"

    # Define a method to choose a path for enemy movement
    def choosePath(self):
        # Save the current x and y positions
        self.saved_x = copy.copy(self.rect.x)
        self.saved_y = copy.copy(self.rect.y)

        # Check for movement to the left
        self.rect.x -= 1
        self.x_change -= 1
        self.collideBlocks('x')
        self.collideGround('x')
        if self.saved_x == self.rect.x:
            move_left = [False, "left"]
        else:
            self.rect.x += 1
            move_left = [True, "left"]

        self.x_change = 0

        # Check for movement to the right
        self.rect.x += 1
        self.x_change += 1
        self.collideBlocks('x')
        self.collideGround('x')
        if self.saved_x == self.rect.x:
            move_right = [False, "right"]
        else:
            self.rect.x -= 1
            move_right = [True, "right"]

        self.x_change = 0

        # Check for movement down
        self.rect.y += 1
        self.y_change += 1
        self.collideBlocks('y')
        self.collideGround('y')
        if self.saved_y == self.rect.y:
            move_down = [False, "down"]
        else:
            self.rect.y -= 1
            move_down = [True, "down"]

        self.y_change = 0

        # Check for movement up
        self.rect.y -= 1
        self.y_change -= 1
        self.collideBlocks('y')
        self.collideGround('y')
        if self.saved_y == self.rect.y:
            move_up = [False, "up"]
        else:
            move_up = [True, "up"]
            self.rect.y += 1

        self.y_change = 0

        # Combine all possible moves into a list
        all_moves = [move_left, move_right, move_up, move_down]
        i = 0
        first_time = True

        # Choose a random move until a valid and non-repeated one is found
        while i < 1:
            # Append the last chosen move if it's not the first time
            if first_time == False:
                all_moves.append(self.choice)
            
            # Generate a random integer to choose a move from the list
            self.random_integer = random.randint(0, 3)
            self.choice = all_moves[self.random_integer]

            # Remove the chosen move from the list
            all_moves.pop(self.random_integer)
            first_time = False

            # Check if the chosen move is valid and not the opposite direction
            if all(self.choice[0] != other_choice[0] for other_choice in all_moves) and self.choice[0]:
                i += 1
            if self.choice[0] and self.facing_other != self.choice[1]:
                i += 1
    # Define a method to handle collisions with blocks in the x and y directions
    def collideBlocks(self, direction):
        if direction == 'x':
            # Check for collisions with blocks in the x direction
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                # Adjust the player's x position based on the collision direction
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right

        elif direction == 'y':
            # Check for collisions with blocks in the y direction
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                # Adjust the player's y position based on the collision direction
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom

    # Define a method to handle collisions with ground objects in the x and y directions
    def collideGround(self, direction):
        if direction == 'x':
            # Check for collisions with ground objects in the x direction
            hits = pygame.sprite.spritecollide(self, self.game.blocked_path, False)
            if hits:
                # Adjust the player's x position based on the collision direction
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right

        elif direction == 'y':
            # Check for collisions with ground objects in the y direction
            hits = pygame.sprite.spritecollide(self, self.game.blocked_path, False)
            if hits:
                # Adjust the player's y position based on the collision direction
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom

    # Define a method to animate the player based on the facing direction
    def animate(self):
        if self.facing == 'down':
            # Set the player's image to the appropriate down-facing animation frame
            self.image = self.down_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.1
            # Loop the animation if it reaches the end
            if self.animation_loop >= 3:
                self.animation_loop = 1
        elif self.facing == 'up':
            # Set the player's image to the appropriate up-facing animation frame
            self.image = self.up_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.1
            # Loop the animation if it reaches the end
            if self.animation_loop >= 3:
                self.animation_loop = 1
        elif self.facing == 'left':
            # Set the player's image to the appropriate left-facing animation frame
            self.image = self.left_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.1
            # Loop the animation if it reaches the end
            if self.animation_loop >= 3:
                self.animation_loop = 1
        elif self.facing == 'right':
            # Set the player's image to the appropriate right-facing animation frame
            self.image = self.right_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.1
            # Loop the animation if it reaches the end
            if self.animation_loop >= 3:
                self.animation_loop = 1

# Define a class for creating buttons
class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        # Initialize the font and button content
        self.font = pygame.font.Font("comici.ttf", fontsize)
        self.content = content
        
        # Set button position and dimensions
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Set text and background colors
        self.fg = fg
        self.bg = bg

        # Create a surface for the button and fill it with the background color
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()
        
        # Set the button's position
        self.rect.x = self.x
        self.rect.y = self.y

        # Render the text and center it on the button surface
        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    # Define a method to check if the button is pressed
    def isPressed(self, pos, pressed):
        # Check if the mouse position collides with the button's rect
        if self.rect.collidepoint(pos):
            # Check if the left mouse button is pressed
            if pressed[0]:
                return True
            return False
        return False
# Define a class for creating ground objects that block paths
class blockedGround(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Initialize the ground object with references to the game and sprite groups
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites, self.game.blocked_path
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Set the initial position and dimensions of the ground object
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = RENDER_SIZE
        self.height = RENDER_SIZE

        # Create the image for the ground object using a floor tile
        self.image = self.game.floor_tile.getSprite(0, 0, self.width, self.height, REGULAR_RATIO)

        # Create a rect object to represent the position and dimensions of the ground object
        self.rect = self.image.get_rect()
        self.rect.x = self.x 
        self.rect.y = self.y

        # Adjust the rect object's position based on offsets
        self.rect.x += X_OFFSET
        self.rect.y += Y_OFFSET



