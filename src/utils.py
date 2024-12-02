import math
from collections import Counter

import numpy as np

from constants import CATEGORY_COUNT, ScoreCategory


def roll_random_dice(dice_no: int):
    """
    Return an array with `dice_no` random values from 1 to 6.
    """
    return np.random.randint(1, 7, size=dice_no)


def reroll(dice_roll: list[int], to_roll: list[int]) -> list[int]:
    """
    Re-roll dice specified in `to_roll`; modify `dice_roll` by replacing
    dice marked as to-roll with newly rolled dice; return new dice roll.
    """
    new_dice = dice_roll[:]
    random_throws = roll_random_dice(len(to_roll))
    for ith_random, to_reroll in enumerate(to_roll):
        new_dice[to_reroll] = random_throws[ith_random]
    return new_dice


def score_roll(dice_roll: list[int]):
    """
    Return list of possible scores for each category of the game
    (excluding bonus) with the given dice roll.
    """
    scores = [0] * CATEGORY_COUNT

    counts = Counter(dice_roll)
    dice_sum = sum(dice_roll)

    for i in range(6):
        # -in-a-row scores
        scores[i] = (i + 1) * dice_roll.count(i + 1)

    if any(count >= 3 for count in counts.values()):
        scores[ScoreCategory.THREE_OF_A_KIND.value] = dice_sum

    if any(count >= 4 for count in counts.values()):
        scores[ScoreCategory.FOUR_OF_A_KIND.value] = dice_sum

    if sorted(counts.values()) == [2, 3]:
        scores[ScoreCategory.FULL_HOUSE.value] = 25

    small_straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
    if any(straight.issubset(dice_roll) for straight in small_straights):
        scores[ScoreCategory.SMALL_STRAIGHT.value] = 30

    large_straights = [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]
    if set(dice_roll) in large_straights:
        scores[ScoreCategory.LARGE_STRAIGHT.value] = 40

    scores[ScoreCategory.CHANCE.value] = dice_sum

    if any(count == 5 for count in counts.values()):
        scores[ScoreCategory.YAHTZEE.value] = 50

    # print(*list(zip(ScoreCategory, scores)), sep='\n')

    return scores


def point_in_convex_polygon(point: tuple[float, float], poly_points: list[tuple[float, float]]):
    """
    Given a point and a convex polygon as a list of vertices, returns if the point is within the
    polygon.
    """
    n = len(poly_points)

    sign = 0

    # for each side of the polygon, AB, use cross product to determine whether the AP vector is
    # on the same side of AB (i.e. left or right)
    for i in range(n):
        ax, ay = poly_points[i]
        bx, by = poly_points[(i + 1) % n]
        px, py = point

        bx -= ax
        by -= ay
        px -= ax
        py -= ay

        cross = bx * py - by * px

        if sign == 0:
            sign = -1 if cross < 0 else 1

        # if the cross product is 0, it means the point is on the edge, which we consider as
        # "inside"
        if cross < 0 < sign or sign < 0 < cross:
            return False

    return True


def distance(a: tuple[float, float], b: tuple[float, float]):
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


# if __name__ == "__main__":
#     print(score_roll([0, 1, 2, 3, 4]))
