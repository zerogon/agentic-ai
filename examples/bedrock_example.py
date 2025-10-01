"""
Example: Using AWS Bedrock Integration

This example demonstrates how to use the new Bedrock helper
to interact with Claude models on AWS Bedrock.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bedrock_helper import BedrockHelper
import pandas as pd


def example_basic_chat():
    """Example 1: Basic chat completion"""
    print("\n" + "="*60)
    print("Example 1: Basic Chat Completion")
    print("="*60)

    # Initialize Bedrock (uses default credentials)
    bedrock = BedrockHelper(region_name="us-east-1")

    # Simple chat
    messages = [
        {"role": "user", "content": "What are the top 3 benefits of using cloud data warehouses?"}
    ]

    result = bedrock.chat_completion(
        messages=messages,
        model_id="anthropic.claude-3-haiku-20240307-v1:0",  # Using fastest model
        temperature=0.7,
        max_tokens=500
    )

    if result["success"]:
        print(f"\n✅ Response:\n{result['content']}")
        print(f"\n📊 Token Usage: {result['usage']}")
    else:
        print(f"\n❌ Error: {result['error']}")


def example_data_analysis():
    """Example 2: Data analysis with Claude"""
    print("\n" + "="*60)
    print("Example 2: Data Analysis")
    print("="*60)

    # Create sample data
    sales_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [45000, 52000, 48000, 61000, 58000, 67000],
        'Customers': [120, 135, 125, 155, 148, 170]
    })

    print("\n📊 Sample Data:")
    print(sales_data.to_string())

    # Initialize Bedrock
    bedrock = BedrockHelper(region_name="us-east-1")

    # Analyze data
    result = bedrock.analyze_data(
        data_summary=sales_data.to_string(),
        question="What trends do you see in this sales data? What recommendations would you make?",
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"  # Using balanced model
    )

    if result["success"]:
        print(f"\n✅ Analysis:\n{result['content']}")
        print(f"\n📊 Token Usage: {result['usage']}")
    else:
        print(f"\n❌ Error: {result['error']}")


def example_sql_explanation():
    """Example 3: SQL query explanation"""
    print("\n" + "="*60)
    print("Example 3: SQL Query Explanation")
    print("="*60)

    sql_query = """
    SELECT
        customer_region,
        COUNT(DISTINCT customer_id) as total_customers,
        SUM(order_amount) as total_revenue,
        AVG(order_amount) as avg_order_value
    FROM sales_orders
    WHERE order_date >= '2024-01-01'
    GROUP BY customer_region
    HAVING SUM(order_amount) > 10000
    ORDER BY total_revenue DESC
    LIMIT 10
    """

    print(f"\n📝 SQL Query:\n{sql_query}")

    # Initialize Bedrock
    bedrock = BedrockHelper(region_name="us-east-1")

    # Explain SQL
    result = bedrock.generate_sql_explanation(
        sql_query=sql_query,
        model_id="anthropic.claude-3-haiku-20240307-v1:0"  # Fast model is enough
    )

    if result["success"]:
        print(f"\n✅ Explanation:\n{result['content']}")
        print(f"\n📊 Token Usage: {result['usage']}")
    else:
        print(f"\n❌ Error: {result['error']}")


def example_model_comparison():
    """Example 4: Compare different Claude models"""
    print("\n" + "="*60)
    print("Example 4: Model Comparison")
    print("="*60)

    bedrock = BedrockHelper(region_name="us-east-1")

    # Get available models
    models = bedrock.get_available_models()

    print("\n📋 Available Claude Models:")
    for model in models:
        print(f"\n  • {model['name']}")
        print(f"    Model ID: {model['model_id']}")
        print(f"    Description: {model['description']}")
        print(f"    Max Tokens: {model['max_tokens']}")


def example_multi_turn_conversation():
    """Example 5: Multi-turn conversation"""
    print("\n" + "="*60)
    print("Example 5: Multi-turn Conversation")
    print("="*60)

    bedrock = BedrockHelper(region_name="us-east-1")

    # Conversation history
    messages = [
        {"role": "user", "content": "I'm analyzing customer churn. What metrics should I track?"}
    ]

    # First turn
    print("\n👤 User: I'm analyzing customer churn. What metrics should I track?")
    result = bedrock.chat_completion(
        messages=messages,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    )

    if result["success"]:
        print(f"\n🤖 Claude: {result['content'][:200]}...")

        # Add to conversation
        messages.append({"role": "assistant", "content": result["content"]})
        messages.append({"role": "user", "content": "How can I calculate customer lifetime value?"})

        # Second turn
        print("\n👤 User: How can I calculate customer lifetime value?")
        result2 = bedrock.chat_completion(
            messages=messages,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )

        if result2["success"]:
            print(f"\n🤖 Claude: {result2['content'][:200]}...")
            print(f"\n📊 Total Token Usage: {result2['usage']}")
    else:
        print(f"\n❌ Error: {result['error']}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("AWS Bedrock Integration Examples")
    print("="*60)

    print("\n⚙️  Configuration:")
    print("  • Region: us-east-1")
    print("  • Authentication: Using default AWS credentials")
    print("  • Note: Make sure AWS credentials are configured")

    try:
        # Run examples
        example_basic_chat()
        example_data_analysis()
        example_sql_explanation()
        example_model_comparison()
        example_multi_turn_conversation()

        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check AWS credentials: aws configure")
        print("  2. Verify Bedrock access in your region")
        print("  3. Check IAM permissions for bedrock:InvokeModel")
        print("  4. Install dependencies: pip install boto3")


if __name__ == "__main__":
    main()
