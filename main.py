"""Conway's Game of Life using pygame-ce.

Controls:
    Space       - pause / resume
    Left click  - draw cells (drag to paint)
    Right click - erase cells (drag to erase)
    N           - step one generation (while paused)
    R           - randomize grid
    C           - clear grid
    Up / Down   - speed up / slow down
    Esc         - quit
"""
import random

import pygame

CELL_SIZE = 10
COLS, ROWS = 100, 55
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
BAR_HEIGHT = 52

BG = (20, 20, 25)
GRID = (40, 40, 48)
ALIVE = (80, 220, 120)
BORN = (60, 150, 90)
TEXT = (220, 220, 220)


def random_grid():
    return [[random.random() < 0.2 for _ in range(COLS)] for _ in range(ROWS)]


def empty_grid():
    return [[False] * COLS for _ in range(ROWS)]


def step(grid):
    new = empty_grid()
    for y in range(ROWS):
        for x in range(COLS):
            n = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx or dy:
                        n += grid[(y + dy) % ROWS][(x + dx) % COLS]
            new[y][x] = n == 3 or (grid[y][x] and n == 2)
    return new


def draw(screen, grid, font, paused, fps, generation):
    screen.fill(BG)
    nxt = step(grid)
    hole = CELL_SIZE // 3
    for y in range(ROWS):
        for x in range(COLS):
            px, py = x * CELL_SIZE, y * CELL_SIZE
            if grid[y][x]:
                screen.fill(ALIVE, (px, py, CELL_SIZE - 1, CELL_SIZE - 1))
                if not nxt[y][x]:
                    # Dying next generation: punch a small hole in the middle
                    off = (CELL_SIZE - 1 - hole) // 2
                    screen.fill(BG, (px + off, py + off, hole, hole))
            elif nxt[y][x]:
                # Born next generation: draw a small donut ring
                center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
                pygame.draw.circle(screen, BORN, center, max(CELL_SIZE // 2 - 1, 2), 1)
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

    status = "PAUSED" if paused else "RUNNING"
    pop = sum(map(sum, grid))
    info = (f"{status} | Gen {generation} | Pop {pop} | Speed {fps} | "
            "Space pause  N step  R random  C clear  Up/Down speed")
    mouse_help = "Left click: bring cells to life  |  Right click: wipe cells out"
    screen.blit(font.render(info, True, TEXT), (8, HEIGHT + 7))
    screen.blit(font.render(mouse_help, True, TEXT), (8, HEIGHT + 29))
    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT + BAR_HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")
    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    grid = random_grid()
    paused = False
    fps = 15
    generation = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n and paused:
                    grid = step(grid)
                    generation += 1
                elif event.key == pygame.K_r:
                    grid, generation = random_grid(), 0
                elif event.key == pygame.K_c:
                    grid, generation = empty_grid(), 0
                elif event.key == pygame.K_UP:
                    fps = min(fps + 5, 120)
                elif event.key == pygame.K_DOWN:
                    fps = max(fps - 5, 1)

        buttons = pygame.mouse.get_pressed()
        if buttons[0] or buttons[2]:
            mx, my = pygame.mouse.get_pos()
            if my < HEIGHT:
                grid[my // CELL_SIZE][mx // CELL_SIZE] = bool(buttons[0])

        if not paused:
            grid = step(grid)
            generation += 1

        draw(screen, grid, font, paused, fps, generation)
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
