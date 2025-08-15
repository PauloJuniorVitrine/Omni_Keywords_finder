import time
import random
import string
import concurrent.futures
import psutil
from infrastructure.processamento.exportador_keywords import ExportadorKeywords
from domain.models import Keyword, IntencaoBusca
from typing import Dict, List, Optional, Any

TOTAL_KEYWORDS = 100_000
CONCURRENCY = 8
EXPORTS = 10


def random_keyword():
    termo = ' '.join(
        [''.join(random.choices(string.ascii_lowercase, key=random.randint(4, 8))) for _ in range(random.randint(3, 7))]
    )
    return Keyword(
        termo=termo,
        volume_busca=random.randint(10, 1000),
        cpc=round(random.uniform(0.1, 5.0), 2),
        concorrencia=round(random.uniform(0.1, 0.5), 2),
        intencao=IntencaoBusca.INFORMACIONAL
    )

def export_job(keywords, idx):
    exp = ExportadorKeywords(output_dir=f"/tmp/teste_extremo_{idx}")
    start = time.time()
    result = exp.exportar_keywords(keywords, f"cli{idx}", f"nich{idx}", f"cat{idx}")
    elapsed = time.time() - start
    return {
        "idx": idx,
        "status": result["status"],
        "tempo": elapsed,
        "arquivos": result["arquivos"]
    }

def main():
    print(f"[INFO] Gerando {TOTAL_KEYWORDS} keywords de cauda longa...")
    keywords = [random_keyword() for _ in range(TOTAL_KEYWORDS)]
    print("[INFO] Iniciando exportações concorrentes...")
    cpu0 = psutil.cpu_percent(interval=None)
    mem0 = psutil.virtual_memory().used
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(export_job, keywords, index) for index in range(EXPORTS)]
        results = [f.result() for f in futures]
    elapsed = time.time() - start
    cpu1 = psutil.cpu_percent(interval=None)
    mem1 = psutil.virtual_memory().used
    print("[RESULTADO] Teste de carga extremo concluído.")
    print(f"Tempo total: {elapsed:.2f}string_data")
    print(f"CPU inicial: {cpu0}%, final: {cpu1}%")
    print(f"Memória inicial: {mem0/1e6:.2f}MB, final: {mem1/1e6:.2f}MB")
    for r in results:
        print(f"Export {r['idx']}: status={r['status']}, tempo={r['tempo']:.2f}string_data, arquivos={r['arquivos']}")
    with open("test-results/relatorio_performance_extremo.txt", "w") as f:
        f.write(f"Tempo total: {elapsed:.2f}string_data\n")
        f.write(f"CPU inicial: {cpu0}%, final: {cpu1}%\n")
        f.write(f"Memória inicial: {mem0/1e6:.2f}MB, final: {mem1/1e6:.2f}MB\n")
        for r in results:
            f.write(f"Export {r['idx']}: status={r['status']}, tempo={r['tempo']:.2f}string_data, arquivos={r['arquivos']}\n")

if __name__ == "__main__":
    main() 