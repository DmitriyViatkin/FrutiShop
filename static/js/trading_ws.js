// ── HTMX helpers ──────────────────────────────────────
document.body.addEventListener('htmx:afterRequest', function(e) {
    if (e.detail.target && e.detail.target.id === 'declarations-count') {
        document.getElementById('file-input').value = '';
    }
    if (e.detail.failed) showToast('Помилка: ' + e.detail.xhr.status, 'error');
});

document.body.addEventListener('htmx:beforeProcessNode', function(e) {
    if (!document.body.contains(e.detail.elt)) {
        e.preventDefault();
    }
});

document.body.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-CSRFToken'] = window.CSRF_TOKEN;
});

// ── Валидация суммы ────────────────────────────────────
function validateAmount() {
    const val = parseFloat(document.getElementById('amount-input').value);
    if (!val || val <= 0) {
        showToast('Введите положительную сумму', 'error');
        return false;
    }
    return true;
}

// ── Toast ──────────────────────────────────────────────
function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ── WebSocket protocol helper ──────────────────────────
const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';

// ── Fruits WebSocket ───────────────────────────────────
let logWs;

function connectLog() {
    logWs = new WebSocket(`${wsProto}://${location.host}/ws/fruits/`);

    logWs.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.toast) {
            showToast(data.toast, data.toast_type || 'info');
            return;
        }

        // Прогресс аудита
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

        // Лог-сообщение
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

    logWs.onclose = function() {
        setTimeout(connectLog, 3000);
    };

    logWs.onerror = function() {
        logWs.close();
    };
}

connectLog();

// ── Chat WebSocket ─────────────────────────────────────
let chatWs;

function connectChat() {
    chatWs = new WebSocket(`${wsProto}://${location.host}/ws/chat/`);

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

    chatWs.onclose = function() {
        setTimeout(connectChat, 3000);
    };

    chatWs.onerror = function() {
        chatWs.close();
    };
}

connectChat();

// ── Chat send ──────────────────────────────────────────
function sendChat() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();

    if (!chatWs || chatWs.readyState !== WebSocket.OPEN) {
        showToast('Нет соединения, переподключение...', 'error');
        return;
    }
    if (!msg) {
        showToast('Сообщение не может быть пустым', 'error');
        return;
    }
    if (msg.length > 500) {
        showToast('Сообщение слишком длинное (макс. 500)', 'error');
        return;
    }

    chatWs.send(JSON.stringify({ message: msg }));
    input.value = '';
}

document.getElementById('chat-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') sendChat();
});