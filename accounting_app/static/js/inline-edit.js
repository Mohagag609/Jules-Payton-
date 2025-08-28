/**
 * Luxury Inline Editing System
 * Professional inline editing with HTMX integration
 */

class InlineEditManager {
    constructor() {
        this.activeEdits = new Map();
        this.init();
    }

    init() {
        // Initialize all inline editable elements
        document.querySelectorAll('[data-inline-edit]').forEach(element => {
            this.setupInlineEdit(element);
        });

        // Listen for HTMX events
        document.body.addEventListener('htmx:afterSwap', (event) => {
            // Re-initialize after HTMX updates
            event.target.querySelectorAll('[data-inline-edit]').forEach(element => {
                this.setupInlineEdit(element);
            });
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.cancelAllEdits();
            }
        });
    }

    setupInlineEdit(element) {
        // Skip if already initialized
        if (element.dataset.initialized) return;

        element.dataset.initialized = 'true';
        element.classList.add('inline-editable');

        // Add edit icon
        const editIcon = document.createElement('i');
        editIcon.className = 'bi bi-pencil-fill inline-edit-icon';
        element.appendChild(editIcon);

        // Double-click to edit
        element.addEventListener('dblclick', () => this.startEdit(element));
        
        // Click on icon to edit
        editIcon.addEventListener('click', (e) => {
            e.stopPropagation();
            this.startEdit(element);
        });
    }

    startEdit(element) {
        // Check if already editing
        if (this.activeEdits.has(element)) return;

        const originalValue = element.textContent.replace(/\s*$/, ''); // Trim trailing icon
        const fieldType = element.dataset.type || 'text';
        const fieldName = element.dataset.field;
        const url = element.dataset.url;

        // Create input based on type
        let input;
        switch (fieldType) {
            case 'textarea':
                input = document.createElement('textarea');
                input.className = 'form-control form-control-luxury inline-edit-input';
                input.rows = 3;
                break;
            case 'select':
                input = document.createElement('select');
                input.className = 'form-select form-select-luxury inline-edit-input';
                // Populate options from data attribute
                const options = JSON.parse(element.dataset.options || '[]');
                options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt.value;
                    option.textContent = opt.label;
                    if (opt.value === originalValue) option.selected = true;
                    input.appendChild(option);
                });
                break;
            case 'number':
                input = document.createElement('input');
                input.type = 'number';
                input.className = 'form-control form-control-luxury inline-edit-input';
                input.step = element.dataset.step || '1';
                break;
            default:
                input = document.createElement('input');
                input.type = 'text';
                input.className = 'form-control form-control-luxury inline-edit-input';
        }

        input.value = originalValue;

        // Store original state
        this.activeEdits.set(element, {
            originalValue,
            fieldName,
            url,
            fieldType
        });

        // Replace element content with input
        element.textContent = '';
        element.appendChild(input);

        // Add action buttons
        const actions = document.createElement('div');
        actions.className = 'inline-edit-actions';
        
        const saveBtn = document.createElement('button');
        saveBtn.className = 'btn-inline-save';
        saveBtn.innerHTML = '<i class="bi bi-check-lg"></i>';
        saveBtn.onclick = () => this.saveEdit(element, input);

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn-inline-cancel';
        cancelBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
        cancelBtn.onclick = () => this.cancelEdit(element);

        actions.appendChild(saveBtn);
        actions.appendChild(cancelBtn);
        element.appendChild(actions);

        // Focus and select
        input.focus();
        if (input.select) input.select();

        // Keyboard handling
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && fieldType !== 'textarea') {
                e.preventDefault();
                this.saveEdit(element, input);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                this.cancelEdit(element);
            }
        });

        // Click outside to cancel
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!element.contains(e.target)) {
                    this.cancelEdit(element);
                }
            }, { once: true });
        }, 100);
    }

    async saveEdit(element, input) {
        const editData = this.activeEdits.get(element);
        if (!editData) return;

        const newValue = input.value.trim();
        
        // Check if value changed
        if (newValue === editData.originalValue) {
            this.cancelEdit(element);
            return;
        }

        // Show loading state
        element.classList.add('saving');
        input.disabled = true;

        try {
            // Send update via HTMX
            const formData = new FormData();
            formData.append('field', editData.fieldName);
            formData.append('value', newValue);
            formData.append('csrfmiddlewaretoken', getCsrfToken());

            const response = await fetch(editData.url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (result.success) {
                // Update successful
                element.textContent = result.value || newValue;
                this.setupInlineEdit(element);
                this.activeEdits.delete(element);
                
                // Show success animation
                element.classList.add('edit-success');
                setTimeout(() => element.classList.remove('edit-success'), 1000);
                
                // Show toast
                showToast('تم الحفظ بنجاح', 'success');
            } else {
                throw new Error(result.error || 'خطأ في الحفظ');
            }
        } catch (error) {
            // Show error
            showToast(error.message, 'error');
            input.disabled = false;
            input.focus();
        } finally {
            element.classList.remove('saving');
        }
    }

    cancelEdit(element) {
        const editData = this.activeEdits.get(element);
        if (!editData) return;

        // Restore original value
        element.textContent = editData.originalValue;
        this.setupInlineEdit(element);
        this.activeEdits.delete(element);
    }

    cancelAllEdits() {
        this.activeEdits.forEach((data, element) => {
            this.cancelEdit(element);
        });
    }
}

// Helper function to get CSRF token
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) return token.value;
    
    // Try from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }
    return '';
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.inlineEditManager = new InlineEditManager();
});

// CSS for inline editing
const style = document.createElement('style');
style.textContent = `
/* Inline Edit Styles */
.inline-editable {
    position: relative;
    cursor: text;
    transition: all var(--transition-fast);
    padding-left: 1.5rem !important;
}

.inline-editable:hover {
    background: var(--bg-tertiary);
    border-radius: var(--radius-sm);
}

.inline-edit-icon {
    position: absolute;
    left: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.875rem;
    color: var(--text-muted);
    opacity: 0;
    transition: opacity var(--transition-fast);
}

.inline-editable:hover .inline-edit-icon {
    opacity: 1;
}

.inline-edit-input {
    animation: slideIn var(--transition-fast) ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-5px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.inline-edit-actions {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 0.25rem;
    display: flex;
    gap: 0.25rem;
    z-index: 10;
}

.btn-inline-save,
.btn-inline-cancel {
    width: 28px;
    height: 28px;
    border: none;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);
    font-size: 0.875rem;
}

.btn-inline-save {
    background: var(--success);
    color: white;
}

.btn-inline-save:hover {
    background: var(--success-light);
}

.btn-inline-cancel {
    background: var(--danger);
    color: white;
}

.btn-inline-cancel:hover {
    background: #ef4444;
}

.saving {
    position: relative;
    pointer-events: none;
}

.saving::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    margin: -10px 0 0 -10px;
    border: 2px solid var(--primary);
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

.edit-success {
    animation: successPulse 0.3s ease-out;
}

@keyframes successPulse {
    0% {
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
    }
    100% {
        box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
    }
}
`;
document.head.appendChild(style);