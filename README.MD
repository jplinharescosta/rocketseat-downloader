# Downloader de Cursos da Rocketseat

## Script original em: https://gist.github.com/felipeadeildo/961587b1f5660a5db42102666e9884d0

## Script de atualização em: https://github.com/Kazbonfim/rocketseat-downloader2

Créditos para @felipeadeildo e @Kazbonfim

Este é um script em Python projetado para automatizar o download de cursos, módulos e materiais da plataforma Rocketseat. Ele utiliza a sessão do usuário para acessar o conteúdo e o `yt-dlp` para baixar as videoaulas de forma eficiente.

## ⚠️ Aviso Legal

Este script foi criado para **fins educacionais** e para facilitar o acesso offline a conteúdos que você **já possui legalmente**. O download e a distribuição de conteúdo protegido por direitos autorais sem permissão são ilegais. Use esta ferramenta por sua conta e risco, respeitando sempre os **Termos de Serviço** da Rocketseat.

Não endorsamos o compartilhamento indevido de conteúdos!

---

## ✨ Funcionalidades

- **Autenticação Segura**: Realiza login na sua conta e salva a sessão localmente para não precisar inserir suas credenciais a cada uso. Suporte a credenciais via variáveis de ambiente e senha mascarada no prompt.
- **Verificação de Dependências**: Checa automaticamente se **FFmpeg** e **yt-dlp** estão instalados e acessíveis no `PATH` do sistema.
- **Seleção Interativa**: Permite escolher interativamente qual formação e quais módulos específicos você deseja baixar.
- **Organização Automática**: Cria uma estrutura de pastas organizada para os cursos baixados: `Cursos/Nome da Formação/Nome do Curso/Nome do Módulo/`.
- **Download Completo**: Baixa os vídeos via `yt-dlp` (com headers obrigatórios) e também materiais de apoio. Gera um `.txt` com metadados (descrição, autor, duração) por aula.
- **Resiliência de Rede**: Requisições HTTP com retries e timeout configurável, reduzindo falhas transitórias.
- **Compatível com múltiplas estruturas da API**: Funciona tanto com nós do tipo `cluster` (com `groups`) quanto do tipo `group` (lições diretamente em `group.lessons`).
- **Relatório Detalhado**: Ao final, gera um relatório (`.txt`) na pasta `relatorios`, informando êxitos, falhas e duração total.
- **Logs para Debug**: Salva a resposta de `/journey-nodes/{slug}` em `logs/{slug}_cluster_details.json` para inspeção quando necessário.

---

## 🚀 Pré-requisitos

Antes de executar o script, garanta que você tem o seguinte instalado e configurado em seu sistema:

