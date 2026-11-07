"""Load synthetic CSVs to SQLite, execute reporting queries, validate basic KPIs.
Run generate_data.py first. Uses only the Python standard library.
"""
from __future__ import annotations
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
OUT = ROOT / 'reports'
OUT.mkdir(exist_ok=True)
con = sqlite3.connect(DATA / 'portfolio.sqlite')
con.execute('PRAGMA foreign_keys=ON')
SCHEMA = '''
DROP TABLE IF EXISTS holdings;
DROP TABLE IF EXISTS prices;
DROP TABLE IF EXISTS instruments;
DROP TABLE IF EXISTS clients;
CREATE TABLE clients (client_id TEXT PRIMARY KEY, client_name TEXT, segment TEXT, city TEXT);
CREATE TABLE instruments (instrument_id TEXT PRIMARY KEY, instrument_name TEXT, asset_class TEXT, reference_price_inr REAL);
CREATE TABLE holdings (holding_id TEXT PRIMARY KEY, client_id TEXT REFERENCES clients(client_id), instrument_id TEXT REFERENCES instruments(instrument_id), units REAL CHECK(units > 0), average_cost_inr REAL CHECK(average_cost_inr > 0));
CREATE TABLE prices (instrument_id TEXT REFERENCES instruments(instrument_id), as_of_date TEXT, price_inr REAL CHECK(price_inr > 0), PRIMARY KEY (instrument_id, as_of_date));
'''
con.executescript(SCHEMA)
for table, file, fields in [
    ('clients','clients.csv',4), ('instruments','instruments.csv',4),
    ('holdings','holdings.csv',5), ('prices','prices.csv',3)]:
    with (DATA / file).open(encoding='utf-8', newline='') as f:
        rows = list(csv.reader(f))[1:]
    con.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in range(fields))})", rows)
con.commit()

# SQL queries intentionally live separately so an interviewer can inspect them.
queries = [q.strip() for q in (ROOT / 'queries.sql').read_text(encoding='utf-8').split(';') if q.strip()]
for idx, query in enumerate(queries, 1):
    cursor = con.execute(query)
    columns = [c[0] for c in cursor.description]
    rows = cursor.fetchall()
    with (OUT / f'query_{idx}_results.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f'Query {idx}: {len(rows)} rows; {columns}')

# Reconcile portfolio-level vs segment-level values, without rounding individual positions.
total_value = con.execute("""SELECT SUM(h.units * p.price_inr) FROM holdings h
JOIN prices p ON p.instrument_id=h.instrument_id WHERE p.as_of_date='2026-10-31'""").fetchone()[0]
by_segment = con.execute("""SELECT SUM(segment_value) FROM (
 SELECT c.segment, SUM(h.units * p.price_inr) segment_value FROM clients c
 JOIN holdings h ON h.client_id=c.client_id JOIN prices p ON p.instrument_id=h.instrument_id
 WHERE p.as_of_date='2026-10-31' GROUP BY c.segment)""").fetchone()[0]
assert abs(total_value-by_segment)<0.01, 'Segment-level totals failed reconciliation.'
assert con.execute('SELECT COUNT(*) FROM clients').fetchone()[0] == 120
print(f'PASS: portfolio AUM and segment AUM reconcile. Demonstration AUM: INR {total_value:,.2f}')
print('Outputs saved in reports/. Synthetic data only, not a real firm or investment portfolio.')
con.close()
