import random

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
    with the given dice roll.
    """
    raise NotImplementedError()

