# LabAI-Comply — Guia de Demo (Low-Spec)

> Roteiro para implantar o LabAI-Comply em máquina com hardware limitado
> (≥ 8 GB RAM, ≥ 10 GB disco livres, sem GPU) e gerar GIFs da execução
> ponta a ponta: do `ansible-playbook` ao relatório CSV de auditoria.

## 1. Pré-requisitos

| Item | Valor |
|---|---|
| SO | Ubuntu 22.04 / Debian 12 (nativo) |
| RAM física | ≥ 8 GB |
| Disco livre | ≥ 10 GB em `/` (ou `/opt` se for mountpoint separado) |
| GPU | **não necessária** (roda em CPU) |
| Ansible | `pip install ansible community.docker` |
| Chave cloud | z.ai (GLM-5.2) ou OpenAI — qualquer provider OpenAI-compatible |
| Docker | instalado e rodando |

### 1.1 Instalar a coleção

```bash
# Clone o repo (ou use um fork local)
git clone https://github.com/haquiticos/LabAI-Comply.git
cd LabAI-Comply

# Instala como coleção Ansible local (symlink)
mkdir -p ~/.ansible/collections/ansible_collections/labai
ln -s "$PWD" ~/.ansible/collections/ansible_collections/labai/comply
```

### 1.2 Configurar secrets (vault)

```bash
cp vault.yml.example vault.yml
# Edite o vault.yml COM SEU VALOR REAL:
#   openai_api_key: "<sua-chave-z.ai>"
ansible-vault encrypt vault.yml
# Anote a senha do vault — você vai precisar em todo comando.
```

### 1.3 (Opcional) Ferramentas de captura de GIF

```bash
# Terminal GIF: asciinema + agg
sudo apt install asciinema
cargo install agg --locked  # ou: download binário de https://github.com/asciinema/agg/releases

# Browser GIF: peek (Linux) ou LICEcap (macOS) ou ScreenToGif (Windows)
sudo apt install peek
```

---

## 2. Comando único de demo (copy-paste)

Este é o comando que ajusta tudo para uma máquina de 8 GB RAM sem GPU,
pula o Ollama (não cabe na RAM), usa z.ai como cloud LLM e pula a
configuração automatizada do AnythingLLM (vai ser manual via browser).

```bash
ansible-playbook labai.comply.setup_lab \
  -i localhost, \
  --connection local \
  --vault-password-file ~/.vault_pass \
  -e '@vault.yml' \
  -e '{
    "skip_ollama": true,
    "skip_anythingllm_api": true,
    "demo_mode": true,
    "openai_base_url": "https://api.z.ai/api/paas/v4",
    "cloud_model_default": "glm-5.2",
    "workspace_registry": {
      "ws-concepcao":   {"finalidade": "concepcao e planejamento da pesquisa", "fase_pesquisa": "concepcao", "provider": "openai", "model": "glm-5.2", "path": "/cloud"},
      "ws-redacao":     {"finalidade": "redacao e revisao de texto",            "fase_pesquisa": "redacao",   "provider": "openai", "model": "glm-5.2", "path": "/cloud"},
      "ws-revisao":     {"finalidade": "revisao bibliografica",                  "fase_pesquisa": "concepcao", "provider": "openai", "model": "glm-5.2", "path": "/cloud"},
      "ws-submissao":   {"finalidade": "formatacao e preparacao para submissao","fase_pesquisa": "submissao", "provider": "openai", "model": "glm-5.2", "path": "/cloud"}
    },
    "workspace_api_keys": {
      "ws-concepcao": "key-concepcao-001",
      "ws-redacao":   "key-redacao-001",
      "ws-revisao":   "key-revisao-001",
      "ws-submissao": "key-submissao-001"
    },
    "presidio_memory_limit": "800m",
    "gateway_memory_limit": "384m",
    "anythingllm_memory_limit": "1500m"
  }'
```

**O que esse comando faz:**
1. Baixa e inicia 4 containers: `presidio-analyzer`, `presidio-anonymizer`, `gateway`, `anythingllm`
2. Gera o código Python do gateway a partir do template Jinja2
3. Cria a rede Docker `labai_net`
4. Configura TLS auto-assinado + Nginx
5. **NÃO** cria admin/workspaces no AnythingLLM (isso é o passo manual abaixo)
6. Mostra um resumo final com status dos serviços

**Tempo esperado em 8 GB / CPU:** 5-10 minutos (maior parte é build das imagens Docker).

**Para gravar GIF #1 (ansible-playbook running):**
```bash
# Comece a gravar o terminal ANTES de rodar o comando
asciinema rec -c "ansible-playbook labai.comply.setup_lab -i localhost, --connection local --vault-password-file ~/.vault_pass -e '@vault.yml' -e '{...veja acima...}'" demo-01-deploy.cast
# Converter para GIF depois:
agg demo-01-deploy.cast gifs/01-deploy.gif --speed 2
```

