# LLM Robot Planner (AutoBot)

Descrição
----
LLM Robot Planner é um orquestrador para planejamento e execução de ações robóticas controladas por um LLM. Ele monta um prompt estruturado (regras, persona, ferramentas e exemplos), envia ao modelo via cliente `ollama`, interpreta a resposta do LLM como uma sequência de ações em JSON e executa as ações mapeadas para funções Python (ferramentas) — muitas delas wrappers para comandos ROS 2.

Principais recursos
----
- Prompt estruturado com: persona, regras de operação, descrição das ferramentas e exemplos.
- Integração com cliente `ollama` para inferência local/hosted.
- Extração robusta de JSON de respostas do LLM (heurísticos em `agent.py`).
- Registro automático das ferramentas disponíveis (decorador em `tool_registry.py`) e validação de parâmetros via Pydantic.
- Conjunto de ferramentas para navegação, manipulação de robô e chamadas ROS: `tools/`.
- Geração de artefatos de depuração (`debug/response.txt`, `debug/raw_response.json`) durante a execução.

Requisitos
----
- Python 3.8+
- Dependência principal: `ollama` (ver `requirements.txt`).
- (Opcional, mas necessário para funcionalidades ROS) ROS 2 instalado e acessível no `PATH`.

Instalação rápida
----
1. Crie e ative um ambiente virtual Python.
2. Instale dependências:

```bash
python3 -m pip install -r requirements.txt
```

3. Ajuste o host do cliente Ollama se necessário editando a variável `host` em [main.py](main.py).

Uso básico
----
1. Ajuste o `user_prompt` e, se desejar, `current_state` em [main.py](main.py).
2. Execute:

```bash
python3 main.py
```

Durante a execução, o orquestrador envia o prompt ao LLM, tenta parsear a resposta com `parse_ai_response` e, para cada ação recebida, chama `execute_tool` em `tool_registry.py`.

Segurança e recomendações de produção
----
- Não execute comandos físicos no robô sem validação humana adicional.
- O projeto usa `subprocess.run(..., shell=True)` em alguns pontos (`call_ros`, `tools/ros_tools.py`) — substitua por clientes e bindings ROS 2 (rclpy) para produção.
- Sempre valide e sanitize entradas/saídas; o uso de Pydantic reduz erros de formato dos parâmetros.

Estrutura do projeto e descrição de arquivos
----
- **`main.py`**: Orquestrador principal. Monta o `system_prompt` (combina `settings/persona.md`, `settings/rules.md`, ferramentas via `get_tools_schema()` e `settings/examples.md`), envia as mensagens ao cliente `ollama.Client`, recebe a resposta, usa `parse_ai_response` para obter JSON e então executa cada etapa com `execute_tool`. Também contém `call_ros()` (wrapper simples para `ros2` CLI) e gera arquivos de debug em `debug/`.
- **`agent.py`**: Funções de parsing de respostas do LLM. Implementa `parse_ai_response(response_text)` com várias heurísticas (tenta parsear direto, procura blocos de código ```json``` e busca substrings que pareçam JSON). Retorna `None` se não conseguir.
- **`tool_registry.py`**: Sistema de registro de ferramentas. Fornece o decorador `@tool(args_schema=...)` que registra funções como ferramentas, constrói metadados (nome, descrição, JSON Schema via Pydantic) e guarda o modelo Pydantic para validação dos parâmetros. `get_tools_schema()` retorna a lista de schemas para injeção no prompt do LLM. `execute_tool(action_name, parameters)` valida e executa a ferramenta.
- **`settings/`**: Conteúdo usado para montar prompts:
   - [settings/persona.md](settings/persona.md): Persona do agente (ex.: "You are AutoBot AI...").
   - [settings/rules.md](settings/rules.md): Regras que o LLM deve seguir (formato de resposta JSON obrigatório, uso de `call_ros` quando necessário, uso de `end_task`/`end_iteration`, etc.).
   - [settings/examples.md](settings/examples.md): Exemplos de prompts e respostas (úteis para few-shot).
- **`requirements.txt`**: Lista mínima de dependências (ex.: `ollama`).
- **`tools/`**: Conjunto de ferramentas registradas via `tool_registry.tool`. Cada módulo define um schema Pydantic e funções anotadas com `@tool(...)`:
   - [tools/ask_for_help.py](tools/ask_for_help.py): Pede intervenção humana; imprime mensagem e lê input do operador.
   - [tools/end_iteration.py](tools/end_iteration.py): Marca o fim de uma iteração e retorna `{'__control__': 'end_iteration'}`.
   - [tools/end_task.py](tools/end_task.py): Marca o fim da tarefa (`{'__control__': 'end_task'}`).
   - [tools/gripper_control.py](tools/gripper_control.py): Funções `open_gripper()` e `close_gripper()` (simples stubs que imprimem e retornam sucesso).
   - [tools/move_arm.py](tools/move_arm.py): `move_arm(x,y,z,orientation)` — stub que imprime o destino; esperado que seja substituído por chamada a ação ROS real.
   - [tools/navigate_to.py](tools/navigate_to.py): `navigate_to(x,y,z,orientation)` — stub de navegação.
   - [tools/ros_tools.py](tools/ros_tools.py): Ferramentas genéricas para listar tópicos, `echo`, publicar e chamar serviços via `ros2` CLI.

Outros diretórios
----
- **`docs/`**: Documentação Sphinx/ReadTheDocs já incluída (páginas em `docs/` e build em `docs/_build/html`). Use `make html` dentro de `docs/` para gerar a versão estática.
- **`debug/`**: (criado em tempo de execução) Contém `raw_response.json` e `response.txt` com a resposta do LLM para análise.

Como as ferramentas são declaradas e validadas
----
O decorador `@tool(args_schema=...)` em `tool_registry.py` recebe um modelo Pydantic descrevendo os parâmetros. Esse modelo gera automaticamente um JSON Schema incluído no prompt do LLM — ajudando o modelo a formar respostas no formato correto. Em tempo de execução, `execute_tool` valida a payload do LLM contra o modelo Pydantic; falhas de validação são retornadas como mensagens de erro legíveis.

Exemplo de fluxo
----
1. `main.py` monta `system_prompt` com persona, regras, ferramentas e exemplos.
2. Envia prompt via `ollama.Client.chat(...)`.
3. Recebe texto do LLM; `parse_ai_response` tenta extrair JSON.
4. Para cada ação no array JSON: chama `execute_tool(action, parameters)`.
5. Ferramentas podem retornar um campo `__control__` para controlar o loop (`end_iteration`, `end_task`, etc.).

Contribuindo
----
- Para adicionar uma nova ferramenta, crie um novo arquivo em `tools/` ou edite um existente. Declare um `BaseModel` Pydantic com os parâmetros esperados e adicione `@tool(args_schema=YourModel)` acima da função implementada.
- Abra issues para discutir mudanças maiores. Testes e exemplos são bem-vindos.

Exemplos e debugging
----
- Exemplos de entrada/saída estão em [settings/examples.md](settings/examples.md).
- Durante a execução `main.py` escreve `debug/response.txt` e `debug/raw_response.json` para inspecionar a resposta bruta do modelo.

Licença
----
Adicione a licença desejada (por exemplo MIT) no repositório.

Contato
----
Abra uma issue no repositório ou envie um PR com melhorias.

