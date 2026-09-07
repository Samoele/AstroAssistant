from app.services.llm_service import generate_companion_response
import time

def run_tests():
    # Test cases designed to trigger different emotional reactions
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
    print("STARTING GEMINI LLM SERVICE INTEGRATION TESTS")
    print("==================================================")

    for i, test in enumerate(test_cases, start=1):
        print(f"\n--- TEST CASE #{i}: {test['scenario']} ---")
        print(f"User Message: \"{test['prompt']}\"")
        
        # Call our Gemini-backed service function
        response = generate_companion_response(test['prompt'])

        # Print the structured fields returned by the model
        print(f"\n[Companion Dialogue]: {response.response_text}")
        print(f"[Avatar Emotion]    : {response.avatar_state.emotion.value}")
        print(f"[Kinetic Animation] : {response.avatar_state.animation.value}")
        print(f"[Mood Reason]       : {response.avatar_state.mood_reason}")
        print(f"[Suggested Actions] : {response.suggested_actions}")
        print("-" * 50)

        time.sleep(1.5)

if __name__ == "__main__":
    run_tests()