document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // Animate Balance
    const balanceElements = document.querySelectorAll('.balance');
    balanceElements.forEach(el => {
        const valueText = el.innerText.replace('R$', '').replace(',', '').trim();
        const value = parseFloat(valueText);
        // Simple scale animation on load
        el.style.transform = "scale(0.8)";
        el.style.opacity = "0";
        el.style.transition = "all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)";

        requestAnimationFrame(() => {
            el.style.transform = "scale(1)";
            el.style.opacity = "1";
        });
    });
});
