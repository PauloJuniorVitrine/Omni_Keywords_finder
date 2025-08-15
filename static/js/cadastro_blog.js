document.addEventListener('DOMContentLoaded', function () {
    const addBtn = document.getElementById('add-categoria');
    const container = document.getElementById('categorias-container');
    const feedback = document.getElementById('feedback');
    const contador = document.getElementById('categorias-contador');
    const previewBtn = document.getElementById('preview-btn');

    function atualizarContador() {
        const total = container.querySelectorAll('.categoria-item').length;
        contador.textContent = `${total}/7 categorias`;
        addBtn.disabled = total >= 7;
    }

    function atualizarRemocao() {
        const items = container.querySelectorAll('.categoria-item');
        items.forEach((item, idx) => {
            const btn = item.querySelector('.remove-categoria');
            btn.style.display = items.length > 1 ? '' : 'none';
            btn.onclick = function () {
                if (items.length > 1) {
                    item.remove();
                    atualizarContador();
                }
            };
        });
    }

    addBtn.addEventListener('click', function () {
        const total = container.querySelectorAll('.categoria-item').length;
        if (total >= 7) {
            feedback.textContent = 'Limite de 7 categorias atingido.';
            feedback.style.color = 'red';
            feedback.setAttribute('role', 'alert');
            return;
        }
        const div = document.createElement('div');
        div.className = 'categoria-item';
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'categorias';
        input.className = 'categoria-input';
        input.placeholder = `Categoria ${total + 1}`;
        input.required = true;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'remove-categoria';
        btn.setAttribute('aria-label', 'Remover categoria');
        btn.textContent = '×';
        div.appendChild(input);
        div.appendChild(btn);
        container.appendChild(div);
        atualizarContador();
        atualizarRemocao();
        feedback.textContent = '';
        feedback.removeAttribute('role');
    });

    previewBtn.addEventListener('click', function () {
        let previewInput = document.getElementById('preview-input');
        if (!previewInput) {
            previewInput = document.createElement('input');
            previewInput.type = 'hidden';
            previewInput.name = 'preview';
            previewInput.value = '1';
            previewInput.id = 'preview-input';
            document.getElementById('form-cadastro-blog').appendChild(previewInput);
        }
        previewInput.value = '1';
        document.getElementById('form-cadastro-blog').submit();
    });

    atualizarContador();
    atualizarRemocao();

    document.getElementById('form-cadastro-blog').addEventListener('submit', function (e) {
        feedback.textContent = 'Salvando...';
        feedback.style.color = 'black';
        feedback.removeAttribute('role');
    });
}); 