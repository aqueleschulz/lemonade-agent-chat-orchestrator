# Orquestrador-de-Agentes
Em meu último semestre cursando matérias pelo curso de tecnólogo em Análise e Desenvolvimento de Sistemas, escrevi meu Projeto Final, equivalente a um trabalho de conclusão de curso,  sobre este projeto de código aberto que utiliza de ferramentas já disponíveis para pequenas e médias empresas utilizarem da inteligencia artificial.

# AI Implementation for SMEs / Implementação de IA para PMEs

This repository contains the prototype developed for the final project: **"Artificial Intelligence Implementation into Small Business: A Catalyst For Organizations Without Technological Proficiency"**.

Este repositório contém o protótipo desenvolvido para o trabalho de conclusão de curso: **"Implementação de Inteligência Artificial em Pequenas Empresas: Um Catalisador Para Empresas Sem Expertise Tecnológica"**, escrito por João Pedro Schulz Rocha.

---

## 🇺🇸 English Instructions

### Prerequisites
To run this project, you need to set up the following environment:

1.  **Python 3.10+**: Ensure Python is installed and added to your system PATH.
2.  **GAIA CLI**: You must install the GAIA CLI directly from the **official AMD GitHub repository**. This is the core engine for running the LLM locally on your hardware.
3.  **Lemonade Server**: Install and configure the Lemonade Server to orchestrate the AI services.
4.  **Cloud Drive App**: You need a cloud storage application (e.g., Google Drive, OneDrive, Dropbox) installed on your machine.
    * **Requirement**: The app must create a real folder accessible via the Operating System's file explorer.

### AI Model Setup
You must download an Artificial Intelligence model of your choice (e.g., GGUF format for local execution).

* **Step 1**: Download the model.
* **Step 2**: Configure the model path inside the **Lemonade Server**.
* **Step 3**: Update the model name/path in this project's code, specifically in the configuration file (e.g., `backend/config.py`), so the prototype knows which model to call.

### Installation
1.  Clone this repository.
2.  Install the Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ensure GAIA and Lemonade Server are running.
4.  Run the initialization script:
    ```bash
    python initialize.py
    ```

---

## 🇧🇷 Instruções em Português

### Pré-requisitos
Para executar este projeto, é necessário configurar o seguinte ambiente:

1.  **Python 3.10+**: Certifique-se de que o Python esteja instalado e adicionado ao PATH do seu sistema.
2.  **GAIA CLI**: É necessário instalar o GAIA CLI através do **repositório oficial da AMD no GitHub**. Este é o motor principal para rodar o LLM localmente no seu hardware.
3.  **Lemonade Server**: Instale e configure o Lemonade Server para orquestrar os serviços de IA.
4.  **Aplicativo de Drive**: Você precisa de um aplicativo de armazenamento em nuvem (ex: Google Drive, OneDrive, Dropbox) instalado em sua máquina.
    * **Requisito**: O aplicativo deve criar uma pasta real acessível através do explorador de arquivos do Sistema Operacional.

### Configuração do Modelo de IA
É necessário baixar um modelo de Inteligência Artificial de sua escolha (ex: formato GGUF para execução local).

* **Passo 1**: Baixe o modelo desejado.
* **Passo 2**: Inclua e configure o modelo dentro do **Lemonade Server**.
* **Passo 3**: Atualize o nome/caminho do modelo no código deste projeto, especificamente no arquivo de configuração (ex: `backend/config.py`), para que o protótipo saiba qual modelo chamar.

### Instalação
1.  Clone este repositório.
2.  Instale as dependências do Python:
    ```bash
    pip install -r requirements.txt
    ```
3.  Certifique-se de que o GAIA e o Lemonade Server estejam em execução.
4.  Execute o script de inicialização:
    ```bash
    python initialize.py
    ```

---

## License / Licença

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** - see the LICENSE file for details.

Este projeto está licenciado sob a **GNU General Public License v3.0 (GPLv3)** - veja o arquivo LICENSE para mais detalhes.
