document.addEventListener('DOMContentLoaded', () => {
    // --- Initial Load ---
    loadCourseDropdowns();
    loadKnowledgeGraph();

    // --- Navigation Tabs & Mobile Drawer ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabPages = document.querySelectorAll('.tab-page');
    const mobileNavToggle = document.getElementById('btn-mobile-nav-toggle');
    const sidebarEl = document.querySelector('.sidebar');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');

    function closeMobileSidebar() {
        if (sidebarEl) sidebarEl.classList.remove('open');
        if (sidebarBackdrop) sidebarBackdrop.classList.remove('active');
    }

    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', () => {
            if (sidebarEl) sidebarEl.classList.toggle('open');
            if (sidebarBackdrop) sidebarBackdrop.classList.toggle('active');
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', closeMobileSidebar);
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');

            closeMobileSidebar();
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
    // Course Dropdowns (shared across tabs)
    // =====================================================================
    let cachedVaultData = null;

    async function getVaultData() {
        if (cachedVaultData) return cachedVaultData;
        try {
            const res = await fetch('data/vault.json');
            cachedVaultData = await res.json();
            return cachedVaultData;
        } catch (e) {
            console.warn('Could not load data/vault.json:', e);
            return { vault: {} };
        }
    }

    async function loadCourseDropdowns() {
        try {
            const data = await getVaultData();
            const courses = Object.keys(data.vault || {}).sort();

            const sel = document.getElementById('graph-course-filter');
            if (!sel) return;
            while (sel.options.length > 1) sel.remove(1);
            courses.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                sel.appendChild(opt);
            });
        } catch (e) {
            console.warn('Could not load courses:', e);
        }
    }

    // Multi-Select Mode (Touch / Mobile & Desktop)
    let isMultiSelectMode = false;
    const btnMultiSelectToggle = document.getElementById('btn-multiselect-toggle');
    const btnClearSelection = document.getElementById('btn-clear-selection');

    if (btnMultiSelectToggle) {
        btnMultiSelectToggle.addEventListener('click', () => {
            isMultiSelectMode = !isMultiSelectMode;
            btnMultiSelectToggle.classList.toggle('btn-multiselect-active', isMultiSelectMode);
            const icon = btnMultiSelectToggle.querySelector('.multiselect-status-icon');
            if (icon) icon.textContent = isMultiSelectMode ? '☑' : '☐';
        });
    }

    if (btnClearSelection) {
        btnClearSelection.addEventListener('click', () => {
            clearHighlight();
            clearNodeDetail();
        });
    }

    function updateSelectionUI() {
        const clearBtn = document.getElementById('btn-clear-selection');
        const countSpan = document.getElementById('selected-count');
        if (countSpan) countSpan.textContent = selectedNodeIds.size.toString();
        if (clearBtn) {
            if (selectedNodeIds.size > 0) {
                clearBtn.classList.remove('hidden');
            } else {
                clearBtn.classList.add('hidden');
            }
        }
    }

    const btnRefreshGraph = document.getElementById('btn-refresh-graph');
    if (btnRefreshGraph) btnRefreshGraph.addEventListener('click', loadKnowledgeGraph);

    const btnFitGraph = document.getElementById('btn-fit-graph');
    if (btnFitGraph) {
        btnFitGraph.addEventListener('click', () => {
            if (graphNetwork) graphNetwork.fit({ animation: { duration: 800, easingFunction: 'easeInOutQuad' } });
        });
    }

    const btnFullscreenGraph = document.getElementById('btn-fullscreen-graph');
    const graphContainerEl = document.querySelector('.graph-container');
    if (btnFullscreenGraph && graphContainerEl) {
        btnFullscreenGraph.addEventListener('click', () => {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                const request = graphContainerEl.requestFullscreen || graphContainerEl.webkitRequestFullscreen;
                if (request) request.call(graphContainerEl);
            }
        });
        document.addEventListener('fullscreenchange', () => {
            const isFullscreen = document.fullscreenElement === graphContainerEl;
            btnFullscreenGraph.textContent = isFullscreen ? 'Exit Fullscreen' : 'Fullscreen';
            if (graphNetwork) {
                setTimeout(() => {
                    graphNetwork.redraw();
                    graphNetwork.fit({ animation: { duration: 400, easingFunction: 'easeInOutQuad' } });
                }, 50);
            }
        });
    }

    // Attach filter & runtime customization listeners
    document.querySelectorAll('.graph-type-filter').forEach(cb => {
        cb.addEventListener('change', () => { if (currentGraphData) renderGraphWithFilters(); });
    });
    const graphCourseFilter = document.getElementById('graph-course-filter');
    if (graphCourseFilter) {
        graphCourseFilter.addEventListener('change', () => { if (currentGraphData) renderGraphWithFilters(); });
    }

    // Runtime layout & physics customization listeners
    const sliderSpringLength = document.getElementById('graph-spring-length');
    const sliderSpringVal    = document.getElementById('graph-spring-val');
    const sliderNodeScale    = document.getElementById('graph-node-scale');
    const sliderNodeScaleVal = document.getElementById('graph-node-scale-val');
    const selectLayoutSolver = document.getElementById('graph-layout-solver');
    const toggleEdgeLabels   = document.getElementById('graph-edge-labels');
    const togglePhysics      = document.getElementById('graph-physics-toggle');

    if (sliderSpringLength) {
        sliderSpringLength.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            if (sliderSpringVal) sliderSpringVal.textContent = `${val}px`;
            updateGraphRuntimeOptions();
        });
    }

    if (sliderNodeScale) {
        sliderNodeScale.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            if (sliderNodeScaleVal) sliderNodeScaleVal.textContent = `${val}px`;
            if (currentGraphData) renderGraphWithFilters();
        });
    }

    if (selectLayoutSolver) {
        selectLayoutSolver.addEventListener('change', () => {
            if (currentGraphData) renderGraphWithFilters();
        });
    }

    if (toggleEdgeLabels) {
        toggleEdgeLabels.addEventListener('change', (e) => {
            const status = document.getElementById('edge-label-status');
            if (status) status.textContent = e.target.checked ? 'Visible' : 'Hidden';
            if (currentGraphData) renderGraphWithFilters();
        });
    }

    if (togglePhysics) {
        togglePhysics.addEventListener('change', (e) => {
            const status = document.getElementById('physics-toggle-status');
            const active = e.target.checked;
            if (status) status.textContent = active ? 'Active' : 'Frozen';
            if (graphNetwork) {
                graphNetwork.setOptions({ physics: { enabled: active } });
            }
        });
    }

    let currentGraphData = null;
    let graphNetwork = null;
    let graphNodesDataSet = null;
    let graphEdgesDataSet = null;

    async function loadKnowledgeGraph() {
        const container = document.getElementById('vis-graph-canvas');
        if (!container) return;

        try {
            const res = await fetch('data/graph.json');
            currentGraphData = await res.json();
            renderGraphWithFilters();
        } catch (err) {
            console.error('Failed to load data/graph.json:', err);
        }
    }

    function updateGraphRuntimeOptions() {
        if (!graphNetwork) return;

        const solver = document.getElementById('graph-layout-solver')?.value || 'forceAtlas2Based';
        const springLength = parseInt(document.getElementById('graph-spring-length')?.value || '180');
        const physicsEnabled = document.getElementById('graph-physics-toggle')?.checked ?? true;

        let physicsConfig = { enabled: physicsEnabled };

        if (solver === 'barnesHut') {
            physicsConfig.solver = 'barnesHut';
            physicsConfig.barnesHut = {
                gravitationalConstant: -7000,
                centralGravity: 0.2,
                springLength: springLength,
                springConstant: 0.04,
                damping: 0.09
            };
        } else if (solver === 'forceAtlas2Based') {
            physicsConfig.solver = 'forceAtlas2Based';
            physicsConfig.forceAtlas2Based = {
                gravitationalConstant: -50,
                centralGravity: 0.01,
                springLength: springLength,
                springConstant: 0.08
            };
        } else if (solver === 'hierarchical') {
            physicsConfig.solver = 'hierarchicalRepulsion';
            physicsConfig.hierarchicalRepulsion = {
                nodeDistance: 200,
                centralGravity: 0.0,
                springLength: 150,
                springConstant: 0.01,
                damping: 0.12,
                avoidOverlap: 1
            };
        }

        graphNetwork.setOptions({ physics: physicsConfig });
    }

    function computeNodeDepths(nodes, edges) {
        const outgoing = new Map();
        nodes.forEach(n => outgoing.set(n.id, []));
        edges.forEach(e => {
            const from = e.from || e.source;
            const to = e.to || e.target;
            if (outgoing.has(from)) outgoing.get(from).push(to);
        });

        const depths = new Map();
        const visiting = new Set();
        function depthOf(id) {
            if (depths.has(id)) return depths.get(id);
            if (visiting.has(id)) return 0;
            visiting.add(id);
            let d = 0;
            for (const t of (outgoing.get(id) || [])) {
                if (outgoing.has(t)) d = Math.max(d, 1 + depthOf(t));
            }
            visiting.delete(id);
            depths.set(id, d);
            return d;
        }

        nodes.forEach(n => depthOf(n.id));
        const maxDepth = Math.max(0, ...depths.values());
        return { depths, maxDepth };
    }

    const DEPTH_COLOR_START = [14, 165, 233];
    const DEPTH_COLOR_END   = [239, 68, 68];

    function depthToColor(depth, maxDepth) {
        const t = maxDepth > 0 ? depth / maxDepth : 0;
        const c = DEPTH_COLOR_START.map((v, i) => Math.round(v + (DEPTH_COLOR_END[i] - v) * t));
        return `#${c.map(v => v.toString(16).padStart(2, '0')).join('')}`;
    }

    const ROLE_BORDER_COLORS = {
        'Object':     '#3b82f6',
        'Statement':  '#f59e0b',
        'Definition': '#10b981',
        'Method':     '#8b5cf6',
        'Formula':    '#06b6d4',
        'Proof':      '#ec4899',
        'Example':    '#14b8a6',
        'Theorem':    '#f59e0b',
        'Lemma':      '#eab308',
        'Concept':    '#94a3b8',
    };

    function escapeHtml(s) {
        const div = document.createElement('div');
        div.textContent = s ?? '';
        return div.innerHTML;
    }

    function clearNodeDetail() {
        const panel = document.getElementById('graph-detail-panel');
        if (!panel) return;
        panel.innerHTML = '<div class="graph-detail-placeholder">Click a node to see its full details.</div>';
    }

    const EDGE_BASE_COLOR = { color: '#3b82f6', opacity: 0.55 };
    const EDGE_BASE_FONT = { color: '#9ca3af', size: 10, face: 'Inter', strokeWidth: 0 };
    const NODE_BASE_FONT = { color: '#ffffff', face: 'Inter', size: 13 };
    const NODE_DIM_FONT = { color: 'rgba(255,255,255,0.08)', face: 'Inter', size: 13 };

    let selectedNodeIds = new Set();

    function highlightNeighborhood(nodeIds) {
        if (!graphNetwork || !graphNodesDataSet || !graphEdgesDataSet) return;
        const keepNodes = new Set(nodeIds);
        const keepEdges = new Set();
        for (const id of nodeIds) {
            graphNetwork.getConnectedNodes(id).forEach(n => keepNodes.add(n));
            graphNetwork.getConnectedEdges(id).forEach(e => keepEdges.add(e));
        }

        graphNodesDataSet.update(graphNodesDataSet.get().map(n => ({
            id: n.id,
            opacity: keepNodes.has(n.id) ? 1 : 0.12,
            font: keepNodes.has(n.id) ? NODE_BASE_FONT : NODE_DIM_FONT,
        })));

        graphEdgesDataSet.update(graphEdgesDataSet.get().map(e => {
            const highlight = keepEdges.has(e.id);
            return {
                id: e.id,
                color: highlight ? { color: '#f59e0b', opacity: 0.95 } : { color: EDGE_BASE_COLOR.color, opacity: 0.06 },
                width: highlight ? 2.5 : 1,
                font: highlight ? { ...EDGE_BASE_FONT, color: '#facc15' } : { ...EDGE_BASE_FONT, color: 'rgba(156,163,175,0.1)' },
            };
        }));
    }

    function clearHighlight() {
        selectedNodeIds.clear();
        updateSelectionUI();
        if (!graphNodesDataSet || !graphEdgesDataSet) return;
        graphNodesDataSet.update(graphNodesDataSet.get().map(n => ({ id: n.id, opacity: 1, font: NODE_BASE_FONT })));
        graphEdgesDataSet.update(graphEdgesDataSet.get().map(e => ({
            id: e.id, color: EDGE_BASE_COLOR, width: 1, font: EDGE_BASE_FONT,
        })));
    }

    // =====================================================================
    // Note Content Viewer — static markdown reader
    // =====================================================================
    const noteViewerOverlay  = document.getElementById('note-viewer-overlay');
    const noteViewerTitle    = document.getElementById('note-viewer-title');
    const noteViewerBody     = document.getElementById('note-viewer-body');
    const btnCloseNoteViewer = document.getElementById('btn-close-note-viewer');

    async function openNoteViewer(path, fallbackTitle) {
        if (!noteViewerOverlay || !noteViewerBody) return;
        noteViewerTitle.textContent = fallbackTitle || 'Note';
        noteViewerBody.innerHTML = '<p style="color: var(--text-muted);">Loading note content…</p>';
        noteViewerOverlay.classList.remove('hidden');

        try {
            const res = await fetch(path);
            if (!res.ok) {
                noteViewerBody.innerHTML = `<p style="color: #ef4444;">Failed to load note: ${res.statusText}</p>`;
                return;
            }
            const markdownText = await res.text();
            noteViewerTitle.textContent = fallbackTitle || path.split('/').pop();
            noteViewerBody.innerHTML = marked.parse(markdownText);
            renderMathInElement(noteViewerBody, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false },
                    { left: '\\(', right: '\\)', display: false },
                    { left: '\\[', right: '\\]', display: true }
                ],
                throwOnError: false
            });
        } catch (err) {
            noteViewerBody.innerHTML = `<p style="color: #ef4444;">Connection error: ${escapeHtml(err.message)}</p>`;
        }
    }

    function closeNoteViewer() {
        if (noteViewerOverlay) noteViewerOverlay.classList.add('hidden');
    }

    if (btnCloseNoteViewer) btnCloseNoteViewer.addEventListener('click', closeNoteViewer);
    if (noteViewerOverlay) {
        noteViewerOverlay.addEventListener('click', (e) => {
            if (e.target === noteViewerOverlay) closeNoteViewer();
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && noteViewerOverlay && !noteViewerOverlay.classList.contains('hidden')) {
            closeNoteViewer();
        }
    });

    function showNodeDetail(nodeId) {
        const panel = document.getElementById('graph-detail-panel');
        if (!panel || !currentGraphData) return;

        const n = currentGraphData.nodes.find(x => x.id === nodeId);
        if (!n) { clearNodeDetail(); return; }

        const role = n.type || n.entity_type || 'Concept';
        const roleColor = ROLE_BORDER_COLORS[role] || '#94a3b8';
        const tax = n.taxonomy || {};
        const aliases = Array.isArray(n.aliases) ? n.aliases : [];
        const provenance = Array.isArray(n.provenance) ? n.provenance : [];

        let html = `<div class="graph-detail-header-row">
            <h3>${escapeHtml(n.label || n.id)}</h3>
            <button class="graph-detail-close-btn" id="btn-close-node-detail" title="Close details">&times;</button>
        </div>`;
        html += `<span class="graph-detail-type" style="background:${roleColor}22; color:${roleColor};">${escapeHtml(role)}</span>`;

        if (n.description) {
            html += `<div class="graph-detail-section">
                <div class="graph-detail-section-label">Description</div>
                <div class="graph-detail-desc">${escapeHtml(n.description)}</div>
            </div>`;
        }

        if (tax.domain || tax.subdomain || tax.topic) {
            html += `<div class="graph-detail-section">
                <div class="graph-detail-section-label">Taxonomy</div>
                <div class="graph-detail-taxonomy">
                    ${tax.domain ? `Domain: ${escapeHtml(tax.domain)}<br>` : ''}
                    ${tax.subdomain ? `Subdomain: ${escapeHtml(tax.subdomain)}<br>` : ''}
                    ${tax.topic ? `Topic: ${escapeHtml(tax.topic)}` : ''}
                </div>
            </div>`;
        }

        if (aliases.length) {
            html += `<div class="graph-detail-section">
                <div class="graph-detail-section-label">Aliases (${aliases.length})</div>
                <div class="graph-detail-chips">
                    ${aliases.map(a => `<span class="graph-detail-chip">${escapeHtml(a)}</span>`).join('')}
                </div>
            </div>`;
        }

        if (provenance.length) {
            html += `<div class="graph-detail-section">
                <div class="graph-detail-section-label">Source Notes (${provenance.length})</div>
                ${provenance.map(p => {
                    const label = escapeHtml(p.doc_title || p.doc_id || 'Unknown note');
                    return p.doc_path
                        ? `<div class="graph-detail-provenance-item note-item-clickable" data-path="${escapeHtml(p.doc_path)}" data-title="${label}">${label}</div>`
                        : `<div class="graph-detail-provenance-item">${label}</div>`;
                }).join('')}
            </div>`;
        }

        html += `<div class="graph-detail-section">
            <div class="graph-detail-section-label">Id</div>
            <div class="graph-detail-taxonomy" style="word-break: break-all;">${escapeHtml(n.id)}</div>
        </div>`;

        panel.innerHTML = html;
    }

    const graphDetailPanelEl = document.getElementById('graph-detail-panel');
    if (graphDetailPanelEl) {
        graphDetailPanelEl.addEventListener('click', (e) => {
            if (e.target.closest('#btn-close-node-detail')) {
                clearNodeDetail();
                return;
            }
            const item = e.target.closest('.note-item-clickable');
            if (item) openNoteViewer(item.dataset.path, item.dataset.title);
        });
    }

    function renderGraphWithFilters() {
        const container = document.getElementById('vis-graph-canvas');
        if (!container || !currentGraphData) return;

        const activeTypes = new Set();
        document.querySelectorAll('.graph-type-filter:checked').forEach(cb => activeTypes.add(cb.value));
        const courseFilter = document.getElementById('graph-course-filter')?.value || '';
        const solver = document.getElementById('graph-layout-solver')?.value || 'forceAtlas2Based';
        const springLength = parseInt(document.getElementById('graph-spring-length')?.value || '180');
        const baseNodeSize = parseInt(document.getElementById('graph-node-scale')?.value || '18');
        const showEdgeLabels = document.getElementById('graph-edge-labels')?.checked ?? true;
        const physicsEnabled = document.getElementById('graph-physics-toggle')?.checked ?? true;

        const filteredNodes = currentGraphData.nodes.filter(n => {
            const kind = n.kind || n.type || n.entity_type || 'Object';
            if (activeTypes.size > 0 && !activeTypes.has(kind)) return false;
            if (courseFilter && n.group !== courseFilter && n.group !== 'Concept') return false;
            return true;
        });
        const nodeIds = new Set(filteredNodes.map(n => n.id));

        const filteredEdges = currentGraphData.edges.filter(e => {
            const from = e.from || e.source;
            const to = e.to || e.target;
            return nodeIds.has(from) && nodeIds.has(to);
        });

        const { depths, maxDepth } = computeNodeDepths(currentGraphData.nodes, currentGraphData.edges);

        const nodesArray = filteredNodes.map(n => {
            const domain = (n.taxonomy && n.taxonomy.domain) ? n.taxonomy.domain : 'Differential Equations';
            const role = n.role ? `${n.kind || n.type || 'Statement'} / ${n.role}` : (n.kind || n.type || n.entity_type || 'Object');
            const depth = depths.get(n.id) || 0;
            const fillColor = depthToColor(depth, maxDepth);
            const nodeSize = (n.kind === 'Statement' && n.role === 'Theorem') ? Math.round(baseNodeSize * 1.25) : baseNodeSize;

            return {
                id: n.id,
                label: n.label || n.name || n.id,
                color: {
                    background: fillColor,
                    border: fillColor,
                    highlight: { background: fillColor, border: '#ffffff' }
                },
                borderWidth: 1,
                font: NODE_BASE_FONT,
                shape: 'dot',
                size: nodeSize,
                title: `[${role}] ${n.label || n.id}\nDomain: ${domain}\nHierarchy depth: ${depth}`
            };
        });

        const edgesArray = filteredEdges.map(e => {
            const rel = e.label || e.relation || '';
            return {
                from: e.from || e.source,
                to: e.to || e.target,
                label: showEdgeLabels && rel !== 'links_to' ? rel : undefined,
                color: EDGE_BASE_COLOR,
                arrows: rel === 'EQUIVALENT_TO' ? undefined : 'to',
                font: EDGE_BASE_FONT
            };
        });

        graphNodesDataSet = new vis.DataSet(nodesArray);
        graphEdgesDataSet = new vis.DataSet(edgesArray);
        const networkData = {
            nodes: graphNodesDataSet,
            edges: graphEdgesDataSet
        };

        let options = {
            interaction: { hover: true, tooltipDelay: 150, hideEdgesOnDrag: true, hideEdgesOnZoom: true },
            edges: { smooth: { enabled: true, type: 'continuous', roundness: 0.15 } },
            physics: {
                enabled: physicsEnabled,
                stabilization: { iterations: 200, fit: true }
            }
        };

        if (solver === 'hierarchical') {
            options.layout = {
                hierarchical: {
                    direction: 'DU',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 150
                }
            };
            options.physics = {
                enabled: physicsEnabled,
                stabilization: { iterations: 200, fit: true },
                solver: 'hierarchicalRepulsion',
                hierarchicalRepulsion: {
                    nodeDistance: 200,
                    centralGravity: 0.0,
                    springLength: 150,
                    springConstant: 0.01,
                    damping: 0.12,
                    avoidOverlap: 1
                }
            };
        } else if (solver === 'forceAtlas2Based') {
            options.physics = {
                enabled: physicsEnabled,
                stabilization: { iterations: 200, fit: true },
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: springLength,
                    springConstant: 0.08
                }
            };
        } else {
            options.physics = {
                enabled: physicsEnabled,
                stabilization: { iterations: 300, fit: true },
                solver: 'barnesHut',
                barnesHut: {
                    gravitationalConstant: -18000,
                    centralGravity: 0.05,
                    springLength: springLength,
                    springConstant: 0.04,
                    damping: 0.15,
                    avoidOverlap: 0.5
                }
            };
        }

        graphNetwork = new vis.Network(container, networkData, options);
        graphNetwork.on('click', (params) => {
            if (params.nodes && params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const src = params.event && params.event.srcEvent;
                const isMulti = isMultiSelectMode || !!(src && (src.ctrlKey || src.metaKey));

                if (isMulti && selectedNodeIds.has(nodeId)) {
                    selectedNodeIds.delete(nodeId);
                } else if (isMulti) {
                    selectedNodeIds.add(nodeId);
                } else {
                    selectedNodeIds = new Set([nodeId]);
                }

                updateSelectionUI();

                if (selectedNodeIds.size === 0) {
                    clearNodeDetail();
                    clearHighlight();
                } else {
                    showNodeDetail(nodeId);
                    highlightNeighborhood(selectedNodeIds);
                }
            } else {
                clearNodeDetail();
                clearHighlight();
            }
        });

        graphNetwork.once('stabilizationIterationsDone', () => {
            graphNetwork.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
            graphNetwork.setOptions({ physics: { enabled: false } });
            const physicsToggle = document.getElementById('graph-physics-toggle');
            const physicsStatus = document.getElementById('physics-toggle-status');
            if (physicsToggle) physicsToggle.checked = false;
            if (physicsStatus) physicsStatus.textContent = 'Frozen';
        });
        setTimeout(() => {
            if (graphNetwork) graphNetwork.fit({ animation: true });
        }, 400);
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
            const data = await getVaultData();
            container.innerHTML = '';
            const vault = data.vault || {};

            if (Object.keys(vault).length === 0) {
                container.innerHTML = '<p style="color: var(--text-muted);">No notes found in vault index.</p>';
                return;
            }

            for (const [course, notes] of Object.entries(vault)) {
                const card = document.createElement('div');
                card.className = 'course-card';
                card.innerHTML = `
                    <h3>📁 ${course}</h3>
                    <div class="note-list">
                        ${notes.map(n => `<div class="note-item note-item-clickable" data-path="${escapeHtml(n.path)}" data-title="${escapeHtml(n.title)}.md">📄 <span>${escapeHtml(n.title)}.md</span></div>`).join('')}
                    </div>
                `;
                container.appendChild(card);
            }
        } catch (err) {
            console.error('Failed to load vault notes:', err);
        }
    }

    const vaultListContainer = document.getElementById('vault-list-container');
    if (vaultListContainer) {
        vaultListContainer.addEventListener('click', (e) => {
            const item = e.target.closest('.note-item-clickable');
            if (item) openNoteViewer(item.dataset.path, item.dataset.title);
        });
    }

    // =====================================================================
    // Settings Tab & Info
    // =====================================================================
    async function loadSystemSettings() {
        try {
            const [vaultData, graphData] = await Promise.all([
                getVaultData(),
                fetch('data/graph.json').then(r => r.json()).catch(() => ({ nodes: [], edges: [] }))
            ]);

            const vault = vaultData.vault || {};
            let totalNotes = 0;
            const courses = Object.keys(vault);
            courses.forEach(c => { totalNotes += (vault[c] || []).length; });

            setText('stat-vault-notes', totalNotes.toString());
            setText('stat-graph-nodes', (graphData.nodes || []).length.toString());
            setText('stat-graph-edges', (graphData.edges || []).length.toString());
            setText('stat-courses', courses.length > 0 ? courses.join(', ') : 'None');
        } catch (e) {
            console.warn('Could not load system settings:', e);
        }
    }

    function setText(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    // =====================================================================
    // Backend & Entity Catalog Inspector
    // =====================================================================
    const btnRefreshBackend = document.getElementById('btn-refresh-backend');
    const searchInput      = document.getElementById('backend-search-input');

    if (btnRefreshBackend) btnRefreshBackend.addEventListener('click', loadBackendCatalog);
    if (searchInput) searchInput.addEventListener('input', filterBackendTable);

    let currentBackendNodes = [];

    async function loadBackendCatalog() {
        const tableBody = document.getElementById('backend-entity-table-body');
        const countSpan = document.getElementById('backend-entity-count');
        const tagsContainer = document.getElementById('backend-tags-container');
        if (!tableBody) return;

        try {
            const res = await fetch('data/graph.json');
            const data = await res.json();
            currentBackendNodes = data.nodes || [];

            if (countSpan) countSpan.textContent = currentBackendNodes.length.toString();

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
                    tagsContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">No tags extracted yet.</span>';
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
            console.error('Failed to load entity catalog:', e);
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
            tableBody.innerHTML = '<tr><td colspan="4" style="padding: 1.5rem; text-align: center; color: var(--text-muted);">Catalog is empty.</td></tr>';
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
