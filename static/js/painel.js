document.addEventListener('DOMContentLoaded', function () {
    const tabela = document.getElementById('tabela-execucoes').getElementsByTagName('tbody')[0];
    const indicadorTotal = document.getElementById('indicador-total');
    const indicadorTempo = document.getElementById('indicador-tempo');
    const indicadorFalhas = document.getElementById('indicador-falhas');
    const indicadorRepetidos = document.getElementById('indicador-repetidos');
    const indicadorPrompts = document.getElementById('indicador-prompts');
    const filtroBlog = document.getElementById('filtro-blog');
    const filtroStatus = document.getElementById('filtro-status');
    const painelLogs = document.getElementById('painel-logs');
    let execucoes = [];
    let logs = [];
    let blogs = [];
    let paginaAtual = 1;
    const porPagina = 10;
    let ordenacao = {col: 'inicio', asc: false};

    function mostrarLoading() {
        tabela.innerHTML = '<tr><td colspan="7" style="text-align:center">Carregando...</td></tr>';
    }

    function atualizarPainel() {
        fetch('/api/painel')
            .then(resp => {
                if (resp.status === 401 || resp.status === 403) {
                    tabela.innerHTML = '<tr><td colspan="7" style="color:red;text-align:center">Acesso não autorizado ao painel. Faça login ou verifique suas permissões.</td></tr>';
                    return Promise.reject();
                }
                return resp.json();
            })
            .then(data => {
                execucoes = data.execucoes;
                logs = data.logs;
                blogs = data.blogs;
                // Indicadores
                indicadorTotal.textContent = data.indicadores.total;
                indicadorTempo.textContent = data.indicadores.tempo_medio;
                indicadorFalhas.textContent = data.indicadores.falhas;
                indicadorRepetidos.textContent = data.indicadores.repetidos;
                indicadorPrompts.textContent = data.indicadores.prompts;
                // Filtros
                filtroBlog.innerHTML = '<option value="">Todos</option>' + blogs.map(b => `<option value="${b}">${b}</option>`).join('');
                renderTabela();
                renderLogs();
            });
    }

    function renderTabela() {
        let filtradas = execucoes;
        if (filtroBlog.value) filtradas = filtradas.filter(e => e.blog === filtroBlog.value);
        if (filtroStatus.value) filtradas = filtradas.filter(e => e.status === filtroStatus.value);
        // Ordenação
        filtradas = filtradas.slice().sort((a, b) => {
            let v1 = a[ordenacao.col], v2 = b[ordenacao.col];
            if (ordenacao.col === 'tempo') { v1 = +v1; v2 = +v2; }
            if (v1 < v2) return ordenacao.asc ? -1 : 1;
            if (v1 > v2) return ordenacao.asc ? 1 : -1;
            return 0;
        });
        // Paginação
        const totalPaginas = Math.ceil(filtradas.length / porPagina) || 1;
        if (paginaAtual > totalPaginas) paginaAtual = totalPaginas;
        const inicio = (paginaAtual - 1) * porPagina;
        const fim = inicio + porPagina;
        const page = filtradas.slice(inicio, fim);
        tabela.innerHTML = '';
        if (!page.length) {
            tabela.innerHTML = '<tr><td colspan="7" style="text-align:center">Nenhuma execução encontrada.</td></tr>';
        } else {
            page.forEach(e => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${e.blog}</td><td>${e.categoria}</td><td class="status-${e.status.toLowerCase()}">${e.status}</td><td>${e.inicio || '-'}</td><td>${e.fim || '-'}</td><td>${e.tempo || '-'}</td><td>${e.falha ? `<span class="falha-tooltip" title="${e.falha}">Sim</span>` : 'Não'}</td>`;
                if (e.status === 'Erro') tr.classList.add('erro');
                if (e.status === 'Em execução') tr.classList.add('execucao');
                tabela.appendChild(tr);
            });
        }
        renderPaginacao(totalPaginas);
    }

    function renderPaginacao(totalPaginas) {
        let paginacao = document.getElementById('painel-paginacao');
        if (!paginacao) {
            paginacao = document.createElement('div');
            paginacao.id = 'painel-paginacao';
            tabela.parentNode.appendChild(paginacao);
        }
        paginacao.innerHTML = '';
        for (let i = 1; i <= totalPaginas; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            btn.disabled = i === paginaAtual;
            btn.onclick = () => { paginaAtual = i; renderTabela(); };
            paginacao.appendChild(btn);
        }
    }

    function renderLogs() {
        painelLogs.innerHTML = logs.map(l => `<div>${l}</div>`).join('');
    }

    filtroBlog.onchange = filtroStatus.onchange = function () {
        paginaAtual = 1;
        renderTabela();
    };

    // Ordenação por coluna
    document.querySelectorAll('.painel-tabela th').forEach((th, idx) => {
        th.onclick = function () {
            const cols = ['blog', 'categoria', 'status', 'inicio', 'fim', 'tempo', 'falha'];
            if (ordenacao.col === cols[idx]) ordenacao.asc = !ordenacao.asc;
            else { ordenacao.col = cols[idx]; ordenacao.asc = false; }
            renderTabela();
        };
        th.style.cursor = 'pointer';
    });

    mostrarLoading();
    atualizarPainel();
    setInterval(atualizarPainel, 4000);
}); 