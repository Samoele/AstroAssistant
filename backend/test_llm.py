import time
from app.services.llm_service import generate_companion_response

def run_tests():
    test_cases = [
        {
            "scenario": "Healthy achievement (Should trigger 'excited' or 'happy')",
            "prompt": "I just crushed a 45-minute gym workout and drank a full liter of water!"
        },
        {
            "scenario": "Bad habit deviation (Should trigger 'grumpy')",
            "prompt": "I stayed up playing video games until 4 AM and ate an entire family-size bag of chips."
        },
        {
            "scenario": "Low energy / Stress (Should trigger 'sad')",
            "prompt": "I had a really overwhelming day at work and I feel completely exhausted."
        },
        {
            "scenario": "Planning / Strategy (Should trigger 'thinking')",
            "prompt": "Can you help me design a meal schedule to hit 120 grams of protein daily?"
        }
    ]

    print("==================================================")
    print("BENCHMARKING LOCAL HERMES INFERENCE LATENCY")
    print("==================================================")

    total_start = time.perf_counter()

    for i, test in enumerate(test_cases, start=1):
        print(f"\n--- TEST CASE #{i}: {test['scenario']} ---")
        print(f"User Message: \"{test['prompt']}\"")
        
        # Start timer right before inference
        start_time = time.perf_counter()
        response = generate_companion_response(test['prompt'])
        elapsed_time = time.perf_counter() - start_time

        print(f"\n[Companion Dialogue]: {response.response_text}")
        print(f"[Avatar Emotion]    : {response.avatar_state.emotion.value}")
        print(f"[Kinetic Animation] : {response.avatar_state.animation.value}")
        print(f"[Mood Reason]       : {response.avatar_state.mood_reason}")
        print(f"[Suggested Actions] : {response.suggested_actions}")
        print(f"⏱️ [Inference Latency]: {elapsed_time:.2f} seconds")
        print("-" * 50)

    total_elapsed = time.perf_counter() - total_start
    print(f"\nTotal benchmark time across all 4 tests: {total_elapsed:.2f} seconds")

if __name__ == "__main__":
    run_tests()