1.  **Python 3.x**: [Instale a partir do site oficial](https://www.python.org/downloads/).
2.  **FFmpeg**: Essencial para que o `yt-dlp` possa juntar os segmentos de áudio e vídeo.
    - **Download**: [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    - **Instrução**: Após o download, **adicione o caminho da pasta `bin` do FFmpeg às suas variáveis de ambiente (PATH)**.
3.  **yt-dlp**: A ferramenta principal para o download dos vídeos.

    - **Download**: [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
    - **Instrução**: Após o download, **adicione o caminho do executável do yt-dlp às suas variáveis de ambiente (PATH)**.

4.  (Opcional) Defina variáveis de ambiente para facilitar o uso sem prompt (ver abaixo).

---

## 🛠️ Instalação

Com os pré-requisitos atendidos, siga os passos abaixo.

1.  **Clone o repositório ou baixe o script**:
    Se estiver usando Git, clone o repositório. Caso contrário, apenas salve o arquivo `.py` em uma pasta de sua escolha.

2.  **Acesse a pasta do projeto**:
    Abra um terminal (CMD, PowerShell ou outro) e navegue até a pasta onde você salvou o script.

    ```bash
    cd caminho/para/a/pasta
    ```

3.  **Instale as dependências Python**:
    Execute o comando a seguir para instalar as bibliotecas necessárias. É recomendado criar um ambiente virtual (`venv`) antes.

    ```bash
    pip install requests beautifulsoup4 m3u8
    ```

    _Observação: O `m3u8` está listado, mas o código atual não o utiliza ativamente._

4.  (Opcional) Configure variáveis de ambiente:

    - `ROCKETSEAT_EMAIL` e `ROCKETSEAT_PASSWORD`: para login sem prompt.
    - `HTTP_TIMEOUT`: timeout padrão das requisições (segundos, ex.: `30`).
    - `CDN_DOMAIN`: domínio da CDN do vídeo (fallback padrão já configurado).
    - `SESSION_DIR`: pasta onde o arquivo `.session.pkl` será salvo (por padrão, a raiz do projeto).

---

## ▶️ Como Usar

1.  **Execute o script** a partir do seu terminal:

    ```bash
    python main.py
    ```

2.  **Login (Primeiro Uso)**:

    - O script verificará se existe um arquivo de sessão (`.session.pkl`).
    - Se não houver, ele solicitará seu **e-mail** e a **senha mascarada**. Alternativamente, use `ROCKETSEAT_EMAIL` e `ROCKETSEAT_PASSWORD` para login automático. Após o login, a sessão será salva para usos futuros.

3.  **Seleção da Formação**:

    - Uma lista das suas formações disponíveis será exibida.
    - Digite o número correspondente à formação que deseja baixar e pressione `Enter`.

4.  **Seleção dos Módulos**:

    - Em seguida, o script listará todos os módulos da formação escolhida.
    - Você pode:
      - Digitar `0` para baixar **todos os módulos**.
      - Digitar os números dos módulos desejados, separados por vírgula (ex: `1, 3, 5`), para baixar apenas os selecionados.

5.  **Aguarde o Download**:
    - O script iniciará o processo, exibindo o progresso no console. Os arquivos serão salvos na pasta `Cursos`.
    - Ao final, um relatório detalhado será impresso no console e salvo em um arquivo na pasta `relatorios`.

---

## 📂 Estrutura de Arquivos Gerada

O script criará a seguinte estrutura de pastas e arquivos:

```
.
├── Cursos/
│   └── Nome da Formação/
│       └── Nome do Curso/
│           └── 01. Nome do Módulo/
│               ├── 01. Nome do Grupo/
│               │   ├── 01. Título da Aula.mp4
│               │   ├── 01. Título da Aula.txt
│               │   └── 01. Título da Aula_arquivos/
│               │       └── material_de_apoio.pdf
│               └── 02. Outro Grupo/
│                   └── ...
├── relatorios/
│   └── relatorio_20240913_223000.txt
├── .session.pkl
└── nome_do_script.py
```

## Jamais compartilhe seu arquivo de sessão, .pkl

---

## ⚙️ Variáveis de Ambiente (Resumo)

- `ROCKETSEAT_EMAIL` / `ROCKETSEAT_PASSWORD`: credenciais para login automático.
- `HTTP_TIMEOUT`: timeout (em segundos) para todas as requisições HTTP (padrão: 30).
- `CDN_DOMAIN`: domínio da CDN usada nos vídeos (ex.: `vz-xxxx.b-cdn.net`).
- `SESSION_DIR`: diretório para salvar `.session.pkl`.

---

## 🪪 Créditos

- Script original: [@felipeadeildo](https://github.com/felipeadeildo)
- Manutenção/atualizações e melhorias: [@Kazbonfim](https://github.com/Kazbonfim)

Obrigado por compartilhar conhecimento e facilitar a vida de quem estuda! 🙌

---

## 🧰 Dicas e Solução de Problemas

- "yt-dlp não encontrado": verifique a instalação e se o executável está no PATH.
- "ffmpeg não encontrado": instale o FFmpeg e adicione a pasta `bin` ao PATH.
- Erros 401/403 ao baixar materiais: garanta que está logado (arquivo `.session.pkl` válido) e que possui acesso ao conteúdo.
- Se a Rocketseat alterar domínios de entrega dos vídeos, ajuste `CDN_DOMAIN`.
- Para diagnósticos, confira `logs/{slug}_cluster_details.json` e os relatórios em `relatorios/`.
