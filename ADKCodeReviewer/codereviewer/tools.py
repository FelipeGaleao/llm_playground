import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Define o diretório workspace padrão onde ficam os arquivos de código
WORKSPACE_DIR = Path(__file__).parent / "workspace"


def _resolve_path(file_path: str) -> Path:
    """Resolve o caminho relativo ou nome de arquivo dentro do workspace."""
    clean_name = Path(file_path).name if "/" not in file_path and "\\" not in file_path else file_path
    target = (WORKSPACE_DIR / clean_name).resolve()
    if not str(target).startswith(str(WORKSPACE_DIR.resolve())):
        raise ValueError(f"Acesso negado: o caminho '{file_path}' está fora do workspace permitido.")
    return target


def list_files(directory: str = "") -> dict[str, Any]:
    """Lista todos os arquivos de código disponíveis no workspace.

    Use esta ferramenta para descobrir quais arquivos existem no projeto antes de perguntar ao usuário.

    Args:
        directory: Subdiretório opcional (deixe vazio para listar todo o workspace).

    Returns:
        Lista com os nomes dos arquivos encontrados.
    """
    try:
        base_dir = _resolve_path(directory) if directory else WORKSPACE_DIR
        if not base_dir.exists() or not base_dir.is_dir():
            return {
                "status": "error",
                "error": f"Diretório '{directory}' não encontrado.",
            }

        files_list = []
        for p in base_dir.rglob("*"):
            if p.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in p.parts):
                files_list.append(str(p.relative_to(WORKSPACE_DIR)))

        return {
            "status": "success",
            "files": sorted(files_list),
            "total_files": len(files_list),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def grep_search(pattern: str, file_pattern: str = "*.py") -> dict[str, Any]:
    """Varre e busca por nomes de funções, classes, variáveis ou textos dentro dos arquivos do workspace.

    SEMPRE use esta ferramenta quando o usuário mencionar um nome de função (ex: 'divide', 'add', 'calcular')
    ou relatar um bug sem especificar exatamente em qual arquivo ele está.

    Args:
        pattern: Termo ou expressão a buscar (ex: 'divide', 'def divide', 'class Calculator').
        file_pattern: Extensão ou filtro de arquivos (padrão: '*.py').

    Returns:
        Lista de correspondências encontradas com arquivo, linha e código correspondente.
    """
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        matches = []

        for p in WORKSPACE_DIR.rglob(file_pattern):
            if not p.is_file() or any(part.startswith(".") or part == "__pycache__" for part in p.parts):
                continue

            try:
                rel_path = str(p.relative_to(WORKSPACE_DIR))
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
                for line_num, line in enumerate(lines, start=1):
                    if regex.search(line):
                        matches.append({
                            "file": rel_path,
                            "line_number": line_num,
                            "line_content": line.strip(),
                        })
            except Exception:
                continue

        if not matches:
            # Fallback amigável: lista quais arquivos existem no workspace para orientar o modelo
            available = [str(f.relative_to(WORKSPACE_DIR)) for f in WORKSPACE_DIR.rglob("*.py") if f.is_file()]
            return {
                "status": "no_matches",
                "message": f"Nenhuma ocorrência de '{pattern}' encontrada.",
                "available_files_in_workspace": available,
            }

        return {
            "status": "success",
            "query": pattern,
            "total_matches": len(matches),
            "matches": matches,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def read_file(file_path: str = "", filename: str = "") -> dict[str, Any]:
    """Lê o conteúdo completo de um arquivo dentro do workspace.

    Args:
        file_path: Caminho ou nome do arquivo no workspace (ex: 'calculator.py').
        filename: Alias para file_path caso fornecido como filename.

    Returns:
        Conteúdo textual do arquivo.
    """
    target_name = file_path or filename
    if not target_name:
        return {
            "status": "error",
            "error": "Nome do arquivo não fornecido. Use list_files para ver os arquivos disponíveis.",
        }

    try:
        path = _resolve_path(target_name)
        if not path.exists():
            available = [str(f.relative_to(WORKSPACE_DIR)) for f in WORKSPACE_DIR.rglob("*.py") if f.is_file()]
            return {
                "status": "error",
                "error": f"Arquivo '{target_name}' não existe no workspace. Arquivos disponíveis: {available}",
            }
        if not path.is_file():
            return {
                "status": "error",
                "error": f"'{target_name}' não é um arquivo regular.",
            }

        content = path.read_text(encoding="utf-8")
        return {
            "status": "success",
            "file_path": str(path.relative_to(WORKSPACE_DIR)),
            "content": content,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def write_file(file_path: str = "", content: str = "", filename: str = "") -> dict[str, Any]:
    """Grava ou atualiza o conteúdo de um arquivo de código dentro do workspace.

    Args:
        file_path: Caminho ou nome do arquivo a ser gravado (ex: 'calculator.py').
        content: Novo conteúdo textual completo do arquivo.
        filename: Alias para file_path caso fornecido como filename.

    Returns:
        Confirmação de gravação do arquivo.
    """
    target_name = file_path or filename
    if not target_name:
        return {
            "status": "error",
            "error": "Nome do arquivo não fornecido.",
        }

    try:
        path = _resolve_path(target_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "file_path": str(path.relative_to(WORKSPACE_DIR)),
            "message": f"Arquivo '{target_name}' gravado com sucesso.",
            "bytes_written": len(content),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def run_tests(test_target: str = "") -> dict[str, Any]:
    """Executa os testes automatizados do workspace via pytest ou unittest.

    Args:
        test_target: Arquivo de teste específico (ex: 'test_calculator.py') ou vazio para executar todos.

    Returns:
        Resultado da execução (passed/failed), stdout e stderr.
    """
    cmd = [sys.executable, "-m", "pytest"]
    if test_target:
        target_path = _resolve_path(test_target)
        cmd.append(str(target_path))
    else:
        cmd.append(str(WORKSPACE_DIR))

    try:
        result = subprocess.run(
            cmd,
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0 and "No module named pytest" in result.stderr:
            cmd_fallback = [sys.executable, "-m", "unittest", "discover", "-s", str(WORKSPACE_DIR)]
            result = subprocess.run(
                cmd_fallback,
                cwd=str(WORKSPACE_DIR),
                capture_output=True,
                text=True,
                timeout=30,
            )

        passed = result.returncode == 0
        return {
            "status": "passed" if passed else "failed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "A execução dos testes excedeu o tempo limite de 30 segundos.",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
