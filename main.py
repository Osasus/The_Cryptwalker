#Import all relevant libraries
import pygame
from sprites import *
from config import *
import sys
from moviepy.editor import*
import time

#The class for the main loop of the game
class Game:
    #Initialize the class
    def __init__(self):
        pygame.init()
        #Set the screen size
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        #Set screen to fullscreen
        pygame.display.toggle_fullscreen()
        #Set a variable for the tickrate
        self.clock = pygame.time.Clock()
        #Variables to say if you're in the game or not 
        self.running = True
        #Variable to say if you've won
        self.win = False

        self.records = "local_record.txt"
        #Import a font
        self.font = pygame.font.Font("comici.ttf", 32)

        #Import graphics (Spritesheets, pictures)
        self.character_spritesheet = Spritesheet('img/character.png')
        self.terrain_spritesheet = Spritesheet('img/terrain.png')
        self.enemy_spritesheet = Spritesheet('img/enemy.png')
        self.floor_tile = Spritesheet('img/nedladdning.png')
        self.wall_tile = Spritesheet('img/Floor_Tile.png')
        self.intro_background = pygame.image.load('img/Front_Page.png')
        self.win_background = pygame.image.load('img/escape.png')
        self.go_background = pygame.image.load('img/jumpscare.png')

        #Import audio files / Set the volume of the audio files
        self.background_audio = pygame.mixer.Sound('audio/Creepy Dark Villain Theme _Lurking Evil_ Royalty Free Music Update.mp3')
        self.background_audio.set_volume(0.1)
        self.intro_audio = pygame.mixer.Sound('audio/ROYALTY FREE Elevator Music _ Waiting Music Royalty Free _ Muzak _ Royalty Free Jazz Music (1).mp3')
        self.intro_audio.set_volume(0.3)
        self.death_screen = pygame.mixer.Sound('audio/jumpscare_audio.mp3')
        self.win_audio = pygame.mixer.Sound('audio/celtic_music.mp3') 
        self.win_audio.set_volume(0.5)
        self.enemy_step = pygame.mixer.Sound('audio/Fast Heartbeat Sound Effects _ Sound Effects For Editor soundeffects.mp3')
        self.enemy_step.set_volume(0)

        self.jumpscare = VideoFileClip('audio/jumpscare_video.mp4')


    #Function to create the map
    def createTilemap(self):
        #Go through every row and column in the tilemap
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                #Set everything as ground
                Ground(self, j, i)
                #If the tile is 2 make it a blockedGround sprite
                if column == 2:
                    blockedGround(self, j, i)
                #If the tile is 0 make it a unpassable block sprite
                if column == 0:
                    Block(self, j, i)
                #If the tile is "P" spawn the player there
                if column == "P":
                    Player(self, j, i)
                #If the tile is "E" place the enemy there
                if column == "E":
                    Enemy(self,j,i)

    #Function to generate a randomized maze
    def generateMaze(self, grid, current_cell):
        row, col = current_cell
        grid[row][col] = 1  # Mark the current cell as visited

        # Possible directions to move
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        #Randomly shuffle the array
        random.shuffle(directions)
        for dr, dc in directions:
            #Add a direction in directions to variables
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < ROW_SIZE and 0 <= new_col < COLUMN_SIZE and grid[new_row][new_col] == 0:
                # If the neighbor is not visited, carve a path and recursively visit it
                grid[row + dr // 2][col + dc // 2] = "1"
                
                self.generateMaze(grid, (new_row, new_col))
            else:
                self.maze_grid = grid

    #Function to import the randomized maze to the tilemap
    def convertMaze(self, grid):
        #Set counting variables
        i = 0
        j = 0

        while i < len(tilemap):
            #Sets the interval in where the maze should be placed in the tilemap
            if i < 6 or i >= 37:
                i+=1
            else:
                while j < len(tilemap[i]):
                    #Sets the interval in where the maze should be placed in the tilemap
                    if j < 1 or j >= 41:
                        j += 1
                    else:
                        #Replace each tile of the tilemap with the corresponding tile in the grid
                        tilemap[i][j] = grid[i - 6][j - 1]
                        j += 1
            i += 1
            j = 0

        #Set the tile below the start to always be a path, so you're never stuck
        tilemap[6][1] = 1

        #Set the enemy spawn above the exit
        tilemap[36][19] = "E"


    #Function to start a new game

    def new(self):
        # a new game starts
        pygame.mixer.stop() #Stop all previous music
        self.playing = True #Variable thats says you're in the main game
        self.win = False
        timer_minutes = 0
        self.timer_seconds = time.perf_counter()
        self.time_elapsed = [timer_minutes, self.timer_seconds]
        self.timer_counter = 1

        #Set up sprite groups
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.outside_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.blocked_path = pygame.sprite.LayeredUpdates()

        #Prepare the variable for the maze generation
        self.maze_grid = [[0] * COLUMN_SIZE for _ in range(ROW_SIZE)]

        #Call the creation of the maze
        self.generateMaze(self.maze_grid, (0,0))
        self.convertMaze(self.maze_grid)
        self.createTilemap()
        self.timer = self.font.render(str(self.time_elapsed[0]) + ':' + str(self.time_elapsed[1]), True, WHITE)
        self.timer_rect = self.timer.get_rect(center=(WIN_WIDTH - 50, 50))

        #Start background audio (loop it)
        self.background_audio.play(loops = -1)
        self.enemy_step.play(loops = -1)

    #Check if you quit the game and end the game if you do
    def events(self):
        #game loop events
        for event in pygame.event.get():
           if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        #game loop updates
        self.all_sprites.update()
        self.timerUpdate()

    def timerUpdate(self):
        self.time_elapsed[1] = int((time.perf_counter() - self.timer_seconds)) % 60
        if self.time_elapsed[1] == 0 and self.timer_counter == 0:
            self.time_elapsed[0] += 1
            self.timer_counter += 1
        elif self.time_elapsed[1] != 0:
            self.timer_counter = 0
        self.timer = self.font.render(str(self.time_elapsed[0]) + ':' + str(self.time_elapsed[1]%60), True, WHITE)
        self.screen.blit(self.timer, self.timer_rect)
        pygame.display.update()

    #Draw everything on the screen
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)

    #The main loop of the game
    def main(self):
        # game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    #Function for the death screen of the game
    def gameOver(self):

        #Stop all music
        pygame.mixer.stop()

        self.jumpscare.preview()

        #Create text for the screen
        text = self.font.render('You Died', True, WHITE)
        #Create a hitbox for the text aswell as align it
        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))

        #Create a restart button and a quit button
        restart_button = Button(10, WIN_HEIGHT-60, 120, 50, WHITE, BLACK, 'Restart', 32)
        quit_button = Button(140, WIN_HEIGHT-60, 120, 50,WHITE, BLACK, 'QUIT', 32)

        #Remove the game map and entities
        for sprite in self.all_sprites:
            sprite.kill()

