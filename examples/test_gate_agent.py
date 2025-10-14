"""
Test script for Gate Agent and Data Agent functionality
Demonstrates condition validation without requiring Databricks connection
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.gate_agent import GateAgent
from datetime import datetime, timedelta, timezone


def test_gate_agent_basic():
    """Test basic Gate Agent initialization and condition loading"""
    print("=== Test 1: Gate Agent Initialization ===")

    gate_agent = GateAgent()

    # Get available report types
    report_types = gate_agent.get_available_report_types()
    print(f"Available report types: {report_types}")

    # Get specific condition
    monthly_sales_condition = gate_agent.get_report_condition("monthly_sales")
    print(f"\nMonthly Sales Condition:")
    print(f"  Description: {monthly_sales_condition.get('description')}")
    print(f"  Required Tables: {monthly_sales_condition.get('required_tables')}")
    print(f"  Min Rows: {monthly_sales_condition.get('min_rows')}")
    print(f"  Freshness Days: {monthly_sales_condition.get('freshness_days')}")

    print("\n✅ Test 1 Passed\n")


def test_gate_agent_validation_ready():
    """Test validation with all conditions satisfied"""
    print("=== Test 2: Validation - READY Status ===")

    gate_agent = GateAgent()

    # Mock metadata with all requirements satisfied
    mock_metadata = {
        "sales_summary": {
            "columns": ["month", "region", "sales"],
            "rows": 100,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exists": True
        },
        "profit_margin": {
            "columns": ["region", "margin"],
            "rows": 80,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exists": True
        }
    }

    validation_result = gate_agent.validate("monthly_sales", mock_metadata)

    print(f"Report Type: {validation_result['report_type']}")
    print(f"Status: {validation_result['status']}")
    print(f"Message: {validation_result['message']}")
    print(f"Missing: {validation_result['missing']}")
    print(f"Warnings: {validation_result['warnings']}")

    assert validation_result["status"] == "READY", "Expected READY status"
    print("\n✅ Test 2 Passed\n")


def test_gate_agent_validation_blocked():
    """Test validation with missing tables"""
    print("=== Test 3: Validation - BLOCKED Status ===")

    gate_agent = GateAgent()

    # Mock metadata with missing table
    mock_metadata = {
        "sales_summary": {
            "columns": ["month", "region", "sales"],
            "rows": 100,
            "last_updated": datetime.now().isoformat() + "Z",
            "exists": True
        }
        # profit_margin table is missing
    }

    validation_result = gate_agent.validate("monthly_sales", mock_metadata)

    print(f"Report Type: {validation_result['report_type']}")
    print(f"Status: {validation_result['status']}")
    print(f"Message: {validation_result['message']}")
    print(f"Missing: {validation_result['missing']}")
    print(f"Warnings: {validation_result['warnings']}")

    assert validation_result["status"] == "BLOCKED", "Expected BLOCKED status"
    assert "profit_margin" in validation_result["missing"], "Expected missing profit_margin"
    print("\n✅ Test 3 Passed\n")


def test_gate_agent_validation_partial():
    """Test validation with data quality warnings"""
    print("=== Test 4: Validation - PARTIAL Status ===")

    gate_agent = GateAgent()

    # Mock metadata with old data (freshness issue)
    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()

    mock_metadata = {
        "sales_summary": {
            "columns": ["month", "region", "sales"],
            "rows": 100,
            "last_updated": old_timestamp,
            "exists": True
        },
        "profit_margin": {
            "columns": ["region", "margin"],
            "rows": 5,  # Below min_rows (10)
            "last_updated": old_timestamp,
            "exists": True
        }
    }

    validation_result = gate_agent.validate("monthly_sales", mock_metadata)

    print(f"Report Type: {validation_result['report_type']}")
    print(f"Status: {validation_result['status']}")
    print(f"Message: {validation_result['message']}")
    print(f"Missing: {validation_result['missing']}")
    print(f"Warnings: {validation_result['warnings']}")

    assert validation_result["status"] == "PARTIAL", "Expected PARTIAL status"
    assert len(validation_result["warnings"]) > 0, "Expected warnings"
    print("\n✅ Test 4 Passed\n")


def test_comprehensive_business_report():
    """Test validation for comprehensive business report"""
    print("=== Test 5: Comprehensive Business Report Validation ===")

    gate_agent = GateAgent()

    # Mock metadata with all required tables
    mock_metadata = {
        "sales_summary": {
            "columns": ["month", "region", "sales"],
            "rows": 100,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exists": True
        },
        "contracts": {
            "columns": ["contract_id", "status", "customer_id"],
            "rows": 50,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exists": True
        },
        "region_summary": {
            "columns": ["region_id", "region_name"],
            "rows": 20,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exists": True
        }
    }

    validation_result = gate_agent.validate("comprehensive_business", mock_metadata)

    print(f"Report Type: {validation_result['report_type']}")
    print(f"Status: {validation_result['status']}")
    print(f"Message: {validation_result['message']}")

    # Get report details
    condition = validation_result.get("condition", {})
    print(f"\nReport Details:")
    print(f"  Description: {condition.get('description')}")
    print(f"  Required Genie Domains: {condition.get('genie_domains')}")

    assert validation_result["status"] == "READY", "Expected READY status"
    print("\n✅ Test 5 Passed\n")


def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("Gate Agent Test Suite")
    print("=" * 60)
    print()

    try:
        test_gate_agent_basic()
        test_gate_agent_validation_ready()
        test_gate_agent_validation_blocked()
        test_gate_agent_validation_partial()
        test_comprehensive_business_report()

        print("=" * 60)
        print("✅ All Tests Passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test Failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
