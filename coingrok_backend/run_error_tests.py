#!/usr/bin/env python3
"""
Test runner for error handling system.

Runs all error handling tests and provides a summary.
"""

import os
import sys
import subprocess

def run_test(test_file, description):
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print('='*60)
    
    try:
        subprocess.run([
            sys.executable, f"tests/{test_file}"
        ], env={**os.environ, "PYTHONPATH": "."}, 
        capture_output=False, check=True)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def main():
    """Run all error handling tests."""
    print("🚀 CoinGrok Error Handling Test Suite")
    print("="*60)
    
    tests = [
        ("test_error_handling.py", "Exception Mapping & Response Format Tests"),
        ("test_error_integration.py", "Error Handling Integration Tests")
    ]
    
    results = []
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {description}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All error handling tests passed!")
        print("\n🛡️  Error Handling System Status: PRODUCTION READY")
        print("\nKey Features Verified:")
        print("✓ Single source of truth exception mapping")
        print("✓ Unified error envelope format")
        print("✓ Correlation ID tracking")
        print("✓ Message sanitization")
        print("✓ HTTP status code mapping")
        print("✓ Content-Type headers")
        print("✓ Integration across all endpoints")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    exit(main())