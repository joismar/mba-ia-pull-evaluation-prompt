"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub

load_dotenv()

def pull_prompts_from_langsmith():
    """Faz pull dos prompts do LangSmith Prompt Hub."""
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print(f"Fazendo pull do prompt: {prompt_name}")
    
    # Faz o pull do prompt do hub
    prompt = hub.pull(prompt_name, api_key=os.getenv("LANGSMITH_API_KEY"), api_url=os.getenv("LANGSMITH_ENDPOINT"))
    
    # Define o caminho de destino
    output_dir = Path("prompts")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "bug_to_user_story_v1.yml"
    
    # Salva o prompt localmente
    print(f"Salvando prompt em: {output_path}")
    prompt.save(str(output_path))
    print("Prompt salvo com sucesso!")

def main():
    """Função principal"""
    try:
        pull_prompts_from_langsmith()
        return 0
    except Exception as e:
        print(f"Erro ao executar o script: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
