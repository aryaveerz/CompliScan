"""
Run test_declaration_validation.py test cases directly.
"""
import sys
import os

# Add workspace to sys.path
sys.path.insert(0, os.path.abspath("."))

from backend.tests.test_declaration_validation import TestDeclarationValidationEngine

def main():
    test_obj = TestDeclarationValidationEngine()
    methods = [m for m in dir(test_obj) if m.startswith("test_case_")]
    print(f"Running {len(methods)} declaration validation test cases...\n")
    
    passed = 0
    failed = 0
    
    for m_name in sorted(methods):
        method = getattr(test_obj, m_name)
        try:
            method()
            print(f"[PASS] {m_name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {m_name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            
    print(f"\n==========================================")
    print(f"Total: {len(methods)} | Passed: {passed} | Failed: {failed}")
    print(f"==========================================")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
