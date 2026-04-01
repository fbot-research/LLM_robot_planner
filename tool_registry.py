from pydantic import BaseModel, ValidationError
from typing import Callable, Any

# Dicionário global para armazenar as ferramentas
_TOOLS = {}

def tool(args_schema: type[BaseModel]):
    """
    Decorador que registra uma ferramenta exigindo um schema do Pydantic.
    """
    def decorator(func: Callable):
        # O Pydantic gera o JSON Schema dos parâmetros automaticamente!
        tool_schema = {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip().split('\n')[0],
            "parameters": args_schema.model_json_schema() 
        }
        
        _TOOLS[func.__name__] = {
            "func": func,
            "schema": tool_schema,
            "args_model": args_schema # Guardamos o modelo para validar a resposta do LLM depois
        }
        return func
    return decorator

def get_tools_schema() -> list:
    """Retorna a lista de schemas para injetar no prompt do LLM."""
    return [t["schema"] for t in _TOOLS.values()]

def execute_tool(action_name: str, parameters: dict) -> Any:
    """Valida os parâmetros do LLM com Pydantic e executa a função."""
    if action_name not in _TOOLS:
        return f"Erro: Ação '{action_name}' desconhecida."
    
    tool_info = _TOOLS[action_name]
    
    try:
        # MAGIA AQUI: Tenta criar o objeto Pydantic com os dados do LLM.
        # Se o LLM alucinou um parâmetro ou mandou o tipo errado, isso vai falhar com um erro claro.
        validated_args = tool_info["args_model"](**parameters)
        
        # Se passou na validação, desempacota e roda a função real
        return tool_info["func"](**validated_args.model_dump())
        
    except ValidationError as e:
        # Retorna o erro exato do Pydantic para você poder mandar de volta pro LLM se quiser
        return f"Erro de validação nos parâmetros enviados: {e.errors()}"
    except Exception as e:
        return f"Erro interno ao executar a ferramenta: {e}"