"""Build the report snapshot from synthetic source CSVs. Standard library only."""
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
SNAPSHOT='2026-10-31'
def read(name):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))
clients={r['client_id']:r for r in read('clients.csv')}
instruments={r['instrument_id']:r for r in read('instruments.csv')}
prices={r['instrument_id']:float(r['price_inr']) for r in read('prices.csv') if r['as_of_date']==SNAPSHOT}
fields=['holding_id','client_id','client_name','segment','city','instrument_id','instrument_name','asset_class','units','average_cost_inr','latest_price_inr','cost_basis_inr','market_value_inr','unrealized_pnl_inr']
result=[]
for h in read('holdings.csv'):
    client=clients[h['client_id']]; instrument=instruments[h['instrument_id']]
    units=float(h['units']); cost=float(h['average_cost_inr']); price=prices[h['instrument_id']]
    row=dict(h,client_name=client['client_name'],segment=client['segment'],city=client['city'],instrument_name=instrument['instrument_name'],asset_class=instrument['asset_class'],units=units,average_cost_inr=cost,latest_price_inr=price,cost_basis_inr=units*cost,market_value_inr=units*price,unrealized_pnl_inr=units*price-units*cost)
    result.append(row)
with (DATA/'holdings_enriched.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(result)
print(f'Built {len(result)} synthetic holdings for {SNAPSHOT}.')
