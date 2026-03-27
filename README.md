# AutoBot — Orquestrador LLM + ROS

Resumo
----
AutoBot é um pequeno script de orquestração que constrói prompts para um LLM (via cliente Ollama), interpreta respostas do modelo como sequências de ações em JSON e fornece um helper mínimo para executar comandos ROS‑2. O código já contém docstrings compatíveis com Sphinx/autodoc para publicação no Read the Docs.

Funcionalidades
----
- Construção de prompt sistemático com regras, ferramentas e exemplos.
- Envio de prompt ao modelo Ollama e recepção de resposta.
- parse_ai_response(response_text): extrai JSON de respostas textuais do LLM (vários heurísticos).
- call_ros(command): invoca o CLI `ros2` e retorna stdout (wrapper simples para prototipagem).
- Representação das ferramentas (tools) em JSON para inclusão no prompt e documentação.
- Geração de arquivo `response.json` com a resposta completa do LLM.

Requisitos
----
- Python 3.8+
- Dependências: `ollama` client (pip) e outras libs padrão (json, subprocess, re, logging).
- ROS 2 instalado e acessível no PATH para usar `call_ros`.

Uso
----
1. Ajuste o host do Ollama se necessário (variável `host` em `main.py`).
2. Modifique `user_prompt` / `current_state` conforme o cenário.
3. Execute:
   ```
   python3 main.py
   ```
4. Saída:
   - Logs e JSON parseado impressos no terminal.
   - Arquivo `response.json` criado com a resposta completa do LLM.

Considerações de segurança e produção
----
- `call_ros` usa `shell=True` e invoca o CLI; para produção, prefira clientes ROS nativos e tratamento seguro de argumentos.
- Valide sempre o JSON retornado pelo LLM antes de executar ações físicas no robô.
- Regras no prompt forçam respostas em JSON; porém, sempre trate falhas de parse.

Estrutura principal
----
- main.py: orquestrador, prompt, parsing, helper ROS, exemplos e execução do cliente Ollama.

Contribuição
----
- Bugs e PRs são bem‑vindos. Para alterações maiores, abrir issue descrevendo o caso de uso.

Licença
----
- Inclua aqui a licença do projeto (por exemplo MIT) conforme desejar.