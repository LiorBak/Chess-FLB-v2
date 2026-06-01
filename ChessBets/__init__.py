from otree.api import *
import random

doc = """
Chess Betting experiment with Holt-Laury switching points.
- Simplified "Points" terminology.
- Refined Simulation Quiz with extra complexity (Game Numbers 1, 4, 5, 6, 10).
"""

class C(BaseConstants):
    NAME_IN_URL = 'ChessBets'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 12
    ENDOWMENT = 200 # Now strictly referred to as 200 Points
    
    # Implied Probabilities for White
    IPW_ROWS = [0.95, 0.80, 0.75, 0.66, 0.50, 0.40, 0.33, 0.25, 0.20, 0.10]
    
    ELO_MAPPING = [
        {'diff': '+200', 'white_win': '76%', 'white_lose': '24%'},
        {'diff': '+100', 'white_win': '64%', 'white_lose': '36%'},
        {'diff': '0', 'white_win': '50%', 'white_lose': '50%'},
        {'diff': '-100', 'white_win': '36%', 'white_lose': '64%'},
        {'diff': '-200', 'white_win': '24%', 'white_lose': '76%'},
    ]

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

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        pattern = [
            (False, False, False), # 0, 0, 0
            (True, False, False),  # 1, 0, 0
            (False, True, False),  # 0, 1, 0
            (True, True, False),   # 1, 1, 0
            (False, False, True),  # 0, 0, 1
            (True, False, True),   # 1, 0, 1
            (True, True, True)     # 1, 1, 1
        ]
        for p in subsession.get_players():
            if not hasattr(p.participant, 'match_order') or p.participant.match_order is None:
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

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Experimental Variables
    is_ML = models.BooleanField()
    white_on_left = models.BooleanField()
    white_best_on_top = models.BooleanField()
    is_practice = models.BooleanField()
    white_elo = models.IntegerField()
    black_elo = models.IntegerField()
    p_white = models.FloatField()
    
    # Decisions
    choice1_white = models.BooleanField()
    choice2_white = models.BooleanField()
    choice3_white = models.BooleanField()
    choice4_white = models.BooleanField()
    choice5_white = models.BooleanField()
    choice6_white = models.BooleanField()
    choice7_white = models.BooleanField()
    choice8_white = models.BooleanField()
    choice9_white = models.BooleanField()
    choice10_white = models.BooleanField()
    switching_point = models.IntegerField()
    use_switching_point = models.BooleanField()
    bets_placed = models.BooleanField(initial=False)
    num_correct_bets = models.IntegerField()
    num_white_bets = models.IntegerField()
    num_white_wins = models.IntegerField()
    num_black_bets = models.IntegerField()
    num_black_wins = models.IntegerField()
    
    # Tracking
    info_points_clicked = models.BooleanField(initial=False)
    info_elo_clicked = models.BooleanField(initial=False)
    info_odds_clicked = models.BooleanField(initial=False)
    info_switch_clicked = models.BooleanField(initial=False)

    # Quiz Answers (Recorded on Round 1)
    q_elo_win = models.IntegerField(blank=True)
    q_elo_lose = models.IntegerField(blank=True)
    q_odds_a = models.IntegerField(blank=True)
    q_odds_b = models.IntegerField(blank=True)
    q_sim_1 = models.IntegerField(blank=True)
    q_sim_4 = models.IntegerField(blank=True)
    q_sim_5 = models.IntegerField(blank=True)
    q_sim_6 = models.IntegerField(blank=True)
    q_sim_10 = models.IntegerField(blank=True)
    q_sim_logic = models.IntegerField(blank=True)
    q_sim_better1 = models.IntegerField(blank=True)
    q_sim_better2 = models.IntegerField(blank=True)

    binding_decision = models.IntegerField()
    game1_outcome = models.StringField()
    game2_outcome = models.StringField()
    game3_outcome = models.StringField()
    game4_outcome = models.StringField()
    game5_outcome = models.StringField()
    game6_outcome = models.StringField()
    game7_outcome = models.StringField()
    game8_outcome = models.StringField()
    game9_outcome = models.StringField()
    game10_outcome = models.StringField()
    
    game1_details = models.StringField()
    game2_details = models.StringField()
    game3_details = models.StringField()
    game4_details = models.StringField()
    game5_details = models.StringField()
    game6_details = models.StringField()
    game7_details = models.StringField()
    game8_details = models.StringField()
    game9_details = models.StringField()
    game10_details = models.StringField()