---

## 3. Setup manual do AnythingLLM (5-10 min, uma vez)

Depois que o playbook terminar com sucesso, abra o navegador:

### 3.1 Criar admin

1. Acesse **http://localhost:3000** (ou `https://<labai_domain>` se configurou domínio)
2. Tela "Welcome to AnythingLLM" → clique em **"Get Started"**
3. Preencha:
   - **Username**: `admin`
   - **Password**: o valor de `anythingllm_admin_password` do seu vault
4. Clique **"Setup account"**

> **GIF #2:** gravar essa etapa (qualquer ferramenta de screen recording → GIF).

### 3.2 Configurar LLM Provider (global)

AnythingLLM usa **uma única configuração de LLM** no nível do sistema (não por workspace). O `docker-compose` já injetou:
```
OPENAI_API_BASE_URL=http://gateway:8000/cloud
```

Mas você precisa confirmar no UI:

1. Settings (ícone de engrenagem no canto) → **"LLM Preference"**
2. Em "Chat LLM Provider", selecione **"Generic OpenAI"**
3. Preencha:
   - **Generic OpenAI API Key**: qualquer valor (não é usado — a chave real está no gateway)
   - **Generic OpenAI Base URL**: `http://gateway:8000/cloud` (já preenchido pelo env var)
   - **Chat Model**: `glm-5.2` (ou digite manualmente se não estiver na lista)
4. Clique **"Save changes"**

### 3.3 Criar workspaces

Para cada workspace do registry (`ws-concepcao`, `ws-redacao`, `ws-revisao`, `ws-submissao`):

1. Clique no seletor de workspace (canto superior esquerdo) → **"New Workspace"**
2. **Name**: `ws-redacao` (use exatamente o nome do registry)
3. Clique **"Create Workspace"**

> Repita para os 4 workspaces.

### 3.4 (Opcional) Setar system prompt de conformidade

Para cada workspace:

1. Entre no workspace → ícone de engrenagem → "Workspace Settings"
2. Em **"System Prompt"**, cole:
   ```
   ATENCAO: A Portaria CNPq 2.664/2026 veda a insercao de projetos de
   pesquisa de terceiros em ferramentas de IAG para elaboracao de
   pareceres cientificos. Confirme que os documentos que voce processa
   aqui sao de sua autoria ou voce possui autorizacao para utiliza-los.
   ```
3. Salve.

### 3.5 (Opcional) Desabilitar auto-registro

Settings → "System" → desligue **"Allow new user registrations"**.

---

## 4. Fluxo de demo — os 6 GIFs

Aqui está o roteiro ideal para gravar. **Cada GIF deve durar 10-20 segundos**
(edite depois se necessário).

### GIF #1 — Deploy via Ansible
- **O que gravar**: terminal rodando o comando da Seção 2
- **Highlight**: o output do post_task "LabAI-Comply Deploy Concluido" no final,
  mostrando todos os containers como "OK"
- **Ferramenta**: `asciinema rec` + `agg`
- **Comando de captura**:
  ```bash
  asciinema rec demo-01-deploy.cast -c "ansible-playbook ..."
  agg demo-01-deploy.cast gifs/01-deploy.gif --speed 3
  ```

### GIF #2 — Setup inicial do AnythingLLM (admin)
- **O que gravar**: browser, da tela de welcome até admin criado
- **Ferramenta**: peek (Linux) ou LICEcap (macOS)
- **Duração alvo**: 15-20s

### GIF #3 — Enviar chat com PII (o momento "uau" da demo)
- **Workspace**: `ws-redacao`
- **Prompt** (copie exatamente):
  ```
  Por favor, revise este trecho do meu artigo:
  "A paciente Maria Silva, CPF 123.456.789-00, apresentou sintomas
  em janeiro de 2025. O médico Dr. João Santos (CRM-SP 12345)
  solicitou exames no Hospital das Clínicas de São Paulo."
  ```
- **O que mostrar**:
  - Mensagem sendo enviada
  - Resposta do LLM voltando normalmente
  - **Crucial**: mostrar que a resposta preserva os nomes originais ("Maria Silva", "João Santos")
    mesmo tendo passado pela pseudonimização no gateway
- **Duração alvo**: 15-20s

### GIF #4 — Audit log com PII detectada (terminal)
- **Comando**:
  ```bash
  tail -5 /var/log/gateway/audit.jsonl | python3 -m json.tool
  ```
  ou, sem `jq`:
  ```bash
  tail -1 /var/log/gateway/audit.jsonl
  ```
- **O que mostrar**: a entrada mais recente com `"pii_detected": true`,
  `"pii_types": ["BR_CPF", "PERSON", ...]`, `"pii_count": N`
- **Captura**:
  ```bash
  asciinema rec demo-04-audit.cast -c 'tail -5 /var/log/gateway/audit.jsonl'
  agg demo-04-audit.cast gifs/04-audit-log.gif
  ```

