// Global success message function
function showSuccessMessage(message) {
    const messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) {
        console.error('Messages container not found');
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg relative shadow-lg transform transition-all duration-300 ease-in-out';
    alertDiv.style.opacity = '0';
    alertDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span class="font-semibold">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="mr-auto">
                <svg class="w-4 h-4 text-green-500 hover:text-green-700 cursor-pointer" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        </div>
    `;
    
    messagesContainer.appendChild(alertDiv);
    
    // Animate in
    setTimeout(() => {
        alertDiv.style.opacity = '1';
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

// Global error message function
function showErrorMessage(message) {
    const messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) {
        console.error('Messages container not found');
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative shadow-lg transform transition-all duration-300 ease-in-out';
    alertDiv.style.opacity = '0';
    alertDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span class="font-semibold">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="mr-auto">
                <svg class="w-4 h-4 text-red-500 hover:text-red-700 cursor-pointer" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        </div>
    `;
    
    messagesContainer.appendChild(alertDiv);
    
    // Animate in
    setTimeout(() => {
        alertDiv.style.opacity = '1';
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

// Listen for HTMX errors
document.body.addEventListener('htmx:responseError', function(evt) {
    showErrorMessage('حدث خطأ في العملية. يرجى المحاولة مرة أخرى.');
});

// Listen for HTMX success with validation errors
document.body.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.xhr.status >= 400 && evt.detail.xhr.status < 500) {
        showErrorMessage('يرجى التحقق من البيانات المدخلة.');
    }
});