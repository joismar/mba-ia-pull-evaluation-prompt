"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        # Extrair dados básicos
        system_prompt = prompt_data.get('system_prompt', '')
        user_prompt = prompt_data.get('user_prompt', '{bug_report}')
        
        # Criar ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
        
        # URL do Hub
        print(f"Fazendo push do prompt '{prompt_name}'...")
        url = hub.push(
            prompt_name,
            prompt,
            new_repo_is_public=True,
            api_key=os.getenv("LANGSMITH_API_KEY"),
            api_url=os.getenv("LANGSMITH_ENDPOINT")
        )
        print(f"✅ Push realizado com sucesso: {url}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    # Validar campos básicos
    required_fields = ['system_prompt', 'user_prompt', 'description', 'version']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")
            
    # Validar se o system_prompt está vazio ou contém TODO
    if 'system_prompt' in prompt_data:
        sp = prompt_data['system_prompt'].strip()
        if not sp:
            errors.append("system_prompt está vazio")
        if 'TODO' in sp:
            errors.append("system_prompt ainda contém TODOs")
            
    # Verificar template variables no user_prompt ou system_prompt
    if 'user_prompt' in prompt_data and '{bug_report}' not in prompt_data['user_prompt'] and '{bug_report}' not in prompt_data.get('system_prompt', ''):
        errors.append("Nenhum de seus prompts contém a variável {bug_report}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Push de Prompts Otimizados")

    # Carregar prompt otimizado (v2)
    yaml_path = "prompts/bug_to_user_story_v2.yml"
    
    if not os.path.exists(yaml_path):
        print(f"❌ Arquivo não encontrado: {yaml_path}")
        print("Certifique-se de preencher a v2 do prompt antes de executar o push.")
        return 1
        
    data = load_yaml(yaml_path)
    if not data:
        return 1
        
    prompt_key = "bug_to_user_story_v2"
    if prompt_key not in data:
        print(f"❌ Chave '{prompt_key}' não encontrada no arquivo YAML.")
        return 1
        
    prompt_data = data[prompt_key]
    
    # Validar prompt
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Erros de validação encontrados:")
        for err in errors:
            print(f"   - {err}")
        return 1
        
    print("✅ Prompt validado com sucesso!")
    
    # Fazer push (obtenha do .env se possível ou use o username)
    hub_owner = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_name = f"{hub_owner}/bug_to_user_story_v2"
    
    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
