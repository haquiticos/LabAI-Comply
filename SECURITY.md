# Política de Segurança

## Versões Suportadas

Apenas versões 0.2.x do LabAI-Comply recebem atualizações de segurança. Versões anteriores são consideradas sem suporte e não receberão patches de segurança.

## Reportando uma Vulnerabilidade

Se você descobrir uma vulnerabilidade de segurança no LabAI-Comply, reporte-a de forma responsável. Não abra issues públicas ou divulgação pública até que tenhamos tempo de avaliar e corrigir o problema.

### Como Reportar

Você pode reportar vulnerabilidades de duas maneiras:

1. **Email**: Envie um email para security@labai.comply com detalhes sobre a vulnerabilidade
2. **GitHub Security Advisories**: Use o recurso [Security Advisory](https://github.com/haquiticos/LabAI-Comply/security/advisories) do GitHub

### O que Incluir no Relatório

Para nos ajudar a entender e corrigir o problema rapidamente, inclua o máximo de informações possível:

- Descrição detalhada da vulnerabilidade
- Passos para reproduzir (se aplicável)
- Impacto potencial da vulnerabilidade
- Sugestões de mitigação (se tiver)
- Informações sobre a versão afetada

### Tempo Esperado de Resposta

Nós nos comprometemos a responder dentro dos seguintes prazos:

- **48 horas**: Confirmação do recebimento do relatório de vulnerabilidade
- **7 dias**: Análise inicial e estimativa de severidade
- **Tempo variável**: Correção e divulgação dependendo da complexidade e severidade

## Política de Divulgação Responsável

Nós seguimos uma política de divulgação responsável:

1. Apoiamos a divulgação coordenada para dar tempo suficiente para que os usuários apliquem patches
2. Trabalharemos com o reporter para determinar uma data de divulgação apropriada
3. Vulnerabilidades críticas serão divulgadas assim que patches estiverem disponíveis
4. Manteremos o reporter informado sobre o progresso da correção

## Escopo do Projeto

O LabAI-Comply lida com dados sensíveis, incluindo:

- **Dados PII de pesquisadores**: Nomes, emails, informações de contato
- **Dados de pacientes**: Possíveis dados de saúde processados via Presidio
- **Dados de pesquisa**: Documentos, PDFs, artigos carregados no sistema
- **Credenciais**: API keys de provedores cloud (OpenAI), senhas de administração

O sistema processa dados brasileiros específicos como CPF, CNPJ, nomes, telefones e outros identificadores pessoais detectados pelo Microsoft Presidio com recognizers brasileiros.

## Medidas de Segurança Implementadas

O projeto implementa várias medidas de segurança para proteger dados sensíveis:

### Gerenciamento de Secrets

- **ansible-vault**: Todas as secrets (API keys, senhas, tokens) são armazenadas criptografadas usando ansible-vault
- **Vault password file**: Separação da senha do vault do repositório
- **Nenhuma secret em texto claro**: Sempre use vault.yml criptografado

### Proteção de Dados Pessoais (PII)

- **Microsoft Presidio**: Scaneamento automático de dados PII antes de enviar para APIs cloud externas
- **Recognizers brasileiros**: Detecção de CPF, CNPJ, nomes, telefones e outros dados brasileiros
- **Pseudonimização**: Substituição de dados PII por placeholders antes de processamento cloud
- **Restauração em streaming**: Respostas da IA restauram os placeholders com os dados originais

### Política Fail-Open

O sistema opera com política **fail-open** para garantir disponibilidade:

- Se o Presidio cair, as requisições seguem com um warning logado
- Se a API cloud cair, retorna erro ao cliente sem exposição de dados
- O sistema continua útil mesmo com componentes degradados
- Logs de auditoria registram todas as falhas para análise posterior

### Isolamento de Rede

- **Docker bridge network**: Todos os componentes rodam em uma rede Docker isolada
- **TLS/HTTPS**: Nginx com Let's Encrypt ou certificado auto-assinado para comunicação criptografada
- **Gateway centralizado**: Todo acesso a IA passa pelo FastAPI Gateway, que aplica controle e auditoria

### Auditoria e Rastreabilidade

- **Audit log**: Toda interação com IA é registrada com timestamp, modelo, provedor, finalidade e fase da pesquisa
- **Relatórios exportáveis**: Logs de auditoria podem ser exportados em CSV e PDF
- **Backup com rotação**: Backup diário com política de rotação 7/4/3

## Boas Práticas para Usuários

Para manter seu ambiente seguro, siga estas recomendações:

1. **Mantenha atualizado**: Sempre use a versão mais recente do LabAI-Comply
2. **Proteja o vault**: Nunca compartilhe o arquivo vault.yml ou a senha do vault
3. **Use TLS**: Configure Let's Encrypt em produção para comunicação criptografada
4. **Rotacione credenciais**: Atualize API keys e senhas periodicamente
5. **Monitore logs**: Revise os logs de auditoria regularmente
6. **Isole o servidor**: Execute o LabAI-Comply em um servidor dedicado com firewall configurado
7. **Backup regular**: Verifique se o backup está funcionando e teste o restore periodicamente

## Agradecimentos

Agradecemos aos pesquisadores de segurança que ajudam a manter o LabAI-Comply seguro reportando vulnerabilidades de forma responsável. Sua contribuição é fundamental para proteger dados de pesquisadores e usuários em universidades brasileiras.