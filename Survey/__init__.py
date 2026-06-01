from otree.api import *
import random

class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    
    MATCHES = [
        {'white_elo': 2700, 'black_elo': 2700, 'p_white': 0.5, 'is_practice': True},
        {'white_elo': 2702, 'black_elo': 2536, 'p_white': 0.72, 'is_practice': False},
        {'white_elo': 2805, 'black_elo': 2655, 'p_white': 0.70, 'is_practice': False},
        {'white_elo': 2785, 'black_elo': 2660, 'p_white': 0.67, 'is_practice': False},
        {'white_elo': 2870, 'black_elo': 2775, 'p_white': 0.63, 'is_practice': False},
        {'white_elo': 2853, 'black_elo': 2772, 'p_white': 0.61, 'is_practice': False},
        {'white_elo': 2800, 'black_elo': 2730, 'p_white': 0.60, 'is_practice': False},
        {'white_elo': 2725, 'black_elo': 2665, 'p_white': 0.59, 'is_practice': False},
        {'white_elo': 2740, 'black_elo': 2700, 'p_white': 0.56, 'is_practice': False},
        {'white_elo': 2740, 'black_elo': 2705, 'p_white': 0.55, 'is_practice': False},
        {'white_elo': 2720, 'black_elo': 2700, 'p_white': 0.53, 'is_practice': False},
        {'white_elo': 2783, 'black_elo': 2772, 'p_white': 0.52, 'is_practice': False},
    ]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    participant_name = models.StringField(label="Your Name:")

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        pattern = [
            (False, False, False),
            (True, False, False),
            (False, True, False),
            (True, True, False),
            (False, False, True),
            (True, False, True),
            (True, True, True)
        ]
        for p in subsession.get_players():
            if 'match_order' not in p.participant.vars or p.participant.vars['match_order'] is None:
                idx = (p.id_in_subsession - 1) % len(pattern)
                is_ML_val, white_on_left_val, white_best_on_top_val = pattern[idx]
                
                # Check for session config overrides
                config_treatment = subsession.session.config.get('treatment', 'random')
                if config_treatment == 'ML':
                    is_ML_val = True
                elif config_treatment == 'Odds':
                    is_ML_val = False
                    
                p.participant.is_ML = is_ML_val
                p.participant.white_on_left = white_on_left_val
                p.participant.white_best_on_top = white_best_on_top_val
                
                real_matches = C.MATCHES[1:]
                random.shuffle(real_matches)
                p.participant.match_order = [C.MATCHES[0]] + real_matches

class SurveyPage(Page):
    form_model = 'player'
    form_fields = ['participant_name']
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.participant_name = player.participant_name

page_sequence = [SurveyPage]
