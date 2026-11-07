"""Generate an explicitly SYNTHETIC wealth-management demo dataset.
No real client data, investment advice, or employer-affiliated data is used.
"""
from __future__ import annotations
import csv
import random
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
RNG = random.Random(20271106)

instruments = [
    ('EQ01', 'Equity Alpha', 'Equity', 152.50),
    ('EQ02', 'Equity Beta', 'Equity', 89.10),
    ('EQ03', 'Equity Gamma', 'Equity', 205.40),
    ('BD01', 'Bond Short Duration', 'Bonds', 101.80),
    ('BD02', 'Bond Long Duration', 'Bonds', 97.60),
    ('MF01', 'Diversified Fund A', 'Mutual Funds', 55.30),
    ('MF02', 'Diversified Fund B', 'Mutual Funds', 73.80),
    ('ETF01', 'Index ETF A', 'ETFs', 122.60),
    ('ETF02', 'Index ETF B', 'ETFs', 194.25),
    ('GD01', 'Gold Fund', 'Gold', 63.40),
    ('CS01', 'Cash Equivalent', 'Cash', 100.00),
    ('MF03', 'Balanced Fund', 'Mutual Funds', 84.50),
]
segments = ['Emerging Affluent', 'Affluent', 'High Net Worth']
clients = []
for n in range(1, 121):
    clients.append((f'C{n:03}', f'Simulated Client {n:03}', RNG.choices(segments, [55, 35, 10])[0],
                    RNG.choice(['Mumbai', 'Pune', 'Bengaluru', 'Hyderabad'])))

holdings = []
for client_id, _, segment, _ in clients:
    picks = RNG.sample(instruments, RNG.randint(3, 7))
    multiplier = {'Emerging Affluent': 1, 'Affluent': 3, 'High Net Worth': 7}[segment]
    for inst_id, _, _, latest_price in picks:
        units = round(RNG.uniform(12, 140) * multiplier, 2)
        # Average cost is a synthetic historical purchase price, not a market forecast.
        avg_cost = round(latest_price * RNG.uniform(.78, 1.16), 2)
        holdings.append((f'H{len(holdings)+1:04}', client_id, inst_id, units, avg_cost))

# Generate 3 monthly snapshots for prices, with prices anchored to the final month.
prices = []
for inst_id, _, _, latest in instruments:
    for snapshot, factor in [('2026-08-31', RNG.uniform(.90, 1.09)),
                             ('2026-09-30', RNG.uniform(.93, 1.07)),
                             ('2026-10-31', 1.0)]:
        prices.append((inst_id, snapshot, round(latest * factor, 2)))

def save(name, headers, rows):
    with (DATA / name).open('w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)

save('clients.csv', ['client_id', 'client_name', 'segment', 'city'], clients)
save('instruments.csv', ['instrument_id', 'instrument_name', 'asset_class', 'reference_price_inr'], instruments)
save('holdings.csv', ['holding_id', 'client_id', 'instrument_id', 'units', 'average_cost_inr'], holdings)
save('prices.csv', ['instrument_id', 'as_of_date', 'price_inr'], prices)
print(f'Generated {len(clients)} clients, {len(holdings)} holdings, {len(instruments)} instruments, {len(prices)} price rows.')
