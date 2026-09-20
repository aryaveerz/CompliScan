import sqlite3, os, json

for db_file in ['compliscan_validation.db', 'compliscan_test.db', 'compliscan.db']:
    if not os.path.exists(db_file):
        continue
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    print('========================================')
    print('=== DB:', db_file, '===')
    print('========================================')
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]
    print('Tables:', tables)
    if 'inspections' not in tables:
        print('No inspections table in', db_file)
        continue
    c.execute("SELECT id, case_number, product_name, origin_status, status FROM inspections")
    inspections = c.fetchall()
    print(f'Total Inspections in {db_file}: {len(inspections)}')
    for insp in inspections:
        insp_id, case_num, prod_name, origin, st = insp
        print(f'\n--- Inspection: {insp_id} | {case_num} | {prod_name} | {origin} | {st} ---')
        c.execute("SELECT id, original_filename, evidence_type, file_size_bytes FROM evidence_assets WHERE inspection_id = ?", (insp_id,))
        evs = c.fetchall()
        print(f'  Evidence Assets ({len(evs)}):', evs)
        c.execute("SELECT id, requirement_name, result, applicability_status, rule_citation FROM compliance_findings WHERE inspection_id = ?", (insp_id,))
        findings = c.fetchall()
        print(f'  Findings ({len(findings)}):', findings)
        if 'product_declarations' in tables:
            c.execute("SELECT id, inspection_id, manufacturer_name_address, mrp, net_quantity, generic_name FROM product_declarations WHERE inspection_id = ?", (insp_id,))
            print('  Product Declarations:', c.fetchall())
        if 'structured_declaration_results' in tables:
            c.execute("SELECT id, inspection_id, evidence_id FROM structured_declaration_results WHERE inspection_id = ?", (insp_id,))
            print('  Structured Declaration Results:', c.fetchall())
