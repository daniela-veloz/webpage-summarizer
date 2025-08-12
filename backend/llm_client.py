from openai import OpenAI


class LLMClient:
    def __init__(self, model):
        self.model = model
        self.openai = OpenAI()

    def generate_text(self, user_prompt, system_prompt="") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.openai.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content