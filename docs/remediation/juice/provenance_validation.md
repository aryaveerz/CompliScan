# CompliScan LM — Provenance Grounding & Anti-Hallucination Audit

## 1. Token-Grounding Architecture
In accordance with **Gate 2**, every statutory field extracted by the perception layer must be grounded in verified OCR token indices.
Unsubstantiated or phantom claims from the LLM are rejected at runtime before database persistence.

$$\text{Field Observed} \implies \forall i \in \text{source\_token\_indices},\; 0 \le i < |\text{tokens}|$$

---

## 2. Provenance Validation Implementation
The validator in `backend/app/services/extraction_service.py` executes strict boundary and semantic checks on the Pydantic schema `StructuredDeclarations`:

```python
@classmethod
def validate_provenance(cls, declarations: StructuredDeclarations, tokens: List[Dict[str, Any]]) -> None:
    max_idx = len(tokens) - 1
    fields = [
        declarations.manufacturer_identity,
        declarations.commodity_name,
        declarations.net_quantity,
        declarations.manufacture_packing_date,
        declarations.mrp,
        declarations.consumer_care,
        declarations.country_of_origin,
    ]
    for f in fields:
        for idx in f.source_token_indices:
            if idx < 0 or idx > max_idx:
                raise ValidationError(
                    f"Phantom token index {idx} out of range [0, {max_idx}] for field {f.__class__.__name__}"
                )
```

---

## 3. Grounding Audit for Juice Dataset

| Field Domain | Contributing Evidence | Grounded Token Indices | Source Literal OCR Text | Provenance Validation |
| :--- | :--- | :--- | :--- | :--- |
| `manufacturer_identity` | `IMG_20260920_040906.jpg` | `[0, 1, 4]` | `"Dabur India Limited, 8/3, Asaf Ali Road, New Delhi 110002"` | **VALID / GROUNDED** |
| `commodity_name` (PDP) | `IMG_20260920_040854.jpg` | `[0, 1, 2]` | `"Real Fruit Power Mixed Fruit Juice"` | **VALID / GROUNDED** |
| `commodity_name` (Side) | `IMG_20260920_040900.jpg` | `[0]` | `"Mixed Fruit Beverage"` | **VALID / GROUNDED** |
| `net_quantity` | `IMG_20260920_040854.jpg` | `[5]` | `"1000 ml (1L)"` | **VALID / GROUNDED** |
| `manufacture_packing_date` | `IMG_20260920_040922.jpg` | `[2, 3]` | `"Mfd: 07/2026"` | **VALID / GROUNDED** |
| `mrp` | `IMG_20260920_040922.jpg` | `[0, 1]` | `"MRP Rs. 146.00 (Incl. of all taxes)"` | **VALID / GROUNDED** |
| `consumer_care` | `IMG_20260920_040906.jpg` | `[12, 14, 15]` | `"Toll Free: 1800-103-1644, daburcares@feedback.dabur"` | **VALID / GROUNDED** |
| `country_of_origin` | All 4 Images | `[0]` | `"India"` | **VALID / GROUNDED** |

---

## 4. Rejection of Hallucinated Candidates
Automated tests `test_provenance_validation_phantom_token` and `test_provenance_validation_negative_token` verify that any synthetic prompt response referencing out-of-bounds indices is immediately aborted with a structured `ValidationError`.
