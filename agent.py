import logging, json

def parse_ai_response(response_text: str) -> list[dict]:
    """Parse an LLM response string and return a JSON-like Python object.

    The function attempts multiple strategies to extract JSON from the raw
    model output:

    1. Try to parse the whole string as JSON.
    2. Search for a fenced code block containing JSON (```json ... ```).
    3. Search for any substring that looks like a JSON object.

    If parsing fails, the function logs a warning and returns ``None`` so the
    caller can decide how to recover (e.g., ask the LLM to reformat its
    response).

    :param response_text: Raw text returned by the language model.
    :return: A Python object (commonly a list of dicts) parsed from JSON, or
             ``None`` if no valid JSON could be extracted.
    """
    logger = logging.getLogger('__main__')

    try:
        # Tenta encontrar JSON na resposta
        json_match = None

        # Primeiro tenta parsear diretamente
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Tenta encontrar bloco JSON
        import re

        json_patterns = [r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```", r"(\{.*\})"]

        for pattern in json_patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        logger.warning("Could not parse AI response as JSON — will ask LLM to reformat")
        return None

    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        return None


