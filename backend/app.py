import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from .llm_gaia import chat
from .mcp_client import gather_snippets

app = Flask(__name__)
CORS(app)

MCP_CMD = None

def clean_snippet(text):
    cleaned_lines = []
    for line in text.splitlines():
        # Se a linha tem muitos caracteres estranhos ou nulos, ignoramos
        if '\x00' in line or line.startswith("PK"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

@app.route("/api/ask", methods=["POST"])
def ask():
    global MCP_CMD
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"answer": "Pergunta vazia."})

    # Coletar e limpar contexto
    snippets, citations = [], []
    try:
        if MCP_CMD:
            raw_snippets, citations = gather_snippets(MCP_CMD, question)
            # Limpar cada snippet de lixo binário
            snippets = [clean_snippet(s) for s in raw_snippets]
    except Exception:
        snippets, citations = [], []

    # Construir Prompt
    context_text = "\n\n".join(snippets[:3])
    
    # Projetar prompt para ser curto e imune a falhas de formato
    final_prompt = f"""Você é um assistente direto e objetivo.
    LEIA O CONTEXTO ABAIXO:
    ---------------------
    {context_text if context_text else "Nenhum contexto disponível."}
    ---------------------

    AGORA, RESPONDA À PERGUNTA DO USUÁRIO:
    "{question}"

    REGRAS OBRIGATÓRIAS:
    1. Responda em Português.
    2. Use no MÁXIMO 2 frases curtas.
    3. Se o contexto tiver caracteres estranhos, IGNORE-OS.
    4. NÃO explique o que você vai fazer, apenas dê a resposta.

    RESPOSTA:"""

    # Chamar LLM (Sem role 'system', tudo em 'user' para evitar confusão do modelo)
    raw_answer = chat([
        {"role": "user", "content": final_prompt}
    ])

    # Pós-processamento de Segurança
    # Remover qualquer tag de arquivo que a IA tenha alucinado (ex: [doc.pdf])
    clean_answer = re.sub(r"\[.*?\]", "", raw_answer)
    # Remover quebras de linha excessivas e espaços
    clean_answer = " ".join(clean_answer.split())
    
    # Fallback final se a IA falhar totalmente
    if not clean_answer or len(clean_answer) < 2:
        clean_answer = "Não encontrei informações suficientes nos arquivos para responder isso brevemente."

    return jsonify({"answer": clean_answer, "citations": citations})

def serve(host: str, port: int, mcp_cmd: list[str]):
    global MCP_CMD
    MCP_CMD = mcp_cmd
    app.run(host=host, port=port, threaded=True)