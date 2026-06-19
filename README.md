# LabAI-Comply

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ansible Collection](https://img.shields.io/badge/Ansible-labai.comply-blue.svg)](https://github.com/haquiticos/LabAI-Comply)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](CHANGELOG.md)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **Em desenvolvimento...**


**Infraestrutura de IA para pesquisa científica — com conformidade CNPq automática.**

Coleção Ansible que provisiona um ambiente completo de IA para pesquisadores: chat com LLMs (local e cloud), base de conhecimento com RAG, proteção de dados sensíveis e — o mais importante — rastreabilidade automática para relatórios de uso de IA exigidos pela [Portaria CNPq 2.664/2026](https://www.gov.br/cnpq/pt-br/assuntos/normas-e-legislacao/portaria-n-2.664-de-2026).

---

## Por que usar o LabAI-Comply?

### Você é pesquisador?

A Portaria CNPq 2.664/2026 (Art. 9º, I, c) exige que você **declare o uso de ferramentas de IA** em qualquer fase da pesquisa — concepção, redação, análise de dados ou submissão. Isso significa:

- Anotar **quando** usou IA
- Especificar **qual ferramenta** (ChatGPT, Claude, Gemini...)
- Declarar **com que finalidade**

**O problema:** se você usa ChatGPT no navegador, não existe registro automático. Na hora de escrever a declaração para o artigo, você precisa reconstruir tudo de memória. E esquecimentos podem caracterizar infração.

**O LabAI-Comply resolve isso** porque **toda interação com IA já é registrada automaticamente**. No fim da pesquisa, você exporta um relatório CSV ou PDF com todas as informações exigidas pela Portaria — data, ferramenta, finalidade, fase da pesquisa, quantidade de interações e tokens consumidos.

E não é só conformidade. O LabAI-Comply oferece:

| Recurso | O que significa na prática |
|:---|:---|
| **RAG local** | Faça upload de PDFs, artigos e dados no AnythingLLM. Converse com seus documentos. Tudo fica no servidor do laboratório. |
| **LLM local (Ollama)** | Para dados sensíveis — dados de pacientes, informações confidenciais. O modelo roda no seu hardware, nada sai da rede. |
| **LLM cloud (OpenAI)** | Para tarefas onde o modelo mais potente faz diferença — revisão de literatura, tradução, reescrita. Com proteção automática de PII. |
| **Proteção de PII** | Antes de enviar qualquer texto para a cloud, o sistema detecta e anonimiza CPF, CNPJ, nomes, telefones e outros dados brasileiros. |
| **Workspaces por finalidade** | Cada workspace já mapeia para uma fase da pesquisa (concepção, redação, análise...) com auditoria separada. |
| **Relatório exportável** | Um endpoint gera o CSV para colar na declaração do artigo. Sem planilha, sem lembrança. |

**Em resumo: o LabAI-Comply é a ferramenta que você escolhe usar porque é mais útil que o ChatGPT solto — e ainda gera os registros que o CNPq exige.**

---

### Você é desenvolvedor?

O LabAI-Comply é software livre (MIT). Contribuições são bem-vindas e necessárias.

**Por que contribuir?**

- **Problema real:** A Portaria CNPq afeta ~100 mil pesquisadores no Brasil. A maioria não tem ferramenta nenhuma para Compliance de IA.
- **Stack moderna e limpa:** Ansible + Docker + FastAPI + Ollama. Código legível, bem estruturado, com PRD detalhado.
- **Impacto direto:** Cada melhoria beneficia pesquisadores que precisam de conformidade para submeter artigos e projetos.
- **Campo aberto:** Muitas oportunidades de contribuição — veja a lista abaixo.

**Arquitetura:**

```
Pesquisador → AnythingLLM (interface)
                  ↓ (todo acesso passa aqui)
            FastAPI Gateway (proxy + audit)
               ↙              ↘
         Ollama (local)    Presidio (PII scanning)
                              ↓ (anonimiza antes de enviar)
                          OpenAI (cloud)
```

O Gateway é o componente central. Todo acesso a IA — local ou cloud — passa por ele. Ele identifica o workspace, registra a interação no audit log, e (no path cloud) escaneia PII antes de enviar para a API externa.

**Stack:**

| Camada | Tecnologia |
|:---|:---|
| Provisionamento | Ansible Collection (`labai.comply`) |
| Interface | AnythingLLM (RAG + chat) |
| LLM local | Ollama (modelos dinâmicos, GPU opcional) |
| Detecção de PII | Microsoft Presidio (com recognizers brasileiros) |
| Proxy + audit | FastAPI (Python 3.12) |
| Infraestrutura | Docker (rede única, bridge) |
| TLS | Nginx + Let's Encrypt / auto-assinado |

---

## Quick Start

### Requisitos do servidor

| Requisito | Mínimo | Recomendado |
|:---|:---|:---|
| SO | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| vCPUs | 4 | 8+ |
| RAM | 8 GB ([modo demo](#modo-demo-low-spec--cloud-only)) / 12 GB (completo) | 32 GB+ |
| Disco em `/opt` | 20 GB livres | 50 GB+ |
| GPU (opcional) | NVIDIA driver 525+ | RTX 3090 / A100 |

### Pré-requisitos do host que executa o Ansible

| Item | Como instalar |
|:---|:---|
| Ansible + coleção Docker | `pip install ansible community.docker` |
| Docker | instalado e em execução no servidor alvo |
| Privilégio `sudo` no alvo | o playbook roda com `become: true`; use `--ask-become-pass` (sudo com senha) ou configure `NOPASSWD` no sudoers |

### 1. Instalar a coleção

Escolha **um** dos caminhos (sem a coleção instalada, o FQCN `labai.comply.setup_lab` não resolve e aparece o erro `the playbook: labai.comply.setup_lab could not be found`):

**A. Da Ansible Galaxy** — produção, versão publicada:

```bash
ansible-galaxy collection install labai.comply
```

**B. De um clone local (symlink)** — desenvolvimento / acompanhar o `main`:

```bash
git clone https://github.com/haquiticos/LabAI-Comply.git
cd LabAI-Comply
mkdir -p ~/.ansible/collections/ansible_collections/labai
ln -s "$PWD" ~/.ansible/collections/ansible_collections/labai/comply
cd ~/LabAI-Comply   # todos os comandos abaixo rodam daqui
```

**C. Direto pelo caminho do arquivo** — sem instalar como coleção:

```bash
ansible-playbook playbooks/setup_lab.yml -i localhost, ...
```

### 2. Configurar secrets (vault)

```bash
cp vault.yml.example vault.yml
# Edite vault.yml com valores reais:
#   openai_api_key:             "<sua-chave-do-provider-cloud>"
#   anythingllm_admin_password: "<senha-forte>"
#   workspace_api_keys:         chaves por workspace (identificam o ws no gateway)
ansible-vault encrypt vault.yml
# Anote a senha do vault — ela é pedida em todos os comandos abaixo:
echo 'minha-senha-vault' > ~/.vault_pass && chmod 600 ~/.vault_pass
```

### 3. Executar o playbook

O playbook é referenciado pelo FQCN `labai.comply.setup_lab`. Para rodar
**localmente na própria máquina** (típico em lab/demo):

```bash
ansible-playbook labai.comply.setup_lab \
  -i localhost, \
  --connection local \
  --vault-password-file ~/.vault_pass \
  --ask-become-pass \
  -e '@vault.yml' \
  -e '{
    "researchers": [
      {"name": "Maria Silva", "email": "maria@lab.edu.br"},
      {"name": "João Santos", "email": "joao@lab.edu.br"}
    ],
    "labai_domain": "labai.pesquisa.uf.br"
  }'
```

Para rodar **remotamente via SSH**, troque o inventário:

```bash
ansible-playbook labai.comply.setup_lab \
  -i labai.pesquisa.uf.br, \
  -u ubuntu \
  --vault-password-file ~/.vault_pass \
  --ask-become-pass \
  -e '@vault.yml' \
  -e '{"labai_domain": "labai.pesquisa.uf.br"}'
```

O playbook detecta o hardware, escolhe o melhor modelo Ollama, provisiona
todos os containers e cria as contas dos pesquisadores. Em ~15 minutos o
ambiente está no ar (5-10 min em modo demo).

### Cloud LLM provider

O path `/cloud/` do gateway aceita qualquer provider **compatível com a
OpenAI API** — basta trocar `openai_base_url` e `cloud_model_default`:

| Provider | `openai_base_url` | Modelo exemplo |
|:---|:---|:---|
| OpenAI | `https://api.openai.com/v1` | `gpt-4` |
| z.ai (GLM) | `https://api.z.ai/api/paas/v4` | `glm-5.2` |
| BigModel | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-plus` |

```bash
... -e '{
  "openai_base_url": "https://api.z.ai/api/paas/v4",
  "cloud_model_default": "glm-5.2"
}'
```

### Modo demo (low-spec / cloud-only)

Para máquinas com **8 GB RAM / sem GPU** — pula o Ollama, reduz os limites
de memória dos containers e usa um cloud LLM (z.ai GLM-5.2 no exemplo):

```bash
ansible-playbook labai.comply.setup_lab \
  -i localhost, \
  --connection local \
  --vault-password-file ~/.vault_pass \
  --ask-become-pass \
  -e '@vault.yml' \
  -e '{
    "skip_ollama": true,
    "skip_anythingllm_api": true,
    "demo_mode": true,
    "openai_base_url": "https://api.z.ai/api/paas/v4",
    "cloud_model_default": "glm-5.2",
    "workspace_registry": {
      "ws-concepcao": {"finalidade": "concepcao e planejamento da pesquisa", "fase_pesquisa": "concepcao", "provider": "openai", "model": "glm-5.2", "path": "/cloud"},
      "ws-redacao":   {"finalidade": "redacao e revisao de texto",            "fase_pesquisa": "redacao",   "provider": "openai", "model": "glm-5.2", "path": "/cloud"}
    },
    "workspace_api_keys": {
      "ws-concepcao": "key-concepcao-001",
      "ws-redacao":   "key-redacao-001"
    },
    "presidio_memory_limit": "800m",
    "gateway_memory_limit": "384m",
    "anythingllm_memory_limit": "1500m"
  }'
```

Walkthrough completo (setup manual do AnythingLLM, validação pós-deploy,
GIFs, troubleshooting): veja **[`docs/DEMO.md`](docs/DEMO.md)**.

### Modo headless (sem interação)

Pula os prompts de seleção de modelo e fixa o Ollama escolhido:

```bash
ansible-playbook labai.comply.setup_lab \
  -i your-server, \
  --vault-password-file ~/.vault_pass \
  --ask-become-pass \
  -e '@vault.yml' \
  -e '{"headless": true, "ollama_model_selected": "qwen2.5:14b-instruct-q4_K_M"}'
```

---

## Como funciona na prática

### Para o pesquisador

1. **Acesse** `https://seu-labai-domain` e faça login
2. **Escolha o workspace** conforme a tarefa:
   - **Análise de Dados** → LLM local (seus dados não saem do servidor)
   - **Redação** → GPT-4 cloud (com proteção automática de PII)
   - **Revisão de Literatura** → GPT-4 cloud
   - **Concepção** → GPT-4 cloud
   - **Submissão** → GPT-4 cloud
3. **Faça upload de documentos** no workspace para RAG
4. **Converse com a IA** normalmente
5. **Na hora do relatório CNPq**, acesse `/audit/report?format=csv` e exporte:

```csv
Data,Ferramenta,Finalidade,Fase da Pesquisa,Interações,Tokens (aprox.)
15/01/2025,"Qwen2.5 14B (Ollama local)","análise e processamento de dados","análise de dados",5,1200
15/01/2025,"GPT-4 (OpenAI)","redação e revisão de texto","redação",8,2400
16/01/2025,"GPT-4 (OpenAI)","revisão bibliográfica","concepção",3,900
```

Pronto. Cole isso na declaração do artigo. Sem esforço adicional.

### Para o operador de TI

```
Roles Ansible (provisionamento):
├── hardware_profiling  — detecta hardware, escolhe modelo
├── system_setup        — Docker, NVIDIA toolkit, rede
├── tls_setup           — Nginx + Let's Encrypt
├── ollama_local        — LLM local dinâmico
├── presidio_guard      — detecção/anonimização de PII
├── fastapi_gateway     — proxy unificado + audit
├── anythingllm_core    — interface + workspaces + contas
├── compliance_audit    — relatórios diários, rotação de logs
└── backup              — backup diário com rotação 7/4/3
```

**Atualizações granulares via tags** — todas exigem `--vault-password-file`,
`-e '@vault.yml'` e `-i <host>,` como no comando completo. Tags disponíveis:
`hardware`, `system`, `tls`, `ollama`, `presidio`, `gateway`, `anythingllm`,
`audit`, `backup`, `validate`.

```bash
# Atualizar só o Ollama
ansible-playbook labai.comply.setup_lab -i your-server, \
  --vault-password-file ~/.vault_pass --ask-become-pass \
  --tags "ollama" -e '@vault.yml'

# Trocar modelo sem tocar no resto
ansible-playbook labai.comply.setup_lab -i your-server, \
  --vault-password-file ~/.vault_pass --ask-become-pass \
  --tags "ollama" -e '@vault.yml' \
  -e '{"ollama_model_selected": "llama3.1:70b-instruct-q4_K_M"}'

# Adicionar pesquisadores
ansible-playbook labai.comply.setup_lab -i your-server, \
  --vault-password-file ~/.vault_pass --ask-become-pass \
  --tags "anythingllm" -e '@vault.yml' \
  -e '{"researchers": [{"name": "Nova Pessoa", "email": "nova@lab.edu.br"}]}'
```

---

## Contribuindo

Contribuições são bem-vindas. O projeto é MIT e roda em qualquer Ubuntu com Ansible. Para o guia completo de contribuição, veja [CONTRIBUTING.md](CONTRIBUTING.md).

### Áreas que precisam de contribuição

| Área | O que precisa | Dificuldade |
|:---|:---|:---|
| **Novos recognizers PII** | Título de eleitor, passaporte, CNH, conta bancária | Média |
| **Suporte a mais LLMs cloud** | Anthropic Claude, Google Gemini, Cohere | Média |
| **Relatórios** | Formato LaTeX, integração com Overleaf, templates por periódico | Média |
| **Multi-tenant** | Suporte a múltiplos laboratórios/grupos de pesquisa | Alta |
| **API pública de audit** | Endpoints para integração com sistemas da instituição | Média |
| **Testes automatizados** | Molecule + Testinfra para validação dos roles | Média |
| **Suporte a outros SOs** | Debian, Rocky Linux, RHEL | Baixa |
| **Dashboard** | Interface web para visualização do audit log | Alta |
| **Internacionalização** | Suporte a recognizers de PII de outros países | Média |
| **Modelos de GPU AMD** | Suporte a ROCm alongside NVIDIA | Média |

### Como contribuir

1. **Fork** o repositório
2. Crie uma branch: `git checkout -b feature/sua-feature`
3. Desenvolva seguindo os padrões existentes (Ansible best practices, Jinja2 templates)
4. Teste com `ansible-playbook --syntax-check` e, se possível, com Molecule
5. Abra um **Pull Request** descrevendo o problema que resolve

### Estrutura do código

```
labai_comply/
├── galaxy.yml                    # Metadados da coleção Ansible
├── defaults/main.yml             # Variáveis padrão (workspace registry, recursos)
├── vault.yml.example             # Template de secrets
├── playbooks/
│   └── setup_lab.yml             # Playbook principal
├── roles/
│   ├── hardware_profiling/       # Detecção de hardware + seleção de modelo
│   ├── system_setup/             # Docker, NVIDIA, rede
│   ├── ollama_local/             # LLM local
│   ├── presidio_guard/           # PII scanning
│   ├── fastapi_gateway/          # Proxy unificado + audit log
│   ├── anythingllm_core/         # Interface do pesquisador
│   ├── tls_setup/                # TLS + Nginx
│   ├── compliance_audit/         # Relatórios + rotação
│   └── backup/                   # Backup com rotação 7/4/3
└── templates/                    # Jinja2 templates (gateway, docker-compose, Nginx, scripts)
```

O componente mais rico é o **Gateway** (`templates/gateway_main_py.j2`) — um FastAPI que atua como proxy para todo acesso a IA, com detecção de PII, pseudonimização, restauração em streaming e geração de relatórios CNPq em CSV/PDF. É onde a maior parte da lógica de negócio vive.

---

## Conformidade CNPq

A [Portaria CNPq 2.664/2026](https://www.gov.br/cnpq/pt-br/assuntos/normas-e-legislacao/portaria-n-2-664-de-2026) (Art. 9º, I, c) exige que o pesquisador:

> *"Declare o uso de ferramentas de IAG, de qualquer espécie e em qualquer fase do desenvolvimento da pesquisa, especificando a ferramenta utilizada e a finalidade."*

O LabAI-Comply atende esse requisito em dois níveis:

1. **Automático:** Cada interação com IA é registrada com timestamp, modelo, provedor, finalidade e fase da pesquisa — tanto no caminho local (Ollama) quanto no cloud (OpenAI).
2. **Exportável:** Relatórios em CSV e PDF prontos para inclusão em declarações de artigos, relatórios técnicos e submissões.

O sistema **não impõe** restrições ao pesquisador. Opera com política **fail-open** — se o Presidio cai, a requisição segue com um warning. Se a API cloud cai, retorna erro ao client. A ferramenta continua útil mesmo com componentes degradados.

---

## Licença

MIT. Use, modifique, distribua. Veja [LICENSE](LICENSE).

---

## Links

- **Issues e feature requests:** [GitHub Issues](https://github.com/haquiticos/LabAI-Comply/issues)
- **PRD completo:** [`PRD-LabAI-Comply-v4.md`](PRD-LabAI-Comply-v4.md) — especificação técnica detalhada de todos os componentes
- **Vault template:** [`vault.yml.example`](vault.yml.example)
- **Guia de contribuição:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Segurança:** [SECURITY.md](SECURITY.md)
- **Código de conduta:** [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Histórico de versões:** [CHANGELOG.md](CHANGELOG.md)
