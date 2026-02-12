# Lumina Orchestrator

**Local AI. Enterprise Architecture. Limitless Context.**

O Lumina Orchestrator é uma solução de Chatbot Corporativo On-Premise projetada para orquestrar LLMs locais (via Lemonade Server) com capacidades reais de manipulação de arquivos e dados.

Diferente de wrappers simples de API, o Lumina implementa uma arquitetura híbrida (C# .NET + Python) para oferecer a robustez e tipagem de um backend corporativo aliada à flexibilidade de manipulação de dados do ecossistema Python.

## Arquitetura do Sistema

Este sistema é dividido em três pilares fundamentais:

### 1. Lumina API (.NET 9/10)

O núcleo do sistema desenvolvido em ASP.NET Core Web API. É responsável por:

* Gerenciar o estado da conversa e requisições do usuário.
* Implementar a lógica de **Tool Calling** manualmente, decidindo quando a IA precisa agir.
* Orquestrar a comunicação entre o usuário, o motor de dados e o servidor de inferência.

### 2. Lumina Engine (Python FastAPI)

Um microserviço especializado em ETL e processamento de dados.

* Utiliza **Microsoft MarkItDown** para converter arquivos complexos (Excel, PDF, Word) em contexto legível (Markdown).
* Expõe ferramentas (Tools) consumidas pela camada .NET via HTTP.

### 3. Lemonade Server (Inference)

O servidor de inferência local compatível com OpenAI API que executa modelos como Gemma, Llama e Mistral utilizando aceleração de hardware (NPU/GPU).

---

## Funcionalidades Principais

* **Privacidade Total:** Execução 100% local. Nenhum dado transita fora da rede interna.
* **Leitura de Arquivos (RAG):** Capacidade de interpretar e cruzar dados de planilhas e documentos anexados.
* **Orquestração Inteligente:** Detecção automática de necessidade de ferramentas para evitar alucinações.
* **Containerização:** Deploy padronizado via Docker Compose.

---

## Como Rodar (Quickstart)

### Pré-requisitos

* Docker Desktop instalado.
* Lemonade Server em execução (acessível via rede ou host local).

### Passo 1: Configurar o Lemonade Server

Certifique-se de que o servidor de inferência está acessível. Se rodando no host Windows, o endereço para o Docker será: `http://host.docker.internal:8000`. A porta padrão de Lemonade Server também é 8000 e pode ser alterada.

### Passo 2: Subir a Orquestração

Na raiz do projeto, execute o comando:

```bash
docker-compose up --build
```

Este comando irá construir as imagens da **Lumina API** e do **Lumina Engine**, além de configurar a rede interna.

### Passo 3: Testar

Acesse a interface do Swagger para interagir com o sistema:
`http://localhost:5006/swagger`

---

## Exemplo de Uso

No endpoint `POST /api/chat/ask`, envie o seguinte payload:

```json
{
  "prompt": "Analise o arquivo 'reunioes.xlsx' e me diga quais reuniões eu tenho na sexta-feira."
}
```

### Fluxo de Execução

1. **Lumina API** recebe o prompt e consulta o **Lemonade Server** com as definições de ferramentas.
2. O modelo identifica a necessidade da função `read_file` para o arquivo citado.
3. A API .NET intercepta a requisição e aciona o **Lumina Engine (Python)**.
4. O Engine processa o arquivo Excel, converte para Markdown e retorna o texto bruto.
5. A API envia o conteúdo processado de volta ao modelo para síntese da resposta final.

---

## Estrutura do Projeto

```text
├── docker-compose.yaml       # Orquestração dos containers
├── src/
│   ├── Lumina.Server/        # O Cérebro (.NET)
│   │   └── Lumina.Api/       # Controllers, Services, DTOs
│   │
│   └── Lumina.Engine/        # O Músculo (Python)
│       ├── data/             # Volume local para arquivos
│       ├── main.py           # API FastAPI
│       └── requirements.txt  # Dependências (MarkItDown, etc)
```

---

## Licença

Este projeto é distribuído sob a licença **MIT**. Desenvolvido como evolução do projeto de TCC "IMPLEMENTAÇÃO DE INTELIGÊNCIA ARTIFICIAL EM PEQUENAS EMPRESAS:
Um Catalisador Para Empresas Sem Expertise Tecnológica" de João Pedro Schulz Rocha, produzido em 2025.
