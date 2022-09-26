from enum import Enum


class Choices(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3
    LIZARD = 4
    SPOCK = 5

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
