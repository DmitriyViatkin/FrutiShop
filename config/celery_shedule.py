from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'buy-apple-periodic': {
        'task': 'trading.tasks.buy_apple',
        'schedule': 6.0,      },
    'buy-bananas-periodic': {
            'task': 'trading.tasks.buy_banana',
            'schedule': 9.0,      },
    'buy-pineapples-periodic': {
            'task': 'trading.tasks.buy_pineapple',
            'schedule': 12.0,      },
    'buy-peaches-periodic': {
            'task': 'trading.tasks.buy_peach',
            'schedule': 15.0,      },
    'sell-apple-periodic': {
        'task': 'trading.tasks.sell_apple',
        'schedule': 6.0, },
    'sell-bananas-periodic': {
        'task': 'trading.tasks.sell_banana',
        'schedule': 9.0, },
    'sell-pineapples-periodic': {
        'task': 'trading.tasks.sell_pineapple',
        'schedule': 12.0, },
    'sell-peaches-periodic': {
        'task': 'trading.tasks.sell_peach',
        'schedule': 15.0, },
}
