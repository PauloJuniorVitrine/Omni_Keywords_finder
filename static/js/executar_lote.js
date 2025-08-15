document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-executar-lote');
    const blogsContainer = document.getElementById('blogs-container');
    const categoriasInput = document.getElementById('categorias_por_blog');
    const feedback = document.getElementById('feedback');
    const resumo = document.getElementById('resumo-lote');
    const barraProgresso = document.getElementById('barra-progresso-lote');
    const progressoPreenchido = document.getElementById('progresso-preenchido-lote');
    const percentualLote = document.getElementById('percentual-lote');
    const statusSection = document.getElementById('lote-status');
    const logsLote = document.getElementById('logs-lote');
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', function (e) {
        // Validação obrigatória
        const checked = blogsContainer.querySelectorAll('input[type="checkbox"]:checked');
        const nCategorias = parseInt(categoriasInput.value, 10);
        if (!checked.length) {
            feedback.textContent = 'Selecione pelo menos um blog.';
            feedback.style.color = 'red';
            e.preventDefault();
            return false;
        }
        if (isNaN(nCategorias) || nCategorias < 1 || nCategorias > 7) {
            feedback.textContent = 'Informe um número de categorias entre 1 e 7.';
            feedback.style.color = 'red';
            e.preventDefault();
            return false;
        }
        // Resumo dos parâmetros
        const blogs = Array.from(checked).map(i => i.parentNode.textContent.trim());
        resumo.innerHTML = `<b>Resumo:</b><ul><li><b>Blogs:</b> ${blogs.join(', ')}</li><li><b>Categorias por blog:</b> ${nCategorias}</li></ul>`;
        resumo.style.display = '';
        // Desabilitar botão
        submitBtn.disabled = true;
        feedback.textContent = 'Enviando...';
        feedback.style.color = 'black';
        barraProgresso.style.display = '';
        progressoPreenchido.style.width = '0%';
        percentualLote.textContent = '';
        logsLote.innerHTML = '';
        // Foco acessível
        statusSection.setAttribute('tabindex', '-1');
        statusSection.focus();
    });

    // Polling de status e logs
    function atualizarStatusLote() {
        fetch('/api/lote_status')
            .then(resp => resp.json())
            .then(data => {
                if (data.status && data.status.length) {
                    let concluidos = 0;
                    let total = data.status.length;
                    statusSection.innerHTML = '';
                    data.status.forEach(item => {
                        const div = document.createElement('div');
                        div.textContent = `${item.blog} / ${item.categoria}: ${item.status}`;
                        if (item.status === 'Concluído') concluidos++;
                        if (item.status === 'Erro') div.style.color = '#b80000';
                        statusSection.appendChild(div);
                    });
                    // Barra de progresso
                    const pct = Math.round((concluidos / total) * 100);
                    progressoPreenchido.style.width = pct + '%';
                    barraProgresso.style.display = '';
                    percentualLote.textContent = pct + '%';
                    if (pct === 100) {
                        submitBtn.disabled = false;
                        feedback.textContent = 'Execução em lote concluída!';
                        feedback.style.color = '#0a7d2c';
                    }
                } else {
                    barraProgresso.style.display = 'none';
                }
                // Logs
                if (data.logs && data.logs.length) {
                    logsLote.innerHTML = data.logs.map(l => `<div>${l}</div>`).join('');
                }
            });
    }
    setInterval(atualizarStatusLote, 3000);
}); 