# POC: https://gist.github.com/felipeadeildo, obrigado 🤲
# Feito a partir de https://github.com/alefd2/script-download-lessons-rs 🚀
# Para executar tenha Python, FFmpeg, e Yt-dlp instalados, e definidos em seu PATH no Windows!
# Rod > pip install m3u8 requests beautifulsoup4
# Importações úteis
import json
import os
import pickle
import re
import time
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_API = "https://skylab-api.rocketseat.com.br"
BASE_URL = "https://app.rocketseat.com.br"
SESSION_PATH = Path(os.getenv("SESSION_DIR", ".")) / ".session.pkl"
SESSION_PATH.parent.mkdir(exist_ok=True)
DEFAULT_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "30"))

# Função para limpar CMD
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Função para limpar strings com caracteres especiais, e espaços no começo, e final
def sanitize_string(string: str):
    return re.sub(r'[@#$%&*/:^{}<>?"]', "", string).strip()

# Verificar dependências, antes de executar qualquer processo
def check_dependencies():
    """Verifica se as dependências de linha de comando (ffmpeg, yt-dlp) estão instaladas."""
    print("Verificando dependências do sistema...")
    required_commands = ["ffmpeg", "yt-dlp"]
    missing_commands = []

    for command in required_commands:
        if shutil.which(command) is None:
            missing_commands.append(command)

    if missing_commands:
        print("\nERRO: Dependências não encontradas. Por favor, instale os seguintes programas:")
        for command in missing_commands:
            print(f" - {command}")
        
        print("\nLinks para instalação:")
        print(" - FFmpeg: https://ffmpeg.org/download.html")
        print(" - yt-dlp: https://github.com/yt-dlp/yt-dlp")
        sys.exit(1) # Encerra o script

    print("✓ Todas as dependências foram encontradas.")

