import requests
from typing import Optional

from .config import GAIA_BASE, GAIA_MODEL, REQUEST_TIMEOUT_SEC

CHAT_URLS = [
    f"{GAIA_BASE}/api/v1/chat/completions",
    f"{GAIA_BASE}/v1/chat/completions",
]

MODELS_URLS = [
    f"{GAIA_BASE}/api/v1/models",
    f"{GAIA_BASE}/v1/models",
]

_cached_model: Optional[str] = None
_cached_urls: Optional[dict] = None  # {"chat_url": str, "models_url": str}


def _pick_first_alive(urls: list[str]) -> Optional[str]:
    for u in urls:
        try:
            r = requests.get(u, timeout=REQUEST_TIMEOUT_SEC)
            if r.status_code < 500:
                return u
        except Exception:
            pass
    return None


def _detect_endpoints() -> tuple[str, str]:
    """
    Descobrir qual par de URLs está respondendo na instância GAIA.
    """
    global _cached_urls
    if _cached_urls:
        return _cached_urls["chat_url"], _cached_urls["models_url"]

    chat = _pick_first_alive(CHAT_URLS) or CHAT_URLS[0]
    models = _pick_first_alive(MODELS_URLS) or MODELS_URLS[0]
    _cached_urls = {"chat_url": chat, "models_url": models}
    return chat, models


def _list_models() -> list[str]:
    """
    Retornar a lista de modelos expostos pelo GAIA.
    """
    _, models_url = _detect_endpoints()
    try:
        r = requests.get(models_url, timeout=REQUEST_TIMEOUT_SEC)
        r.raise_for_status()
        data = r.json()
        # formatos comuns:
        # {"data":[{"id":"nome-do-modelo", ...}, ...]}
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            ids = []
            for item in data["data"]:
                mid = item.get("id") or item.get("name")
                if isinstance(mid, str):
                    ids.append(mid)
            return ids
        # fallback simples
        if isinstance(data, list):
            return [m.get("id") or m.get("name") for m in data if isinstance(m, dict)]
    except Exception:
        pass
    return []


def _resolve_model(preferred: Optional[str]) -> Optional[str]:
    """
    Tentar usar o modelo preferido; se não existir, usa o primeiro disponível.
    Cache o resultado para não consultar sempre.
    """
    global _cached_model
    if _cached_model:
        return _cached_model

    models = _list_models()
    if not models:
        # não conseguimos listar; ainda tentaremos com o preferred (se houver)
        _cached_model = preferred
        return _cached_model

    if preferred and preferred in models:
        _cached_model = preferred
    else:
        _cached_model = models[0]  # primeiro disponível
    return _cached_model


def chat(messages, temperature=0.2, max_tokens=512) -> str:
    """
    messages: [{"role":"system"|"user"|"assistant","content":"..."}]
    Resolver o modelo dinamicamente e tenta as rotas conhecidas.
    Em caso de erro 4xx/5xx, devolver o body para debug.
    """
    model = _resolve_model(GAIA_MODEL)
    chat_url, _ = _detect_endpoints()

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        resp = requests.post(chat_url, json=payload, timeout=REQUEST_TIMEOUT_SEC)
        if not resp.ok:
            # devolver o corpo para debug (422, 404, etc.)
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            return f"(GAIA retornou {resp.status_code} em {chat_url} com payload model='{model}': {body})"

        data = resp.json()
        # OpenAI-compatible shape
        content = data["choices"][0]["message"]["content"]
        return (content or "").strip()
    except Exception as e:
        return f"(Falha ao consultar GAIA em {chat_url} com model='{model}': {e})"
