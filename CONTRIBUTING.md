# Como contribuir para o LabAI-Comply

Obrigado pelo interesse em contribuir com o LabAI-Comply. Este documento guia você através do processo de desenvolvimento e contribuição.

## Bem-vindo(a)

O LabAI-Comply é uma coleção Ansible open source que provisiona infraestrutura de IA para pesquisadores brasileiros, com conformidade automática para a Portaria CNPq 2.664/2026. Seja você pesquisador, desenvolvedor ou entusiasta de infraestrutura como código, sua contribuição é bem-vinda.

Este projeto é 100% em Português porque o público-alvo são pesquisadores e desenvolvedores brasileiros. Mantenha documentação e commits em PT-BR.

## Requisitos do ambiente de desenvolvimento

Para contribuir com o LabAI-Comply, você precisa do seguinte ambiente:

- **Ansible**: versão 2.15 ou superior
- **community.docker**: >= 3.0.0 (dependência da coleção)
- **Python**: 3.12 ou superior (para Molecule e linters)
- **Docker**: versão 24.0 ou superior (para testes locais)
- **Docker Compose**: versão 2.20 ou superior
- **Git**: versão 2.40 ou superior
- **Molecule**: 6.x ou superior (para testes de roles)
- **ansible-lint**: versão 6.x ou superior
- **yamllint**: para validação de YAML
- **pytest**: para testes Python
- **ruff** ou **flake8**: para lint Python

### Instalação rápida (Ubuntu/Debian)

```bash
# Atualize o sistema
sudo apt update && sudo apt upgrade -y

# Instale Python e pip
sudo apt install -y python3.12 python3.12-venv python3-pip

# Instale Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instale Ansible e ferramentas
pip install --user ansible-core ansible-lint yamllint molecule molecule-plugins[docker] pytest ruff
ansible-galaxy collection install community.docker

# Adicione ao PATH (adicione ao ~/.bashrc se necessário)
export PATH="$HOME/.local/bin:$PATH"
```

## Como configurar o ambiente local

### 1. Clone o repositório

```bash
git clone https://github.com/haquiticos/LabAI-Comply.git
cd comply
```

### 2. Configure o ambiente virtual (recomendado)

```bash
python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt  # se existir
# ou manualmente
pip install ansible-core ansible-lint yamllint molecule molecule-plugins[docker] pytest ruff
```

### 3. Configure o vault para testes

```bash
cp vault.yml.example vault.yml
ansible-vault encrypt vault.yml
# Edite conforme necessário para testes locais
```

### 4. Valide a sintaxe da coleção

```bash
ansible-galaxy collection build --force
ansible-galaxy collection install labai-comply-0.2.0.tar.gz --force
```

### 5. Teste o playbook principal

```bash
# Verifique a sintaxe
ansible-playbook playbooks/setup_lab.yml --syntax-check

# Verifique com lint
ansible-lint playbooks/setup_lab.yml
```

## Estrutura do projeto

O LabAI-Comply segue a estrutura padrão de coleção Ansible:

```
labai_comply/
├── galaxy.yml                    # Metadados da coleção
├── defaults/main.yml             # Variáveis padrão (configurações globais)
├── vault.yml.example             # Template de secrets (NÃO comite no vault real)
├── playbooks/
│   └── setup_lab.yml             # Playbook principal (orchestration)
├── roles/                        # Roles modulares
│   ├── hardware_profiling/       # Detecção de hardware e seleção de modelo Ollama
│   ├── system_setup/             # Configuração de Docker, NVIDIA toolkit, rede
│   ├── tls_setup/                # Nginx + Let's Encrypt / certificado auto-assinado
│   ├── ollama_local/             # Provisionamento do LLM local
│   ├── presidio_guard/           # Detecção e anonimização de PII
│   ├── fastapi_gateway/          # Proxy unificado + audit log (componente central)
│   ├── anythingllm_core/         # Interface do pesquisador (RAG + chat)
│   ├── compliance_audit/         # Relatórios diários, rotação de logs
│   └── backup/                   # Backup com rotação 7/4/3 (diário/semanal/mensal)
├── templates/                    # Jinja2 templates
│   ├── gateway_main_py.j2        # FastAPI Gateway (coração do sistema)
│   ├── docker-compose.yml.j2     # Configurações de containers
│   ├── anythingllm_nginx_conf.j2 # Configuração Nginx
│   ├── audit_script.sh.j2        # Script de auditoria
│   └── backup_script.sh.j2       # Script de backup
├── docs/                         # Documentação adicional (PRD)
├── README.md                     # Documentação principal
├── CONTRIBUTING.md               # Este arquivo
├── CODE_OF_CONDUCT.md            # Código de conduta
└── LICENSE                       # Licença MIT

## Integração CI/CD

Este projeto usa GitHub Actions para CI. Todo Pull Request executa automaticamente:

- `ansible-lint` - Validação de qualidade do código Ansible
- `ansible-playbook --syntax-check` - Verificação de sintaxe
- `ruff` - Lint de código Python (com line-length 120)
- `yamllint` - Validação YAML (com line-length 200)

Verifique o status do CI no seu PR antes de pedir review.
```

