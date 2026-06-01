from otree.api import Bot, Submission
from . import *

class PlayerBot(Bot):
    def play_round(self):
        yield Submission(SurveyPage, dict(participant_name="Test User"), check_html=False)
