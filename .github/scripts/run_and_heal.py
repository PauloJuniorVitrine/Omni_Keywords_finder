import argparse
import subprocess
import json
import os
import time
import glob
from datetime import datetime
from openai import OpenAI

# Lê a chave da API do ambiente (injetada pelo GitHub Actions)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_language(test_path):
    """Detecta a linguagem de testes com base nos arquivos e configs."""
    if glob.glob(f"{test_path}/**/*.py", recursive=True) or os.path.exists("requirements.txt"):
        return "python"
    elif glob.glob(f"{test_path}/**/*.php", recursive=True) or os.path.exists("composer.json"):
        return "php"
    elif glob.glob(f"{test_path}/**/*.js", recursive=True) or glob.glob(f"{test_path}/**/*.ts", recursive=True) or os.path.exists("package.json"):
        return "node"
    return None

def run_tests(test_path, lang):
    """Executa os testes de acordo com a linguagem detectada."""
    if lang == "python":
        cmd = ["pytest", "-q", test_path, "--maxfail=1", "--disable-warnings"]
    elif lang == "php":
        cmd = ["vendor/bin/phpunit", test_path, "--testdox"]
    elif lang == "node":
        if os.path.exists("package.json"):
            cmd = ["npm", "test", "--", test_path]
        else:
            cmd = ["npx", "jest", test_path]
    else:
        raise ValueError("Não foi possível detectar linguagem de testes.")

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout + "\n" + result.stderr

def request_fix(stage, logs, lang):
    """Envia logs de erro para o GPT-4.1 e solicita patch mínimo."""
    lang_label = {"python": "Python", "php": "PHP", "node": "JavaScript/Node.js"}[lang]
    prompt = f"""
Você é um especialista em {lang_label}.
Analise os logs abaixo e sugira um patch mínimo no formato git diff para corrigir o erro.

Regras:
- Nunca modifique arquivos sensíveis (.env, secrets)
- Preserve comentários e documentação existentes
- Evite reescrever arquivos inteiros, apenas diffs pontuais

Logs:
{logs}
"""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

def apply_patch(stage, patch):
    """Aplica o patch sugerido e cria Pull Request."""
    patch_dir = f"patches/{stage}"
    os.makedirs(patch_dir, exist_ok=True)
    patch_file = f"{patch_dir}/patch_{int(time.time())}.diff"
    with open(patch_file, "w") as f:
        f.write(patch)

    branch_name = f"auto-heal/{stage}/{int(time.time())}"
    subprocess.run(["git", "checkout", "-b", branch_name])
    subprocess.run(["git", "apply", patch_file])
    subprocess.run(["git", "commit", "-am", f"Auto-heal patch for {stage}"])
    subprocess.run(["gh", "pr", "create", "--fill"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests", required=True, help="Caminho para os testes")
    parser.add_argument("--stage", required=True, help="Nome do estágio (unit, integration, e2e)")
    parser.add_argument("--max-attempts", type=int, default=8, help="Número máximo de tentativas de healing")
    args = parser.parse_args()

    lang = detect_language(args.tests)
    if not lang:
        print("⚠️ Nenhuma linguagem detectada nos testes.")
        return

    os.makedirs(f"logs/{args.stage}", exist_ok=True)
    report = {"stage": args.stage, "language": lang, "attempts": []}

    for attempt in range(1, args.max_attempts + 1):
        code, logs = run_tests(args.tests, lang)
        report["attempts"].append({
            "attempt": attempt,
            "result": "pass" if code == 0 else "fail",
            "logs": logs
        })
        if code == 0:
            break
        patch = request_fix(args.stage, logs, lang)
        apply_patch(args.stage, patch)

    with open(f"logs/{args.stage}_healing_report.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()