O **Gateway** (`templates/gateway_main_py.j2`) é o componente mais complexo e crítico. Ele implementa toda a lógica de proxy, detecção de PII, auditoria e geração de relatórios para conformidade CNPq. Qualquer mudança aqui requer testes cuidadosos.

## Convenções de código

### Ansible

- Use **FQCN** (Fully Qualified Collection Names) para módulos:
  ```yaml
  - name: Instalar pacote
    ansible.builtin.apt:
      name: "{{ item }}"
      state: present
    loop: packages_list
  ```
- Use **snake_case** para nomes de variáveis e tasks
- Use **descrições claras** em português para todas as tasks
- Evite tasks com `changed_when: false` desnecessários
- Use tags de forma consistente para permitir execução granular
- Prefira loops simples em vez de when excessivos quando possível

### Jinja2 Templates

- Use 2 espaços de indentação para lógica Jinja2
- Mantenha o código Python dentro de templates limpo e legível
- Use filtros Jinja2 padrão do Ansible
- Escape variáveis corretamente: `{{ variavel }}` para output, `{% if %}` para lógica
- Comentários dentro de templates: `{# explicação #}`

### YAML

- Use **2 espaços** de indentação (não tabs)
- Use aspas duplas para strings que podem conter caracteres especiais
- Adicione comentários explicativos para lógica complexa
- Mantenha linhas abaixo de 120 caracteres quando possível
- Use blocos YAML para estruturas aninhadas complexas

### Python (Gateway e scripts)

- Use **type hints** para funções públicas
- Siga PEP 8 para estilo
- Use docstrings em português
- Preferir comprehensions quando apropriados
- Tratar erros de forma específica e informativa

## Fluxo de trabalho Git

### Branch naming

Use prefixos descritivos para suas branches:

- `feature/` para novas funcionalidades
  - `feature/suporte-claude-antropic`
  - `feature/recognizer-titulo-eleitor`
- `fix/` para correções de bugs
  - `fix/gateway-timeout-large-payloads`
  - `fix/audit-log-rotation`
- `docs/` para documentação
  - `docs/guia-instalacao-detalhado`
  - `docs/contributing-improvements`
- `refactor/` para refatoração sem mudança de comportamento
  - `refactor/modularizar-gateway-logging`
- `test/` para adição ou melhoria de testes
  - `test/molecule-scenario-presidio`

### Commit messages

Use **Conventional Commits** em português:

```
<tipo>(<escopo>): <descrição curta em português>

<corpo detalhado opcional>

<rodapé opcional>
```

Tipos comuns:
- `feat`: nova funcionalidade
- `fix`: correção de bug
- `docs`: mudança em documentação
- `style`: formatação, ponto e vírgula, etc (sem mudança de código)
- `refactor`: refatoração que não é nem feat nem fix
- `perf`: melhoria de performance
- `test`: adição ou modificação de testes
- `chore`: mudanças no processo de build ou ferramentas auxiliares

Escopos comuns: `gateway`, `ollama`, `presidio`, `anythingllm`, `audit`, `tls`, `backup`, `docs`, `tests`

Exemplos:

```
feat(gateway): adicionar suporte a modelo Claude Anthropic

Implementa integração com API da Anthropic no path /cloud.
Adiciona configuração de API key no vault e mapeamento
de workspaces para o provider 'anthropic'.

Resolves #42
```

```
fix(presidio): corrigir detecção de CPF com formatação variada

O recognizer anterior não detectava CPFs formatados como
XXX.XXX.XXX-XX. Atualiza regex para suportar formatos
com e sem pontuação.

Closes #87
```

```
docs(contributing): adicionar seção sobre testes Molecule

Documenta como rodar e escrever cenários de teste Molecule
para os roles da coleção.
```

### Workflow padrão

