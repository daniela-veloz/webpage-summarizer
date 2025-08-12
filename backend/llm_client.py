from openai import OpenAI


class LLMClient:
    """
    Client for interacting with OpenAI's language models.
    
    This class provides a simplified interface for generating text using OpenAI's GPT models.
    It handles the OpenAI API client initialization and message formatting for chat completions.
    
    Attributes:
        model (str): The OpenAI model name to use for text generation
        openai (OpenAI): The OpenAI client instance
    """
    def __init__(self, model):
        """
        Initialize the LLM client.
        
        Args:
            model (str): The OpenAI model name (e.g., 'gpt-4o-mini', 'gpt-4')
        """
        self.model = model
        self.openai = OpenAI()

    def generate_text(self, user_prompt, system_prompt="") -> str:
        """
        Generate text using the OpenAI chat completion API.
        
        This method sends a user prompt and optional system prompt to the OpenAI API
        and returns the generated response text.
        
        Args:
            user_prompt (str): The user's input prompt
            system_prompt (str, optional): System prompt to guide the model's behavior.
                                         Defaults to empty string.
        
        Returns:
            str: The generated text response from the model
            
        Raises:
            openai.OpenAIError: If the API request fails
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.openai.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content