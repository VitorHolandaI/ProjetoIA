import os

from .models import GenerationStats


def wait_on_finish(pygame, screen, clock, font, small_font, stats: GenerationStats) -> None:
    if os.environ.get("SDL_VIDEODRIVER") == "dummy":
        return
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key in {pygame.K_ESCAPE, pygame.K_RETURN}:
                running = False
        screen.fill((34, 36, 40))
        _draw_lines(pygame, screen, font, small_font, stats)
        pygame.display.flip()
        clock.tick(30)


def _draw_lines(pygame, screen, font, small_font, stats: GenerationStats) -> None:
    best_path = "-" if stats.best_path_length is None else str(stats.best_path_length)
    minotaur_unique = (
        "-" if stats.best_minotaur_unique_cells is None else str(stats.best_minotaur_unique_cells)
    )
    lines = [
        "Run finished",
        f"Generations: {stats.generation}",
        f"Human best fitness: {stats.best_human_fitness:.1f}",
        f"Minotaur best fitness: {stats.best_minotaur_fitness:.1f}",
        f"Average escaped: {stats.average_escaped:.1f}",
        f"Average caught: {stats.average_caught:.1f}",
        f"Best path length: {best_path}",
        f"Minotaur unique cells: {minotaur_unique}",
        "",
        "Press Enter, Esc, or close the window",
    ]
    y = 32
    for index, line in enumerate(lines):
        selected_font = font if index == 0 else small_font
        color = (255, 255, 255) if index == 0 else (225, 228, 232)
        screen.blit(selected_font.render(line, True, color), (32, y))
        y += 36 if index == 0 else 26

