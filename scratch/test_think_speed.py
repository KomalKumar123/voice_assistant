import sys, time
sys.path.insert(0, 'd:/Projects/Voice_assist')
from llm.llm_factory import LLMFactory

llm = LLMFactory.create()
print(f"think enabled: {llm.enable_thinking}")

# Test 1: think=False + plain text — should be fast
start = time.time()
resp = llm.generate("You are a helpful assistant.", "What is 2+2? Answer in one sentence.")
t1 = time.time() - start
print(f"\nTest 1 (plain, no JSON): {t1:.2f}s")
print(f"  Response: {repr(resp)}")
print(f"  Has <think>: {'<think>' in resp}")

# Test 2: think=False + format=json — does it stay fast or regress to slow?
start = time.time()
resp2 = llm.generate(
    "Output only valid JSON. No other text.",
    "Return JSON with keys: status (ok) and value (42).",
    response_format="json"
)
t2 = time.time() - start
print(f"\nTest 2 (JSON mode): {t2:.2f}s")
print(f"  Response: {repr(resp2[:300])}")
print(f"  Has <think>: {'<think>' in resp2}")

print(f"\nConclusion: JSON mode overhead = {t2 - t1:.2f}s extra")
