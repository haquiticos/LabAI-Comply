# LabAI-Comply — Guia de Demo (Cloud-Only / Low-Spec)

> Roteiro ponta a ponta, validado em máquina de ~9 GB RAM sem GPU: do
> `ansible-playbook` ao relatório CSV/PDF de conformidade CNPq, passando pelo
> **momento "uau"** — enviar um trecho com PII (CPF, nome) e ver a resposta
> preservar os dados originais enquanto o audit log registra a detecção.

Este guia usa **apenas o path cloud** (z.ai GLM-5.2), sem Ollama. O Ollama
(path local) exige ≥ 16 GB RAM/GPU e está fora do escopo desta demo.

---

## 0. Leitura obrigatória — Z.ai Coding Plan x PaaS

A z.ai expõe **dois endpoints** com a mesma chave, mas cobrança diferente:

| Endpoint | Produto | Quando usar |
|---|---|---|
| `https://api.z.ai/api/coding/paas/v4` | **Coding Plan** (assinatura) | ✅ Você tem o plano de codificação da z.ai |
| `https://api.z.ai/api/paas/v4` | PaaS (pay-per-use) | Você recarregou saldo / comprou pacote de recursos |

> **⚠️ Erro #1 mais comum:** usar `…/api/paas/v4` com uma chave de Coding Plan
> retorna `{"error":{"code":"1113","message":"Insufficient balance or no
> resource package. Please recharge."}}`. A chave é válida — o endpoint é que
> está errado. Se você assina o Coding Plan, use sempre `…/api/coding/paas/v4`.
>
> Dica: o endpoint correto é o mesmo que o `zai-coding-plan` do opencode usa.

---

## 1. Pré-requisitos

| Item | Valor |
|---|---|
| SO | Ubuntu 22.04 / Debian 12 |
| RAM física | ≥ 8 GB (validado com 9 GB) |
| Disco livre | ≥ 10 GB em `/` |
| GPU | **não necessária** |
| Ansible | `ansible-core` + coleção `community.docker` |
| Docker | instalado e rodando |
| Chave | z.ai (GLM-5.2) — Coding Plan **ou** PaaS com saldo |

### 1.1 Verificar pré-requisitos

```bash
ansible-playbook --version                                  # ansible-core
ansible-galaxy collection list | grep community.docker      # coleção docker
docker version --format '{{.Server.Version}}'               # docker server
python3 -c "import urllib.request; urllib.request.urlopen('https://api.z.ai').read()"  # rede
```

> O pacote Python `docker` **não** é necessário — a coleção `community.docker`
> 5.x fala direto com a API do Docker.

### 1.2 Instalar a coleção (symlink local)

```bash
cd /home/billy/labAI-comply
mkdir -p ~/.ansible/collections/ansible_collections/labai
ln -sfn "$PWD" ~/.ansible/collections/ansible_collections/labai/comply
```

### 1.3 Configurar secrets (vault)

```bash
cp vault.yml.example vault.yml
# Edite vault.yml com a SUA chave z.ai:
#   openai_api_key: "sua-chave-z.ai"
ansible-vault encrypt vault.yml
echo 'sua-senha-do-vault' > ~/.vault_pass
chmod 600 ~/.vault_pass
```

---

## 2. Deploy — comando único

Crie um arquivo de variáveis de demo (evita problemas de escape de aspas no
shell) e rode o playbook:

```bash
cat > /tmp/labai-demo-vars.json <<'EOF'
{
  "skip_ollama": true,
  "skip_anythingllm_api": true,
  "demo_mode": true,
  "min_ram_mb": 4096,
  "openai_base_url": "https://api.z.ai/api/coding/paas/v4",
  "cloud_model_default": "glm-5.2",
  "workspace_registry": {
    "ws-concepcao": {"finalidade": "concepcao e planejamento da pesquisa", "fase_pesquisa": "concepcao", "provider": "openai", "model": "glm-5.2", "path": "/cloud"},
    "ws-redacao":   {"finalidade": "redacao e revisao de texto",            "fase_pesquisa": "redacao",   "provider": "openai", "model": "glm-5.2", "path": "/cloud"},
    "ws-revisao":   {"finalidade": "revisao bibliografica",                  "fase_pesquisa": "concepcao", "provider": "openai", "model": "glm-5.2", "path": "/cloud"},
    "ws-submissao": {"finalidade": "formatacao e preparacao para submissao","fase_pesquisa": "submissao", "provider": "openai", "model": "glm-5.2", "path": "/cloud"}
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
}
EOF

ansible-playbook labai.comply.setup_lab \
  -i localhost, \
  --connection local \
  --become \
  --vault-password-file ~/.vault_pass \
  -e '@vault.yml' \
  -e '@/tmp/labai-demo-vars.json'
```

> Se você usa **PaaS com saldo** (não Coding Plan), troque
> `openai_base_url` por `https://api.z.ai/api/paas/v4`.

**O que esse comando faz:**

