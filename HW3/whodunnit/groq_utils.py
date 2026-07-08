import os

from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY")

MODEL_NAME = "llama-3.3-70b-versatile"
SMALL_MODEL_NAME = "llama-3.1-8b-instant"
TEST_SYSTEM_PROMPT = "You are a helpful asssitant. Please Answer only in True or False"


def get_groq_client():
    if not API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")
    return Groq(api_key=API_KEY)

def query_llama(prompt, sys_prompt, use_small_model=False, temperature=0.8, max_tokens=512, client=None):
    model_name = SMALL_MODEL_NAME if use_small_model else MODEL_NAME

    try:
        if client is None:
            client = get_groq_client()
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"

def test_connection():
    query = "Is the sky blue?"
    response = query_llama(query, TEST_SYSTEM_PROMPT, use_small_model=True, temperature=0.0)
    print(query)
    print(response)

if __name__ == "__main__":
    test_connection()