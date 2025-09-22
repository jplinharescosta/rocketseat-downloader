# Downloader de Cursos da Rocketseat

## Script original em: https://gist.github.com/felipeadeildo/961587b1f5660a5db42102666e9884d0
Créditos para @felipeadeildo 

Este é um script em Python projetado para automatizar o download de cursos, módulos e materiais da plataforma Rocketseat. Ele utiliza a sessão do usuário para acessar o conteúdo e o `yt-dlp` para baixar as videoaulas de forma eficiente.

## ⚠️ Aviso Legal

Este script foi criado para **fins educacionais** e para facilitar o acesso offline a conteúdos que você **já possui legalmente**. O download e a distribuição de conteúdo protegido por direitos autorais sem permissão são ilegais. Use esta ferramenta por sua conta e risco, respeitando sempre os **Termos de Serviço** da Rocketseat.

Não endorsamos o compartilhamento indevido de conteúdos!

---

## ✨ Funcionalidades

-   **Autenticação Segura**: Realiza login na sua conta e salva a sessão localmente para não precisar inserir suas credenciais a cada uso.
-   **Verificação de Dependências**: Checa automaticamente se **FFmpeg** e **yt-dlp** estão instalados e acessíveis no `PATH` do sistema.
-   **Seleção Interativa**: Permite escolher interativamente qual formação e quais módulos específicos você deseja baixar.
-   **Organização Automática**: Cria uma estrutura de pastas organizada para os cursos baixados: `Cursos/Nome da Formação/Nome do Módulo/`.
-   **Download Completo**: Baixa não apenas os vídeos, mas também os materiais de apoio (arquivos, links) e cria um arquivo de texto (`.txt`) com metadados da aula (descrição, autor, duração).
-   **Relatório Detalhado**: Ao final do processo, gera um relatório completo (`.txt`) na pasta `relatorios`, informando quais aulas foram baixadas com sucesso e quais falharam, além do tempo total da operação.

---

## 🚀 Pré-requisitos

Antes de executar o script, garanta que você tem o seguinte instalado e configurado em seu sistema:

1.  **Python 3.x**: [Instale a partir do site oficial](https://www.python.org/downloads/).
2.  **FFmpeg**: Essencial para que o `yt-dlp` possa juntar os segmentos de áudio e vídeo.
    -   **Download**: [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    -   **Instrução**: Após o download, **adicione o caminho da pasta `bin` do FFmpeg às suas variáveis de ambiente (PATH)**.
3.  **yt-dlp**: A ferramenta principal para o download dos vídeos.
    -   **Download**: [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
    -   **Instrução**: Após o download, **adicione o caminho do executável do yt-dlp às suas variáveis de ambiente (PATH)**.

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
    *Observação: O `m3u8` está listado, mas o código atual não o utiliza ativamente.*

---

## ▶️ Como Usar

1.  **Execute o script** a partir do seu terminal:
    ```bash
    python nome_do_script.py
    ```

2.  **Login (Primeiro Uso)**:
    -   O script verificará se existe um arquivo de sessão (`.session.pkl`).
    -   Se não houver, ele solicitará seu **e-mail e senha da Rocketseat**. Após o login bem-sucedido, a sessão será salva para usos futuros.

3.  **Seleção da Formação**:
    -   Uma lista das suas formações disponíveis será exibida.
    -   Digite o número correspondente à formação que deseja baixar e pressione `Enter`.

4.  **Seleção dos Módulos**:
    -   Em seguida, o script listará todos os módulos da formação escolhida.
    -   Você pode:
        -   Digitar `0` para baixar **todos os módulos**.
        -   Digitar os números dos módulos desejados, separados por vírgula (ex: `1, 3, 5`), para baixar apenas os selecionados.

5.  **Aguarde o Download**:
    -   O script iniciará o processo, exibindo o progresso no console. Os arquivos serão salvos na pasta `Cursos`.
    -   Ao final, um relatório detalhado será impresso no console e salvo em um arquivo na pasta `relatorios`.

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
