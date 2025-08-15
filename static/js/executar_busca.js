document.addEventListener('DOMContentLoaded', function () {
    // Elementos principais
    const blogSelect = document.getElementById('blog');
    const categoriasContainer = document.getElementById('categorias-container');
    const statusSection = document.getElementById('execucao-status');
    const form = document.getElementById('form-executar-busca');
    const feedback = document.getElementById('feedback');
    const promptUpload = document.getElementById('prompt_upload');
    const promptBase = document.getElementById('prompt_base');
    const resumo = document.getElementById('resumo-parametros');
    const barraProgresso = document.getElementById('barra-progresso');
    const progressoPreenchido = document.getElementById('progresso-preenchido');
    const submitBtn = form.querySelector('button[type="submit"]');

    // Acessibilidade para feedback
    feedback.setAttribute('aria-live', 'polite');
    feedback.setAttribute('role', 'status');

    // Spinner de carregamento responsivo
    let spinner = null;
    function showSpinner() {
        if (!spinner) {
            spinner = document.createElement('div');
            spinner.id = 'spinner-loading';
            spinner.innerHTML = '<div class="spinner" aria-label="Carregando" role="status"></div>';
            spinner.style.display = 'flex';
            spinner.style.position = 'fixed';
            spinner.style.top = 0;
            spinner.style.left = 0;
            spinner.style.width = '100vw';
            spinner.style.height = '100vh';
            spinner.style.background = 'rgba(255,255,255,0.6)';
            spinner.style.justifyContent = 'center';
            spinner.style.alignItems = 'center';
            spinner.style.zIndex = 9999;
            document.body.appendChild(spinner);
        } else {
            spinner.style.display = 'flex';
        }
    }
    function hideSpinner() {
        if (spinner) {
            spinner.style.display = 'none';
            spinner.remove();
            spinner = null;
        }
    }

    // Modularização: atualizar feedback
    function atualizarFeedback(msg, cor = 'black', foco = true) {
        feedback.textContent = msg;
        feedback.style.color = cor;
        if (foco) feedback.focus();
    }

    // Modularização: limpar barra de progresso
    function limparBarraProgresso() {
        barraProgresso.style.display = 'none';
        progressoPreenchido.style.width = '0%';
    }

    // Pré-carregamento de categorias (Idle) com requestIdleCallback
    let idleTimeout;
    function preCarregarCategorias() {
        if (blogSelect.value) return;
        fetch('/api/blog_categorias?dominio=' + encodeURIComponent(blogSelect.value))
            .then(resp => resp.json())
            .then(data => {/* aquece cache */});
    }
    blogSelect.addEventListener('focus', function () {
        if ('requestIdleCallback' in window) {
            idleTimeout = requestIdleCallback(preCarregarCategorias, {timeout: 2000});
        } else {
            idleTimeout = setTimeout(preCarregarCategorias, 2000);
        }
    });
    blogSelect.addEventListener('blur', function () {
        if ('cancelIdleCallback' in window && idleTimeout) {
            cancelIdleCallback(idleTimeout);
        } else {
            clearTimeout(idleTimeout);
        }
    });

    // Limpar feedback e barra ao trocar blog/categoria
    blogSelect.addEventListener('change', function () {
        categoriasContainer.innerHTML = '';
        limparBarraProgresso();
        atualizarFeedback('', 'black', false);
        const dominio = blogSelect.value;
        if (!dominio) return;
        fetch(`/api/blog_categorias?dominio=${encodeURIComponent(dominio)}`)
            .then(resp => {
                if (resp.status === 401 || resp.status === 403) {
                    atualizarFeedback('Acesso não autorizado às categorias. Faça login ou verifique suas permissões.', 'red');
                    return Promise.reject();
                }
                return resp.json();
            })
            .then(data => {
                if (data.categorias && data.categorias.length) {
                    data.categorias.forEach(cat => {
                        const label = document.createElement('label');
                        label.className = 'categoria-checkbox';
                        const input = document.createElement('input');
                        input.type = 'checkbox';
                        input.name = 'categorias';
                        input.value = cat;
                        label.appendChild(input);
                        label.appendChild(document.createTextNode(' ' + cat));
                        categoriasContainer.appendChild(label);
                    });
                } else {
                    categoriasContainer.textContent = 'Nenhuma categoria cadastrada para este blog.';
                }
            })
            .catch(() => atualizarFeedback('Erro ao carregar categorias.', 'red'));
    });

    promptUpload.addEventListener('change', function () {
        if (promptUpload.files.length) {
            const file = promptUpload.files[0];
            if (!file.name.endsWith('.txt')) {
                atualizarFeedback('Apenas arquivos .txt são permitidos.', 'red');
                promptUpload.value = '';
                return;
            }
            if (file.size > 2 * 1024 * 1024) { // 2MB
                atualizarFeedback('Arquivo muito grande (máx. 2MB).', 'red');
                promptUpload.value = '';
                return;
            }
            atualizarFeedback('Arquivo selecionado: ' + file.name, '#0057b8', false);
        }
    });

    // Submissão do formulário
    form.addEventListener('submit', function (e) {
        // Validação de pelo menos uma categoria
        const checked = categoriasContainer.querySelectorAll('input[type="checkbox"]:checked');
        if (!checked.length) {
            atualizarFeedback('Selecione pelo menos uma categoria.', 'red');
            e.preventDefault();
            return false;
        }
        // Resumo dos parâmetros
        const blog = blogSelect.options[blogSelect.selectedIndex].text;
        const categorias = Array.from(checked).map(i => i.value);
        const prompt = promptBase.value || (promptUpload.files.length ? promptUpload.files[0].name : '');
        const modo = form.modo.value;
        resumo.innerHTML = `<b>Resumo:</b><ul><li><b>Blog:</b> ${blog}</li><li><b>Categorias:</b> ${categorias.join(', ')}</li><li><b>Prompt:</b> ${prompt}</li><li><b>Modo:</li> ${modo}</li></ul>`;
        resumo.style.display = '';
        // Desabilitar botão
        submitBtn.disabled = true;
        atualizarFeedback('Enviando...', 'black');
        statusSection.innerHTML = '';
        barraProgresso.style.display = '';
        progressoPreenchido.style.width = '0%';
        // Foco acessível
        statusSection.setAttribute('tabindex', '-1');
        statusSection.focus();
        showSpinner();
    });

    // Polling de status e barra de progresso
    let pollingInterval = null;
    function atualizarStatusExecucao() {
        fetch('/api/execucao_status')
            .then(resp => {
                if (resp.status === 401 || resp.status === 403) {
                    atualizarFeedback('Acesso não autorizado ao status de execução. Faça login ou verifique suas permissões.', 'red');
                    hideSpinner();
                    submitBtn.disabled = false;
                    if (pollingInterval) {
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                    }
                    return Promise.reject();
                }
                return resp.json();
            })
            .then(data => {
                if (data.status && data.status.length) {
                    statusSection.innerHTML = '';
                    let concluidos = 0;
                    data.status.forEach(item => {
                        const div = document.createElement('div');
                        div.textContent = `${item.categoria}: ${item.status}`;
                        if (item.status === 'Concluído') concluidos++;
                        statusSection.appendChild(div);
                    });
                    // Atualizar barra de progresso com animação suave
                    const pct = Math.round((concluidos / data.status.length) * 100);
                    progressoPreenchido.style.transition = 'width 0.5s';
                    progressoPreenchido.style.width = pct + '%';
                    barraProgresso.style.display = '';
                    if (pct === 100) {
                        submitBtn.disabled = false;
                        atualizarFeedback('Execução concluída!', '#0a7d2c');
                        hideSpinner();
                        if (pollingInterval) {
                            clearInterval(pollingInterval);
                            pollingInterval = null;
                        }
                        feedback.focus();
                    }
                } else {
                    limparBarraProgresso();
                }
            })
            .catch(() => {
                atualizarFeedback('Erro ao consultar status. Tente novamente.', 'red');
                hideSpinner();
                submitBtn.disabled = false;
                if (pollingInterval) {
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                }
            });
    }
    pollingInterval = setInterval(atualizarStatusExecucao, 3000);

    // CSS para spinner (adicionar em style.css):
    /*
    .spinner {
      border: 8px solid #f3f3f3;
      border-top: 8px solid #0057b8;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      animation: spin 1s linear infinite;
      max-width: 20vw;
      max-height: 20vw;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    */
}); 