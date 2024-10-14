import math
import random
from copy import deepcopy

import pygame


class Dies:
    size = 64
    space_between_dice = 16

    def __init__(self, game_bounds, fps):
        self.dice_faces = [
            pygame.transform.scale(
                pygame.image.load(f"assets/dice/dice{i}.png").convert_alpha(),
                (Dies.size, Dies.size),
            )
            for i in range(1, 7)
        ]
        self.dice_values = [i + 1 for i in range(5)]
        self.dies = [self.dice_faces[i] for i in range(5)]

        dice_start_x = (
                game_bounds.center[0] - (Dies.size * 5 + Dies.space_between_dice * 4) // 2
        )

        self.dice_pos = [
            (
                dice_start_x + i * (Dies.size + Dies.space_between_dice),
                game_bounds.bottom - 30 + 4 - Dies.size,
            )
            for i in range(5)
        ]
        self.dice_bottom_pos = deepcopy(self.dice_pos)
        self.dice_top_pos = [
            (x, game_bounds.top + 30 - 4 + Dies.size) for x, _ in self.dice_pos
        ]

        # dice animation stuff
        self.animate = False
        # the keyframes of the animation (a tuple of form (duration in seconds, duration in frames)):
        # - first item: off-screen animation
        # - second item: "dice throw" animation
        self.keyframes = [(1, 1 * fps), (0.3, 0.3 * fps)]
        self.frame_count = 0
        self.curr_keyframe = 0
        self.dice_vectors = [(0, 0)] * 5

        self.off_screen_pos = (
            self.dice_pos[2][0],
            game_bounds.bottom + Dies.size + 256,
        )

        self.throw_bounds = pygame.Rect(
            game_bounds.x,
            game_bounds.y + game_bounds.height // 4,
            game_bounds.width,
            game_bounds.height // 2,
        )
        self.dice_throw_pos = [(0.0, 0.0, 0.0)] * 5
        self.rotated_dies = [
            self.get_rotated_dice(pygame.Rect(pos, dice.get_size()), rotation)
            for pos, dice, (_, _, rotation) in zip(
                self.dice_pos, self.dies, self.dice_throw_pos
            )
        ]

    def throw(self, dice_values: list[int]):
        """
        Perform a throw of the dice on the screen, updating the dice values to `dice_values` when
        the throw is finished.
        """
        if not self.animate:
            self.dice_values = deepcopy(dice_values)

            self.start_throw_animation()

    # generate 5 throws in the space defined by throw_bounds such that the dies are not overlapping
    # the returned value is an array of tuples of form (x, y, rotation)
    def get_random_dice_throw(self):
        dice_diag = math.ceil((Dies.size * (2 ** 0.5)))

        # normalize throw_bounds such that if dices are rotated they wont be drawn outside of the
        # original throw bounds
        throw_bounds_copy = self.throw_bounds.copy()
        throw_bounds_copy.x += dice_diag // 2
        throw_bounds_copy.y += dice_diag // 2
        throw_bounds_copy.width -= dice_diag
        throw_bounds_copy.height -= dice_diag

        # generate random (x, y, rotation) tuples
        def get_spots():
            return [
                (
                    throw_bounds_copy.x + throw_bounds_copy.width * random.random(),
                    throw_bounds_copy.y + throw_bounds_copy.height * random.random(),
                    360 * random.random(),
                )
                for _ in range(5)
            ]

        def distance(a, b): return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

        # pick 5 random spots in this space until they are non overlapping
        overlapping = True
        spots = []

        while overlapping:
            spots = get_spots()
            overlapping = False

            for i in range(5):
                for j in range(i + 1, 5):
                    # check if distance between points < dice_diag
                    if distance(spots[i], spots[j]) < dice_diag:
                        overlapping = True

        # the (x, y) picked above are assumed to be the center of the dice, so we need to subtract
        # half of the diagonal
        return [
            (x - dice_diag / 2, y - dice_diag / 2, rotation) for x, y, rotation in spots
        ]

    @staticmethod
    def get_rotated_dice(rotated_dice_rect, rotation):
        rect = pygame.Rect(0, 0, Dies.size, Dies.size)
        rect.center = rotated_dice_rect.center
        pivot = pygame.math.Vector2(rotated_dice_rect.center)

        poly = [
            (pygame.math.Vector2(rect.topleft) - pivot).rotate(-rotation) + pivot,
            (pygame.math.Vector2(rect.topright) - pivot).rotate(-rotation) + pivot,
            (pygame.math.Vector2(rect.bottomright) - pivot).rotate(-rotation) + pivot,
            (pygame.math.Vector2(rect.bottomleft) - pivot).rotate(-rotation) + pivot,
        ]

        return [(p.x, p.y) for p in poly]

    def start_throw_animation(self):
        """Initializes the state for starting the throw animation."""
        self.animate = True
        self.dice_pos = deepcopy(self.dice_bottom_pos)

        self.dice_throw_pos = self.get_random_dice_throw()

        fx, fy = self.off_screen_pos
        self.dice_vectors = [(fx - x, fy - y) for x, y in self.dice_pos]

    def throw_animation_frame(self, dt):
        """
        Performs the updates needed for one frame of the throw animation (i.e. moving the dice).
        """
        duration, total_frames = self.keyframes[self.curr_keyframe]

        if self.frame_count < total_frames:  # if current keyframe is still running
            self.dice_pos = [
                (
                    x + (dx * dt / duration),
                    y + (dy * dt / duration),
                )
                for (x, y), (dx, dy) in zip(self.dice_pos, self.dice_vectors)
            ]

            self.frame_count += 1
        else:  # if current keyframe ended, do different things depending on current keyframe

            if self.curr_keyframe == 0:
                # snap dice to their final position
                self.dice_pos = [self.off_screen_pos] * 5

                # prepare direction vectors for the dice throw
                self.dice_vectors = [
                    (fx - x, fy - y)
                    for (x, y), (fx, fy, _) in zip(self.dice_pos, self.dice_throw_pos)
                ]

                # reset frame_count and move to next keyframe
                self.frame_count = 0
                self.curr_keyframe += 1
            else:
                # snap dice to their final position
                self.dice_pos = [(x, y) for x, y, _ in self.dice_throw_pos]

                # update dice values
                # rotate the dice for a more realistic throw animation
                self.dies = [
                    pygame.transform.rotate(self.dice_faces[value - 1], rotation)
                    for value, (_, _, rotation) in zip(self.dice_values, self.dice_throw_pos)
                ]

                # get the bounds of the rotated dice as a set of points of a polygon
                # this is used in determining if a die is clicked
                self.rotated_dies = [
                    self.get_rotated_dice(pygame.Rect(pos, dice.get_size()), rotation)
                    for pos, dice, (_, _, rotation) in zip(
                        self.dice_pos, self.dies, self.dice_throw_pos
                    )
                ]

                # reset frame_count and curr_keyframe and stop the animation
                self.frame_count = 0
                self.curr_keyframe = 0
                self.animate = False

    def draw(self, screen):
        for i in range(5):
            screen.blit(self.dies[i], self.dice_pos[i])
