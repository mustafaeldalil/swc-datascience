from django.conf import settings
import openai


def generate_gpt_answer(prompt, context=None):
    messages = []
    if context is not None:
        messages.append({"role": "system", "content": context})
    messages.append({"role": "user", "content": prompt})

    openai.api_key = settings.OPEN_AI_TOKEN
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=settings.GPT_TEMPERATURE,
        max_tokens=500,
        messages=messages,
        stop=None,
    )
    message = response["choices"][0]["message"]["content"]
    return message
