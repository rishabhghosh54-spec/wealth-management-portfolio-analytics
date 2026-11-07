"""Reconcile the report dataset, including a combined filter example."""
import csv,json
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parent
with (ROOT/'data/holdings_enriched.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
expected=json.loads((ROOT/'validation/expected_results.json').read_text(encoding='utf-8'))
assert len(rows)==609
assert len({r['holding_id'] for r in rows})==609
assert len({r['client_id'] for r in rows})==120
for r in rows:
    u=Decimal(r['units']); cost=Decimal(r['average_cost_inr']); price=Decimal(r['latest_price_inr'])
    v=Decimal(r['market_value_inr']); c=Decimal(r['cost_basis_inr']); g=Decimal(r['unrealized_pnl_inr'])
    assert abs(u*cost-c)<Decimal('0.000001')
    assert abs(u*price-v)<Decimal('0.000001')
    assert abs(v-c-g)<Decimal('0.000001')
def check(rs,ex):
    for k in ['market_value_inr','cost_basis_inr','unrealized_pnl_inr']:
        assert abs(sum(Decimal(r[k]) for r in rs)-Decimal(str(ex[k])))<Decimal('0.000001'),k
    cost=sum(Decimal(r['cost_basis_inr']) for r in rs)
    gain=sum(Decimal(r['unrealized_pnl_inr']) for r in rs)
    assert abs(gain/cost-Decimal(str(ex['return_on_cost'])))<Decimal('0.00000001')
    assert len({r['client_id'] for r in rs})==ex['clients']
check(rows,expected['all'])
for dim,groups in expected['groups'].items():
    for value,ex in groups.items(): check([r for r in rows if r[dim]==value],ex)
check([r for r in rows if r['segment']=='Affluent' and r['asset_class']=='Equity'],expected['filtered_example'])
print('PASS: 609 holdings, 120 clients, all asset/segment/city subtotals and combined filter checks reconcile.')
