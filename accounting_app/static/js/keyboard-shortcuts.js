/**
 * Keyboard Shortcuts Manager
 * Professional keyboard navigation system
 */

class KeyboardShortcutsManager {
    constructor() {
        this.shortcuts = new Map();
        this.enabled = true;
        this.init();
    }

    init() {
        // Register default shortcuts
        this.registerDefaults();

        // Listen for keydown events
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));

        // Show help on ?
        this.register('?', () => this.showHelp(), 'عرض المساعدة');
    }

    registerDefaults() {
        // Navigation
        this.register('g h', () => window.location.href = '/', 'الذهاب للرئيسية');
        this.register('g u', () => window.location.href = '/units/', 'الذهاب للوحدات');
        this.register('g c', () => window.location.href = '/customers/', 'الذهاب للعملاء');
        this.register('g o', () => window.location.href = '/contracts/', 'الذهاب للعقود');
        this.register('g i', () => window.location.href = '/installments/', 'الذهاب للأقساط');
        this.register('g r', () => window.location.href = '/reports/', 'الذهاب للتقارير');

        // Actions
        this.register('n', () => this.triggerNew(), 'جديد', 'ctrl');
        this.register('s', () => this.triggerSave(), 'حفظ', 'ctrl');
        this.register('/', () => this.focusSearch(), 'البحث');
        this.register('Escape', () => this.closeModal(), 'إغلاق النافذة');
        
        // Edit actions
        this.register('e', () => this.editCurrent(), 'تعديل');
        this.register('d', () => this.deleteCurrent(), 'حذف', 'shift');
        
        // Navigation within lists
        this.register('j', () => this.navigateNext(), 'التالي');
        this.register('k', () => this.navigatePrevious(), 'السابق');
        this.register('Enter', () => this.selectCurrent(), 'اختيار');
        
        // Undo/Redo
        this.register('z', () => this.undo(), 'تراجع', 'ctrl');
        this.register('z', () => this.redo(), 'إعادة', 'ctrl+shift');
        this.register('y', () => this.redo(), 'إعادة', 'ctrl');
    }

    register(key, callback, description = '', modifiers = '') {
        const shortcut = {
            key: this.normalizeKey(key),
            callback,
            description,
            modifiers: modifiers.split('+').filter(Boolean)
        };
        
        const id = this.getShortcutId(shortcut);
        this.shortcuts.set(id, shortcut);
    }

    normalizeKey(key) {
        // Handle special keys
        const keyMap = {
            'escape': 'Escape',
            'esc': 'Escape',
            'enter': 'Enter',
            'return': 'Enter',
            'space': ' ',
            'up': 'ArrowUp',
            'down': 'ArrowDown',
            'left': 'ArrowLeft',
            'right': 'ArrowRight'
        };
        
        return keyMap[key.toLowerCase()] || key;
    }

    getShortcutId(shortcut) {
        const parts = [...shortcut.modifiers.sort(), shortcut.key];
        return parts.join('+');
    }

    handleKeyDown(event) {
        if (!this.enabled) return;
        
        // Skip if in input/textarea (unless it's a global shortcut)
        const target = event.target;
        const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName);
        const isContentEditable = target.contentEditable === 'true';
        
        if (isInput || isContentEditable) {
            // Only allow certain shortcuts in inputs
            if (!['Escape', 'Enter'].includes(event.key) && !event.ctrlKey && !event.metaKey) {
                return;
            }
        }

        // Build shortcut ID from event
        const modifiers = [];
        if (event.ctrlKey) modifiers.push('ctrl');
        if (event.shiftKey) modifiers.push('shift');
        if (event.altKey) modifiers.push('alt');
        if (event.metaKey) modifiers.push('meta');
        
        const id = this.getShortcutId({
            key: event.key,
            modifiers
        });

        // Check for shortcut
        const shortcut = this.shortcuts.get(id);
        if (shortcut) {
            event.preventDefault();
            shortcut.callback(event);
        }

        // Handle sequences (like 'g h')
        this.handleSequence(event);
    }

    handleSequence(event) {
        // Simple sequence handling for 'g' shortcuts
        if (event.key === 'g' && !event.ctrlKey && !event.shiftKey) {
            this.waitingForSequence = true;
            event.preventDefault();
            
            // Show sequence indicator
            this.showSequenceIndicator();
            
            // Wait for next key
            const handler = (e) => {
                if (this.waitingForSequence) {
                    const sequenceId = `g ${e.key}`;
                    const shortcut = Array.from(this.shortcuts.entries())
                        .find(([id, s]) => s.key === sequenceId);
                    
                    if (shortcut) {
                        e.preventDefault();
                        shortcut[1].callback(e);
                    }
                    
                    this.waitingForSequence = false;
                    this.hideSequenceIndicator();
                    document.removeEventListener('keydown', handler);
                }
            };
            
            document.addEventListener('keydown', handler);
            
            // Timeout sequence
            setTimeout(() => {
                this.waitingForSequence = false;
                this.hideSequenceIndicator();
                document.removeEventListener('keydown', handler);
            }, 2000);
        }
    }

    showSequenceIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'sequence-indicator';
        indicator.className = 'sequence-indicator';
        indicator.textContent = 'g...';
        document.body.appendChild(indicator);
    }

    hideSequenceIndicator() {
        const indicator = document.getElementById('sequence-indicator');
        if (indicator) indicator.remove();
    }

    // Action methods
    triggerNew() {
        const newBtn = document.querySelector('[data-shortcut="new"]');
        if (newBtn) newBtn.click();
    }

    triggerSave() {
        const saveBtn = document.querySelector('[data-shortcut="save"]');
        if (saveBtn) saveBtn.click();
    }

    focusSearch() {
        const searchInput = document.querySelector('.search-input, [type="search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    closeModal() {
        if (typeof closeModal === 'function') {
            closeModal();
        }
    }

    editCurrent() {
        const editBtn = document.querySelector('[data-shortcut="edit"]');
        if (editBtn) editBtn.click();
    }

    deleteCurrent() {
        const deleteBtn = document.querySelector('[data-shortcut="delete"]');
        if (deleteBtn && confirm('هل أنت متأكد من الحذف؟')) {
            deleteBtn.click();
        }
    }

    navigateNext() {
        // Navigate in lists/tables
        const rows = document.querySelectorAll('tr[data-selectable], .list-item[data-selectable]');
        const current = document.querySelector('.selected');
        
        if (rows.length === 0) return;
        
        let nextIndex = 0;
        if (current) {
            const currentIndex = Array.from(rows).indexOf(current);
            nextIndex = Math.min(currentIndex + 1, rows.length - 1);
            current.classList.remove('selected');
        }
        
        rows[nextIndex].classList.add('selected');
        rows[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    navigatePrevious() {
        const rows = document.querySelectorAll('tr[data-selectable], .list-item[data-selectable]');
        const current = document.querySelector('.selected');
        
        if (rows.length === 0) return;
        
        let prevIndex = rows.length - 1;
        if (current) {
            const currentIndex = Array.from(rows).indexOf(current);
            prevIndex = Math.max(currentIndex - 1, 0);
            current.classList.remove('selected');
        }
        
        rows[prevIndex].classList.add('selected');
        rows[prevIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    selectCurrent() {
        const selected = document.querySelector('.selected');
        if (selected) {
            const link = selected.querySelector('a[href]');
            if (link) link.click();
        }
    }

    undo() {
        if (typeof htmx !== 'undefined') {
            htmx.ajax('POST', '/api/undo/');
        }
    }

    redo() {
        if (typeof htmx !== 'undefined') {
            htmx.ajax('POST', '/api/redo/');
        }
    }

    showHelp() {
        const shortcuts = Array.from(this.shortcuts.values())
            .filter(s => s.description)
            .sort((a, b) => a.description.localeCompare(b.description));

        const modal = document.createElement('div');
        modal.className = 'shortcuts-help-modal';
        modal.innerHTML = `
            <div class="shortcuts-help-content">
                <div class="shortcuts-help-header">
                    <h3>اختصارات لوحة المفاتيح</h3>
                    <button class="btn-close" onclick="this.closest('.shortcuts-help-modal').remove()">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="shortcuts-help-body">
                    <div class="shortcuts-grid">
                        ${shortcuts.map(s => `
                            <div class="shortcut-item">
                                <kbd>${this.formatShortcut(s)}</kbd>
                                <span>${s.description}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="shortcuts-help-footer">
                    <small>اضغط <kbd>Esc</kbd> للإغلاق</small>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on Esc or click outside
        const close = () => modal.remove();
        modal.addEventListener('click', (e) => {
            if (e.target === modal) close();
        });
    }

    formatShortcut(shortcut) {
        const parts = [];
        if (shortcut.modifiers.includes('ctrl')) parts.push('Ctrl');
        if (shortcut.modifiers.includes('shift')) parts.push('Shift');
        if (shortcut.modifiers.includes('alt')) parts.push('Alt');
        
        // Format key
        let key = shortcut.key;
        if (key === ' ') key = 'Space';
        if (key.startsWith('Arrow')) key = key.replace('Arrow', '');
        
        parts.push(key);
        return parts.join('+');
    }

    enable() {
        this.enabled = true;
    }

    disable() {
        this.enabled = false;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.keyboardShortcuts = new KeyboardShortcutsManager();
});

// CSS
const style = document.createElement('style');
style.textContent = `
/* Keyboard Shortcuts Styles */
.sequence-indicator {
    position: fixed;
    bottom: 2rem;
    left: 2rem;
    background: var(--primary);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-md);
    font-family: var(--font-mono);
    font-size: 1.125rem;
    box-shadow: var(--shadow-lg);
    z-index: 9999;
    animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.shortcuts-help-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    animation: fadeIn var(--transition-fast);
}

.shortcuts-help-content {
    background: var(--bg-secondary);
    border-radius: var(--radius-xl);
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-2xl);
}

.shortcuts-help-header {
    padding: var(--space-lg);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.shortcuts-help-header h3 {
    margin: 0;
    font-family: var(--font-display);
}

.shortcuts-help-body {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-lg);
}

.shortcuts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: var(--space-md);
}

.shortcut-item {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    padding: var(--space-sm);
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
}

.shortcut-item:hover {
    background: var(--bg-tertiary);
}

.shortcut-item kbd {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 0.25rem 0.5rem;
    font-family: var(--font-mono);
    font-size: 0.875rem;
    box-shadow: 0 2px 0 var(--border-color);
    white-space: nowrap;
}

.shortcut-item span {
    color: var(--text-secondary);
}

.shortcuts-help-footer {
    padding: var(--space-md) var(--space-lg);
    border-top: 1px solid var(--border-color);
    text-align: center;
    color: var(--text-muted);
}

/* Selectable rows */
tr[data-selectable],
.list-item[data-selectable] {
    cursor: pointer;
    transition: all var(--transition-fast);
}

tr[data-selectable]:hover,
.list-item[data-selectable]:hover {
    background: var(--bg-tertiary);
}

tr.selected,
.list-item.selected {
    background: var(--primary) !important;
    color: white;
}

tr.selected td,
.list-item.selected * {
    color: white !important;
}
`;
document.head.appendChild(style);