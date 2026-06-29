import os
import sys
import json
from dataclasses import asdict

# Add project root to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metadata.road_registry import RoadRegistry
from nlp.intent_parser import IntentParser
from llm.llm_factory import LLMFactory


def setup_mock_registry():
    """
    Sets up a mock dataset registry for testing the Intent Parser.
    """
    RoadRegistry.register_dataset(
        dataset_id="dataset_1",
        name="Road_A",
        file_path="uploaded_files/Road_A.xlsx",
        available_sheets=["Jul-24", "Mar-25"]
    )
    RoadRegistry.register_dataset(
        dataset_id="dataset_2",
        name="Road_B",
        file_path="uploaded_files/Road_B.xlsx",
        available_sheets=["Jul-24", "Mar-25"]
    )
    print("Mock registry configured for test:")
    print(json.dumps(RoadRegistry.get_registry(), indent=2))


def run_intent_tests():
    setup_mock_registry()
    
    # Initialize parser
    try:
        model = LLMFactory.create()
        parser = IntentParser(model)
    except Exception as e:
        print(f"Error initializing LLM provider: {str(e)}")
        print("Please ensure your LLM provider is running/accessible as configured in settings.")
        return

    test_queries = [
        # Ranking queries
        "Which chainage has maximum rut depth?",
        "Show top 10 stretches with highest potholes.",
        
        # Aggregation queries
        "Which lane has highest average roughness?",
        "What is the average cracking area in Road_A?",
        
        # Comparison queries
        "Compare Road_A and Road_B for worst potholes.",
        
        # Trend queries
        "Which road deteriorated most between Jul-24 and Mar-25?",
        
        # Violation queries
        "Which sections violate the Concession Agreement?",
        
        # Multi-metric / Semantic queries
        "Where is the pavement condition deteriorating fastest?",
        "Show stretches where roughness improved but cracking worsened."
    ]

    print("\n--- Running Intent Parser Tests ---")
    for i, q in enumerate(test_queries, 1):
        print(f"\nQuery {i}: \"{q}\"")
        try:
            road_query = parser.parse(q)
            print(f"Resulting RoadQuery object:")
            print(json.dumps(asdict(road_query), indent=2))
        except Exception as e:
            print(f"Failed to parse query: {str(e)}")
            
        print("-" * 50)


if __name__ == "__main__":
    run_intent_tests()
