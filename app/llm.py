import re
from openai import OpenAI

def create_client(api_key: str):
    return OpenAI(api_key=api_key)

def parse_llm_response(response_text: str) -> tuple[str, str]:
    response_text = response_text.strip()
    comment = ""
    sql = response_text

    if response_text.startswith("--"):
        lines = response_text.split("\n", 1)
        comment = lines[0].strip()
        if len(lines) > 1:
            sql = lines[1].strip()
        else:
            sql = ""

    sql = re.sub(r"^--.*$", "", sql, flags=re.MULTILINE).strip()
    return comment, sql

def generate_sql(client, system_message: str, user_request: str):
    llm_response = client.chat.completions.create(
        model="gpt-5.4-mini",
        temperature=0.0,
        messages=[
            {"role": "developer", "content": system_message},
            {"role": "user", "content": user_request}
        ]
    )
    return llm_response.choices[0].message.content.strip()