1. Sobe 4 containers: `presidio-analyzer`, `presidio-anonymizer`, `gateway`, `anythingllm`
2. Gera o código Python do gateway a partir do template Jinja2 e builda a imagem
3. Cria a rede Docker `labai_net` e o registry de workspaces
4. Configura TLS auto-assinado + Nginx
5. **Não** cria admin/workspaces no AnythingLLM (passo manual, Seção 3)

**Tempo esperado:** 3–6 min (maior parte é build da imagem do gateway e
inicialização do spaCy no Presidio).

**Saída esperada no resumo final:**

```
Status dos Servicos:
  Ollama: SKIPPED
  Gateway: OK
  AnythingLLM: OK
  Audit Log: OK
```

> O gateway pode aparecer como **FALHOU (503)** se você esquecer `skip_ollama`
> ou se a imagem do gateway não tiver sido reconstruída após editar o template.
> Veja a Seção 7.

---

## 3. Setup manual do AnythingLLM (5–10 min, uma vez)

Como `skip_anythingllm_api=true`, a configuração do AnythingLLM é por browser.

### 3.1 Criar admin

1. Acesse **http://localhost:3000**
2. Tela "Welcome to AnythingLLM" → **Get Started**
3. **Username**: `admin` · **Password**: o valor de `anythingllm_admin_password` do vault
4. **Setup account**

> **Importante:** o `SERVER_PORT` do AnythingLLM foi corrigido para `3000`
> (a imagem `mintplexlabs/anythingllm:latest` defaulta para 3001). Sem isso a
> UI nunca responde em `:3000`.

### 3.2 Configurar LLM Provider (global)

Settings → **LLM Preference**:

1. Chat LLM Provider: **Generic OpenAI**
2. Generic OpenAI Base URL: `http://gateway:8000/cloud` (já vem do env `OPENAI_API_BASE_URL`)
3. API Key: qualquer valor (a chave real vive no gateway)
4. Chat Model: `glm-5.2`
5. **Save changes**

### 3.3 Criar workspaces

Para cada workspace do registry (`ws-concepcao`, `ws-redacao`, `ws-revisao`,
`ws-submissao`): seletor de workspace → **New Workspace** → nome exato →
**Create Workspace**.

### 3.4 (Opcional) System prompt de conformidade

Em cada workspace → Settings → **System Prompt**:

```
ATENCAO: A Portaria CNPq 2.664/2026 veda a insercao de projetos de pesquisa de
terceiros em ferramentas de IAG para elaboracao de pareceres cientificos.
Confirme que os documentos que voce processa aqui sao de sua autoria ou voce
possui autorizacao para utiliza-los.
```

---

## 4. Fluxo da demo — os 6 GIFs

Cada GIF: 10–20s. Ferramentas: `asciinema` + `agg` (terminal); `peek`/LICEcap
(browser).

### GIF #1 — Deploy via Ansible

Terminal rodando o comando da Seção 2. Destaque: o resumo final com todos os
containers como OK.

```bash
asciinema rec demo-01-deploy.cast -c "ansible-playbook labai.comply.setup_lab ..."
agg demo-01-deploy.cast gifs/01-deploy.gif --speed 3
```

### GIF #2 — Setup inicial do AnythingLLM (browser)

Da tela de welcome ao admin criado + provider Generic OpenAI configurado.

### GIF #3 — Chat com PII (o momento "uau")

- **Workspace:** `ws-redacao`
- **Prompt:**

```
Por favor, revise este trecho do meu artigo:
"A paciente Maria Silva, CPF 123.456.789-00, apresentou sintomas em janeiro de
2025. O medico Dr. Joao Santos (CRM-SP 12345) solicitou exames no Hospital das
Clinicas de Sao Paulo."
```

- **O que mostrar:** a resposta volta normal e **preserva os nomes originais**
  ("Maria Silva", "Joao Santos") — mesmo tendo passado pela pseudonimização no
  gateway (a PII é trocada por pseudônimos só no trecho enviado ao LLM e
  restaurada na volta).

### GIF #4 — Audit log com PII detectada (terminal)

```bash
tail -1 /var/log/gateway/audit.jsonl | python3 -m json.tool
```

Mostrar: `"pii_detected": true`, `"pii_types": ["BR_CPF","LOCATION","BR_RG","PERSON"]`,
`"pii_count": 6`, `"workspace": "ws-redacao"`, `"fase_pesquisa": "redacao"`.

### GIF #5 — Relatório CSV de conformidade CNPq

```bash
curl -s http://localhost:8000/audit/report?format=csv | column -t -s,
```

Colunas: `Data, Ferramenta, Finalidade, Fase da Pesquisa, Interações, Tokens (aprox.)`.

### GIF #6 — Relatório PDF

Browser: **http://localhost:8000/audit/report?format=pdf** → baixa
`audit_report.pdf` com a tabela formatada ("Relatório de Uso de IA - LabAI-Comply").

### GIF extra — Chat sem PII (opcional)

Workspace `ws-concepcao`, prompt sem PII. Mostra que o path cloud também
funciona (mais rápido, sem etapa de pseudonimização).

---

## 5. Testar o gateway direto (sem AnythingLLM)

Útil para validar a ponta a ponta sem abrir o browser:

