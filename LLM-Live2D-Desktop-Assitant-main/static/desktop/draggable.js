/**
 * Draggable VTuber Model Handler
 * Allows the Live2D model to be dragged anywhere on screen
 */

class VTuberDragHandler {
    constructor() {
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.init();
    }

    init() {
        // Create invisible drag handle at top of window
        const dragArea = document.createElement('div');
        dragArea.id = 'drag-area';
        dragArea.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 80px;
            cursor: move;
            z-index: 9999;
            background: transparent;
            -webkit-app-region: drag;
        `;
        
        // Add visual feedback on hover (optional)
        dragArea.addEventListener('mouseenter', () => {
            dragArea.style.background = 'rgba(255, 255, 255, 0.05)';
        });
        
        dragArea.addEventListener('mouseleave', () => {
            dragArea.style.background = 'transparent';
        });
        
        document.body.appendChild(dragArea);
        
        // Double-click to reset position
        dragArea.addEventListener('dblclick', () => {
            this.resetPosition();
        });
        
        // Right-click for context menu
        dragArea.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showContextMenu(e.clientX, e.clientY);
        });
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+R to reset position
            if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                this.resetPosition();
            }
            // Ctrl+Shift+L to lock/unlock position
            if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                this.toggleLock();
            }
        });
        
        console.log('VTuber drag handler initialized');
    }
    
    resetPosition() {
        // Reset to default position (bottom right)
        if (window.electronAPI && window.electronAPI.resetPosition) {
            window.electronAPI.resetPosition();
        } else {
            // Fallback: Send message to main process
            if (window.electronAPI && window.electronAPI.send) {
                window.electronAPI.send('reset-position');
            }
        }
        console.log('Position reset requested');
    }
    
    toggleLock() {
        // Toggle position lock
        const isLocked = document.body.dataset.positionLocked === 'true';
        document.body.dataset.positionLocked = !isLocked;
        
        const dragArea = document.getElementById('drag-area');
        if (dragArea) {
            dragArea.style.display = isLocked ? 'block' : 'none';
            console.log(`Position ${isLocked ? 'unlocked' : 'locked'}`);
        }
    }
    
    showContextMenu(x, y) {
        // Create simple context menu
        const existingMenu = document.getElementById('vtuber-context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }
        
        const menu = document.createElement('div');
        menu.id = 'vtuber-context-menu';
        menu.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            background: rgba(30, 30, 30, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            padding: 4px;
            z-index: 10000;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        `;
        
        const menuItems = [
            { label: 'Reset Position', action: () => this.resetPosition() },
            { label: 'Lock Position', action: () => this.toggleLock() },
            { separator: true },
            { label: 'Small Size', action: () => this.setSize('small') },
            { label: 'Medium Size', action: () => this.setSize('medium') },
            { label: 'Large Size', action: () => this.setSize('large') },
            { separator: true },
            { label: 'Always on Top', action: () => this.toggleAlwaysOnTop() },
            { label: 'Minimize', action: () => this.minimize() }
        ];
        
        menuItems.forEach(item => {
            if (item.separator) {
                const separator = document.createElement('hr');
                separator.style.cssText = 'margin: 4px 0; border: none; border-top: 1px solid rgba(255, 255, 255, 0.1);';
                menu.appendChild(separator);
            } else {
                const menuItem = document.createElement('div');
                menuItem.textContent = item.label;
                menuItem.style.cssText = `
                    padding: 8px 16px;
                    color: white;
                    cursor: pointer;
                    font-size: 13px;
                    font-family: Arial, sans-serif;
                    transition: background 0.2s;
                `;
                menuItem.addEventListener('mouseenter', () => {
                    menuItem.style.background = 'rgba(255, 255, 255, 0.1)';
                });
                menuItem.addEventListener('mouseleave', () => {
                    menuItem.style.background = 'transparent';
                });
                menuItem.addEventListener('click', () => {
                    item.action();
                    menu.remove();
                });
                menu.appendChild(menuItem);
            }
        });
        
        document.body.appendChild(menu);
        
        // Remove menu when clicking elsewhere
        setTimeout(() => {
            document.addEventListener('click', function removeMenu() {
                menu.remove();
                document.removeEventListener('click', removeMenu);
            }, { once: true });
        }, 100);
    }
    
    setSize(size) {
        const sizes = {
            small: { width: 250, height: 350 },
            medium: { width: 350, height: 500 },
            large: { width: 450, height: 650 }
        };
        
        if (window.electronAPI && window.electronAPI.setSize) {
            window.electronAPI.setSize(sizes[size]);
        }
        console.log(`Size set to ${size}`);
    }
    
    toggleAlwaysOnTop() {
        if (window.electronAPI && window.electronAPI.toggleAlwaysOnTop) {
            window.electronAPI.toggleAlwaysOnTop();
        }
    }
    
    minimize() {
        if (window.electronAPI && window.electronAPI.minimize) {
            window.electronAPI.minimize();
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.vtuberDragHandler = new VTuberDragHandler();
    });
} else {
    window.vtuberDragHandler = new VTuberDragHandler();
}

// Add minimal CSS for smooth operation
const style = document.createElement('style');
style.textContent = `
    body {
        -webkit-user-select: none;
        user-select: none;
    }
    
    #drag-area {
        transition: background 0.2s;
    }
    
    #vtuber-context-menu {
        animation: fadeIn 0.2s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

console.log('Draggable VTuber feature loaded successfully!');