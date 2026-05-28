"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

load_dotenv()

# Carregar o prompt da versão 2 para os testes (ou v1 como fallback)
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
if not PROMPT_FILE.exists():
    PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"

PROMPT_DATA = load_prompts(str(PROMPT_FILE))
PROMPT_KEY = next(iter(PROMPT_DATA.keys()))
PROMPT_SPEC = PROMPT_DATA[PROMPT_KEY]

def evaluate_with_llm(text: str, criterion: str) -> bool:
    """Usa o LLM para avaliar de forma semântica se um texto atende a um critério."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    except Exception as e:
        pytest.skip(f"A OpenAI API Key não está configurada ou falhou: {e}")

    prompt = PromptTemplate.from_template(
        "Você é um avaliador de prompts. Analise o texto do prompt abaixo criticamente.\n\n"
        "Critério a ser avaliado: {criterion}\n\n"
        "Texto do Prompt:\n{text}\n\n"
        "O prompt atende ao critério de forma explícita e clara?\n"
        "Responda EXATAMENTE COM 'SIM' ou 'NAO'."
    )
    chain = prompt | llm
    
    response = chain.invoke({"criterion": criterion, "text": text})
    return "SIM" in response.content.upper()

class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in PROMPT_SPEC, "O campo 'system_prompt' está ausente."
        assert isinstance(PROMPT_SPEC["system_prompt"], str), "'system_prompt' deve ser string."
        assert len(PROMPT_SPEC["system_prompt"].strip()) > 0, "O 'system_prompt' está vazio."

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = PROMPT_SPEC.get("system_prompt", "")
        criterion = "O texto define uma persona, papel ou profissão clara para a inteligência artificial assumir? (exemplo: 'Você é um product manager experiente', 'Você atua como QA', etc)."
        assert evaluate_with_llm(system_prompt, criterion), "A persona/role definition não foi encontrada no system prompt."

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = PROMPT_SPEC.get("system_prompt", "").lower()
        has_format_keyword = "markdown" in system_prompt or "user story" in system_prompt or "critérios de aceite" in system_prompt
        assert has_format_keyword, "Não foi encontrada exigência clara do formato (ex: Markdown, User Story)."

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = PROMPT_SPEC.get("system_prompt", "")
        criterion = "O texto apresenta um ou mais exemplos concretos ilustrando a entrada (o relato do bug) e a estrutura exata esperada da saída (a user story formatada)? Isso é uma aplicação da técnica Few-Shot Learning."
        assert evaluate_with_llm(system_prompt, criterion), "Exemplos Few-Shot não foram identificados no prompt."

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = PROMPT_SPEC.get("system_prompt", "")
        assert "[TODO]" not in system_prompt, "Foram encontrados placeholders [TODO] no texto do prompt."

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        tags = PROMPT_SPEC.get("tags", [])
        assert len(tags) >= 2, "É necessário listar pelo menos 2 técnicas (nas 'tags' ou campo similar) nos metadados do yaml."

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])