1. Atualize sua branch `main` local:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. Crie uma nova branch para sua contribuição:
   ```bash
   git checkout -b feature/sua-feature
   ```

3. Faça suas mudanças e commite seguindo as convenções

4. Faça push para o seu fork:
   ```bash
   git push origin feature/sua-feature
   ```

5. Abra um Pull Request no GitHub

## Como rodar testes

### Sintaxe do Ansible

```bash
# Verificar playbook principal
ansible-playbook playbooks/setup_lab.yml --syntax-check

# Verificar role específico
ansible-lint roles/ollama_local/
```

### Linting

```bash
# Lint do playbook
ansible-lint playbooks/setup_lab.yml

# Lint de toda a coleção
ansible-lint .

# Lint de YAML
yamllint .
```

### Molecule (testes de roles)

**Nota**: Os cenários Molecule ainda não estão implementados. Esta é uma área de contribuição aberta.

Quando disponíveis, os testes seguirão este padrão:

```bash
# Listar cenários disponíveis
molecule list

# Rodar todos os testes de um cenário
molecule test --scenario-name default

# Rodar apenas criação e converge
molecule converge --scenario-name default

# Verificar logs
molecule verify --scenario-name default
```

### Testes Python

```bash
# Rodar todos os testes (quando implementados)
pytest

# Rodar com coverage (quando implementados)
pytest --cov=tests --cov-report=html

# Rodar teste específico (quando implementados)
pytest tests/test_gateway.py::test_pii_detection
```

**Nota**: A infraestrutura de testes (diretório tests/, molecule/) ainda está em desenvolvimento. Por enquanto, valide mudanças usando ansible-lint, ansible-playbook --syntax-check, e testes manuais em VM de teste.

### Lint Python

```bash
# Note: Arquivos Jinja2 (.j2) contêm sintaxe que Python linters não interpretam.
# Para validar o código Python em templates, use Molecule ou extraia o código.

# Usando ruff em arquivos Python (não .j2)
ruff check .
ruff format .

# Ou usando flake8
flake8 .
```

### Validação completa antes do PR

```bash
#!/bin/bash
# run_checks.sh

echo "Verificando sintaxe Ansible..."
ansible-playbook playbooks/setup_lab.yml --syntax-check || exit 1

echo "Rodando ansible-lint..."
ansible-lint playbooks/setup_lab.yml || exit 1

echo "Verificando YAML..."
yamllint . || exit 1

echo "Rodando testes Python..."
pytest || exit 1

echo "Verificando lint Python..."
ruff check . || exit 1

echo "Todos os checks passaram!"
```

## Processo de Pull Request

Antes de abrir um PR, verifique se você completou os seguintes itens:

