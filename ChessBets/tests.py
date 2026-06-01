from otree.api import Currency as c, currency_range, Bot, Submission
from . import *
import random

class PlayerBot(Bot):
    def play_round(self):
        # Step 1: Onboarding (only in round 1 if not skipped)
        if self.round_number == 1 and not self.player.subsession.session.config.get('skip_onboarding', False):
            is_ML = self.player.participant.is_ML
            wb_top = self.player.participant.white_best_on_top
            
            p_rows = get_p_rows(wb_top)
            sim_indices = [1, 4, 5, 6, 10]
            ans_dict = {}
            for idx in sim_indices:
                pw = p_rows[idx-1]
                bet_white = (idx >= 4)
                if bet_white:
                    win = True
                    p_win = pw
                else:
                    win = False
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
            
            if wb_top:
                ans_better1, ans_better2 = 1, 2
            else:
                ans_better1, ans_better2 = 2, 10
                
            yield Submission(Onboarding, dict(
                q_elo_win=3,
                q_elo_lose=1,
                q_odds_a=800,
                q_odds_b=300,
                q_sim_1=0,
                q_sim_4=ans_dict[4],
                q_sim_5=ans_dict[5],
                q_sim_6=ans_dict[6],
                q_sim_10=ans_dict[10],
                q_sim_logic=3,
                q_sim_better1=ans_better1,
                q_sim_better2=ans_better2,
                info_points_clicked=True,
                info_elo_clicked=True,
                info_odds_clicked=True,
                info_switch_clicked=True
            ), check_html=False)
            
        # Step 2: Decision page in all rounds
        switching_point = random.randint(1, 11)
        wb_top = self.player.participant.white_best_on_top
        decision_dict = {'switching_point': switching_point, 'use_switching_point': True}
        for i in range(1, 11):
            if wb_top:
                choice_white = (i >= switching_point)
            else:
                choice_white = (i < switching_point)
            decision_dict[f'choice{i}_white'] = choice_white
            
        yield Submission(Decision, decision_dict, check_html=False)
        
        # Step 3: Results page on final round
        if self.round_number == C.NUM_ROUNDS:
            yield Submission(Results, check_html=False)
