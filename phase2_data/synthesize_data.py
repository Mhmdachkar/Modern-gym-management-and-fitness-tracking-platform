#!/usr/bin/env python3
"""
Synthetic Data Generator for Phase 2 Analysis
- Expands Phase 1 CSVs with realistic synthetic rows
- Preserves schema and referential integrity between members, coaches, plans, packages, sessions, subscriptions
- Writes outputs to phase2_data/synthetic/

Usage (from repo root):
  python phase2_data/synthesize_data.py

Optional environment variables:
  SCALE_MEMBERS, SCALE_SUBSCRIPTIONS, SCALE_SESSIONS, SEED
"""

import os
import math
import random
from datetime import datetime, timedelta, time
import pandas as pd
import numpy as np
from typing import List

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIRS_TRY = [
    os.path.join(REPO_ROOT, 'data'),
    os.path.join(REPO_ROOT, '..', 'phase1_database_exploration', 'extracted_data'),
]
OUTPUT_DIR = os.path.join(REPO_ROOT, 'synthetic')

SEED = int(os.environ.get('SEED', '42'))
SCALE_MEMBERS = float(os.environ.get('SCALE_MEMBERS', '2.0'))
SCALE_SUBSCRIPTIONS = float(os.environ.get('SCALE_SUBSCRIPTIONS', '3.0'))
SCALE_SESSIONS = float(os.environ.get('SCALE_SESSIONS', '4.0'))

random.seed(SEED)
np.random.seed(SEED)


def find_data_dir() -> str:
    for d in DATA_DIRS_TRY:
        if os.path.exists(d) and os.path.exists(os.path.join(d, 'members.csv')):
            return d
    raise FileNotFoundError('Could not find data directory with members.csv. Tried: ' + ', '.join(DATA_DIRS_TRY))


