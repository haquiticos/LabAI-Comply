# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere a [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [0.2.0] - 2025-06-01

### Adicionado
- Infraestrutura inicial da comunidade (CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, CHANGELOG.md, GitHub templates, CI básico)
- Sistema de auditoria automática para conformidade com Portaria CNPq 2.664/2026
- FastAPI Gateway com proxy unificado para acesso a IA (local e cloud)
- Role `hardware_profiling` para detecção automática de hardware e seleção de modelo Ollama
- Role `system_setup` para configuração do Docker, NVIDIA toolkit e rede
- Role `tls_setup` para Nginx com Let's Encrypt ou certificado auto-assinado
- Role `ollama_local` para provisão dinâmica de LLMs locais
- Role `presidio_guard` para detecção e anonimização de PII (CPF, CNPJ, nomes, telefones)
- Role `anythingllm_core` para interface de pesquisa com RAG e workspaces por fase
- Role `compliance_audit` para relatórios diários, rotação de logs e exportação CSV/PDF
- Role `backup` para backup diário com política de rotação 7/4/3
- Proteção automática de dados PII brasileiros via Microsoft Presidio
- Política fail-open para garantir disponibilidade com componentes degradados
- Sistema de workspaces mapeados para fases da pesquisa (concepção, redação, análise, submissão)
- Auditoria completa de interações com IA (timestamp, modelo, provedor, finalidade, tokens)
- Gerenciamento de secrets via ansible-vault
- Suporte a GPU NVIDIA com seleção automática de modelos baseada em hardware
- Templates Jinja2 para gateway FastAPI, docker-compose, Nginx e scripts

### Alterado
- Versão inicial da coleção Ansible labai.comply (namespace: labai, name: comply)

[Unreleased]: https://github.com/haquiticos/LabAI-Comply/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/haquiticos/LabAI-Comply/releases/tag/v0.2.0