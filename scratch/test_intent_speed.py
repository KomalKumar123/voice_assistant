import sys, time, json
sys.path.insert(0, 'd:/Projects/Voice_assist')
from llm.llm_factory import LLMFactory
from nlp.intent_parser import IntentParser
from metadata.road_registry import RoadRegistry
from dataclasses import asdict

RoadRegistry.register_dataset('dataset_1', 'Road_A', 'x', ['Jul-24', 'Mar-25'])

llm    = LLMFactory.create()
parser = IntentParser(llm)

questions = [
    'Which chainage has the maximum rut depth?',
    'Compare Road_A potholes between Jul-24 and Mar-25.',
    'What is the average roughness index?',
]

print("=== Intent Parser Speed Test (max_tokens=256 cap + compact prompt) ===")
total = 0
for q in questions:
    start = time.time()
    rq    = parser.parse(q)
    t     = time.time() - start
    total += t
    d     = asdict(rq)
    # Show only non-None/non-empty fields
    compact = {k: v for k, v in d.items() if v is not None and v != [] and v != 1}
    print(f"Q: {q}")
    print(f"   Result : {compact}")
    print(f"   Elapsed: {t:.2f}s")
    print()

print(f"Total for {len(questions)} queries: {total:.2f}s  avg: {total/len(questions):.2f}s/query")
