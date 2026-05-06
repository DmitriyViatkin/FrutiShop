// HTMX helpers
document.body.addEventListener('htmx:afterRequest', function(e) {
    if (e.detail.target && e.detail.target.id === 'declarations-count') {
        document.getElementById('file-input').value = '';
    }
    if (e.detail.failed) showToast('Ошибка: ' + e.detail.xhr.status, 'error');
});

document.body.addEventListener('htmx:beforeProcessNode', function(e) {
    if (!document.body.contains(e.detail.elt)) {
        e.preventDefault();
    }
});

document.body.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-CSRFToken'] = window.CSRF_TOKEN;
});


// Validation
function validateAmount() {
    const val = parseFloat(document.getElementById('amount-input').value);
    if (!val || val <= 0) {
        showToast('Введите корректную сумму', 'error');
        return false;
    }
    return true;
}


// Toast
function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}


// 💥 FIX 1: нормальный WebSocket helper (ВАЖНО)
function wsUrl(path) {
    return (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + path;
}


// ===================== LOG WS =====================
let logWs;

function connectLog() {
    logWs = new WebSocket(wsUrl('/ws/fruits/'));

    logWs.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.toast) {
            showToast(data.toast, data.toast_type || 'info');
            return;
        }

        if (data.progress !== undefined) {
            const progressValue = data.progress;

            const auditBar = document.getElementById('bank-progress');
            const auditLabel = document.getElementById('bank-progress-label');
            const auditWrapper = document.getElementById('audit-progress');

            if (auditWrapper) auditWrapper.classList.add('active');
            if (auditBar) auditBar.style.width = progressValue + '%';
            if (auditLabel) auditLabel.textContent = progressValue + '%';

            if (progressValue >= 100) {
                setTimeout(() => {
                    if (auditBar) auditBar.style.width = '0%';
                    if (auditLabel) auditLabel.textContent = '0%';
                    if (auditWrapper) auditWrapper.classList.remove('active');
                }, 2000);
            }
            return;
        }

        if (data.message) {
            const el = document.createElement('div');
            const isError = data.error === true;

            el.className = 'log-entry ' + (isError ? 'log-error' : 'log-success');
            el.textContent = data.message;

            document.getElementById('log-list').prepend(el);

            const bankBalance = document.getElementById('bank-balance');

            if (isError) {
                bankBalance.style.color = 'var(--red)';
                bankBalance.style.background = 'var(--red-bg)';
                bankBalance.style.borderColor = 'var(--red)';

                setTimeout(() => {
                    bankBalance.style.color = 'var(--accent)';
                    bankBalance.style.background = 'var(--orange-bg)';
                    bankBalance.style.borderColor = 'var(--border)';
                }, 3000);

                showToast(data.message, 'error');
            }
        }

        if (data.balance != null) {
            document.getElementById('bank-balance').textContent = data.balance + ' USD';
        }
    };

    logWs.onclose = () => setTimeout(connectLog, 3000);
    logWs.onerror = () => logWs.close();
}


// ===================== CHAT WS =====================
let chatWs;

function connectChat() {
    chatWs = new WebSocket(wsUrl('/ws/chat/'));

    chatWs.onmessage = function(e) {
        const data = JSON.parse(e.data);

        const msgs = document.getElementById('chat-messages');
        const el = document.createElement('div');
        el.className = 'chat-msg';

        const time = document.createElement('span');
        time.className = 'time';
        time.textContent = data.time;

        const name = document.createElement('span');
        name.className = 'name';
        name.textContent = data.username + ':';

        const text = document.createTextNode(' ' + data.message);

        el.appendChild(time);
        el.appendChild(name);
        el.appendChild(text);

        msgs.appendChild(el);
        msgs.scrollTop = msgs.scrollHeight;
    };

    chatWs.onclose = () => setTimeout(connectChat, 3000);
    chatWs.onerror = () => chatWs.close();
}


// ===================== CHAT SEND =====================
function sendChat() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();

    if (!chatWs || chatWs.readyState !== WebSocket.OPEN) {
        showToast('Чат не подключен...', 'error');
        return;
    }

    if (!msg) {
        showToast('Введите сообщение', 'error');
        return;
    }

    if (msg.length > 500) {
        showToast('Слишком длинное сообщение (макс. 500)', 'error');
        return;
    }

    chatWs.send(JSON.stringify({ message: msg }));
    input.value = '';
}


// Enter send
document.getElementById('chat-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') sendChat();
});


// 🚀 INIT (ВАЖНО)
document.addEventListener('DOMContentLoaded', () => {
    connectLog();
    connectChat();
});