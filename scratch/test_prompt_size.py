import sys, json
sys.path.insert(0, 'd:/Projects/Voice_assist')
from llm.prompts import INTENT_PARSER_SYSTEM_PROMPT
from data.road_concepts import ROAD_CONCEPTS

# Simulate what IntentParser sends to the model
available_roads  = ["Mar-25 Comparison As per CA Delhi Vadodara NH-148N Pkg-8 (ID: dataset_1)"]
available_months = ["Repair and Maintenance asper CA", "Mar-25 Summary", "Roughness,Rut,Crack,Ravelling",
                    "Mar-25 Comparision with CA@100m", "100m", "50m", "Mar-25 Comparison with CA @50m",
                    "Mar-25 Potholes", "Mar-25 Minor Depression", "Jul-24 Summary",
                    "Jul-24 Comparison with CA @100m", "Jul-24 Comparison with CA @50m",
                    "Jul-24 Potholes", "Jul-24 Minor Depression"]

sys_prompt = INTENT_PARSER_SYSTEM_PROMPT.format(
    available_roads=json.dumps(available_roads),
    available_months=json.dumps(available_months),
    road_concepts=json.dumps(ROAD_CONCEPTS, indent=2),
)
usr_prompt = "Parse this question into the RoadQuery JSON schema: Which chainage has the maximum rut depth?"

sys_chars = len(sys_prompt)
usr_chars = len(usr_prompt)
total_chars = sys_chars + usr_chars

# Rough token estimate: ~4 chars per token
sys_tokens  = sys_chars  // 4
usr_tokens  = usr_chars  // 4
total_tokens = total_chars // 4

print("=== Intent Parser Prompt Size Analysis ===")
print(f"System prompt: {sys_chars:,} chars  ~{sys_tokens:,} tokens")
print(f"User prompt:   {usr_chars:,} chars  ~{usr_tokens:,} tokens")
print(f"TOTAL input:   {total_chars:,} chars  ~{total_tokens:,} tokens")
print()
print("--- System Prompt Sections ---")
print(f"  Header/schema:       ~{len(INTENT_PARSER_SYSTEM_PROMPT) // 4} tokens (template)")
print(f"  available_roads:     {len(json.dumps(available_roads)) // 4} tokens")
print(f"  available_months:    {len(json.dumps(available_months)) // 4} tokens")
print(f"  road_concepts:       {len(json.dumps(ROAD_CONCEPTS, indent=2)) // 4} tokens  <- biggest cost")
print()
print("--- road_concepts preview ---")
for k, v in list(ROAD_CONCEPTS.items())[:5]:
    print(f"  {k!r}: {v!r}")
print(f"  ... ({len(ROAD_CONCEPTS)} total entries)")
