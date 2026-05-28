# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto criado para o segundo Desafio Técnico do NBA em Engenharia de Software com IA, com objetivo de entregar um software capaz de:

1. Fazer pull de prompts do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. Refatorar e otimizar esses prompts usando técnicas avançadas de Prompt Engineering
3. Fazer push dos prompts otimizados de volta ao LangSmith
4. Avaliar a qualidade através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. Atingir pontuação mínima de 0.9 (90%) em todas as métricas de avaliação

## Técnicas Aplicadas (Fase 2)

Durante o processo de otimização do prompt para a versão `v2`, foram utilizadas as seguintes técnicas de engenharia de prompt:

1. **Few-shot Learning (Obrigatório)**:
   - **O que foi feito**: Foram incluídos dois exemplos claros de entrada (um relato comum de falha na UI e um relato vago de insatisfação) com as respectivas saídas desejadas em formato de User Story e Critérios de Aceite.
   - **Justificativa**: Dar ao LLM o padrão exato da formatação esperada reduz alucinações de formatação e calibra o nível de detalhes exigido para a geração da User Story.
   - **Exemplo prático**: Foi incluído um EXEMPLO DE REFERÊNCIA que não possuía na versão 1:

   > EXEMPLO DE REFERÊNCIA:
   > Usuário: "Relatório demora 2 min com 1000 linhas. SQL sem index na data. Browser dá timeout 120s."
   > Assistente:
   > **Título:** Otimização de performance do Relatório de Vendas (Indexação e Timeout)
   > **User Story:** Como um Analista Financeiro, eu preciso gerar relatórios de grandes volumes em tempo ágil para que eu possa tomar decisões sem travamentos no sistema.
   > **Critérios de Aceite:**
   > - Dado que solicito um relatório com mais de 1000 registros
   > - Quando inicio o processamento
   > - Então o sistema deve concluir a geração em menos de 30 segundos
   > - E deve ser implementado um índice na coluna `data_venda` para evitar Full Table Scan.
   > - E não deve ocorrer erro de timeout (120s) no navegador.


2. **Role Prompting**:
   - **O que foi feito**: O modelo atua sob a persona de um "experiente Product Manager (PM) e Analista de Qualidade em uma equipe de desenvolvimento ágil de software".
   - **Justificativa**: Fornece um contexto profissional. O LLM, assumindo essa persona técnica e de negócio, prioriza o valor para o usuário (foco do PM) e a exatidão técnica/testabilidade (foco do QA) ao elaborar os critérios de aceite.
   - **Exemplo prático**: Foi definido uma role para o modelo:

   > Você é um Product Manager (PM) Sênior com foco em Engenharia de Software. Sua especialidade é traduzir relatos de bugs — muitas vezes imprecisos — em especificações técnicas rigorosas e User Stories acionáveis.


3. **Chain of Thought (CoT)**:
   - **O que foi feito**: O prompt instrui o modelo a "Pense passo a passo (Chain of Thought)", listando as etapas mentais: identificar o problema, identificar o usuário, comparar comportamentos (esperado vs. atual) e listar critérios de aceite.
   - **Justificativa**: Essa decomposição do raciocínio ajuda o modelo a não pular informações chave presentes no bug, resultando em User Stories mais ricas e bem construídas em vez de traduções simplórias do relato original.
   - **Exemplo prático**: Foram dado um passo a passo bem definido:

   > INSTRUÇÕES LÓGICAS (Chain of Thought):
   >  1. ANALISE O RELATO: Extraia o erro (comportamento atual), o desejo (comportamento esperado) e as variáveis técnicas (IDs, logs, timeouts, dispositivos).
   >  2. PERSONA: Defina quem sofre o impacto (Usuário Final, Admin, Desenvolvedor de API).
   >  3. ESTRUTURAÇÃO:
   >     - Título: Deve conter a falha e o componente afetado.
   >     - User Story: Siga o padrão "Como [persona], eu quero [ação] para que [valor]".
   >     - Critérios de Aceite (Gherkin): Sempre que possível, utilize o formato "Dado que... Quando... Então... E...".
   >     - Requisitos de Performance/Segurança: Se houver dados numéricos (ex: timeout de 120s), defina metas de correção explícitas (ex: < 30s).

*Além dessas técnicas, também foram incluídos tratamentos explícitos de "Edge Cases" no prompt. Caso o usuário envie apenas um xingamento ou relato muito genérico ("tá tudo quebrado"), o LLM é instruído a não inventar informações falsas, mas sim gerar uma User Story focada em investigação e coleta de logs.*

## Resultados Finais

Foram realizadas 6 iterações de otimização. A evolução do prompt pode ser vista em: https://smith.langchain.com/hub/joismar/bug_to_user_story_v2. Após as iterações, a versão `v2` do prompt atingiu as seguintes pontuações:

### Screenshots das avaliações:
![Avaliacao 1](image-1.png)

### Tracing do Langsmith:
![Imagem 1](langsmith_prints\image1.png)
![Imagem 2](langsmith_prints\image2.png)
![Imagem 3](langsmith_prints\image3.png)
![Imagem 4](langsmith_prints\image4.png)

## Como Executar

### Requisitos
- Python 3
- Conta no LangSmith
- API Key da OpenAI ou Google Gemini

### Configurar VirtualEnv
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configurar .env
Crie um arquivo `.env` na raiz do projeto, copie o contendo do `.env.example` e preencha com suas chaves de API.

### Ordem de execução

1. Executar pull dos prompts: `python src/pull_prompts.py`;
2. Refatorar prompt `bug_to_user_story_v2.yml`;
3. Fazer push dos prompts otimizados: `python src/push_prompts.py`;
4. Executar avaliação: `python src/evaluate.py`

## Como testar
```bash
./venv/bin/python -m pytest tests/test_prompts.py -v
```