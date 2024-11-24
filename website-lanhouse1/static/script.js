document.addEventListener('DOMContentLoaded', function () {
    // Verifica se há mensagens flash na página
    const flashMessage = document.querySelector('.flash-message');
    
    // Se a mensagem flash existir, configura o tempo para escondê-la
    if (flashMessage) {
        setTimeout(function() {
            flashMessage.classList.add('hide');  // Adiciona a classe hide para desaparecer
        }, 3000); // 3000ms = 3 segundos
    }
});

