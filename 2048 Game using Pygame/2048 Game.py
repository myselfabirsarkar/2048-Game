import pygame
import random
import math

pygame.init() #Initializes the Pygame library, allowing its features to be used.
FPS = 60 #Sets the frames per second for smooth animations.

WIDTH, HEIGHT = 800, 800 #Define the screen dimensions.
#Define the grid dimensions (4x4).
ROWS = 4
COLS = 4
#Calculate the dimensions of each tile on the grid.
RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160) #Color of grid lines.
OUTLINE_THICKNESS = 10 #Thickness of grid lines.
BACKGROUND_COLOR = (205, 192, 180) #Background color of the game window.
FONT_COLOR = (119, 110, 101) #Color of the text on tiles.

FONT = pygame.font.SysFont("comicsans", 60, bold=True) #Configures the font type and size for rendering text.
MOVE_VEL = 20 #Speed of tile animations.

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT)) #Creates the main game window.
pygame.display.set_caption("2048") #Sets the window title.

#Stores tile colors corresponding to their values
class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT
    #Determines the tile's color based on its value using logarithmic indexing.
    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color
    #Renders the tile as a rectangle and displays its value as text.
    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

#Draws horizontal and vertical lines to form the 4x4 grid.
def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

#Renders the background, tiles, grid, and updates the display.
def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)

    pygame.display.update()

# Finds an empty position to generate a new tile.
def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col
"""
window: Likely the display surface where tiles are drawn.
tiles: A data structure (probably a dictionary) mapping positions to tile objects.
clock: Presumably used to manage timing for smooth animation.
direction: Indicates the direction of movement, e.g., "left" in the provided snippet.
"""
def move_tiles(window, tiles, clock, direction): 
    updated = True #It is used to indicate if any tiles moved during this operation.
    blocks = set() #It is used to track tiles that have merged or reached their final position.

    if direction == "left":
        sort_func = lambda x: x.col #Sorts tiles by column (col) to determine movement order.
        reverse = False #A boolean for sorting direction; False means ascending.
        delta = (-MOVE_VEL, 0) #A tuple representing the movement vector (negative in the x-direction for "left").
        boundary_check = lambda tile: tile.col == 0 #Determines if a tile is at the edge of the grid.
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}") #Finds the tile adjacent to the current tile in the specified direction.
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL #Checks if a tile should merge with the next tile.
        move_check = (lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL) #Checks if a tile has space to move into without merging.
        ceil = True #It indicates if movement should "snap" to a grid boundary.
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)

    return end_move(tiles)

# Adds a new random tile if possible. Ends the game if no moves are available.
def end_move(tiles):
    if len(tiles) == 16:
        game_over_popup()
        #print("Game End")
        return "lost"
    
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"


def game_over_popup():
    # Create a translucent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)  # Set transparency
    overlay.fill((0, 0, 0))  # Black background
    
    # Render the "Game Over" text
    text = FONT.render("Game Over!", True, (255, 255, 255))
    subtext = pygame.font.SysFont("comicsans", 40).render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    
    WINDOW.blit(overlay, (0, 0))
    WINDOW.blit(text,(WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 50))
    WINDOW.blit(subtext,(WIDTH // 2 - subtext.get_width() // 2, HEIGHT // 2 - subtext.get_height() // 2 + 50))
    pygame.display.update()
    
    # Pause for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main(WINDOW)  # Restart the game
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()

def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)

# Initializes the game with two tiles of value 2.
def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles

# Main game loop handling events, rendering, and game state transitions.
def main(window):
    clock = pygame.time.Clock() #Creates a Clock object to control the frame rate of the game. This ensures smooth animations and consistent gameplay speed.
    run = True

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get(): #Retrieves all pending user inputs (events) like key presses, mouse movements, or window close actions.
            if event.type == pygame.QUIT: #Checks if the user has clicked the "close" button on the game window.
                run = False #To exit the loop and close the game.
                break

            if event.type == pygame.KEYDOWN: #Checks if a key was pressed.
                if event.key == pygame.K_LEFT:  #Checks if the left arrow key was pressed. Similar checks are made for other arrow keys.
                    move_tiles(window, tiles, clock, "left")
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, "right")
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, "up")
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, "down")

        draw(window, tiles)

    pygame.quit()

#Ensures the game logic doesn't run when the script is imported elsewhere.
if __name__ == "__main__":
    main(WINDOW)
