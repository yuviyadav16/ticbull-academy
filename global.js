// global.js - The Central Ecosystem Controller
const Global = {
    init() {
        this.applyTheme();
        this.attachGlobalListeners();
    },

    applyTheme() {
        const theme = localStorage.getItem('tb_theme') || 'dark';
        if (theme === 'light') document.body.classList.add('light-theme');
        else document.body.classList.remove('light-theme');
    },

    playSound() {
        if (localStorage.getItem('tb_sound') !== 'off') {
            const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3');
            audio.play().catch(() => {});
        }
    },

    attachGlobalListeners() {
        document.addEventListener('click', (e) => {
            // Har click par sound
            if(e.target.closest('button, .sub-card, .action-card, .btn-access, .option')) {
                this.playSound();
            }
        });
    }
};

// Har page load hote hi ye chal jayega
document.addEventListener('DOMContentLoaded', () => Global.init());
