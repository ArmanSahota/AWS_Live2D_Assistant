// Subtitle display handler with comprehensive diagnostics

// Define the displaySubtitles function that's missing
window.displaySubtitles = function(text) {
    console.log('[SUBTITLE DEBUG] displaySubtitles function called with:', text);
    
    const messageElement = document.getElementById('message');
    if (!messageElement) {
        console.error('[SUBTITLE DEBUG] ERROR: Message element not found!');
        return;
    }
    
    // Update the text
    messageElement.textContent = text;
    
    // Ensure it's visible
    if (messageElement.classList.contains('hidden')) {
        console.log('[SUBTITLE DEBUG] Removing hidden class from message element');
        messageElement.classList.remove('hidden');
    }
    
    // Log the current state
    const computedStyle = window.getComputedStyle(messageElement);
    console.log('[SUBTITLE DEBUG] After displaySubtitles:');
    console.log('  - Text set to:', text);
    console.log('  - Display:', computedStyle.display);
    console.log('  - Visibility:', computedStyle.visibility);
    console.log('  - Is visible:', computedStyle.display !== 'none' && computedStyle.visibility !== 'hidden');
};

// Startup diagnostic
document.addEventListener('DOMContentLoaded', function() {
    console.log('[SUBTITLE DEBUG] ========== STARTUP DIAGNOSTIC ==========');
    
    // Check if message element exists
    const messageElement = document.getElementById('message');
    if (!messageElement) {
        console.error('[SUBTITLE DEBUG] CRITICAL: Message element not found in DOM!');
        return;
    }
    
    console.log('[SUBTITLE DEBUG] Message element found');
    
    // Check initial state
    const computedStyle = window.getComputedStyle(messageElement);
    console.log('[SUBTITLE DEBUG] Initial state:');
    console.log('  - ID:', messageElement.id);
    console.log('  - Classes:', messageElement.className);
    console.log('  - Text content:', messageElement.textContent);
    console.log('  - Display:', computedStyle.display);
    console.log('  - Visibility:', computedStyle.visibility);
    console.log('  - Opacity:', computedStyle.opacity);
    console.log('  - Position:', computedStyle.position);
    console.log('  - Z-index:', computedStyle.zIndex);
    console.log('  - Background:', computedStyle.backgroundColor);
    console.log('  - Color:', computedStyle.color);
    console.log('  - Hidden class present:', messageElement.classList.contains('hidden'));
    
    // Check parent
    const parent = messageElement.parentElement;
    if (parent) {
        const parentStyle = window.getComputedStyle(parent);
        console.log('[SUBTITLE DEBUG] Parent element:');
        console.log('  - ID:', parent.id);
        console.log('  - Display:', parentStyle.display);
        console.log('  - Visibility:', parentStyle.visibility);
    }
    
    // Check CSS rules
    console.log('[SUBTITLE DEBUG] Checking CSS rules for #message:');
    const styleSheets = document.styleSheets;
    for (let i = 0; i < styleSheets.length; i++) {
        try {
            const rules = styleSheets[i].cssRules || styleSheets[i].rules;
            for (let j = 0; j < rules.length; j++) {
                const rule = rules[j];
                if (rule.selectorText && rule.selectorText.includes('#message')) {
                    console.log('  - Rule:', rule.selectorText);
                    console.log('    Style:', rule.style.cssText);
                }
            }
        } catch (e) {
            // Skip cross-origin stylesheets
        }
    }
    
    // Test subtitle display
    console.log('[SUBTITLE DEBUG] Testing subtitle display...');
    window.displaySubtitles('Test subtitle on startup');
    
    // Check if subtitle toggle is properly initialized
    setTimeout(() => {
        console.log('[SUBTITLE DEBUG] Checking subtitle toggle state after 1 second...');
        const finalStyle = window.getComputedStyle(messageElement);
        console.log('  - Display:', finalStyle.display);
        console.log('  - Hidden class:', messageElement.classList.contains('hidden'));
        console.log('  - Text:', messageElement.textContent);
    }, 1000);
    
    console.log('[SUBTITLE DEBUG] ========== END STARTUP DIAGNOSTIC ==========');
});

// Monitor for dynamic changes to the message element
if (window.MutationObserver) {
    document.addEventListener('DOMContentLoaded', function() {
        const messageElement = document.getElementById('message');
        if (messageElement) {
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        console.log('[SUBTITLE DEBUG] Class changed on message element:');
                        console.log('  - Old classes:', mutation.oldValue);
                        console.log('  - New classes:', messageElement.className);
                        console.log('  - Hidden class present:', messageElement.classList.contains('hidden'));
                    } else if (mutation.type === 'childList' || mutation.type === 'characterData') {
                        console.log('[SUBTITLE DEBUG] Text content changed:', messageElement.textContent);
                    }
                });
            });
            
            observer.observe(messageElement, {
                attributes: true,
                attributeOldValue: true,
                characterData: true,
                childList: true,
                subtree: true
            });
            
            console.log('[SUBTITLE DEBUG] MutationObserver attached to message element');
        }
    });
}