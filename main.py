"""Conway's Game of Life using pygame-ce.

Controls:
    Space       - pause / resume
    Left click  - draw cells (drag to paint)
    Right click - erase cells (drag to erase)
    N           - step one generation (while paused)
    R           - randomize grid
    C           - clear grid
    Up / Down   - speed up / slow down
    T           - cycle through preset rules
    E           - type a custom rule (e.g. B36/S23), Enter to apply, Esc to cancel
    Esc         - quit
"""
import random
import re

import pygame

# True: cells going off one edge come back on the opposite edge.
# False: the edges are walls and everything outside the grid counts as dead.
WRAP_EDGES = True

CELL_SIZE = 10
COLS, ROWS = 100, 55
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
BAR_HEIGHT = 74

BG = (20, 20, 25)
GRID = (40, 40, 48)
ALIVE = (80, 220, 120)
BORN = (60, 150, 90)
TEXT = (220, 220, 220)
ERROR = (230, 90, 90)

PRESETS = [
    ("B3/S23", "Conway's Life"),
    ("B36/S23", "HighLife"),
    ("B2/S", "Seeds"),
    ("B3678/S34678", "Day & Night"),
    ("B1357/S1357", "Replicator"),
    ("B3/S012345678", "Life Without Death"),
    ("B368/S245", "Morley"),
    ("B35678/S5678", "Diamoeba"),
    ("B4678/S35678", "Anneal"),
]

RULE_PATTERN = re.compile(r"^B([0-8]*)/S([0-8]*)$")


def parse_rule(text):
    """Turn 'B3/S23' into ({3}, {2, 3}). Returns None if the text isn't a valid rule."""
    match = RULE_PATTERN.match(text.strip().upper())
    if not match:
        return None
    return {int(c) for c in match.group(1)}, {int(c) for c in match.group(2)}


def rule_name(text):
    for rule, name in PRESETS:
        if rule == text:
            return name
    return "Custom"


def random_grid():
    return [[random.random() < 0.2 for _ in range(COLS)] for _ in range(ROWS)]


def empty_grid():
    return [[False] * COLS for _ in range(ROWS)]


def step(grid, birth, survive):
    new = empty_grid()
    for y in range(ROWS):
        for x in range(COLS):
            n = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if not (dx or dy):
                        continue
                    ny, nx = y + dy, x + dx
                    if WRAP_EDGES:
                        n += grid[ny % ROWS][nx % COLS]
                    elif 0 <= ny < ROWS and 0 <= nx < COLS:
                        n += grid[ny][nx]
            new[y][x] = n in survive if grid[y][x] else n in birth
    return new


def draw(screen, grid, font, paused, fps, generation, rule_text, birth, survive,
         typing, typed, error):
    screen.fill(BG)
    nxt = step(grid, birth, survive)
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
    if typing:
        rule_line = f"Type a rule like B36/S23: {typed}_   (Enter apply, Esc cancel)"
    else:
        rule_line = f"Rule: {rule_text} ({rule_name(rule_text)})  |  T next preset  E type your own"
    screen.blit(font.render(info, True, TEXT), (8, HEIGHT + 7))
    screen.blit(font.render(mouse_help, True, TEXT), (8, HEIGHT + 29))
    screen.blit(font.render(rule_line, True, TEXT), (8, HEIGHT + 51))
    if error:
        screen.blit(font.render(error, True, ERROR), (WIDTH - font.size(error)[0] - 8, HEIGHT + 51))
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

    preset_index = 0
    rule_text = PRESETS[0][0]
    birth, survive = parse_rule(rule_text)
    typing = False
    typed = ""
    error = ""

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and typing:
                if event.key == pygame.K_ESCAPE:
                    typing = False
                elif event.key == pygame.K_RETURN:
                    parsed = parse_rule(typed)
                    if parsed:
                        birth, survive = parsed
                        rule_text = typed.strip().upper()
                        typing, error = False, ""
                    else:
                        error = "Invalid rule, use the form B3/S23"
                elif event.key == pygame.K_BACKSPACE:
                    typed = typed[:-1]
                elif event.unicode and event.unicode.upper() in "BS/012345678" and len(typed) < 24:
                    typed += event.unicode.upper()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n and paused:
                    grid = step(grid, birth, survive)
                    generation += 1
                elif event.key == pygame.K_r:
                    grid, generation = random_grid(), 0
                elif event.key == pygame.K_c:
                    grid, generation = empty_grid(), 0
                elif event.key == pygame.K_UP:
                    fps = min(fps + 5, 120)
                elif event.key == pygame.K_DOWN:
                    fps = max(fps - 5, 1)
                elif event.key == pygame.K_t:
                    preset_index = (preset_index + 1) % len(PRESETS)
                    rule_text = PRESETS[preset_index][0]
                    birth, survive = parse_rule(rule_text)
                    error = ""
                elif event.key == pygame.K_e:
                    typing, typed, error = True, "", ""

        buttons = pygame.mouse.get_pressed()
        if buttons[0] or buttons[2]:
            mx, my = pygame.mouse.get_pos()
            if my < HEIGHT:
                grid[my // CELL_SIZE][mx // CELL_SIZE] = bool(buttons[0])

        if not paused and not typing:
            grid = step(grid, birth, survive)
            generation += 1

        draw(screen, grid, font, paused, fps, generation, rule_text, birth, survive,
             typing, typed, error)
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