# --- Helpers ---
def prob_to_odds(p):
    return round(1.0 / p, 2)

def prob_to_ml(p):
    if p >= 0.5: return int(-100 * p / (1 - p))
    return int(100 * (1 - p) / p)

def format_ml(ml):
    return f"+{ml}" if ml > 0 else str(ml)

def get_p_rows(white_best_on_top):
    # If True: Best payouts for White (lowest probs) are at the top (Row 1)
    if white_best_on_top:
        return list(reversed(C.IPW_ROWS))
    else:
        return C.IPW_ROWS # Best payouts for White at bottom (Row 10)

# --- Pages ---

class Onboarding(Page):
    form_model = 'player'
    form_fields = [
        'q_elo_win', 'q_elo_lose', 'q_odds_a', 'q_odds_b', 
        'q_sim_1', 'q_sim_4', 'q_sim_5', 'q_sim_6', 'q_sim_10', 'q_sim_logic',
        'q_sim_better1', 'q_sim_better2',
        'info_points_clicked', 'info_elo_clicked', 'info_odds_clicked', 'info_switch_clicked'
    ]
    
    @staticmethod
    def is_displayed(player: Player):
        if player.subsession.session.config.get('skip_onboarding', False):
            return False
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        is_ML = player.participant.is_ML
        wb_top = player.participant.white_best_on_top
        
        player.is_ML = is_ML
        player.white_best_on_top = wb_top
        player.white_on_left = player.participant.white_on_left
        
        p_rows = get_p_rows(wb_top)
        rows = []
        for i, pw in enumerate(p_rows):
            if is_ML: vw, vb = format_ml(prob_to_ml(pw)), format_ml(prob_to_ml(1-pw))
            else: vw, vb = str(prob_to_odds(pw)), str(prob_to_odds(1-pw))
            rows.append({'index': i+1, 'val_w': vw, 'val_b': vb})
            
        # Payout calculations for simulation (Game Numbers 1, 4, 5, 6, 10)
        # Simulation scenario: Switch at Row 4. White Wins.
        sim_indices = [1, 4, 5, 6, 10]
        ans_dict = {}
        
        for idx in sim_indices:
            pw = p_rows[idx-1]
            bet_white = (idx >= 4)
            
            if bet_white:
                win = True # Scenario says White wins
                p_win = pw
            else:
                win = False # Scenario says White wins, but bet was Black
                p_win = 1 - pw
            
            if win:
                if is_ML:
                    ml = prob_to_ml(p_win)
                    profit = (C.ENDOWMENT / 100) * ml if p_win < 0.5 else (C.ENDOWMENT / abs(ml)) * 100
                    ans_dict[idx] = int(profit + C.ENDOWMENT)
                else:
                    ans_dict[idx] = int(C.ENDOWMENT * prob_to_odds(p_win))
            else:
                ans_dict[idx] = 0
            
        # Answers for "Which game is better to bet on White?"
        # If wb_top is True: Game 1 > Game 2, Game 2 > Game 10
        # If wb_top is False: Game 2 > Game 1, Game 10 > Game 2
        if wb_top:
            ans_better1, ans_better2 = 1, 2
        else:
            ans_better1, ans_better2 = 2, 10
            
        return dict(
            is_ML=is_ML,
            white_best_on_top=wb_top,
            elo_mapping=C.ELO_MAPPING,
            rows=rows,
            ans_sim_1 = ans_dict[1],
            ans_sim_4 = ans_dict[4],
            ans_sim_5 = ans_dict[5],
            ans_sim_6 = ans_dict[6],
            ans_sim_10 = ans_dict[10],
            ans_better1 = ans_better1,
            ans_better2 = ans_better2,
            debug = player.subsession.session.config.get('debug', False) or True # Force true for your testing
        )

