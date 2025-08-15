document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-configuracoes');
    const feedback = document.getElementById('feedback');
    const apiKeyInput = document.getElementById('api_key');

    // Botão para mostrar/ocultar chave
    const toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.textContent = 'Mostrar';
    toggleBtn.style.marginLeft = '0.5em';
    apiKeyInput.parentNode.insertBefore(toggleBtn, apiKeyInput.nextSibling);
    toggleBtn.onclick = function () {
        if (apiKeyInput.type === 'password') {
            apiKeyInput.type = 'text';
            toggleBtn.textContent = 'Ocultar';
        } else {
            apiKeyInput.type = 'password';
            toggleBtn.textContent = 'Mostrar';
        }
    };

    form.addEventListener('submit', function () {
        feedback.textContent = 'Salvando...';
        feedback.style.color = 'black';
    });
}); 