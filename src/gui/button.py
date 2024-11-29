import pygame


class Button:
    def __init__(self, bounds: pygame.Rect, text, font):
        self.bounds = bounds
        self.text = font.render(text, True, "black")
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.bounds.center

    def draw(self, screen):
        pygame.draw.rect(screen, "white", self.bounds)
        screen.blit(self.text, self.text_rect)

    def clicked(self, pos):
        return self.bounds.collidepoint(*pos)
