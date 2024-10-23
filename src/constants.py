from enum import Enum

FPS = 144


class ScoreCategory(Enum):
    UNSELECTED = -1
    ONES = 0
    TWOS = 1
    THREES = 2
    FOURS = 3
    FIVES = 4
    SIXES = 5
    SUM = 6
    BONUS = 7
    THREE_OF_A_KIND = 8
    FOUR_OF_A_KIND = 9
    FULL_HOUSE = 10
    SMALL_STRAIGHT = 11
    LARGE_STRAIGHT = 12
    CHANCE = 13
    YAHTZEE = 14


CATEGORY_COUNT = len(list(ScoreCategory)) - 1

# static scores as in un-updatable by the user
STATIC_SCORES = [ScoreCategory.SUM.value, ScoreCategory.BONUS.value]
