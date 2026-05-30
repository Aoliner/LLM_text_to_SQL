from openai import OpenAI

def create_client(api_key: str):
    return OpenAI(api_key=api_key)

def parse_llm_response(response_text: str) -> tuple[str, str]:
    if not isinstance(response_text, str):
        return "-- CANNOT_ANSWER: model returned non-text output", ""

    lines = [line.rstrip() for line in response_text.splitlines()]

    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return "-- CANNOT_ANSWER: empty model response", ""

    first_line = lines[0].strip()
    if not first_line.startswith("--"):
        return "-- CANNOT_ANSWER: missing required control comment", ""

    sql = "\n".join(lines[1:]).strip()
    return first_line, sql

def generate_sql(client, system_message: str, user_request: str):
    llm_response = client.chat.completions.create(
        model="gpt-5.4-mini",
        temperature=0.0,
        messages=[
            {"role": "developer", "content": system_message},
            {"role": "user", "content": user_request},
        ],
    )

    content = llm_response.choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Model returned empty or non-text content.")

    return content.strip()