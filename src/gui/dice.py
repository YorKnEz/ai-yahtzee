import random
from copy import deepcopy

import pygame

from utils import distance

from .die import Die


class Dice:
    die_size = 64
    dice_gap = 16
    die_diag = die_size * (2**0.5)

    def __init__(self, game_bounds: pygame.Rect, dice_values: list[int] = None):
        self.faces = [
            pygame.transform.scale(
                pygame.image.load(f"assets/dice/dice{i}.png").convert_alpha(),
                (Dice.die_size, Dice.die_size),
            )
            for i in range(1, 7)
        ]

        dice_start_x = game_bounds.center[0] - 4 * (Dice.die_size + Dice.dice_gap) // 2

        self.dice_pos = [
            # start (center) position for bottom (human) player
            [
                (
                    dice_start_x + i * (Dice.die_size + Dice.dice_gap),
                    game_bounds.bottom - 30 + 4 - Dice.die_size / 2,
                )
                for i in range(5)
            ],
            # start (center) position for top (AI) player
            [
                (
                    dice_start_x + i * (Dice.die_size + Dice.dice_gap),
                    game_bounds.top + 30 - 4 + Dice.die_size / 2,
                )
                for i in range(5)
            ],
        ]
        self.current_pos = 0

        if not dice_values:
            self.dice = [Die(self.faces[i], i + 1, self.dice_pos[self.current_pos][i]) for i in range(5)]
        else:
            self.dice = [
                Die(self.faces[value - 1], value, self.dice_pos[self.current_pos][i])
                for i, value in enumerate(dice_values)
            ]

        self.off_screen_pos = [
            (self.dice[2].bounds.center[0], game_bounds.bottom + Dice.die_size + 256),
            (self.dice[2].bounds.center[0], game_bounds.top - Dice.die_size - 256),
        ]
        self.play_area_bounds = pygame.Rect(
            game_bounds.x,
            game_bounds.y + game_bounds.height // 4,
            game_bounds.width,
            game_bounds.height // 2,
        )
        self.throw_bounds = deepcopy(self.play_area_bounds)
        self.throw_bounds.x += Dice.die_diag // 2
        self.throw_bounds.y += Dice.die_diag // 2
        self.throw_bounds.width -= Dice.die_diag
        self.throw_bounds.height -= Dice.die_diag

    def __generate_spot(self):
        return (
            self.throw_bounds.x + self.throw_bounds.width * random.random(),
            self.throw_bounds.y + self.throw_bounds.height * random.random(),
            360 * random.random(),
        )

    def __get_random_dice_throw(self):
        spots = []
        # make sure the generated dice don't overlap with the picked dice (which are not rerolled)
        picked_dice_pos = [die.throw_pos for die in self.dice if die.picked()]

        while len(spots) != len(self.dice):
            new_spot = self.__generate_spot()
            is_overlapping = False

            for spot in spots + picked_dice_pos:
                if distance(spot, new_spot) < Dice.die_diag:
                    is_overlapping = True
                    break

            if not is_overlapping:
                spots.append(new_spot)

        return spots

    def click(self, mouse_pos: (int, int)):
        for die in self.dice:
            die.click(mouse_pos)

    def update(self, dt):
        for die in self.dice:
            die.update(dt)

    def draw(self, screen: pygame.Surface):
        for die in self.dice:
            die.draw(screen)

    def throw(self, dice_values: list[int]):
        spots = self.__get_random_dice_throw()
        for value, die, spot in zip(dice_values, self.dice, spots):
            die.throw(value, self.off_screen_pos[self.current_pos], spot, self.throw_bounds)

    def reset(self):
        self.current_pos = (self.current_pos + 1) % 2
        for die, new_pos in zip(self.dice, self.dice_pos[self.current_pos]):
            die.reset(new_pos)

    def unpicked_indexes(self) -> list[int]:
        return [i for i, die in enumerate(self.dice) if not die.picked()]

    def in_animation(self) -> bool:
        return any(die.in_animation() for die in self.dice)

    def pick(self, indexes: list[int]):
        for index in indexes:
            self.dice[index].pick()