### GIF #5 — Relatório CSV de conformidade CNPq
- **Comando** (browser ou curl):
  ```bash
  curl -s http://localhost:8000/audit/report?format=csv
  ```
  Ou abrir no browser: **http://localhost:8000/audit/report?format=csv**
- **O que mostrar**: o CSV renderizado com as colunas
  `Data, Ferramenta, Finalidade, Fase da Pesquisa, Interações, Tokens (aprox.)`
- **Captura**:
  ```bash
  asciinema rec demo-05-csv.cast -c 'curl -s http://localhost:8000/audit/report?format=csv | column -t -s,'
  agg demo-05-csv.cast gifs/05-csv-report.gif
  ```

### GIF #6 — Relatório PDF (opcional, mas visualmente forte)
- **URL**: http://localhost:8000/audit/report?format=pdf
- **Browser**: vai baixar `audit_report.pdf` — abra num visualizador
- **Mostra**: tabela formatada com título "Relatório de Uso de IA - LabAI-Comply"

### GIF extra — Chat sem PII (opcional)
- **Workspace**: `ws-concepcao` (ou qualquer um)
- **Prompt** (sem PII):
  ```
  Escreva uma introdução para um artigo sobre o uso de IA em pesquisa científica.
  ```
- **Mostra**: que o path cloud funciona também quando não há PII (mais rápido, sem pseudonimização)

---

## 5. Validação pós-deploy (debug rápido)

Se algo parecer errado:

```bash
# Status de todos os containers
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Health do gateway (deve retornar JSON com status de cada backend)
curl -s http://localhost:8000/health | python3 -m json.tool

# Testar PII detection isoladamente
curl -s -X POST http://localhost:8000/cloud/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer key-redacao-001" \
  -H "X-User-Email: demo@lab.ai" \
  -d '{
    "model": "glm-5.2",
    "messages": [{"role": "user", "content": "O CPF 123.456.789-00 foi aprovado."}],
    "stream": false
  }'

# Verificar chamada chegando no z.ai (logs do gateway)
docker logs gateway --tail 50

# Listar workspaces configurados no gateway
cat /opt/labai/gateway/workspace_registry.yml
```

---

## 6. Encerrar a demo

```bash
# Parar containers sem destruir volumes (permite re-deploy rápido)
docker stop anythingllm gateway presidio-analyzer presidio-anonymizer

# Reverter tudo (CUIDADO: apaga audit logs e storage do AnythingLLM)
docker rm -f anythingllm gateway presidio-analyzer presidio-anonymizer
sudo rm -rf /opt/labai /var/log/gateway
docker network rm labai_net
```

---

## 7. Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Playbook falha em "Validar espaco em disco" | Disco < 8 GB livres | Libere espaço OU rode com `-e '{"min_disk_gb": 5}'` |
| Playbook falha em "Validar requisitos minimos de hardware" | RAM < 6 GB | Libere RAM OU rode com `-e '{"min_ram_mb": 4096}'` |
| AnythingLLM não responde | Container não ficou healthy em 30s | `docker logs anythingllm`; aguarde mais 1 min |
| Chat no AnythingLLM retorna erro 502 | Gateway não consegue falar com z.ai | Verifique `OPENAI_API_KEY` no vault e conectividade de rede |
| `pii_detected: false` mesmo com CPF no prompt | Presidio Analyzer sem spaCy `pt` model | `docker logs presidio-analyzer`; rebuild do Dockerfile |
| PDF retorna erro 500 | Versão do `fpdf2` incompatível | `docker exec gateway pip install fpdf2==2.7.4` e restart |
| CSV vazio | Audit log ainda não tem registros | Envie pelo menos 1 chat antes de pedir relatório |

---

## 8. Especificações da demo

| Aspecto | Valor na demo |
|---|---|
| RAM usada (pico) | ~3-4 GB |
| Disco usado | ~6-8 GB (imagens + storage) |
| Tempo de deploy | 5-10 min |
| Tempo de setup manual AnythingLLM | 5-10 min |
| Latência de chat (cloud path) | 2-8 s por resposta (dep. da z.ai) |
| Componentes ativos | 4 (AnythingLLM, Gateway, Presidio×2) |
| Componentes pulados | Ollama (path local) |

---

## 9. Roadmap pós-demo

Depois da demo, para voltar ao modo produção (todas as features):

1. Provisionar em VM com 16+ GB RAM
2. Trocar `skip_ollama: true` → `skip_ollama: false`
3. Adicionar GPU ou usar CPU com modelo pequeno (`qwen2.5:0.5b-instruct-q4_K_M`)
4. Setar `skip_anythingllm_api: false` **somente após** corrigir os bugs da
   role anythingllm_core (paths `/api/...` → `/v1/...` e remoção de campos
   inválidos `openAiEndpoint`/`openAiKey` em workspace)

Veja `docs/PRD-LabAI-Comply-v4.md` para a especificação completa.
