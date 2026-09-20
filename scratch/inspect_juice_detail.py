import sqlite3, json

conn = sqlite3.connect('compliscan_validation.db')
c = conn.cursor()
c.execute("SELECT id, case_number, product_name, origin_status, status, processing_state, finalization_status FROM inspections WHERE id LIKE '%juice%'")
for row in c.fetchall():
    insp_id, case_num, name, origin, st, proc, fin = row
    print(f"\n========================================================")
    print(f"ID: {insp_id}, Case: {case_num}, Product: {name}, Origin: {origin}, Status: {st}, Final: {fin}")
    
    c.execute("SELECT id, original_filename, evidence_type, file_size_bytes, storage_path, sha256_hash FROM evidence_assets WHERE inspection_id = ?", (insp_id,))
    for ev in c.fetchall():
        print(f"  Evidence: ID={ev[0]}, File={ev[1]}, Type={ev[2]}, Size={ev[3]}, Path={ev[4]}")
        
    c.execute("SELECT id, requirement_name, result, applicability_status, rule_citation, metadata_payload FROM compliance_findings WHERE inspection_id = ?", (insp_id,))
    for f in c.fetchall():
        print(f"  Finding: ID={f[0]}, Req={f[1]}, Result={f[2]}, Rule={f[4]}, Payload={f[5]}")

    c.execute("SELECT id, evidence_id, declarations FROM structured_declaration_results WHERE inspection_id = ?", (insp_id,))
    for s in c.fetchall():
        print(f"  Structured Decl: ID={s[0]}, EvidenceID={s[1]}, Declarations={s[2]}")
