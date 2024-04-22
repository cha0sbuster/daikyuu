from typing import List, Dict

import openai
import httpx


# TODO: can we pull this from the API?
BASE_TOKENS = 1
PER_MESSAGE_TOKENS = 4
CONTEXT_LENGTH = 8000


class CompletionClient:
    def __init__(self, model: str, base_url: str) -> None:
        self.model = model
        self.client = openai.OpenAI(base_url=base_url)

        self.max_tokens = CONTEXT_LENGTH
    
    def get_completion(self, messages: List[Dict[str, str]]) -> str:
        res = self.client.chat.completions.create(
            messages=messages, # type: ignore
            model=self.model,
            temperature=1.0,
            top_p=1.0,
            stop=['<|end_of_turn|>', '<|eot_id|>']
        )
        if len(res.choices) == 0: # TODO: better handling here
            return ''
        return res.choices[0].message.content or ''

    def get_token_length(self, text: str) -> int:
        tokens = self.client.post('/tokenize', cast_to=httpx.Response, body={"content": text})
        return len(tokens.json()['tokens'])