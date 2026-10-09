#!/usr/bin/env python3
"""Issue #12 native-placement paired E0; local finalized evidence only."""
import argparse
import json
from pathlib import Path
import statistics
import sys

import analyze_e0b as paired

NATIVE_ENVIRONMENT = {
    'OMP_NUM_THREADS': '8', 'MKL_NUM_THREADS': '8', 'OMP_DYNAMIC': 'FALSE',
    'OMP_PROC_BIND': None, 'OMP_PLACES': None, 'GOMP_CPU_AFFINITY': None,
}
SANITY_THRESHOLDS = {
    'stock_median_qps_min': 2471.42,
    'stock_median_mean_latency_us_max': 3212.82,
    'reference_issue8_stock_median_qps': 4942.84,
    'reference_issue8_stock_median_mean_latency_us': 1606.41,
}


def validate_native_environment(records, plan):
    for key, expected in NATIVE_ENVIRONMENT.items():
        if key not in plan['environment'] or plan['environment'][key] != expected:
            raise ValueError(f'Native/unbound environment violation: {key}')
    for record in records:
        # The historical harness records four OpenMP/MKL fields. Full command
        # exports/unsets are also checked by paired.load_run. Extra fields, when
        # supplied, cannot contradict the native contract.
        environment = record['manifest']['environment']
        for key, expected in NATIVE_ENVIRONMENT.items():
            if key in environment and environment[key] != expected:
                raise ValueError(f'Native/unbound manifest environment violation: {key}')
        for snapshot in record.get('runtime_snapshots', []):
            observed = snapshot.get('benchmark_environment')
            if observed is not None:
                if any(key not in observed or observed[key] != value
                       for key, value in NATIVE_ENVIRONMENT.items()):
                    raise ValueError('Native/unbound process environment violation')


def native_sanity(records, plan):
    if any(plan['native_sanity'].get(key) != value for key, value in SANITY_THRESHOLDS.items()):
        raise ValueError('Native-regime sanity thresholds differ from Issue #12')
    stock = [r['summary'] for r in records if r['case'] == 'STOCK']
    qps = statistics.median(s['qps'] for s in stock)
    latency = statistics.median(s['mean_latency_us'] for s in stock)
    return {'stock_median_qps': qps, 'stock_median_mean_latency_us': latency,
            'thresholds': SANITY_THRESHOLDS,
            'pass': qps >= SANITY_THRESHOLDS['stock_median_qps_min'] and
                    latency <= SANITY_THRESHOLDS['stock_median_mean_latency_us_max'],
            'meaning': 'Broad native operating-regime check; not equivalence'}


def analyze_records(records, plan):
    validate_native_environment(records, plan)
    result = paired.analyze_records(records, plan)
    sanity = native_sanity(records, plan)
    relative = result['classification'].removeprefix('E0B_')
    classification = ('E0C_FAIL' if relative == 'FAIL' else
                      'E0C_INCONCLUSIVE' if relative == 'INCONCLUSIVE' or not sanity['pass'] else
                      'E0C_PROCEED')
    return {**result, 'classification': classification,
            'relative_classification': relative, 'native_regime_sanity': sanity,
            'protocol': 'paired-native-e0c-v1', 'g0_stage_bc_executed': False}


def analyze_campaign(campaign):
    return paired.analyze_campaign(campaign, issue=12, record_analyzer=analyze_records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New directory; never overwrite')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        result = analyze_campaign(args.campaign)
    except (ValueError, KeyError, TypeError, OSError, statistics.StatisticsError) as error:
        result = {'campaign_valid': False, 'classification': None,
                  'protocol_status': 'INVALID/STOP', 'error': str(error)}
    (args.output / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({key: result.get(key) for key in
                     ('campaign_valid', 'classification', 'campaign_id', 'error')}, indent=2))
    return 2 if not result['campaign_valid'] else 1 if result['classification'] == 'E0C_FAIL' else 0


if __name__ == '__main__':
    sys.exit(main())
