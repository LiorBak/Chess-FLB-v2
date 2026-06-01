from otree.api import *
import random

class C(BaseConstants):
    NAME_IN_URL = 'bet_sizing'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 12
    ENDOWMENT = 200
    
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
    is_ML = models.BooleanField()
    white_on_left = models.BooleanField()
    white_best_on_top = models.BooleanField()
    is_practice = models.BooleanField()
    white_elo = models.IntegerField()
    black_elo = models.IntegerField()
    p_white = models.FloatField()

    # Decisions for the single bet
    bet_choice = models.StringField(choices=['white', 'black'])
    bet_size = models.IntegerField(min=0, max=500, initial=0)
    
    # Recorded odds shown to player
    odds_white = models.StringField()
    odds_black = models.StringField()
    
    # Outcomes and simulation results for the single bet
    game_outcome = models.StringField()
    game_details = models.StringField()
    payout = models.IntegerField()

def prob_to_odds(p):
    return round(1.0 / p, 2)

def prob_to_ml(p):
    if p >= 0.5: return int(-100 * p / (1 - p))
    return int(100 * (1 - p) / p)

def format_ml(ml):
    return f"+{ml}" if ml > 0 else str(ml)

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

class BetPage(Page):
    form_model = 'player'
    form_fields = ['bet_choice', 'bet_size']

    @staticmethod
    def error_message(player: Player, values):
        if values['bet_size'] <= 0:
            return "You must bet at least 1 point to proceed. Please adjust your bet size above 0."

    @staticmethod
    def vars_for_template(player: Player):
        # Fallback initialization in case participant variables aren't set
        if 'match_order' not in player.participant.vars or player.participant.vars['match_order'] is None:
            player.participant.is_ML = True
            player.participant.white_on_left = True
            player.participant.white_best_on_top = True
            player.participant.match_order = C.MATCHES

        match = player.participant.match_order[player.round_number - 1]
        player.is_ML = player.participant.is_ML
        player.white_on_left = player.participant.white_on_left
        player.white_best_on_top = player.participant.white_best_on_top
        player.white_elo = match['white_elo']
        player.black_elo = match['black_elo']
        player.p_white = match['p_white']
        player.is_practice = match['is_practice']

        pw = player.p_white
        pb = 1.0 - pw

        # Odds conversion for display
        if player.is_ML:
            odds_w = format_ml(prob_to_ml(pw))
            odds_b = format_ml(prob_to_ml(pb))
        else:
            odds_w = str(prob_to_odds(pw))
            odds_b = str(prob_to_odds(pb))

        player.odds_white = odds_w
        player.odds_black = odds_b

        return {
            'odds_w': odds_w,
            'odds_b': odds_b,
            'pw': pw,
            'pb': pb,
            'is_ML_js': 'true' if player.is_ML else 'false',
            'ml_w_raw': prob_to_ml(pw) if player.is_ML else 0,
            'ml_b_raw': prob_to_ml(pb) if player.is_ML else 0,
            'dec_w_raw': prob_to_odds(pw),
            'dec_b_raw': prob_to_odds(pb),
            'real_round_number': player.round_number - 1 if player.round_number > 1 else 0,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Determine the simulated outcome
        r_outcome = random.random()
        if r_outcome < player.p_white:
            outcome = 'white'
        else:
            outcome = 'draw' if random.random() < 0.70 else 'black'
        player.game_outcome = outcome

        # Set game details (moves, etc.)
        moves = random.randint(30, 65)
        if outcome in ['white', 'black']:
            term_r = random.random()
            if term_r < 0.75:
                player.game_details = f"Resignation ({moves} moves)"
            elif term_r < 0.90:
                player.game_details = f"Checkmate ({moves} moves)"
            else:
                player.game_details = f"Timeout ({moves} moves)"
        else:
            player.game_details = f"Agreement ({moves} moves)"

        # Calculate payout
        choice = player.bet_choice
        bet_size = player.bet_size
        pw = player.p_white
        pb = 1.0 - pw

        # Check if the bet is won
        bet_won = (choice == 'white' and outcome == 'white') or (choice == 'black' and outcome in ['black', 'draw'])

        if bet_won:
            p_win = pw if choice == 'white' else pb
            if player.is_ML:
                ml = prob_to_ml(p_win)
                profit = (bet_size / 100) * ml if p_win < 0.5 else (bet_size / abs(ml)) * 100
                player.payout = int(profit + bet_size)
            else:
                player.payout = int(bet_size * prob_to_odds(p_win))
        else:
            player.payout = 0

        # Payoff applies if it is not practice
        if not player.is_practice:
            player.payoff = player.payout
        else:
            player.payoff = 0

class BetSummaryPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        all_rounds = player.in_all_rounds()
        
        # Calculate totals
        total_payout = sum(r.payout for r in all_rounds)
        total_real_payoff = sum(r.payoff for r in all_rounds)
        
        rounds_data = []
        for r in all_rounds:
            elo_diff = r.white_elo - r.black_elo
            diff_str = f"White +{elo_diff}" if elo_diff > 0 else (f"Black +{abs(elo_diff)}" if elo_diff < 0 else "Equal")
            
            # Outcome format
            if r.game_outcome == 'white':
                outcome_str = 'White Won'
            elif r.game_outcome == 'black':
                outcome_str = 'Black Won'
            else:
                outcome_str = 'Draw / Tie'
                
            chosen_odds = r.odds_white if r.bet_choice == 'white' else r.odds_black
            
            rounds_data.append({
                'round_number': r.round_number,
                'is_practice': r.is_practice,
                'white_elo': r.white_elo,
                'black_elo': r.black_elo,
                'elo_diff': diff_str,
                'bet_choice': 'White' if r.bet_choice == 'white' else 'Black / Tie',
                'bet_size': r.bet_size,
                'odds': chosen_odds,
                'outcome': outcome_str,
                'payout': r.payout,
            })
            
        return {
            'rounds_data': rounds_data,
            'total_payout': total_payout,
            'total_real_payoff': total_real_payoff,
        }

page_sequence = [BetPage, BetSummaryPage]

