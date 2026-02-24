```python
import os
import json
import requests
from datetime import datetime

# Load environment variables
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')

# cTrader REST API endpoint
API_ENDPOINT = 'https://api.ctrader.com'

# Trade logger file
TRADE_LOGGER_FILE = 'trade_logger.json'

# Daily P&L tracker file
DAILY_PNL_TRACKER_FILE = 'daily_pnl_tracker.json'

# Drawdown monitor file
DRAWDOWN_MONITOR_FILE = 'drawdown_monitor.json'

# Stats dashboard file
STATS_DASHBOARD_FILE = 'stats_dashboard.json'

def position_size_calculator(account_balance, risk_percentage, stop_loss_pips):
    """
    Calculate the exact lot size based on account balance, risk percentage, and stop loss pips.
    """
    lot_size = (account_balance * risk_percentage / 100) / (stop_loss_pips * 0.01)
    return lot_size

def risk_reward_calculator(entry, stop_loss, risk_percentage):
    """
    Calculate take profit at 1R, 2R, 3R based on entry, stop loss, and risk percentage.
    """
    take_profit_1r = entry + (entry - stop_loss)
    take_profit_2r = entry + (entry - stop_loss) * 2
    take_profit_3r = entry + (entry - stop_loss) * 3
    return take_profit_1r, take_profit_2r, take_profit_3r

def trade_logger(symbol, direction, entry, exit, lot_size, pnl, duration):
    """
    Log every trade to JSON with timestamp, symbol, direction, entry/exit, lot size, P&L, and duration.
    """
    trade_log = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'symbol': symbol,
        'direction': direction,
        'entry': entry,
        'exit': exit,
        'lot_size': lot_size,
        'pnl': pnl,
        'duration': duration
    }
    with open(TRADE_LOGGER_FILE, 'a') as f:
        json.dump(trade_log, f)
        f.write('\n')

def daily_pnl_tracker(pnl):
    """
    Sum daily P&L and trigger a max daily loss alert at 5%.
    """
    with open(DAILY_PNL_TRACKER_FILE, 'r+') as f:
        daily_pnl = json.load(f)
        daily_pnl['total_pnl'] += pnl
        if daily_pnl['total_pnl'] < -0.05 * daily_pnl['initial_balance']:
            print('Max daily loss alert triggered!')
        f.seek(0)
        json.dump(daily_pnl, f)
        f.truncate()

def drawdown_monitor(current_balance, max_balance):
    """
    Monitor current and max drawdown percentage and auto-stop if >10%.
    """
    drawdown_percentage = (current_balance - max_balance) / max_balance * 100
    if drawdown_percentage < -10:
        print('Auto-stop triggered due to drawdown!')
    with open(DRAWDOWN_MONITOR_FILE, 'w') as f:
        json.dump({'current_balance': current_balance, 'max_balance': max_balance, 'drawdown_percentage': drawdown_percentage}, f)

def stats_dashboard(trade_logs):
    """
    Calculate win rate, avg winner, avg loser, and profit factor.
    """
    wins = 0
    losses = 0
    total_pnl = 0
    for trade_log in trade_logs:
        if trade_log['pnl'] > 0:
            wins += 1
        else:
            losses += 1
        total_pnl += trade_log['pnl']
    win_rate = wins / (wins + losses) * 100
    avg_winner = total_pnl / wins
    avg_loser = total_pnl / losses
    profit_factor = total_pnl / (wins + losses)
    return win_rate, avg_winner, avg_loser, profit_factor

def main():
    # Initialize daily P&L tracker
    with open(DAILY_PNL_TRACKER_FILE, 'w') as f:
        json.dump({'initial_balance': 10000, 'total_pnl': 0}, f)

    # Initialize drawdown monitor
    with open(DRAWDOWN_MONITOR_FILE, 'w') as f:
        json.dump({'current_balance': 10000, 'max_balance': 10000, 'drawdown_percentage': 0}, f)

    # Initialize stats dashboard
    with open(STATS_DASHBOARD_FILE, 'w') as f:
        json.dump({'trade_logs': []}, f)

    while True:
        # Get account balance
        response = requests.get(f'{API_ENDPOINT}/accounts/{ACCOUNT_ID}/balance', headers={'Authorization': f'Bearer {API_KEY}'})
        account_balance = response.json()['balance']

        # Get open trades
        response = requests.get(f'{API_ENDPOINT}/accounts/{ACCOUNT_ID}/trades', headers={'Authorization': f'Bearer {API_KEY}'})
        open_trades = response.json()['trades']

        # Calculate position size
        position_size = position_size_calculator(account_balance, 2, 50)

        # Calculate risk-reward
        take_profit_1r, take_profit_2r, take_profit_3r = risk_reward_calculator(1.2000, 1.1900, 2)

        # Log trades
        for trade in open_trades:
            trade_logger(trade['symbol'], trade['direction'], trade['entry'], trade['exit'], trade['lot_size'], trade['pnl'], trade['duration'])

        # Update daily P&L tracker
        daily_pnl_tracker(100)

        # Update drawdown monitor
        drawdown_monitor(account_balance, 10000)

        # Update stats dashboard
        with open(STATS_DASHBOARD_FILE, 'r') as f:
            stats_dashboard_data = json.load(f)
        stats_dashboard_data['trade_logs'].append({'pnl': 100})
        with open(STATS_DASHBOARD_FILE, 'w') as f:
            json.dump(stats_dashboard_data, f)

        # Calculate stats
        win_rate, avg_winner, avg_loser, profit_factor = stats_dashboard(stats_dashboard_data['trade_logs'])

        print(f'Position size: {position_size}')
        print(f'Take profit 1R: {take_profit_1r}, 2R: {take_profit_2r}, 3R: {take_profit_3r}')
        print(f'Daily P&L: {daily_pnl_tracker(100)}')
        print(f'Drawdown percentage: {drawdown_monitor(account_balance, 10000)}')
        print(f'Win rate: {win_rate}, Avg winner: {avg_winner}, Avg loser: {avg_loser}, Profit factor: {profit_factor}')

if __name__ == '__main__':
    main()
```