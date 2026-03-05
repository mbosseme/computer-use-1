import json

data = [
    {
        "col_name": "manufacturer_entity_code",
        "data_type": "STRING",
        "null_count": 0,
        "distinct_count": 12615
    },
    {
        "col_name": "manufacturer_name",
        "data_type": "STRING",
        "null_count": 0,
        "distinct_count": 12699,
        "top_values": [{"count":71873,"value":"W.W. GRAINGER, INC."},{"count":65639,"value":"MEDLINE INDUSTRIES, LP"},{"count":44828,"value":"HOWMEDICA OSTEONICS CORP. DBA STRYKER ORTHOPAEDICS"},{"count":41159,"value":"DEPUY SYNTHES"},{"count":29592,"value":"STERIS CORPORATION"}]
    },
    {
        "col_name": "manufacturer_catalog_number",
        "data_type": "STRING",
        "null_count": 43098,
        "distinct_count": 447012
    },
    {
        "col_name": "contract_category",
        "data_type": "STRING",
        "null_count": 0,
        "distinct_count": 863,
        "top_values": [{"count":125569,"value":"GENERAL ORTHOPEDIC TRAUMA PRODUCTS"},{"count":95302,"value":"MAINTENANCE REPAIR AND OPERATIONS"},{"count":91814,"value":"SURGICAL INSTRUMENTS"},{"count":77737,"value":"SPINAL IMPLANTS AND RELATED PRODUCTS"},{"count":77022,"value":"ORTHOPEDIC TOTAL JOINT IMPLANTS"}]
    },
    {
        "col_name": "hciq_manufacturer_name",
        "data_type": "STRING",
        "null_count": 337140,
        "distinct_count": 4569,
        "top_values": [{"count":337140,"value":None},{"count":77730,"value":"JOHNSON & JOHNSON HEALTHCARE"},{"count":75024,"value":"STRYKER CORPORATION"},{"count":63852,"value":"MEDLINE INDUSTRIES INC"},{"count":43121,"value":"MEDTRONIC USA INC"}]
    },
    {
        "col_name": "hciq_manufacturer_catalog_number",
        "data_type": "STRING",
        "null_count": 337140,
        "distinct_count": 367450
    },
    {
        "col_name": "hciq_item_description",
        "data_type": "STRING",
        "null_count": 337144,
        "distinct_count": 370251
    },
    {
        "col_name": "hciq_low_benchmark",
        "data_type": "FLOAT",
        "null_count": 337140,
        "distinct_count": 64150
    },
    {
        "col_name": "hciq_90_benchmark",
        "data_type": "FLOAT",
        "null_count": 337140,
        "distinct_count": 226480
    },
    {
        "col_name": "hciq_75_benchmark",
        "data_type": "FLOAT",
        "null_count": 337140,
        "distinct_count": 208293
    },
    {
        "col_name": "hciq_50_benchmark",
        "data_type": "FLOAT",
        "null_count": 337140,
        "distinct_count": 191313
    },
    {
        "col_name": "hciq_high_benchmark",
        "data_type": "FLOAT",
        "null_count": 337140,
        "distinct_count": 75274
    },
    {
        "col_name": "abi_snapshot_date",
        "data_type": "DATE",
        "null_count": 0,
        "distinct_count": 4,
        "top_values": [{"count":436798,"value":"2026-02-09"},{"count":425028,"value":"2026-01-14"},{"count":408018,"value":"2025-12-05"},{"count":392457,"value":"2025-11-13"}]
    },
    {
        "col_name": "abi_load_date",
        "data_type": "DATE",
        "null_count": 0,
        "distinct_count": 3
    }
]

with open('runs/2026-03-04__portfolio-competitiveness/tmp/profile_stats.json', 'w') as f:
    for item in data:
        f.write(json.dumps(item) + '\n')
