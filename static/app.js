document.addEventListener('DOMContentLoaded', () => {
    // --- Initial Health Check & Course List ---
    checkOllamaHealth();
    loadCourseDropdowns();

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
            if (targetTab === 'tab-backend') loadBackendCatalog();
            if (targetTab === 'tab-settings') loadSystemSettings();
        });
    });

    // =====================================================================
    // Ollama Health Check
    // =====================================================================
    async function checkOllamaHealth() {
        const dot = document.getElementById('ollama-status-dot');
        const label = document.getElementById('ollama-status-label');
        if (!dot || !label) return;

        try {
            const res = await fetch('/api/health/ollama?t=' + Date.now(), { cache: 'no-store' });
            const data = await res.json();
            if (data.service_online && data.model_available) {
                dot.className = 'status-dot online';
                label.textContent = `Local VLM Ready (${data.target_model})`;
            } else if (data.service_online) {
                dot.className = 'status-dot offline';
                label.textContent = `Ollama Online (${data.target_model} missing)`;
            } else {
                dot.className = 'status-dot offline';
                label.textContent = 'Ollama Service Offline';
            }
        } catch (e) {
            dot.className = 'status-dot offline';
            label.textContent = 'Ollama Offline';
        }
    }

    // =====================================================================
    // Course Dropdowns (shared across tabs)
    // =====================================================================
    async function loadCourseDropdowns() {
        try {
            const res = await fetch('/api/courses');
            const data = await res.json();
            const courses = data.courses || [];

            const targets = ['query-course', 'graph-course-filter'];
            targets.forEach(id => {
                const sel = document.getElementById(id);
                if (!sel) return;
                // Keep the first "All Courses" option
                while (sel.options.length > 1) sel.remove(1);
                courses.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c;
                    opt.textContent = c;
                    sel.appendChild(opt);
                });
            });
        } catch (e) {
            console.warn('Could not load courses:', e);
        }
    }

    // =====================================================================
    // Slider Value Displays
    // =====================================================================
    const topkSlider = document.getElementById('query-topk');
    const topkVal   = document.getElementById('query-topk-val');
    const tempSlider = document.getElementById('query-temp');
    const tempVal   = document.getElementById('query-temp-val');
    const dpiSlider = document.getElementById('ingest-dpi');
    const dpiVal    = document.getElementById('ingest-dpi-val');

    if (topkSlider && topkVal) {
        topkSlider.addEventListener('input', () => { topkVal.textContent = topkSlider.value; });
    }
    if (tempSlider && tempVal) {
        tempSlider.addEventListener('input', () => {
            tempVal.textContent = (parseInt(tempSlider.value) / 100).toFixed(1);
        });
    }
    if (dpiSlider && dpiVal) {
        dpiSlider.addEventListener('input', () => { dpiVal.textContent = dpiSlider.value; });
    }

    // Toggle label updates
    const graphToggle = document.getElementById('query-use-graph');
    const graphLabel  = document.getElementById('graph-toggle-label');
    if (graphToggle && graphLabel) {
        graphToggle.addEventListener('change', () => {
            graphLabel.textContent = graphToggle.checked ? 'Enabled' : 'Disabled';
        });
    }
    const autoIdxToggle = document.getElementById('ingest-autoindex');
    const autoIdxLabel  = document.getElementById('autoindex-toggle-label');
    if (autoIdxToggle && autoIdxLabel) {
        autoIdxToggle.addEventListener('change', () => {
            autoIdxLabel.textContent = autoIdxToggle.checked ? 'Enabled' : 'Disabled';
        });
    }

    // =====================================================================
    // Query Assistant
    // =====================================================================
    const queryInput      = document.getElementById('query-input');
    const btnSubmitQuery  = document.getElementById('btn-submit-query');
    const queryLoading    = document.getElementById('query-loading');
    const responseCard    = document.getElementById('query-response-card');
    const responseContent = document.getElementById('response-content');

    btnSubmitQuery.addEventListener('click', async () => {
        const prompt = queryInput.value.trim();
        if (!prompt) return;

        queryLoading.classList.remove('hidden');
        responseCard.classList.add('hidden');
        btnSubmitQuery.disabled = true;

        // Gather retrieval settings
        const topK        = parseInt(document.getElementById('query-topk')?.value || '5');
        const temperature = parseInt(document.getElementById('query-temp')?.value || '30') / 100;
        const course      = document.getElementById('query-course')?.value || '';
        const useGraph    = document.getElementById('query-use-graph')?.checked ?? true;

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    top_k: topK,
                    temperature,
                    course: course || null,
                    use_graph: useGraph
                })
            });

            const data = await res.json();
            if (res.ok && data.status === 'success') {
                responseContent.innerHTML = marked.parse(data.answer);
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

    // =====================================================================
    // PDF Ingestion
    // =====================================================================
    const dropZone         = document.getElementById('drop-zone');
    const pdfFileInput     = document.getElementById('pdf-file-input');
    const selectedFileInfo = document.getElementById('selected-file-info');
    const selectedFileName = document.getElementById('selected-file-name');
    const btnClearFile     = document.getElementById('btn-clear-file');
    const btnStartIngest   = document.getElementById('btn-start-ingest');
    const ingestLoading    = document.getElementById('ingest-loading');
    const ingestResult     = document.getElementById('ingest-result');
    const ingestPreviewCard   = document.getElementById('ingest-preview-card');
    const previewMarkdownBody = document.getElementById('preview-markdown-body');
    const previewPathBadge    = document.getElementById('preview-path-badge');

    let currentPdfFile = null;

    dropZone.addEventListener('click', () => pdfFileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) handleFileSelect(e.dataTransfer.files[0]);
    });
    pdfFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
    });

    function handleFileSelect(file) {
        if (!file.name.endsWith('.pdf')) { alert('Please select a PDF file.'); return; }
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
        if (!currentPdfFile) { alert('Please select or drop a PDF file first.'); return; }

        const courseName = document.getElementById('course-name-input').value.trim() || 'Handwritten Coursework';
        const ocrMode    = document.getElementById('ocr-mode-select')?.value || 'local_handwriting';
        const dpi        = parseInt(document.getElementById('ingest-dpi')?.value || '200');
        const autoIndex  = document.getElementById('ingest-autoindex')?.checked ?? true;

        const formData = new FormData();
        formData.append('file', currentPdfFile);
        formData.append('course', courseName);
        formData.append('ocr_mode', ocrMode);
        formData.append('dpi', dpi.toString());
        formData.append('auto_index', autoIndex.toString());

        ingestLoading.classList.remove('hidden');
        ingestResult.classList.add('hidden');
        ingestPreviewCard.classList.add('hidden');
        btnStartIngest.disabled = true;

        try {
            const res = await fetch('/api/ingest', { method: 'POST', body: formData });
            const data = await res.json();

            if (res.ok && data.status === 'success') {
                let successMsg = `<strong>Successfully Ingested!</strong><br>Note saved: <code>${data.note_path}</code>`;
                if (data.graph_indexed) successMsg += '<br>✅ Knowledge graph updated';
                if (data.vector_chunks > 0) successMsg += `<br>✅ ${data.vector_chunks} chunks indexed in vector store`;
                ingestResult.className = 'alert-box success';
                ingestResult.innerHTML = successMsg;
                ingestResult.classList.remove('hidden');

                if (data.content) {
                    previewMarkdownBody.innerHTML = marked.parse(data.content);
                    previewPathBadge.textContent = `${courseName} Note Saved`;
                    renderMathInElement(previewMarkdownBody, {
                        delimiters: [
                            { left: '$$', right: '$$', display: true },
                            { left: '$', right: '$', display: false },
                            { left: '\\(', right: '\\)', display: false },
                            { left: '\\[', right: '\\]', display: true }
                        ],
                        throwOnError: false
                    });
                    ingestPreviewCard.classList.remove('hidden');
                }

                // Refresh course dropdowns
                loadCourseDropdowns();
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

    // =====================================================================
    // Knowledge Graph Visualization (with filters)
    // =====================================================================
    const btnRefreshGraph = document.getElementById('btn-refresh-graph');
    if (btnRefreshGraph) btnRefreshGraph.addEventListener('click', loadKnowledgeGraph);

    // Attach filter listeners
    document.querySelectorAll('.graph-type-filter').forEach(cb => {
        cb.addEventListener('change', () => { if (currentGraphData) renderGraphWithFilters(); });
    });
    const graphCourseFilter = document.getElementById('graph-course-filter');
    if (graphCourseFilter) {
        graphCourseFilter.addEventListener('change', () => { if (currentGraphData) renderGraphWithFilters(); });
    }

    let currentGraphData = null;
    let graphNetwork = null;

    async function loadKnowledgeGraph() {
        const container = document.getElementById('vis-graph-canvas');
        if (!container) return;

        try {
            const res = await fetch('/api/graph');
            currentGraphData = await res.json();
            renderGraphWithFilters();
        } catch (err) {
            console.error('Failed to load graph:', err);
        }
    }

    function renderGraphWithFilters() {
        const container = document.getElementById('vis-graph-canvas');
        if (!container || !currentGraphData) return;

        // Gather active type filters
        const activeTypes = new Set();
        document.querySelectorAll('.graph-type-filter:checked').forEach(cb => activeTypes.add(cb.value));
        const courseFilter = document.getElementById('graph-course-filter')?.value || '';

        // Filter nodes
        const filteredNodes = currentGraphData.nodes.filter(n => {
            if (!activeTypes.has(n.type || 'Concept')) return false;
            if (courseFilter && n.group !== courseFilter && n.group !== 'Concept') return false;
            return true;
        });
        const nodeIds = new Set(filteredNodes.map(n => n.id));

        // Filter edges to only include visible nodes
        const filteredEdges = currentGraphData.edges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));

        const domainColors = {
            'Differential Equations': '#8b5cf6',
            'Calculus':               '#10b981',
            'Linear Algebra':         '#3b82f6',
            'Handwritten Coursework': '#f43f5e',
            'General':                '#6366f1',
        };

        const roleBorderColors = {
            'Theorem':    '#f59e0b',
            'Definition': '#10b981',
            'Formula':    '#06b6d4',
            'Proof':      '#ec4899',
            'Lemma':      '#eab308',
            'Note':       '#818cf8',
            'Concept':    '#94a3b8',
        };

        const nodesArray = filteredNodes.map(n => {
            const domain = (n.taxonomy && n.taxonomy.domain) ? n.taxonomy.domain : 'Differential Equations';
            const role = n.type || n.entity_type || 'Concept';
            const fillColor = domainColors[domain] || '#6366f1';
            const borderColor = roleBorderColors[role] || '#94a3b8';
            const borderWidth = role === 'Theorem' ? 4 : (role === 'Definition' ? 3 : 2);

            return {
                id: n.id,
                label: n.label || n.name || n.id,
                color: {
                    background: fillColor,
                    border: borderColor,
                    highlight: { background: fillColor, border: '#ffffff' }
                },
                borderWidth: borderWidth,
                font: { color: '#ffffff', face: 'Inter', size: 13 },
                shape: 'dot',
                size: role === 'Note' ? 24 : 17,
                title: `[${role}] ${n.label || n.id}\nDomain: ${domain}`
            };
        });

        const edgesArray = filteredEdges.map(e => ({
            from: e.from,
            to: e.to,
            label: e.label !== 'links_to' ? e.label : undefined,
            color: { color: '#3b82f6', opacity: 0.5 },
            arrows: 'to',
            font: { color: '#9ca3af', size: 10, face: 'Inter', strokeWidth: 0 }
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

        graphNetwork = new vis.Network(container, networkData, options);
    }

    // =====================================================================
    // Vault Explorer
    // =====================================================================
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

    // =====================================================================
    // Settings Tab
    // =====================================================================
    const btnRebuildGraph   = document.getElementById('btn-rebuild-graph');
    const btnRebuildVectors = document.getElementById('btn-rebuild-vectors');
    const rebuildResult     = document.getElementById('rebuild-result');

    async function loadSystemSettings() {
        try {
            const res = await fetch('/api/settings');
            const data = await res.json();

            setText('stat-gemini-model', data.gemini_model || '—');
            setText('stat-embed-model', data.embed_model || '—');
            setText('stat-vector-chunks', data.vector_store?.total_chunks ?? '—');
            setText('stat-graph-nodes', data.graph?.total_nodes ?? '—');
            setText('stat-graph-edges', data.graph?.total_edges ?? '—');

            const courses = data.vector_store?.courses || [];
            setText('stat-courses', courses.length > 0 ? courses.join(', ') : 'None');
        } catch (e) {
            console.warn('Could not load settings:', e);
        }
    }

    function setText(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    if (btnRebuildGraph) {
        btnRebuildGraph.addEventListener('click', async () => {
            btnRebuildGraph.disabled = true;
            btnRebuildGraph.textContent = '⏳ Rebuilding...';
            rebuildResult.classList.add('hidden');

            try {
                const res = await fetch('/api/rebuild/graph', { method: 'POST' });
                const data = await res.json();
                rebuildResult.className = 'alert-box success';
                rebuildResult.innerHTML = `<strong>Graph Rebuilt!</strong> ${data.nodes} nodes, ${data.edges} edges.`;
                rebuildResult.classList.remove('hidden');
                loadSystemSettings();
            } catch (e) {
                rebuildResult.className = 'alert-box error';
                rebuildResult.innerHTML = `<strong>Error:</strong> ${e.message}`;
                rebuildResult.classList.remove('hidden');
            } finally {
                btnRebuildGraph.disabled = false;
                btnRebuildGraph.textContent = '🕸️ Rebuild Knowledge Graph';
            }
        });
    }

    if (btnRebuildVectors) {
        btnRebuildVectors.addEventListener('click', async () => {
            btnRebuildVectors.disabled = true;
            btnRebuildVectors.textContent = '⏳ Re-embedding...';
            rebuildResult.classList.add('hidden');

            try {
                const res = await fetch('/api/rebuild/vectors', { method: 'POST' });
                const data = await res.json();
                rebuildResult.className = 'alert-box success';
                rebuildResult.innerHTML = `<strong>Vector Index Rebuilt!</strong> ${data.chunks} chunks indexed.`;
                rebuildResult.classList.remove('hidden');
                loadSystemSettings();
            } catch (e) {
                rebuildResult.className = 'alert-box error';
                rebuildResult.innerHTML = `<strong>Error:</strong> ${e.message}`;
                rebuildResult.classList.remove('hidden');
            } finally {
                btnRebuildVectors.disabled = false;
                btnRebuildVectors.textContent = '📊 Rebuild Vector Index';
            }
        });
    }

    // =====================================================================
    // Backend & Entity Catalog Inspector
    // =====================================================================
    const btnRefreshBackend = document.getElementById('btn-refresh-backend');
    const btnClearAllDbs   = document.getElementById('btn-clear-all-dbs');
    const searchInput      = document.getElementById('backend-search-input');

    if (btnRefreshBackend) btnRefreshBackend.addEventListener('click', loadBackendCatalog);
    if (searchInput) searchInput.addEventListener('input', filterBackendTable);

    if (btnClearAllDbs) {
        btnClearAllDbs.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all databases (Knowledge Graph, KùzuDB, LanceDB Vector Store, Vault Tracker)?')) {
                return;
            }
            btnClearAllDbs.disabled = true;
            btnClearAllDbs.textContent = '⏳ Clearing...';

            try {
                const res = await fetch('/api/clear', { method: 'POST' });
                const data = await res.json();
                alert(data.message || 'All databases cleared successfully.');
                loadBackendCatalog();
                loadSystemSettings();
            } catch (e) {
                alert('Failed to clear databases: ' + e.message);
            } finally {
                btnClearAllDbs.disabled = false;
                btnClearAllDbs.textContent = '🗑️ Clear All Databases';
            }
        });
    }

    let currentBackendNodes = [];

    async function loadBackendCatalog() {
        const tableBody = document.getElementById('backend-entity-table-body');
        const countSpan = document.getElementById('backend-entity-count');
        const tagsContainer = document.getElementById('backend-tags-container');
        if (!tableBody) return;

        try {
            const res = await fetch('/api/graph');
            const data = await res.json();
            currentBackendNodes = data.nodes || [];

            if (countSpan) countSpan.textContent = currentBackendNodes.length.toString();

            // Compute tag summary frequencies
            const tagCounts = {};
            currentBackendNodes.forEach(n => {
                const role = n.type || n.entity_type || 'Concept';
                tagCounts[role] = (tagCounts[role] || 0) + 1;

                if (n.taxonomy && n.taxonomy.domain) {
                    const dom = n.taxonomy.domain;
                    tagCounts[dom] = (tagCounts[dom] || 0) + 1;
                }
            });

            if (tagsContainer) {
                tagsContainer.innerHTML = '';
                if (Object.keys(tagCounts).length === 0) {
                    tagsContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">No tags extracted yet. Ingest a note to populate.</span>';
                } else {
                    for (const [tag, count] of Object.entries(tagCounts)) {
                        const badge = document.createElement('span');
                        badge.className = 'chip';
                        badge.style.backgroundColor = 'var(--surface-color)';
                        badge.style.border = '1px solid var(--border-color)';
                        badge.style.padding = '0.25rem 0.6rem';
                        badge.style.borderRadius = '12px';
                        badge.style.fontSize = '0.8rem';
                        badge.textContent = `${tag}: ${count}`;
                        tagsContainer.appendChild(badge);
                    }
                }
            }

            renderBackendTable(currentBackendNodes);
        } catch (e) {
            console.error('Failed to load backend catalog:', e);
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="4" style="padding: 1.5rem; text-align: center; color: #ef4444;">Error loading catalog: ${e.message}</td></tr>`;
            }
        }
    }

    function renderBackendTable(nodes) {
        const tableBody = document.getElementById('backend-entity-table-body');
        if (!tableBody) return;

        tableBody.innerHTML = '';
        if (nodes.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="padding: 1.5rem; text-align: center; color: var(--text-muted);">Database is clean and empty. Ingest a note to populate!</td></tr>';
            return;
        }

        nodes.forEach(n => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid var(--border-color)';

            const role = n.type || n.entity_type || 'Concept';
            const domain = n.taxonomy ? `${n.taxonomy.domain} › ${n.taxonomy.subdomain}` : 'General';
            const desc = n.description || '—';

            tr.innerHTML = `
                <td style="padding: 0.75rem; font-weight: 500; color: var(--text-primary);">${n.label || n.name || n.id}</td>
                <td style="padding: 0.75rem;"><span class="chip" style="font-size: 0.75rem; background: var(--surface-color); padding: 0.15rem 0.4rem; border-radius: 4px; border: 1px solid var(--border-color);">${role}</span></td>
                <td style="padding: 0.75rem; color: var(--text-secondary); font-size: 0.85rem;">${domain}</td>
                <td style="padding: 0.75rem; color: var(--text-muted); font-size: 0.85rem;">${desc}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function filterBackendTable() {
        const query = (document.getElementById('backend-search-input')?.value || '').toLowerCase();
        const filtered = currentBackendNodes.filter(n => {
            const name = (n.label || n.name || n.id || '').toLowerCase();
            const role = (n.type || n.entity_type || '').toLowerCase();
            const desc = (n.description || '').toLowerCase();
            const domain = n.taxonomy ? (n.taxonomy.domain || '').toLowerCase() : '';
            return name.includes(query) || role.includes(query) || desc.includes(query) || domain.includes(query);
        });
        renderBackendTable(filtered);
    }
});

// =====================================================================
// Global Helpers
// =====================================================================
function setQueryPrompt(text) {
    const input = document.getElementById('query-input');
    if (input) input.value = text;
}

function copyResponseText() {
    const content = document.getElementById('response-content');
    if (content) {
        navigator.clipboard.writeText(content.innerText);
        // Show brief feedback instead of alert
        const btn = content.closest('.response-card')?.querySelector('.btn-icon');
        if (btn) {
            const orig = btn.textContent;
            btn.textContent = '✅';
            setTimeout(() => { btn.textContent = orig; }, 1500);
        }
    }
}
