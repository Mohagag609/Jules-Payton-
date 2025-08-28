// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('App.js loaded');
});

// Global success message function
function showSuccessMessage(message) {
    console.log('Showing success message:', message);
    
    let messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) {
        console.log('Creating messages container');
        messagesContainer = document.createElement('div');
        messagesContainer.id = 'messages-container';
        messagesContainer.className = 'fixed top-20 right-5 z-[100] space-y-2';
        document.body.appendChild(messagesContainer);
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-lg transform transition-all duration-300 ease-in-out';
    alertDiv.style.opacity = '0';
    alertDiv.style.transform = 'translateX(100%)';
    
    alertDiv.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <svg class="w-6 h-6 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="font-semibold mr-2">${message}</span>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-green-500 hover:text-green-700">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        </div>
    `;
    
    messagesContainer.appendChild(alertDiv);
    
    // Animate in
    setTimeout(() => {
        alertDiv.style.opacity = '1';
        alertDiv.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translateX(100%)';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

// Global error message function
function showErrorMessage(message) {
    console.log('Showing error message:', message);
    
    let messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.id = 'messages-container';
        messagesContainer.className = 'fixed top-20 right-5 z-[100] space-y-2';
        document.body.appendChild(messagesContainer);
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-lg transform transition-all duration-300 ease-in-out';
    alertDiv.style.opacity = '0';
    alertDiv.style.transform = 'translateX(100%)';
    
    alertDiv.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <svg class="w-6 h-6 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="font-semibold mr-2">${message}</span>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-red-500 hover:text-red-700">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        </div>
    `;
    
    messagesContainer.appendChild(alertDiv);
    
    // Animate in
    setTimeout(() => {
        alertDiv.style.opacity = '1';
        alertDiv.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translateX(100%)';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

// Listen for HTMX events
document.body.addEventListener('htmx:afterRequest', function(evt) {
    console.log('HTMX request completed:', evt.detail);
});

document.body.addEventListener('htmx:responseError', function(evt) {
    console.log('HTMX error:', evt.detail);
    showErrorMessage('حدث خطأ في العملية. يرجى المحاولة مرة أخرى.');
});

// Remove server-side messages after showing them
document.addEventListener('DOMContentLoaded', function() {
    const serverMessages = document.querySelectorAll('#messages-container .alert');
    serverMessages.forEach(function(msg) {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => {
                msg.remove();
            }, 300);
        }, 5000);
    });
});