# Classe para criar reportes de download, em tempo de execução
class DownloadReport:
    def __init__(self):
        self.successful_downloads = []
        self.failed_downloads = []
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = datetime.now()
        print(f"Início do download: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    def add_success(self, module_title, lesson_title):
        self.successful_downloads.append({
            'module': module_title,
            'lesson': lesson_title,
            'timestamp': datetime.now()
        })
        print(f"✓ Aula baixada com sucesso: {module_title} - {lesson_title}")
    
    def add_failure(self, module_title, lesson_title, error):
        self.failed_downloads.append({
            'module': module_title,
            'lesson': lesson_title,
            'error': str(error),
            'timestamp': datetime.now()
        })
        print(f"✗ Erro ao baixar aula: {module_title} - {lesson_title}")
        print(f"   Erro: {str(error)}")
    
    def finish(self):
        self.end_time = datetime.now()
        self.generate_report()
    
    def generate_report(self):
        if not self.start_time or not self.end_time:
            return "Relatório incompleto - download não finalizado"
        
        duration = self.end_time - self.start_time
        total_attempts = len(self.successful_downloads) + len(self.failed_downloads)
        
        report = [
            "=== RELATÓRIO DE DOWNLOAD ===",
            f"Data: {self.end_time.strftime('%d/%m/%Y %H:%M:%S')}",
            f"Duração total: {duration}",
            f"Total de aulas: {total_attempts}",
            f"Aulas baixadas com sucesso: {len(self.successful_downloads)}",
            f"Aulas com erro: {len(self.failed_downloads)}",
            "\n=== AULAS BAIXADAS COM SUCESSO ==="
        ]
        
        for download in self.successful_downloads:
            report.append(f"- Módulo: {download['module']}")
            report.append(f"  Aula: {download['lesson']}")
            report.append(f"  Horário: {download['timestamp'].strftime('%H:%M:%S')}")
        
        if self.failed_downloads:
            report.append("\n=== AULAS COM ERRO ===")
            for download in self.failed_downloads:
                report.append(f"- Módulo: {download['module']}")
                report.append(f"  Aula: {download['lesson']}")
                report.append(f"  Erro: {download['error']}")
                report.append(f"  Horário: {download['timestamp'].strftime('%H:%M:%S')}")
        
        report_text = "\n".join(report)
        
        # Salvar relatório em arquivo
        report_path = Path("relatorios") / f"relatorio_{self.end_time.strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        # Imprimir relatório no console
        print("\n" + "="*50)
        print(report_text)
        print("="*50)
        print(f"\nRelatório salvo em: {report_path}")

# Baixar usando CDN [mais preciso]
class CDNVideo:
    def __init__(self, video_id: str, save_path: str):
        self.video_id = video_id
        self.save_path = str(save_path)
        self.domain = os.getenv("CDN_DOMAIN", "vz-dc851587-83d.b-cdn.net")
        
        # Cabeçalhos importantes que o yt-dlp precisa enviar
        self.referer = "https://iframe.mediadelivery.net/"
        self.origin = "https://iframe.mediadelivery.net"

    def download(self):
        # 1. Verifica se o arquivo já existe
        if os.path.exists(self.save_path):
            print(f"\tArquivo já existe: {os.path.basename(self.save_path)}. Pulando.")
            return True

        print(f"Baixando com yt-dlp (CDN): {os.path.basename(self.save_path)}")

        # 2. Monta a URL da playlist
        playlist_url = f"https://{self.domain}/{self.video_id}/playlist.m3u8"
        
        print(f"URL da playlist: {playlist_url}")  # Debug da URL da playlist

        # 3. Monta o comando do yt-dlp em lista para evitar problemas de shell/quotes
        ytdlp_args = [
            "yt-dlp",
            playlist_url,
            "--merge-output-format", "mp4",
            "--concurrent-fragments", "10",
            "--add-header", f"Referer: {self.referer}",
            "--add-header", f"Origin: {self.origin}",
            "-o", self.save_path,
        ]

        # 4. Executa o comando e verifica o resultado
        try:
            completed = subprocess.run(
                ytdlp_args,
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode == 0:
                print("✓ Download (CDN) concluído com sucesso!")
                return True
            else:
                print(f"✗ yt-dlp retornou código {completed.returncode}.")
                if completed.stderr:
                    print("Stderr:")
                    print(completed.stderr.strip())
                if completed.stdout:
                    print("Stdout (parcial):")
                    print(completed.stdout.strip()[:2000])
                return False
        except FileNotFoundError:
            print("✗ yt-dlp não encontrado no PATH. Verifique a instalação.")
            return False
    
# Gerenciador de Downloads, vai instanciar as duas classes acima - ou somente uma delas, se indisponível
class VideoDownloader:
    def __init__(self, video_id: str, save_path: str):
        self.video_id = video_id
        self.save_path = save_path
        print(video_id, 'Dados dos vídeos em plaintext para Debug')
        self.cdn = CDNVideo(video_id, save_path)

    def download(self):
        # A verificação de arquivo existente já é feita dentro de cada
        # classe responsável (CDNVideo), então não precisamos dela aqui.

        print("--- Iniciando tentativa de download ---")
        
        # 1. Se o download com Panda falhou (retornou False), tenta com CDN.
        # print("\nFalha na fonte Panda. Tentando com a fonte CDN...")[DEPRECIADO]
        print("Realizando download das aulas via CDN, por favor, aguarde enquanto processamos os dados!")
        if self.cdn.download():
            # Se retornou True, o download foi bem-sucedido.
            print("-----------------------------------------")
            return
        
        # 2. Se ambas as tentativas falharam.
        print("\n✗ Não foi possível baixar o vídeo de nenhuma das fontes disponíveis.")
        print("-----------------------------------------")
    
# Processo responsável por capturar os dados no site da Rocketseat [necessário refatorar]
class Rocketseat:
    def __init__(self):
        self._session_exists = SESSION_PATH.exists()
        if self._session_exists:
            print("Carregando sessão salva...")
            self.session = pickle.load(SESSION_PATH.open("rb"))
        else:
            self.session = requests.session()
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Referer": BASE_URL,
            })
            # Configura retries e backoff para chamadas HTTP
            retries = Retry(
                total=5,
                backoff_factor=0.3,
                status_forcelist=(500, 502, 503, 504),
                allowed_methods=("GET", "POST"),
            )
            adapter = HTTPAdapter(max_retries=retries)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        self.timeout = DEFAULT_TIMEOUT
        self.download_report = DownloadReport()

    def _get(self, url: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(url, **kwargs)

    def _post(self, url: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(url, **kwargs)
    # Processo para validar credenciais, não adianta tentar baixar nada sem acesso legítimo ao conteúdo!
    def login(self, username: str, password: str):
        print("Realizando login...")
        payload = {"email": username, "password": password}
        res = self._post(f"{BASE_API}/sessions", json=payload)
        res.raise_for_status()
        data = res.json()

        self.session.headers["Authorization"] = f"{data['type'].capitalize()} {data['token']}"
        self.session.cookies.update({
            "skylab_next_access_token_v4": data["token"],
            "skylab_next_refresh_token_v4": data["refreshToken"],
        })
        
        account_infos = self._get(f"{BASE_API}/account").json()
        print(f"Bem-vindo, {account_infos['name']}!")
        pickle.dump(self.session, SESSION_PATH.open("wb"))
    # Processo para recuperar dados presentes no site
    def __load_modules(self, specialization_slug: str):
        print(f"Buscando módulos para a formação: {specialization_slug}")
        start_time = time.time()
        
        # Get modules data from API
        url = f"{BASE_API}/v2/journeys/{specialization_slug}/progress/temp"
        res = self._get(url)
        res.raise_for_status()

        modules_data = []
        print('Recebendo dados dos cursos disponíveis; lembre-se de que é necessário ter acesso legítimo para concluir o download!')
        # type: 'challenge', e que o title começe com Quiz
        # challenge: {slug: 'quiz-formacao-desenvolvimento-ia-estatistica'}

        try:
            progress_data = res.json()
            modules_data = progress_data.get("nodes", [])

            journey_url = f"https://app.rocketseat.com.br/journey/{specialization_slug}/contents"
            html_content = self._get(journey_url).text

            for module in modules_data:
                if module.get("type") in ("cluster", "group"):
                    # 1) Preferimos usar o slug do módulo quando disponível (alinha com a API /journey-nodes/{slug})
                    cluster_slug = module.get("slug")
                    if cluster_slug:
                        print(f"Usando slug do módulo (type={module.get('type')}) como cluster_slug para {module.get('title', 'Sem título')}: {cluster_slug}")
                        module["cluster_slug"] = cluster_slug
                        continue

                    # 2) Fallback (mais frágil): varrer o HTML procurando links para classroom
                    search_pattern = f'<a class="w-full" href="/classroom/'
                    html_pos = html_content.find(search_pattern)
                    if html_pos != -1:
                        start_pos = html_pos + len(search_pattern)
                        end_pos = html_content.find('"', start_pos)
                        cluster_slug = html_content[start_pos:end_pos]
                        print(f"Encontrado cluster_slug (fallback HTML) para módulo {module.get('title', 'Sem título')}: {cluster_slug}")
                        module["cluster_slug"] = cluster_slug
                        html_content = html_content[end_pos:]
                    else:
                        print(f"Não encontrado cluster_slug para módulo {module.get('title', 'Sem título')}")
                        module["cluster_slug"] = None
                else:
                    print(f"Módulo {module.get('title', 'Sem título')} não é do tipo cluster/group")
                    module["cluster_slug"] = None

            print(f"Encontrados {len(modules_data)} módulos.")
        except Exception as e:
            print(f"Erro ao processar os módulos: {e}")

        elapsed_time = time.time() - start_time
        print(f"Início: {time.strftime('%H:%M:%S')} | Busca pelos módulos concluída! | Número de módulos encontrados: {len(modules_data)} | Tempo executado: {elapsed_time:.2f} segundos")
        return modules_data

    def __load_lessons_from_cluster(self, cluster_slug: str):
        # Carrega as aulas de um nó específico (cluster ou group)
        print(f"Buscando lições para o nó: {cluster_slug}")
        url = f"{BASE_API}/journey-nodes/{cluster_slug}"
        
        try:
            res = self._get(url)
            res.raise_for_status()
            
            module_data = res.json()
            print(f"Resposta da API para o nó {cluster_slug}:")
            # print(json.dumps(module_data, indent=2)) # Debug completo da resposta da API <<<<<<<<<----------
            
            # Salva estrutura para debug
            Path("logs").mkdir(parents=True, exist_ok=True)
            with open(f"logs/{sanitize_string(cluster_slug)}_cluster_details.json", "w", encoding="utf-8") as f:
                json.dump(module_data, f, indent=2)
            
            groups = []
            # Caso 1: nó do tipo cluster (contém groups)
            if module_data.get("cluster"):
                cluster = module_data["cluster"]

                for group in cluster.get("groups", []):
                    group_title = group.get('title', 'Sem Grupo')
                    print(f"\nProcessando grupo: {group_title}")

                    group_lessons = []
                    for lesson in group.get("lessons", []):
                        if "last" in lesson and lesson["last"]:
                            lesson_data = lesson["last"]
                            lesson_data["group_title"] = group_title
                            print(f"Adicionando aula: {lesson_data.get('title', 'Sem título')}")
                            group_lessons.append(lesson_data)

                    if group_lessons:
                        groups.append({"title": group_title, "lessons": group_lessons})

            # Caso 2: nó do tipo group (lições diretamente em "lessons")
            elif module_data.get("group"):
                group_node = module_data["group"]
                group_title = group_node.get('title', 'Sem Grupo')
                print(f"\nProcessando grupo único: {group_title}")

                group_lessons = []
                for lesson in group_node.get("lessons", []):
                    if "last" in lesson and lesson["last"]:
                        lesson_data = lesson["last"]
                        lesson_data["group_title"] = group_title
                        print(f"Adicionando aula: {lesson_data.get('title', 'Sem título')}")
                        group_lessons.append(lesson_data)

                if group_lessons:
                    groups.append({"title": group_title, "lessons": group_lessons})
            
            print(f"\nEncontrados {len(groups)} grupos com um total de {sum(len(g['lessons']) for g in groups)} lições")
            return groups
        except Exception as e:
            print(f"Erro ao buscar lições do cluster {cluster_slug}: {e}")
            return []

    def _download_video(self, video_id: str, save_path: Path):
        VideoDownloader(video_id, str(save_path / "aulinha.mp4")).download()

    def _download_lesson(self, lesson: dict, save_path: Path, group_index: int, lesson_index: int):
        if isinstance(lesson, dict) and 'title' in lesson:
            title = lesson.get('title', 'Sem título')
            group_title = lesson.get('group_title', 'Sem Grupo')
            print(f"\tBaixando aula {group_index}.{lesson_index}: {title} (Grupo: {group_title})")
            
            try:
                # Criar pasta do grupo se não existir
                group_folder = save_path / f"{group_index:02d}. {sanitize_string(group_title)}"
                group_folder.mkdir(exist_ok=True)
                
                # Criar arquivo base com número sequencial do grupo
                base_name = f"{lesson_index:02d}. {sanitize_string(title)}"
                
                # Salvar metadados em arquivo .txt
                with open(group_folder / f"{base_name}.txt", "w", encoding="utf-8") as f:
                    f.write(f"Grupo: {group_title}\n")
                    f.write(f"Aula: {title}\n\n")
                    
                    # Adicionar descrição se existir
                    if 'description' in lesson and lesson['description']:
                        f.write(f"Descrição:\n{lesson['description']}\n\n")
                    
                    # Adicionar outras informações se existirem
                    if 'duration' in lesson:
                        minutes = lesson['duration'] // 60
                        seconds = lesson['duration'] % 60
                        f.write(f"Duração: {minutes}min {seconds}s\n")
                    
                    if 'author' in lesson and lesson['author'] and isinstance(lesson['author'], dict):
                        author_name = lesson['author'].get('name', '')
                        if author_name:
                            f.write(f"Autor: {author_name}\n")
                
                # Baixar o vídeo se tiver resource
                if 'resource' in lesson and lesson['resource']:
                    resource = lesson["resource"].split("/")[-1] if "/" in lesson["resource"] else lesson["resource"]
                    VideoDownloader(resource, str(group_folder / f"{base_name}.mp4")).download()
                    self.download_report.add_success(group_title, title)
                else:
                    print(f"\tAula '{title}' não tem recurso de vídeo")
                    self.download_report.add_success(group_title, title)  # Considera sucesso mesmo sem vídeo
                
                # Baixar arquivos adicionais
                if 'downloads' in lesson and lesson['downloads']:
                    downloads_dir = group_folder / f"{base_name}_arquivos"
                    downloads_dir.mkdir(exist_ok=True)
                    
                    for download in lesson['downloads']:
                        # Suporta variações comuns de chaves na API
                        download_url = (
                            download.get('file_url') or
                            download.get('fileUrl') or
                            download.get('url')
                        )

                        if download_url:
                            download_title = download.get('title') or download.get('name') or 'arquivo'
                            file_ext = os.path.splitext(download_url)[1]

                            download_path = downloads_dir / f"{sanitize_string(download_title)}{file_ext}"
                            print(f"\t\tBaixando material: {download_title}")

                            try:
                                # Usa a sessão autenticada para downloads que possam exigir cookies/headers
                                response = self._get(download_url)
                                response.raise_for_status()

                                with open(download_path, 'wb') as f:
                                    f.write(response.content)

                                print(f"\t\tMaterial salvo em: {download_path}")
                            except Exception as e:
                                print(f"\t\tErro ao baixar material: {e}")
            except Exception as e:
                self.download_report.add_failure(group_title, title, e)
                print(f"\tErro ao baixar aula: {str(e)}")
        else:
            print(f"\tFormato de aula não reconhecido: {lesson}")

    def _download_courses(self, specialization_slug: str, specialization_name: str):
        print(f"Baixando cursos da especialização: {specialization_name}")
        self.download_report.start()
        
        try:
            modules = self.__load_modules(specialization_slug)

            print("\nEscolha os módulos que você quer baixar:")
            print("[0] - Baixar todos os módulos")
            for i, module in enumerate(modules, 1):
                print(f"[{i}] - {module['title']}")

            choices = input("Digite 0 para baixar todos os módulos ou os números dos módulos separados por vírgula (ex: 1, 3, 5): ")
            
            if choices.strip() == "0":
                selected_modules = modules
                print("\nBaixando todos os módulos...")
            else:
                selected_modules = [modules[int(choice.strip()) - 1] for choice in choices.split(",")]

            for module in selected_modules:
                module_title = module["title"]
                course_name = module.get("course", {}).get("title", "Sem Nome")
                print(f"\nBaixando módulo: {module_title} do curso: {course_name}")
                save_path = Path("Cursos") / specialization_name / sanitize_string(course_name) / sanitize_string(module_title)
                save_path.mkdir(parents=True, exist_ok=True)

                # Verifica se o módulo tem um cluster_slug
                if "cluster_slug" in module and module["cluster_slug"]:
                    cluster_slug = module["cluster_slug"]
                    print(f"Usando cluster_slug: {cluster_slug}")
                    
                    # Obter grupos e aulas a partir do cluster_slug
                    groups = self.__load_lessons_from_cluster(cluster_slug)
                    
                    if not groups:
                        print(f"Nenhum grupo encontrado para o módulo: {module_title}")
                        continue
                    
                    # Baixa cada grupo sequencialmente
                    for group_index, group in enumerate(groups, 1):
                        group_title = group["title"]
                        print(f"\nProcessando grupo {group_index}: {group_title}")
                        
                        # Baixa cada aula do grupo
                        for lesson_index, lesson in enumerate(group["lessons"], 1):
                            self._download_lesson(lesson, save_path, group_index, lesson_index)
                        
                        print(f"Grupo {group_index} ({group_title}) concluído!")
                else:
                    print(f"Módulo não possui cluster_slug: {module_title}. Pulando.")
                    continue
        finally:
            self.download_report.finish()

    def select_specializations(self):
        print("Buscando especializações disponíveis...")
        params = {
            "types[0]": "SPECIALIZATION",
            "types[1]": "COURSE",
            "types[2]": "EXTRA",
            "limit": "1000",
            "offset": "0",
            "page": "1",
            "sort_by": "relevance",
        }
        specializations = self._get(f"{BASE_API}/catalog/list", params=params).json()["items"]
        clear_screen()
        print("Selecione uma formação ou 0 para selecionar todas:")
        for i, specialization in enumerate(specializations, 1):
            print(f"[{i}] - {specialization['title']}")

        choice = int(input(">> "))
        if choice == 0:
            for specialization in specializations:
                self._download_courses(specialization["slug"], specialization["title"])
        else:
            specialization = specializations[choice - 1]
            self._download_courses(specialization["slug"], specialization["title"])

    def run(self):
        if not self._session_exists:
            # Permite autenticar via variáveis de ambiente ou prompt (senha mascarada)
            email = os.getenv("ROCKETSEAT_EMAIL") or input("Seu email Rocketseat: ")
            try:
                import getpass
                pwd = os.getenv("ROCKETSEAT_PASSWORD") or getpass.getpass("Sua senha: ")
            except Exception:
                pwd = os.getenv("ROCKETSEAT_PASSWORD") or input("Sua senha: ")

            self.login(username=email, password=pwd)
        self.select_specializations()


# Principal, vai chamar e executar tudo
if __name__ == "__main__":
    # 1. Executa a verificação de dependências primeiro
    check_dependencies()

    # 2. Se tudo estiver OK, o resto do script continua
    print("\nIniciando o processo de download...")
    agent = Rocketseat()
    agent.run()    