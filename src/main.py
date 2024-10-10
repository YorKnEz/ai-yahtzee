
import pygame

pygame.init()

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

running = True
dt = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("purple")

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
