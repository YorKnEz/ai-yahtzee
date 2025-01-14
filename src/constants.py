import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
FPS = 144


class ScoreCategory(Enum):
    UNSELECTED = -1
    ONES = 0
    TWOS = 1
    THREES = 2
    FOURS = 3
    FIVES = 4
    SIXES = 5
    THREE_OF_A_KIND = 6
    FOUR_OF_A_KIND = 7
    FULL_HOUSE = 8
    SMALL_STRAIGHT = 9
    LARGE_STRAIGHT = 10
    CHANCE = 11
    YAHTZEE = 12


CATEGORY_COUNT = len(list(ScoreCategory)) - 1
