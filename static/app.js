document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation Tabs ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabPages = document.querySelectorAll('.tab-page');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');

            navItems.forEach(nav => nav.classList.remove('active'));
            tabPages.forEach(page => page.classList.remove('active'));

            item.classList.add('active');
            const activePage = document.getElementById(targetTab);
            if (activePage) activePage.classList.add('active');

            if (targetTab === 'tab-graph') loadKnowledgeGraph();
            if (targetTab === 'tab-vault') loadVaultNotes();
        });
    });

    // --- Query Assistant ---
    const queryInput = document.getElementById('query-input');
    const btnSubmitQuery = document.getElementById('btn-submit-query');
    const queryLoading = document.getElementById('query-loading');
    const responseCard = document.getElementById('query-response-card');
    const responseContent = document.getElementById('response-content');

    btnSubmitQuery.addEventListener('click', async () => {
        const prompt = queryInput.value.trim();
        if (!prompt) return;

        queryLoading.classList.remove('hidden');
        responseCard.classList.add('hidden');
        btnSubmitQuery.disabled = true;

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });

            const data = await res.json();
            if (res.ok && data.status === 'success') {
                responseContent.innerHTML = marked.parse(data.answer);
                
                // Render KaTeX formulas
                renderMathInElement(responseContent, {
                    delimiters: [
                        { left: '$$', right: '$$', display: true },
                        { left: '$', right: '$', display: false },
                        { left: '\\(', right: '\\)', display: false },
                        { left: '\\[', right: '\\]', display: true }
                    ],
                    throwOnError: false
                });

                responseCard.classList.remove('hidden');
            } else {
                alert('Query Error: ' + (data.detail || 'Failed to generate answer.'));
            }
        } catch (err) {
            alert('Server connection error: ' + err.message);
        } finally {
            queryLoading.classList.add('hidden');
            btnSubmitQuery.disabled = false;
        }
    });

    // --- PDF Ingestion Drop Zone ---
    const dropZone = document.getElementById('drop-zone');
    const pdfFileInput = document.getElementById('pdf-file-input');
    const selectedFileInfo = document.getElementById('selected-file-info');
    const selectedFileName = document.getElementById('selected-file-name');
    const btnClearFile = document.getElementById('btn-clear-file');
    const btnStartIngest = document.getElementById('btn-start-ingest');
    const ingestLoading = document.getElementById('ingest-loading');
    const ingestResult = document.getElementById('ingest-result');
    let currentPdfFile = null;

    dropZone.addEventListener('click', () => pdfFileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    pdfFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (!file.name.endsWith('.pdf')) {
            alert('Please select a PDF file.');
            return;
        }
        currentPdfFile = file;
        selectedFileName.textContent = file.name;
        selectedFileInfo.classList.remove('hidden');
    }

    btnClearFile.addEventListener('click', () => {
        currentPdfFile = null;
        pdfFileInput.value = '';
        selectedFileInfo.classList.add('hidden');
    });

    btnStartIngest.addEventListener('click', async () => {
        if (!currentPdfFile) {
            alert('Please select or drop a PDF file first.');
            return;
        }

        const courseName = document.getElementById('course-name-input').value.trim() || 'General Math';

        const formData = new FormData();
        formData.append('file', currentPdfFile);
        formData.append('course', courseName);

        ingestLoading.classList.remove('hidden');
        ingestResult.classList.add('hidden');
        btnStartIngest.disabled = true;

        try {
            const res = await fetch('/api/ingest', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (res.ok && data.status === 'success') {
                ingestResult.className = 'alert-box success';
                ingestResult.innerHTML = `<strong>Successfully Ingested!</strong><br>Note saved in Obsidian Vault: <code>${data.note_path}</code>`;
                ingestResult.classList.remove('hidden');
            } else {
                ingestResult.className = 'alert-box error';
                ingestResult.innerHTML = `<strong>Ingestion Failed:</strong> ${data.detail || 'Unknown error'}`;
                ingestResult.classList.remove('hidden');
            }
        } catch (err) {
            ingestResult.className = 'alert-box error';
            ingestResult.innerHTML = `<strong>Server Connection Error:</strong> ${err.message}`;
            ingestResult.classList.remove('hidden');
        } finally {
            ingestLoading.classList.add('hidden');
            btnStartIngest.disabled = false;
        }
    });

    // --- Knowledge Graph Visualization ---
    const btnRefreshGraph = document.getElementById('btn-refresh-graph');
    if (btnRefreshGraph) btnRefreshGraph.addEventListener('click', loadKnowledgeGraph);

    async function loadKnowledgeGraph() {
        const container = document.getElementById('vis-graph-canvas');
        if (!container) return;

        try {
            const res = await fetch('/api/graph');
            const data = await res.json();

            const nodesArray = data.nodes.map(n => ({
                id: n.id,
                label: n.label,
                color: n.type === 'Note' ? '#6366f1' : '#ec4899',
                font: { color: '#ffffff', face: 'Inter' },
                shape: 'dot',
                size: n.type === 'Note' ? 22 : 16
            }));

            const edgesArray = data.edges.map(e => ({
                from: e.from,
                to: e.to,
                color: { color: '#3b82f6', opacity: 0.6 },
                arrows: 'to'
            }));

            const networkData = {
                nodes: new vis.DataSet(nodesArray),
                edges: new vis.DataSet(edgesArray)
            };

            const options = {
                physics: {
                    barnesHut: { gravitationalConstant: -3000, centralGravity: 0.3, springLength: 95 }
                },
                interaction: { hover: true, tooltipDelay: 200 }
            };

            new vis.Network(container, networkData, options);

        } catch (err) {
            console.error('Failed to load graph:', err);
        }
    }

    // --- Vault Explorer ---
    const btnRefreshVault = document.getElementById('btn-refresh-vault');
    if (btnRefreshVault) btnRefreshVault.addEventListener('click', loadVaultNotes);

    async function loadVaultNotes() {
        const container = document.getElementById('vault-list-container');
        if (!container) return;

        try {
            const res = await fetch('/api/vault');
            const data = await res.json();

            container.innerHTML = '';
            const vault = data.vault || {};

            if (Object.keys(vault).length === 0) {
                container.innerHTML = '<p style="color: var(--text-muted);">No notes found in vault yet. Ingest a PDF to get started!</p>';
                return;
            }

            for (const [course, notes] of Object.entries(vault)) {
                const card = document.createElement('div');
                card.className = 'course-card';
                card.innerHTML = `
                    <h3>📁 ${course}</h3>
                    <div class="note-list">
                        ${notes.map(n => `<div class="note-item">📄 <span>${n.title}.md</span></div>`).join('')}
                    </div>
                `;
                container.appendChild(card);
            }
        } catch (err) {
            console.error('Failed to load vault notes:', err);
        }
    }
});

// Helper for Quick Prompt buttons
function setQueryPrompt(text) {
    const input = document.getElementById('query-input');
    if (input) input.value = text;
}

function copyResponseText() {
    const content = document.getElementById('response-content');
    if (content) {
        navigator.clipboard.writeText(content.innerText);
        alert('Response copied to clipboard!');
    }
}
