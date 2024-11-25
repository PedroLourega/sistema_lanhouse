document.addEventListener('DOMContentLoaded', function () {
    
    const flashMessage = document.querySelector('.flash-message');
    
    
    if (flashMessage) {
        setTimeout(function() {
            flashMessage.classList.add('hide');  
        }, 3000); 
    }
});