# Create a loop for handling events when the game is not playing
        while self.running and not self.playing:
            # Check for events in the event queue
            for event in pygame.event.get():
                # Check if the user closes the game window
                if event == pygame.QUIT:
                    self.running = False

            # Get the current mouse position and button press status
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            # Check if the restart button is pressed
            if restart_button.isPressed(mouse_pos, mouse_pressed):
                # Start a new game
                self.new()

            # Check if the quit button is pressed
            if quit_button.isPressed(mouse_pos, mouse_pressed):
                # Exit the game
                self.playing = False
                pygame.quit()
                sys.exit

            # Draw the text, quit button, and restart button on the screen
            self.screen.blit(text, text_rect)
            self.screen.blit(quit_button.image, quit_button.rect)
            self.screen.blit(restart_button.image, restart_button.rect)

            # Limit the frames per second and update the display
            self.clock.tick(FPS)
            pygame.display.update()

    def winScreen(self):
        # Stop any playing audio and start playing the win audio in a loop
        pygame.mixer.stop()
        self.win_audio.play(loops=-1)

        # Update the display
        pygame.display.update()

        # Create restart and quit buttons for the win screen
        restart_button = Button(10, WIN_HEIGHT-60, 120, 50, WHITE, BLACK, 'Restart', 32)
        quit_button = Button(140, WIN_HEIGHT-60, 120, 50, WHITE, BLACK, 'QUIT', 32)

        # Remove all sprites from the game
        for sprite in self.all_sprites:
            sprite.kill()

        # Draw the win background and buttons on the screen
        self.screen.blit(self.win_background, (0, 0))
        self.screen.blit(restart_button.image, restart_button.rect)
        self.screen.blit(quit_button.image, quit_button.rect)

        # Update the display
        pygame.display.update()

        # Create a loop for handling events when the game is not playing
        while self.running and not self.playing:
            # Check for events in the event queue
            for event in pygame.event.get():
                # Check if the user closes the game window
                if event == pygame.QUIT:
                    self.running = False

            # Get the current mouse position and button press status
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            # Check if the restart button is pressed
            if restart_button.isPressed(mouse_pos, mouse_pressed):
                # Start a new game
                self.new()

            # Check if the quit button is pressed
            if quit_button.isPressed(mouse_pos, mouse_pressed):
                # Exit the game
                self.playing = False
                pygame.quit()
                sys.exit()

    
    def introScreen(self):
        # Set the intro flag to True
        intro = True

        # Start playing the intro audio in a loop
        self.intro_audio.play(loops=-1)

        # Create play and quit buttons for the intro screen
        play_button = Button(WIN_WIDTH/2 - 50, WIN_HEIGHT/2+30, 100, 50, WHITE, BLACK, 'PLAY', 32)
        quit_button = Button(WIN_WIDTH/2 - 50, WIN_HEIGHT/2 + 90, 100, 50, WHITE, BLACK, 'QUIT', 32)

        # Enter a loop for handling events during the intro screen
        while intro:
            # Check for events in the event queue
            for event in pygame.event.get():
                # Check if the user closes the game window
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False

            # Get the current mouse position and button press status
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            # Check if the play button is pressed
            if play_button.isPressed(mouse_pos, mouse_pressed):
                intro = False

            # Check if the quit button is pressed
            if quit_button.isPressed(mouse_pos, mouse_pressed):
                self.playing = False
                pygame.quit()
                sys.exit()

            # Draw the intro background and buttons on the screen
            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(play_button.image, play_button.rect)
            self.screen.blit(quit_button.image, quit_button.rect)

            # Control the frame rate
            self.clock.tick(FPS)

            # Update the display
            pygame.display.update()



# Create a variable for the game class
g = Game()

# Display the introduction screen
g.introScreen()

# Start a new game
g.new()

# Enter the main game loop while the game is running
while g.running:
    # Execute the main game logic
    g.main()

    # Check if the player has won
    if g.win:
        # Display the win screen
        g.winScreen()
    else:
        # Display the game over screen
        g.gameOver()

# Quit the pygame module and exit the system
pygame.quit()
sys.exit()
