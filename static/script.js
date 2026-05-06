const runBtn = document.getElementById('run-btn');
const queryInput = document.getElementById('query');

const cards = {
    baseline: {
        status: document.getElementById('baseline-status'),
        content: document.getElementById('baseline-content'),
        metrics: document.getElementById('baseline-metrics'),
        card: document.getElementById('baseline-card')
    },
    'multi-agent': {
        status: document.getElementById('multi-agent-status'),
        content: document.getElementById('multi-agent-content'),
        metrics: document.getElementById('multi-agent-metrics'),
        card: document.getElementById('multi-agent-card')
    }
};

async function runResearch(type) {
    const card = cards[type];
    const query = queryInput.value;

    card.status.textContent = 'Running...';
    card.status.className = 'status-badge running';
    card.card.classList.add('running');
    card.content.innerHTML = '<div class="loader">Thinking...</div>';

    try {
        const response = await fetch(`/api/research/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        if (!response.ok) throw new Error('API Error');

        const data = await response.json();
        
        card.status.textContent = 'Done';
        card.status.className = 'status-badge done';
        card.card.classList.remove('running');

        // Update metrics
        const m = data.metrics;
        card.metrics.innerHTML = `
            <div class="metric">Latency: <span class="val">${m.latency_seconds.toFixed(2)}s</span></div>
            <div class="metric">Tokens: <span class="val">${m.total_tokens || 0}</span></div>
            <div class="metric">Cost: <span class="val">$${(m.estimated_cost_usd || 0).toFixed(4)}</span></div>
        `;

        // Update content
        let html = `<div class="answer">${data.answer.replace(/\n/g, '<br>')}</div>`;
        if (data.sources) {
            html += '<div class="sources"><h3>Sources</h3><ul>';
            data.sources.forEach(s => {
                html += `<li><a href="${s.url}" target="_blank">${s.title}</a></li>`;
            });
            html += '</ul></div>';
        }
        card.content.innerHTML = html;

    } catch (err) {
        card.status.textContent = 'Error';
        card.status.className = 'status-badge error';
        card.content.innerHTML = `<p style="color: #ef4444">Error: ${err.message}</p>`;
    }
}

runBtn.addEventListener('click', () => {
    if (!queryInput.value) return;
    runResearch('baseline');
    runResearch('multi-agent');
});