```bash
# Chat com PII pelo path cloud (workspace ws-redacao)
curl -s -X POST http://localhost:8000/cloud/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer key-redacao-001" \
  -H "X-User-Email: demo@lab.ai" \
  -d '{
    "model": "glm-5.2",
    "messages": [{"role":"user","content":"Revise: O CPF 123.456.789-00 foi aprovado para Maria Silva."}],
    "stream": false
  }' | python3 -m json.tool
```

**Endpoints do gateway:**

| Endpoint | Descrição |
|---|---|
| `GET /health` | Status de cada backend (ollama/analyzer/anonymizer) |
| `POST /cloud/v1/chat/completions` | Path cloud (z.ai) com pseudonimização |
| `POST /local/v1/chat/completions` | Path local (Ollama) — exige `skip_ollama=false` |
| `GET /audit/usage` | Registros de auditoria em JSON |
| `GET /audit/report?format=csv` | Relatório agregado CSV (CNPq) |
| `GET /audit/report?format=pdf` | Relatório agregado PDF |

---

## 6. Validação pós-deploy (debug rápido)

```bash
# Status de todos os containers (todos devem estar "healthy")
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Health do gateway (status=healthy, analyzer/anonymizer=up, ollama=disabled)
curl -s http://localhost:8000/health | python3 -m json.tool

# Audit log (última entrada)
tail -1 /var/log/gateway/audit.jsonl | python3 -m json.tool

# Registry de workspaces no gateway
cat /opt/labai/gateway/workspace_registry.yml

# Logs do gateway (ver chamadas chegando na z.ai)
docker logs gateway --tail 50
```

---

## 7. Encerrar / reverter a demo

```bash
# Parar sem destruir volumes (re-deploy rápido)
docker stop anythingllm gateway presidio-analyzer presidio-anonymizer

# Reverter tudo (CUIDADO: apaga audit logs e storage do AnythingLLM)
docker rm -f anythingllm gateway presidio-analyzer presidio-anonymizer
sudo rm -rf /opt/labai /var/log/gateway
docker network rm labai_net
```

---

## 8. Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Chat retorna `code 1113 "Insufficient balance"` | Endpoint PaaS com chave de Coding Plan | Trocar `openai_base_url` para `…/api/coding/paas/v4` |
| Presidio Analyzer `/health` trava para sempre (worker gunicorn travado) | `nlp.yml` aponta para `en_core_web_sm`, mas a imagem base traz `en_core_web_lg` | Usar `en_core_web_lg` no template `presidio_nlp.yml.j2` |
| AnythingLLM em loop de restart: `unable to open database file: ../storage/anythingllm.db` | Storage dir `root:root`, mas o container roda como uid 1000 | `chown -R 1000:1000` no storage (ou o role já faz isso) |
| AnythingLLM healthy mas UI não responde em `:3000` | Imagem defaulta `SERVER_PORT=3001` | Setar `SERVER_PORT=3000` no env do container |
| Presidio Anonymizer sempre `unhealthy` / gateway `presidio_anonymizer: down` | Anonymizer defaulta porta interna 3000, mas publica/healthcheck em 5001 | Setar `-e PORT=5001` no anonymizer |
| Gateway `degraded`/503 com `ollama: down` em modo cloud-only | Health conta ollama ausente como falha | Env `OLLAMA_DISABLED=true` (setado quando `skip_ollama=true`) |
| Gateway ainda com código antigo após editar template | `community.docker.docker_image` não detectou a mudança (cache) | `docker build -t labai-gateway /opt/labai/gateway/` e recriar o container |
| Playbook falha em "Validar requisitos minimos de hardware" | RAM < 6 GB | `-e '{"min_ram_mb":4096}'` |
| PDF retorna erro 500 | `fpdf2` incompatível | `docker exec gateway pip install fpdf2==2.7.4` |
| CSV vazio | Audit log sem registros | Envie ≥ 1 chat antes de pedir o relatório |

---

## 9. Especificações da demo (valores medidos)

| Aspecto | Valor |
|---|---|
| Containers ativos | 4 (AnythingLLM, Gateway, Presidio Analyzer, Presidio Anonymizer) |
| Containers pulados | Ollama (path local) |
| RAM usada (pico) | ~3–4 GB |
| Disco usado | ~6–8 GB (imagens + storage) |
| Tempo de deploy | 3–6 min |
| Tempo de setup manual AnythingLLM | 5–10 min |
| Latência de chat (cloud + pseudonimização) | 15–25 s/resposta (GLM-5.2 com reasoning) |
| Modelo | glm-5.2 (z.ai Coding Plan) |

---

## 10. Roadmap pós-demo (modo produção)

Para voltar ao modo completo (path local + todas as features):

1. Provisionar VM com 16+ GB RAM (e GPU opcional)
2. `skip_ollama: false` e `skip_anythingllm_api: false`
3. Modelo local pequeno em CPU: `qwen2.5:0.5b-instruct-q4_K_M` (ou GPU para maiores)
4. Corrigir os endpoints legados da role `anythingllm_core` (`/api/…` → `/v1/…`) antes de reativar o setup automatizado

Veja `docs/PRD-LabAI-Comply-v4.md` para a especificação completa.
