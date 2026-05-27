# LabAI-Comply 
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
         Ollama (local)    OpenAI (cloud)
                              ↓
                      Presidio (PII scanning)
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
| RAM | 8 GB | 32 GB+ |
| Disco em `/opt` | 20 GB livres | 50 GB+ |
| GPU (opcional) | NVIDIA driver 525+ | RTX 3090 / A100 |

### Instalação

```bash
# 1. Instale a coleção
ansible-galaxy collection install labai.comply

# 2. Copie e edite o vault com suas secrets
cp vault.yml.example vault.yml
ansible-vault encrypt vault.yml
# Edite: openai_api_key, anythingllm_admin_password, workspace_api_keys

# 3. Execute o playbook
ansible-playbook labai.comply.setup_lab \
  -i your-server, \
  --vault-password-file ~/.vault_pass \
  --extra-vars '{
    "researchers": [
      {"name": "Maria Silva", "email": "maria@lab.edu.br"},
      {"name": "João Santos", "email": "joao@lab.edu.br"}
    ],
    "labai_domain": "labai.pesquisa.uf.br"
  }'
```

O playbook detecta o hardware, escolhe o melhor modelo, provisiona tudo e cria as contas dos pesquisadores. Em ~15 minutos o ambiente está no ar.

### Modo headless (sem interação)

```bash
ansible-playbook labai.comply.setup_lab \
  -i your-server, \
  --extra-vars "headless=true ollama_model_selected=qwen2.5:14b-instruct-q4_K_M"
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

**Atualizações granulares via tags:**

```bash
# Atualizar só o Ollama
ansible-playbook labai.comply.setup_lab --tags "ollama"

# Trocar modelo sem tocar no resto
ansible-playbook labai.comply.setup_lab --tags "ollama" \
  --extra-vars "ollama_model_selected=llama3.1:70b-instruct-q4_K_M"

# Adicionar pesquisadores
ansible-playbook labai.comply.setup_lab --tags "anythingllm" \
  --extra-vars '{"researchers": [{"name": "Nova Pessoa", "email": "nova@lab.edu.br"}]}'
```

---

## Contribuindo

Contribuições são bem-vindas. O projeto é MIT e roda em qualquer Ubuntu com Ansible.

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

- **Issues e feature requests:** [GitHub Issues](https://github.com/labai/comply/issues)
- **PRD completo:** [`PRD-LabAI-Comply-v4.md`](PRD-LabAI-Comply-v4.md) — especificação técnica detalhada de todos os componentes
- **Vault template:** [`vault.yml.example`](vault.yml.example)
