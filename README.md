# Template de bot para Discord

Uma base simples em Python com comandos prefixados, um comando de ajuda e
configuração do token por variável de ambiente.

## Requisitos

- Python 3.10 ou superior
- Uma aplicação e um bot criados no
  [Discord Developer Portal](https://discord.com/developers/applications)

## Instalação

1. Clone este repositório e entre na pasta do projeto.
2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   No Windows PowerShell, ative-o com:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Copie `.env.example` para `.env` e preencha `DISCORD_TOKEN` com o token do
   bot. Você pode alterar `COMMAND_PREFIX`; o padrão é `!`.
5. No Developer Portal, habilite **Message Content Intent** em
   **Bot > Privileged Gateway Intents**. Convide o bot ao servidor com as
   permissões necessárias para ler e enviar mensagens.
6. Inicie o bot:

   ```bash
   python main.py
   ```

## Comandos de exemplo

- `!ajuda` — lista os comandos disponíveis.
- `!cenoura` — exemplo de comando de texto.
- `!temperatura` — outro exemplo de comando.

## Segurança

Nunca publique o token do bot. O arquivo `.env` está ignorado pelo Git; mantenha
os valores reais fora do repositório e use `.env.example` apenas com valores de
exemplo. Se um token já foi publicado, revogue-o no Developer Portal e gere um
novo. Antes de enviar alterações, confira os arquivos preparados para commit:
o `.gitignore` não impede o envio de arquivos que já estejam sendo rastreados
nem de arquivos adicionados explicitamente com `git add -f`.