class Decision(Page):
    form_model = 'player'
    form_fields = [f'choice{i}_white' for i in range(1, 11)] + ['switching_point', 'use_switching_point']

    @staticmethod
    def live_method(player: Player, data):
        if data.get('type') == 'save_bets':
            player.switching_point = int(data['switching_point'])
            player.use_switching_point = bool(data['use_switching_point'])
            for idx in range(1, 11):
                setattr(player, f'choice{idx}_white', bool(data['choices'][str(idx)]))
            player.bets_placed = True
            return {player.id_in_group: {'status': 'saved'}}

    @staticmethod
    def vars_for_template(player: Player):
        match = player.participant.match_order[player.round_number - 1]
        player.is_ML = player.participant.is_ML
        player.white_on_left = player.participant.white_on_left
        player.white_best_on_top = player.participant.white_best_on_top
        player.white_elo = match['white_elo']
        player.black_elo = match['black_elo']
        player.p_white = match['p_white']
        player.is_practice = match['is_practice']
        
        # Pre-generate outcomes and details if not already done
        if not player.field_maybe_none('game1_outcome'):
            for i in range(1, 11):
                # Winner determination
                r_outcome = random.random()
                if r_outcome < player.p_white:
                    outcome = 'white'
                else:
                    outcome = 'draw' if random.random() < 0.70 else 'black'
                setattr(player, f'game{i}_outcome', outcome)
                
                # Move count and details
                moves = random.randint(30, 65)
                if outcome in ['white', 'black']:
                    term_r = random.random()
                    if term_r < 0.75:
                        details = f"Resignation ({moves} moves)"
                    elif term_r < 0.90:
                        if random.random() < 0.3:
                            moves = random.randint(12, 22)
                            details = f"Checkmate ({moves} moves, Super fast!)"
                        else:
                            details = f"Checkmate ({moves} moves)"
                    else:
                        details = f"Timeout ({moves} moves)"
                else:  # draw
                    term_r = random.random()
                    if term_r < 0.60:
                        details = f"Agreement ({moves} moves)"
                    elif term_r < 0.90:
                        details = f"Repetition ({moves} moves)"
                    else:
                        moves = random.randint(65, 110)
                        details = f"Stalemate ({moves} moves)"
                setattr(player, f'game{i}_details', details)
            
            player.binding_decision = random.randint(1, 10)

        p_rows = get_p_rows(player.white_best_on_top)
        rows = []
        for i, pw in enumerate(p_rows):
            idx = i + 1
            outcome = getattr(player, f'game{idx}_outcome')
            details = getattr(player, f'game{idx}_details')
            
            # Extract moves count
            try:
                moves = int(details.split('(')[1].split()[0])
            except Exception:
                moves = 40
            
            # Calculate payout if choice is White
            if outcome == 'white':
                if player.is_ML:
                    ml = prob_to_ml(pw)
                    profit = (C.ENDOWMENT / 100) * ml if pw < 0.5 else (C.ENDOWMENT / abs(ml)) * 100
                    payout_if_white = int(profit + C.ENDOWMENT)
                else:
                    payout_if_white = int(C.ENDOWMENT * prob_to_odds(pw))
            else:
                payout_if_white = 0
                
            # Calculate payout if choice is Black/Tie
            if outcome in ['black', 'draw']:
                p_win_black = 1 - pw
                if player.is_ML:
                    ml = prob_to_ml(p_win_black)
                    profit = (C.ENDOWMENT / 100) * ml if p_win_black < 0.5 else (C.ENDOWMENT / abs(ml)) * 100
                    payout_if_black = int(profit + C.ENDOWMENT)
                else:
                    payout_if_black = int(C.ENDOWMENT * prob_to_odds(p_win_black))
            else:
                payout_if_black = 0

            if player.is_ML:
                vw, vb = format_ml(prob_to_ml(pw)), format_ml(prob_to_ml(1-pw))
            else:
                vw, vb = str(prob_to_odds(pw)), str(prob_to_odds(1-pw))
                
            rows.append({
                'index': idx,
                'val_w': vw,
                'val_b': vb,
                'pw': pw,
                'outcome': outcome,
                'details': details,
                'moves': moves,
                'payout_if_white': payout_if_white,
                'payout_if_black': payout_if_black,
            })
            
        # History of past rounds
        import json
        history = []
        for p in player.in_previous_rounds():
            p_rows_p = get_p_rows(p.participant.white_best_on_top)
            rows_p = []
            for i, pw_p in enumerate(p_rows_p):
                idx_p = i + 1
                outcome_p = getattr(p, f'game{idx_p}_outcome')
                details_p = getattr(p, f'game{idx_p}_details')
                
                try:
                    moves_p = int(details_p.split('(')[1].split()[0])
                except Exception:
                    moves_p = 40
                
                if outcome_p == 'white':
                    if p.is_ML:
                        ml_p = prob_to_ml(pw_p)
                        profit_p = (C.ENDOWMENT / 100) * ml_p if pw_p < 0.5 else (C.ENDOWMENT / abs(ml_p)) * 100
                        payout_if_white_p = int(profit_p + C.ENDOWMENT)
                    else:
                        payout_if_white_p = int(C.ENDOWMENT * prob_to_odds(pw_p))
                else:
                    payout_if_white_p = 0
                    
                if outcome_p in ['black', 'draw']:
                    p_win_black_p = 1 - pw_p
                    if p.is_ML:
                        ml_p = prob_to_ml(p_win_black_p)
                        profit_p = (C.ENDOWMENT / 100) * ml_p if p_win_black_p < 0.5 else (C.ENDOWMENT / abs(ml_p)) * 100
                        payout_if_black_p = int(profit_p + C.ENDOWMENT)
                    else:
                        payout_if_black_p = int(C.ENDOWMENT * prob_to_odds(p_win_black_p))
                else:
                    payout_if_black_p = 0

                if p.is_ML:
                    vw_p, vb_p = format_ml(prob_to_ml(pw_p)), format_ml(prob_to_ml(1-pw_p))
                else:
                    vw_p, vb_p = str(prob_to_odds(pw_p)), str(prob_to_odds(1-pw_p))
                    
                rows_p.append({
                    'index': idx_p,
                    'val_w': vw_p,
                    'val_b': vb_p,
                    'pw': pw_p,
                    'outcome': outcome_p,
                    'details': details_p,
                    'moves': moves_p,
                    'payout_if_white': payout_if_white_p,
                    'payout_if_black': payout_if_black_p,
                    'choice_is_white': getattr(p, f'choice{idx_p}_white')
                })
            
            history.append({
                'round_number': p.round_number,
                'is_practice': p.is_practice,
                'white_elo': p.white_elo,
                'black_elo': p.black_elo,
                'white_on_left': p.white_on_left,
                'white_best_on_top': p.white_best_on_top,
                'switching_point': p.switching_point,
                'use_switching_point': p.use_switching_point,
                'payoff': int(p.payoff),
                'num_white_bets': p.num_white_bets,
                'num_white_wins': p.num_white_wins,
                'num_black_bets': p.num_black_bets,
                'num_black_wins': p.num_black_wins,
                'rows': rows_p
            })

        history_json = json.dumps(history)

        return dict(
            rows=rows,
            binding_decision=player.binding_decision,
            real_round_number=player.round_number - 1 if player.round_number > 1 else 0,
            history_json=history_json
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        p_rows = get_p_rows(player.participant.white_best_on_top)
        
        total_payoff = 0
        num_correct_bets = 0
        num_white_bets = 0
        num_white_wins = 0
        num_black_bets = 0
        num_black_wins = 0
        
        for idx in range(1, 11):
            choice_is_white = getattr(player, f'choice{idx}_white')
            if choice_is_white:
                num_white_bets += 1
            else:
                num_black_bets += 1
                
            game_outcome = getattr(player, f'game{idx}_outcome')
            pw = p_rows[idx - 1]
            
            is_win = (choice_is_white and game_outcome == 'white') or (not choice_is_white and game_outcome in ['black', 'draw'])
            
            if is_win:
                num_correct_bets += 1
                if choice_is_white:
                    num_white_wins += 1
                else:
                    num_black_wins += 1
                    
                p_win = pw if choice_is_white else 1 - pw
                if player.participant.is_ML:
                    ml = prob_to_ml(p_win)
                    profit = (C.ENDOWMENT / 100) * ml if p_win < 0.5 else (C.ENDOWMENT / abs(ml)) * 100
                    total_payoff += profit + C.ENDOWMENT
                else:
                    total_payoff += C.ENDOWMENT * prob_to_odds(p_win)
            
        player.payoff = total_payoff
        player.num_correct_bets = num_correct_bets
        player.num_white_bets = num_white_bets
        player.num_white_wins = num_white_wins
        player.num_black_bets = num_black_bets
        player.num_black_wins = num_black_wins

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    @staticmethod
    def vars_for_template(player: Player):
        real_rounds = [p for p in player.in_all_rounds() if not p.is_practice]
        binding_round = random.choice(real_rounds)
        player.payoff = binding_round.payoff
        cumulative_points = sum(int(p.payoff) for p in real_rounds)
        return dict(
            binding_round_num=binding_round.round_number, 
            final_points=int(player.payoff),
            cumulative_points=cumulative_points
        )

page_sequence = [Onboarding, Decision, Results]

