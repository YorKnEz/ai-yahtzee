import random

from collections import Counter

from constants import ScoreCategory

def roll_random_dice(dice_no: int):
    """
    Return an array with `dice_no` random values from 1 to 6.
    """
    return [random.randint(1, 6) for _ in range(dice_no)]

def reroll(dice_roll: list[int], to_roll: list[int]):
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
    scores = [-1] * 13

    counts = Counter(dice_roll)
    dice_sum = sum(dice_roll)

    for i in range(6):
        # -in-a-row scores
        scores[i] = i * dice_roll.count(i)

    if any(count >= 3 for count in counts.values()):
        scores[ScoreCategory.THREE_OF_A_KIND.value] = sum(dice_roll)
    else:
        scores[ScoreCategory.THREE_OF_A_KIND.value] = 0

    if any(count >= 4 for count in counts.values()):
        scores[ScoreCategory.FOUR_OF_A_KIND.value] = dice_sum
    else:
        scores[ScoreCategory.FOUR_OF_A_KIND.value] = 0

    if sorted(counts.values()) == [2, 3]:
        scores[ScoreCategory.FULL_HOUSE.value] = 25
    else:
        scores[ScoreCategory.FULL_HOUSE.value] = 0

    small_straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
    if any(straight.issubset(dice_roll) for straight in small_straights):
        scores[ScoreCategory.SMALL_STRAIGHT.value] = 30
    else:
        scores[ScoreCategory.SMALL_STRAIGHT.value] = 0

    large_straights = [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]
    if set(dice_roll) in large_straights:
        scores[ScoreCategory.LARGE_STRAIGHT.value] = 40
    else:
        scores[ScoreCategory.LARGE_STRAIGHT.value] = 0

    scores[ScoreCategory.CHANCE.value] = dice_sum

    if any(count == 5 for count in counts.values()):
        scores[ScoreCategory.YAHTZEE.value] = 50
    else:
        scores[ScoreCategory.YAHTZEE.value] = 0

    return scores


# if __name__ == "__main__":
#     print(score_roll([0, 1, 2, 3, 4]))