- [ ] **Sintaxe**: O playbook/role passa em `ansible-playbook --syntax-check`
- [ ] **Lint**: O código passa em `ansible-lint` e `yamllint`
- [ ] **Testes locais**: Você testou a mudança localmente (ansible-lint, syntax-check, VM de teste se necessário)
- [ ] **Documentação**: Se mudou funcionalidade, atualizou README.md ou docs relevantes
- [ ] **Commits**: Todos os commits seguem Conventional Commits em português
- [ ] **Branch**: A branch segue o padrão de nomenclatura (feature/, fix/, docs/, etc)
- [ ] **Descrição**: O PR inclui descrição clara do que mudou e por que
- [ ] **Referências**: O PR referencia issues relacionadas (Fixes #xxx, Closes #xxx, etc)
- [ ] **CI**: Pipeline do GitHub Actions passou (ansible-lint, syntax-check, ruff, yamllint)

### Template de descrição de PR

```markdown
## Tipo de mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Melhoria de performance
- [ ] Mudança breaking
- [ ] Documentação

## Descrição
Descreva brevemente o que este PR faz e por que é necessário.

## Motivação e contexto
Explique o problema que resolve ou a melhoria que traz.

## Como testar
Instruções para testar a mudança:
1. Passo 1
2. Passo 2
3. ...

## Screenshots (se aplicável)

## Checklist
- [ ] Meu código segue o estilo do projeto
- [ ] Testei localmente
- [ ] Adicionei/atualizei documentação
- [ ] Commits seguem Conventional Commits

## Issues relacionadas
Closes #xxx
Relates to #yyy
```

## Áreas que precisam de contribuição

O LabAI-Comply tem várias oportunidades de contribuição em diferentes níveis de dificuldade:

| Área | O que precisa | Dificuldade |
|:---|:---|:---|
| **Novos recognizers PII** | Implementar recognizers para título de eleitor, passaporte brasileiro, CNH, conta bancária, RG | Média |
| **Suporte a mais LLMs cloud** | Integrar Anthropic Claude, Google Gemini, Cohere, Mistral no path /cloud do gateway | Média |
| **Relatórios** | Gerar relatórios em LaTeX, integração com Overleaf, templates customizados por periódico | Média |
| **Multi-tenant** | Suporte a múltiplos laboratórios/grupos de pesquisa com isolamento de dados e audit log separado | Alta |
| **API pública de audit** | Expor endpoints públicos para integração com sistemas institucionais de gestão de pesquisa | Média |
| **Testes automatizados** | Escrever cenários Molecule + Testinfra para validação dos 9 roles | Média |
| **Suporte a outros SOs** | Portar para Debian 12, Rocky Linux, RHEL 9 | Baixa |
| **Dashboard** | Interface web para visualização do audit log em tempo real, gráficos de uso, alertas | Alta |
| **Internacionalização** | Suporte a recognizers de PII de outros países (para pesquisa internacional) | Média |
| **Modelos de GPU AMD** | Suporte a ROCm alongside NVIDIA para laboratórios com hardware AMD | Média |

Se você quer contribuir mas não sabe por onde começar, procure issues com a label `good first issue` ou `help wanted` no GitHub.

## Reportar bugs e sugerir features

Use o [GitHub Issues](https://github.com/haquiticos/LabAI-Comply/issues) para:

- **Reportar bugs**: Inclua detalhes do ambiente, passos para reproduzir, logs relevantes e comportamento esperado
- **Sugerir features**: Descreva o problema que a feature resolve, casos de uso e, se possível, como você imagina a implementação
- **Fazer perguntas**: Use as discussions para dúvidas gerais

### Template para bug report

```markdown
## Descrição do bug
Descrição clara e concisa do que está acontecendo.

## Ambiente
- Versão do LabAI-Comply:
- Sistema operacional do servidor:
- Versão do Ansible:
- Versão do Docker:

## Passos para reproduzir
1. Execute '...'
2. Clique em '....'
3. Role para '....'
4. Veja o erro

## Comportamento esperado
Descrição do que você esperava que acontecesse.

## Logs/prints
Cole logs relevantes, mensagens de erro ou screenshots.

## Contexto adicional
Outras informações relevantes sobre o bug.
```

### Template para feature request

```markdown
## Descrição da feature
Descrição clara e concisa da funcionalidade desejada.

## Problema que resolve
Qual problema ou dor esta feature resolve? Por que é útil?

## Solução proposta
Descreva como você imagina que a feature funcione.

## Alternativas consideradas
Descreva soluções alternativas ou features que você já considerou.

## Contexto adicional
Outras informações, mockups, exemplos, etc.
```

## Links úteis

- **Issues e discussions**: [GitHub Issues](https://github.com/haquiticos/LabAI-Comply/issues) | [GitHub Discussions](https://github.com/haquiticos/LabAI-Comply/discussions)
- **PRD completo**: [`docs/PRD-LabAI-Comply-v4.md`](docs/PRD-LabAI-Comply-v4.md) — especificação técnica detalhada
- **Segurança**: [SECURITY.md](SECURITY.md) — política de segurança
- **Vault template**: [`vault.yml.example`](vault.yml.example)

## Código de Conduta

Este projeto adota o [Código de Conduta](CODE_OF_CONDUCT.md). Espera-se que os participantes:

- Ser respeitosos e inclusivos
- Focar no que é melhor para a comunidade
- Mostrar empatia para com outros membros

Violações do código de conduta podem ser reportadas através do GitHub ou enviando email para [conduct@labai.comply](mailto:conduct@labai.comply).

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a licença MIT, a mesma do projeto.

## CHANGELOG

Ao fazer mudanças significativas, considere adicionar uma entrada ao [CHANGELOG.md](CHANGELOG.md) sob a seção `[Unreleased]`. Siga o formato Keep a Changelog.

## Obrigado

Novamente, obrigado por contribuir com o LabAI-Comply. Cada contribuição ajuda pesquisadores brasileiros a usar IA de forma ética e em conformidade com o CNPq. Juntos, podemos construir infraestrutura de IA que respeita a privacidade e a ciência.

Se você tem dúvidas, abra uma issue ou discussion no GitHub. Estamos aqui para ajudar.