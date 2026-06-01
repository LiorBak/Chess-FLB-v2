from otree.api import Bot, Submission
from . import *
import random

class PlayerBot(Bot):
    def play_round(self):
        yield Submission(BetPage, dict(
            bet_choice=random.choice(['white', 'black']),
            bet_size=random.randint(10, 500)
        ), check_html=False)

        if self.round_number == C.NUM_ROUNDS:
            yield Submission(BetSummaryPage, check_html=False)

