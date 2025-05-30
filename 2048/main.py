import pygame
import random
import math

pygame.init()

FPS = 120
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 4, 4
RECT_HEIGHT, RECT_WIDTH = HEIGHT // ROWS, WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


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

    def get_color(self):
        index = int(math.log2(self.value)) - 1
        return self.COLORS[min(index, len(self.COLORS) - 1)]

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


def draw_grid(window):
    for row in range(1, ROWS):
        pygame.draw.line(window, OUTLINE_COLOR, (0, row * RECT_HEIGHT), (WIDTH, row * RECT_HEIGHT), OUTLINE_THICKNESS)
    for col in range(1, COLS):
        pygame.draw.line(window, OUTLINE_COLOR, (col * RECT_WIDTH, 0), (col * RECT_WIDTH, HEIGHT), OUTLINE_THICKNESS)
    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles, score):
    window.fill(BACKGROUND_COLOR)
    for tile in tiles.values():
        tile.draw(window)
    draw_grid(window)

    score_text = FONT.render(f"Score: {score}", 1, FONT_COLOR)
    window.blit(score_text, (20, 20))

    pygame.display.update()


def draw_game_over(window, score):
    window.fill(BACKGROUND_COLOR)

    game_over_text = FONT.render("Game Over!", True, (255, 0, 0))
    score_text = FONT.render(f"Final Score: {score}", True, FONT_COLOR)
    restart_text = pygame.font.SysFont("comicsans", 40).render("Press R to Restart or ESC to Quit", True, FONT_COLOR)

    window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    window.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    window.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))

    pygame.display.update()


def get_random_pos(tiles):
    while True:
        row, col = random.randrange(0, ROWS), random.randrange(0, COLS)
        if f"{row}{col}" not in tiles:
            return row, col


def move_tiles(window, tiles, clock, direction, score):
    updated = True
    blocks = set()

    if direction == "left":
        key, reverse, delta = lambda t: t.col, False, (-MOVE_VEL, 0)
        boundary = lambda t: t.col == 0
        next_tile = lambda t: tiles.get(f"{t.row}{t.col - 1}")
        merge_check = lambda t, n: t.x > n.x + MOVE_VEL
        move_check = lambda t, n: t.x > n.x + RECT_WIDTH + MOVE_VEL
        ceil = True
    elif direction == "right":
        key, reverse, delta = lambda t: t.col, True, (MOVE_VEL, 0)
        boundary = lambda t: t.col == COLS - 1
        next_tile = lambda t: tiles.get(f"{t.row}{t.col + 1}")
        merge_check = lambda t, n: t.x < n.x - MOVE_VEL
        move_check = lambda t, n: t.x + RECT_WIDTH + MOVE_VEL < n.x
        ceil = False
    elif direction == "up":
        key, reverse, delta = lambda t: t.row, False, (0, -MOVE_VEL)
        boundary = lambda t: t.row == 0
        next_tile = lambda t: tiles.get(f"{t.row - 1}{t.col}")
        merge_check = lambda t, n: t.y > n.y + MOVE_VEL
        move_check = lambda t, n: t.y > n.y + RECT_HEIGHT + MOVE_VEL
        ceil = True
    else:  # down
        key, reverse, delta = lambda t: t.row, True, (0, MOVE_VEL)
        boundary = lambda t: t.row == ROWS - 1
        next_tile = lambda t: tiles.get(f"{t.row + 1}{t.col}")
        merge_check = lambda t, n: t.y < n.y - MOVE_VEL
        move_check = lambda t, n: t.y + RECT_HEIGHT + MOVE_VEL < n.y
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=key, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary(tile):
                continue

            next_t = next_tile(tile)
            if not next_t:
                tile.move(delta)
            elif tile.value == next_t.value and tile not in blocks and next_t not in blocks:
                if merge_check(tile, next_t):
                    tile.move(delta)
                else:
                    next_t.value *= 2
                    score += next_t.value
                    sorted_tiles.pop(i)
                    blocks.add(next_t)
            elif move_check(tile, next_t):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles, score)

    return end_move(tiles), score


def update_tiles(window, tiles, sorted_tiles, score):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    draw(window, tiles, score)


def end_move(tiles):
    if len(tiles) == 16:
        return "lost"
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"


def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
    return tiles


def main(window):
    clock = pygame.time.Clock()
    run = True
    tiles = generate_tiles()
    score = 0
    game_over = False

    while run:
        clock.tick(FPS)

        if game_over:
            draw_game_over(window, score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        tiles = generate_tiles()
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        run = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    status, score = move_tiles(window, tiles, clock, "left", score)
                if event.key == pygame.K_RIGHT:
                    status, score = move_tiles(window, tiles, clock, "right", score)
                if event.key == pygame.K_UP:
                    status, score = move_tiles(window, tiles, clock, "up", score)
                if event.key == pygame.K_DOWN:
                    status, score = move_tiles(window, tiles, clock, "down", score)
                if status == "lost":
                    game_over = True

        draw(window, tiles, score)

    pygame.quit()


if __name__ == "__main__":
    main(WINDOW)