def read_csvs(base_dir: str):
    files = {
        'members': 'members.csv',
        'coaches': 'coaches.csv',
        'subscriptions': 'subscriptions.csv',
        'sessions': 'sessions.csv',
        'plans': 'plans.csv',
        'packages': 'packages.csv',
    }
    dfs = {}
    for k, fname in files.items():
        path = os.path.join(base_dir, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(f'Missing required file: {path}')
        dfs[k] = pd.read_csv(path)
    return dfs


def to_dt(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    return df


def generate_members(members: pd.DataFrame, target_count: int) -> pd.DataFrame:
    if target_count <= len(members):
        return members.copy()
    new_members = [members]
    next_id = (members['id'].max() if 'id' in members.columns else len(members)) + 1
    needed = target_count - len(members)
    base = members.reset_index(drop=True)
    for i in range(needed):
        src = base.iloc[i % len(base)].copy()
        # Assign new id
        src['id'] = next_id
        next_id += 1
        # Mutate fields to avoid duplicates
        if 'name' in src:
            src['name'] = f"Member {src['id']}"
        if 'email' in src:
            local = f"user{src['id']}"
            domain = 'example.com'
            src['email'] = f"{local}@{domain}"
        if 'phone' in src:
            src['phone'] = f"07{random.randint(10000000, 99999999)}"
        if 'dob' in src:
            # Random DOB between 1965 and 2008
            rand_year = random.randint(1965, 2008)
            rand_day = datetime(rand_year, random.randint(1, 12), random.randint(1, 28))
            src['dob'] = rand_day.strftime('%Y-%m-%d')
        if 'created_at' in src:
            # Spread registrations over last 18 months
            days_back = random.randint(0, 540)
            created = datetime.now() - timedelta(days=days_back)
            src['created_at'] = created.strftime('%Y-%m-%d %H:%M:%S')
        new_members.append(pd.DataFrame([src]))
    return pd.concat(new_members, ignore_index=True)


def expand_subscriptions(subs: pd.DataFrame, members: pd.DataFrame, plans: pd.DataFrame, target_count: int) -> pd.DataFrame:
    if target_count <= len(subs):
        return subs.copy()
    out = [subs]
    next_id = (subs['id'].max() if 'id' in subs.columns else len(subs)) + 1
    plan_ids = plans['id'].dropna().astype(int).tolist()
    member_ids = members['id'].dropna().astype(int).tolist()
    # Use real status distribution if present
    if 'status' in subs.columns and len(subs['status'].dropna()) > 0:
        status_probs = subs['status'].dropna().value_counts(normalize=True).to_dict()
        status_choices = list(status_probs.keys())
        status_weights = list(status_probs.values())
    else:
        status_choices = ['paid', 'confirmed', 'cancelled']
        status_weights = [0.8, 0.15, 0.05]

    for _ in range(target_count - len(subs)):
        user_id = random.choice(member_ids)
        plan_id = random.choice(plan_ids)
        # start date in last 9 months
        start = datetime.now() - timedelta(days=random.randint(0, 270))
        # plan duration fallback
        plan_days = None
        if 'days' in plans.columns:
            try:
                plan_days = int(plans.loc[plans['id'] == plan_id, 'days'].iloc[0])
            except Exception:
                plan_days = 30
        plan_days = plan_days if (plan_days is not None and plan_days > 0) else 30
        end = start + timedelta(days=plan_days)
        # price from plans if available, else sample around existing
        if 'price' in plans.columns:
            try:
                price = float(plans.loc[plans['id'] == plan_id, 'price'].iloc[0])
            except Exception:
                price = max(10000, float(subs['price'].dropna().median()) if 'price' in subs.columns else 100000)
        else:
            price = max(10000, float(subs['price'].dropna().median()) if 'price' in subs.columns else 100000)
        # occasional discounts
        if random.random() < 0.1:
            price = round(price * random.uniform(0.7, 0.95))
        status = random.choices(status_choices, weights=status_weights, k=1)[0]
        row = {
            'id': next_id,
            'user_id': user_id,
            'start_date': start.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': end.strftime('%Y-%m-%d %H:%M:%S'),
            'plan_id': plan_id,
            'created_at': start.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': start.strftime('%Y-%m-%d %H:%M:%S'),
            'price': price,
            'status': status,
            'notes': ''
        }
        # optional freeze fields if exist
        for c in ['freeze_days_used', 'freeze_attempts', 'frozen_until', 'has_discount', 'discount_amount']:
            if c in subs.columns:
                row[c] = np.nan
        out.append(pd.DataFrame([row]))
        next_id += 1
    result = pd.concat(out, ignore_index=True)
    # recompute duration if exists
    if 'duration_days' in result.columns:
        result['duration_days'] = (pd.to_datetime(result['end_date']) - pd.to_datetime(result['start_date'])).dt.days
    return result


def expand_sessions(sessions: pd.DataFrame, members: pd.DataFrame, coaches: pd.DataFrame, packages: pd.DataFrame, target_count: int) -> pd.DataFrame:
    if target_count <= len(sessions):
        return sessions.copy()
    out = [sessions]
    next_id = (sessions['id'].max() if 'id' in sessions.columns else len(sessions)) + 1
    member_ids = members['id'].dropna().astype(int).tolist()
    coach_ids = coaches['id'].dropna().astype(int).tolist() if 'id' in coaches.columns else []
    package_ids = packages['id'].dropna().astype(int).tolist()

    # status distribution
    if 'status' in sessions.columns and len(sessions['status'].dropna()) > 0:
        st_probs = sessions['status'].dropna().value_counts(normalize=True).to_dict()
        st_choices = list(st_probs.keys())
        st_weights = list(st_probs.values())
    else:
        st_choices = ['scheduled', 'completed', 'cancelled']
        st_weights = [0.7, 0.25, 0.05]

    # choose model per package
    pkg_lookup = packages.set_index('id')

    for _ in range(target_count - len(sessions)):
        user_id = random.choice(member_ids)
        package_id = random.choice(package_ids)
        pkg_row = pkg_lookup.loc[package_id]
        package_name = str(pkg_row.get('name', 'Package'))
        package_price = float(pkg_row.get('price', 100000))
        model = str(pkg_row.get('model', 'instructor'))
        model_id = random.choice(coach_ids) if model == 'instructor' and coach_ids else None
        payment_method = random.choice(['cash', 'card', 'orange_money'])
        # date over last 6 months
        date = datetime.now() - timedelta(days=random.randint(0, 180))
        # hour between 7 and 21
        start_hour = random.randint(7, 21)
        start_time = datetime.combine(date.date(), time(hour=start_hour, minute=random.choice([0, 15, 30, 45])))
        duration_min = random.choice([30, 45, 60, 75])
        end_time = start_time + timedelta(minutes=duration_min)
        session_number = random.randint(1, 12)
        status = random.choices(st_choices, weights=st_weights, k=1)[0]

        row = {
            'id': next_id,
            'user_id': user_id,
            'package_id': package_id,
            'package_name': package_name,
            'package_price': package_price,
            'package_days': pkg_row.get('days', np.nan),
            'model': model,
            'model_id': model_id,
            'model_name': np.nan,
            'with_partner': pkg_row.get('with_partner', 0),
            'payment_method': payment_method,
            'date': date.strftime('%Y-%m-%d'),
            'start_time': start_time.strftime('%H:%M:%S'),
            'end_time': end_time.strftime('%H:%M:%S'),
            'session_number': session_number,
            'status': status,
            'reservation_id': np.nan,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        out.append(pd.DataFrame([row]))
        next_id += 1

    return pd.concat(out, ignore_index=True)


def main():
    print('🔄 Generating synthetic data for Phase 2...')
    base_dir = find_data_dir()
    print(f'📁 Using base data from: {base_dir}')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dfs = read_csvs(base_dir)
    members = dfs['members']
    coaches = dfs['coaches']
    subscriptions = dfs['subscriptions']
    sessions = dfs['sessions']
    plans = dfs['plans']
    packages = dfs['packages']

    # Normalize numeric ids
    for df in [members, coaches, subscriptions, sessions, plans, packages]:
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')

    # Scale targets
    target_members = max(len(members), math.ceil(len(members) * SCALE_MEMBERS))
    target_subs = max(len(subscriptions), math.ceil(len(subscriptions) * SCALE_SUBSCRIPTIONS))
    target_sessions = max(len(sessions), math.ceil(len(sessions) * SCALE_SESSIONS))

    print(f'👥 Members: {len(members)} -> {target_members}')
    members_syn = generate_members(members, target_members)

    print(f'💳 Subscriptions: {len(subscriptions)} -> {target_subs}')
    subs_syn = expand_subscriptions(subscriptions, members_syn, plans, target_subs)

    print(f'🏋️ Sessions: {len(sessions)} -> {target_sessions}')
    sessions_syn = expand_sessions(sessions, members_syn, coaches, packages, target_sessions)

    # Save all (including original plans/packages/coaches for completeness)
    outputs = {
        'members.csv': members_syn,
        'coaches.csv': coaches,
        'plans.csv': plans,
        'packages.csv': packages,
        'subscriptions.csv': subs_syn,
        'sessions.csv': sessions_syn,
    }
    for fname, df in outputs.items():
        out_path = os.path.join(OUTPUT_DIR, fname)
        df.to_csv(out_path, index=False)
        print(f'✅ Wrote {fname}: {len(df):,} rows')

    print(f'🎯 Synthetic data ready in: {OUTPUT_DIR}')
    print('Tip: set SCALE_* env vars to adjust volume, e.g.:')
    print('  SET SCALE_SESSIONS=6 & python phase2_data/synthesize_data.py (Windows)')
    print('  SCALE_SESSIONS=6 python3 phase2_data/synthesize_data.py (macOS/Linux)')


if __name__ == '__main__':
    main()
