from os import environ

SESSION_CONFIGS = [
    dict(
        name='ChessBets',
        display_name="Chess Betting Experiment",
        num_demo_participants=1,
        app_sequence=['Survey', 'BetSizing', 'ChessBets'],
        # Use 'treatment': 'ML' or 'treatment': 'Odds' to force a group.
        # Otherwise, it randomizes.
        treatment='random', 
        skip_onboarding=True,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, 
    participation_fee=0.00, 
    doc=""
)

PARTICIPANT_FIELDS = [
    'is_ML', 
    'match_order', 
    'onboarding_step', 
    'white_on_left', 
    'white_best_on_top',
    'participant_name'
]
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = environ.get('OTREE_SECRET_KEY', '5348914612345')
INSTALLED_APPS = ['otree']
