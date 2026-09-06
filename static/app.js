// Feather-style icon set (matches the inline SVGs already hand-written into
// index.html's nav/chips) for the handful of icons app.js builds into
// dynamic HTML strings — keeps emoji out of generated markup too.
const ICONS = {
    folder: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>',
    fileText: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>',
    checkCircle: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
    check: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
    square: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>',
    checkSquare: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>',
    shareGraph: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>',
    barChart: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    trash: '<svg class="icon-inline" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>',
};

document.addEventListener('DOMContentLoaded', () => {
    // --- State Variables (declared first to prevent TDZ ReferenceErrors) ---
    let currentGraphData = null;
    let graphNetwork = null;
    let graphNodesDataSet = null;
    let graphEdgesDataSet = null;
    let currentSolverUsed = null;
    let selectedNodeIds = new Set();
    let isMultiSelectMode = false;

    // --- Build Mode: 'live' talks to the FastAPI backend (/api/...); 'static'
    // (GitHub Pages) has no backend and reads the pre-exported data/*.json
    // instead. Same index.html/app.js serve both — export_static_site.py
    // flips the <meta name="build-mode"> tag and rewrites /static/ asset
    // paths when it copies these files into dist_static/.
    const STATIC_MODE = document.querySelector('meta[name="build-mode"]')?.content === 'static';

    if (STATIC_MODE) {
        document.querySelectorAll('[data-build="live-only"]').forEach(el => el.remove());
        document.querySelectorAll('[data-build="static-only"]').forEach(el => { el.hidden = false; });

        // tab-query was the default active tab and it was just removed —
        // fall back to the first remaining nav item (Knowledge Graph).
        if (!document.querySelector('.nav-item.active')) {
            const firstNav = document.querySelector('.nav-item');
            const firstTab = firstNav?.getAttribute('data-tab');
            firstNav?.classList.add('active');
            if (firstTab) document.getElementById(firstTab)?.classList.add('active');
        }
    }

    let cachedStaticVaultData = null;
    async function getStaticVaultData() {
        if (cachedStaticVaultData) return cachedStaticVaultData;
        try {
            const res = await fetch('data/vault.json');
            cachedStaticVaultData = await res.json();
        } catch (e) {
            console.warn('Could not load data/vault.json:', e);
            cachedStaticVaultData = { vault: {} };
        }
        return cachedStaticVaultData;
    }

    // --- Initial Health Check & Course List ---
    if (!STATIC_MODE) checkOllamaHealth();
    loadCourseDropdowns();

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
            const courses = STATIC_MODE
                ? Object.keys((await getStaticVaultData()).vault || {})
                : (await (await fetch('/api/courses')).json()).courses || [];
            const coursesSet = new Set(courses);
            if (currentGraphData && Array.isArray(currentGraphData.nodes)) {
                currentGraphData.nodes.forEach(n => {
                    if (n.course) coursesSet.add(n.course);
                    if (Array.isArray(n.provenance)) {
                        n.provenance.forEach(p => {
                            const dp = p.doc_path || '';
                            if (dp.startsWith('notes/')) {
                                const parts = dp.split('/');
                                if (parts.length > 2 && parts[1] && !parts[1].endsWith('.md')) {
                                    coursesSet.add(parts[1]);
                                }
                            }
                        });
                    }
                });
            }
            const allCourses = Array.from(coursesSet).sort();

            const courseChipsContainer = document.getElementById('graph-course-chips');
            if (courseChipsContainer) {
                const prevChecked = new Map();
                courseChipsContainer.querySelectorAll('.graph-course-filter').forEach(cb => {
                    prevChecked.set(cb.value, cb.checked);
                });

                courseChipsContainer.innerHTML = '';
                allCourses.forEach(c => {
                    const isChecked = prevChecked.has(c) ? prevChecked.get(c) : true;
                    const label = document.createElement('label');
                    label.className = 'chip-check';
                    label.innerHTML = `<input type="checkbox" value="${escapeHtml(c)}" ${isChecked ? 'checked' : ''} class="graph-course-filter"><span class="chip">${ICONS.folder} ${escapeHtml(c)}</span>`;
                    const input = label.querySelector('input');
                    input.addEventListener('change', () => {
                        if (currentGraphData) renderGraphWithFilters();
                    });
                    courseChipsContainer.appendChild(label);
                });
            }

            const sel = document.getElementById('query-course');
            if (sel) {
                // Keep the first "All Courses" option
                while (sel.options.length > 1) sel.remove(1);
                courses.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c;
                    opt.textContent = c;
                    sel.appendChild(opt);
                });
            }
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

    if (btnSubmitQuery) btnSubmitQuery.addEventListener('click', async () => {
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

    if (dropZone) {
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
                    if (data.graph_indexed) successMsg += `<br>${ICONS.checkCircle} Knowledge graph updated`;
                    if (data.vector_chunks > 0) successMsg += `<br>${ICONS.checkCircle} ${data.vector_chunks} chunks indexed in vector store`;
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
    }

    function handleFileSelect(file) {
        if (!file.name.endsWith('.pdf')) { alert('Please select a PDF file.'); return; }
        currentPdfFile = file;
        selectedFileName.textContent = file.name;
        selectedFileInfo.classList.remove('hidden');
    }

    // =====================================================================
    // Knowledge Graph Visualization (with filters)
    // =====================================================================
    // Multi-Select Mode (Touch / Mobile & Desktop)
    const btnMultiSelectToggle = document.getElementById('btn-multiselect-toggle');
    const btnClearSelection = document.getElementById('btn-clear-selection');

    if (btnMultiSelectToggle) {
        btnMultiSelectToggle.addEventListener('click', () => {
            isMultiSelectMode = !isMultiSelectMode;
            btnMultiSelectToggle.classList.toggle('btn-multiselect-active', isMultiSelectMode);
            const icon = btnMultiSelectToggle.querySelector('.multiselect-status-icon');
            if (icon) icon.innerHTML = isMultiSelectMode ? ICONS.checkSquare : ICONS.square;
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
            // The canvas' pixel size changed (600px tall panel -> full
            // viewport or back) — vis-network sizes its <canvas> off the
            // container's dimensions at creation time, so it needs an
            // explicit redraw/refit or it stays sized for the old box.
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
    const btnTypesAll = document.getElementById('btn-types-all');
    if (btnTypesAll) {
        btnTypesAll.addEventListener('click', () => {
            document.querySelectorAll('.graph-type-filter').forEach(cb => cb.checked = true);
            if (currentGraphData) renderGraphWithFilters();
        });
    }
    const btnTypesNone = document.getElementById('btn-types-none');
    if (btnTypesNone) {
        btnTypesNone.addEventListener('click', () => {
            document.querySelectorAll('.graph-type-filter').forEach(cb => cb.checked = false);
            if (currentGraphData) renderGraphWithFilters();
        });
    }
    const btnCoursesAll = document.getElementById('btn-courses-all');
    if (btnCoursesAll) {
        btnCoursesAll.addEventListener('click', () => {
            document.querySelectorAll('.graph-course-filter').forEach(cb => cb.checked = true);
            if (currentGraphData) renderGraphWithFilters();
        });
    }
    const btnCoursesNone = document.getElementById('btn-courses-none');
    if (btnCoursesNone) {
        btnCoursesNone.addEventListener('click', () => {
            document.querySelectorAll('.graph-course-filter').forEach(cb => cb.checked = false);
            if (currentGraphData) renderGraphWithFilters();
        });
    }

    // Runtime layout & physics customization listeners
    const sliderSpringLength = document.getElementById('graph-spring-length');
    const sliderSpringVal    = document.getElementById('graph-spring-val');
    const sliderNodeScale    = document.getElementById('graph-node-scale');
    const sliderNodeScaleVal = document.getElementById('graph-node-scale-val');
    const selectLayoutSolver = document.getElementById('graph-layout-solver');
    const toggleNodeLabels   = document.getElementById('graph-node-labels');
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

    if (toggleNodeLabels) {
        toggleNodeLabels.addEventListener('change', (e) => {
            const status = document.getElementById('node-label-status');
            if (status) status.textContent = e.target.checked ? 'Visible' : 'Hidden';
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

    async function loadKnowledgeGraph() {
        const container = document.getElementById('vis-graph-canvas');
        if (!container) return;

        try {
            const res = await fetch(STATIC_MODE ? 'data/graph.json' : '/api/graph');
            currentGraphData = await res.json();
            renderGraphWithFilters();
        } catch (err) {
            console.error('Failed to load graph:', err);
        }
    }

    function updateGraphRuntimeOptions() {
        if (!graphNetwork) return;

        const solver = document.getElementById('graph-layout-solver')?.value || 'forceAtlas2Based';
        const springLength = parseInt(document.getElementById('graph-spring-length')?.value || '250');
        const physicsEnabled = document.getElementById('graph-physics-toggle')?.checked ?? true;

        let physicsConfig = { enabled: physicsEnabled };

        if (solver === 'barnesHut') {
            physicsConfig.solver = 'barnesHut';
            physicsConfig.barnesHut = {
                gravitationalConstant: -7000,
                centralGravity: 0.2,
                springLength: springLength,
                springConstant: 0.04,
                damping: 0.09,
                avoidOverlap: 0.8
            };
        } else if (solver === 'forceAtlas2Based') {
            physicsConfig.solver = 'forceAtlas2Based';
            physicsConfig.forceAtlas2Based = {
                gravitationalConstant: -60,
                centralGravity: 0.008,
                springLength: springLength,
                springConstant: 0.06,
                damping: 0.4,
                avoidOverlap: 1
            };
        } else if (solver === 'repulsion') {
            physicsConfig.solver = 'repulsion';
            physicsConfig.repulsion = {
                nodeDistance: springLength,
                centralGravity: 0.05,
                springLength: springLength,
                springConstant: 0.05,
                damping: 0.12
            };
        } else if (solver === 'hierarchical') {
            physicsConfig.solver = 'hierarchicalRepulsion';
            physicsConfig.hierarchicalRepulsion = {
                nodeDistance: springLength,
                centralGravity: 0.0,
                springLength: springLength,
                springConstant: 0.01,
                damping: 0.12,
                avoidOverlap: 1
            };
        }

        graphNetwork.setOptions({ physics: physicsConfig });
    }

    // ------------------------------------------------------------------
    // Hierarchy depth → gradient fill color
    // ------------------------------------------------------------------
    // DEPENDS_ON(A, B) means A requires B (B is the more foundational
    // concept) and is drawn edge.from=A, edge.to=B. A node that depends on
    // nothing (no outgoing edge) is depth 0 — maximally foundational.
    // depth(A) = 1 + max(depth(B)) over everything A depends on, so depth
    // increases the further a concept sits from the foundations.
    function computeNodeDepths(nodes, edges) {
        const outgoing = new Map();
        nodes.forEach(n => outgoing.set(n.id, []));
        edges.forEach(e => {
            const from = e.from || e.source;
            const to = e.to || e.target;
            if (outgoing.has(from)) outgoing.get(from).push(to);
        });

        const depths = new Map();
        const visiting = new Set(); // cycle guard: a node revisited while
                                     // still being computed contributes 0
                                     // for that edge instead of recursing.
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

    const DEPTH_COLOR_START = [14, 165, 233];  // #0ea5e9 — foundational (electric blue)
    const DEPTH_COLOR_END   = [239, 68, 68];   // #ef4444 — advanced (vivid red)

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

    // ------------------------------------------------------------------
    // Node detail panel
    // ------------------------------------------------------------------

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

    function highlightNeighborhood(nodeIds) {
        if (!graphNetwork || !graphNodesDataSet || !graphEdgesDataSet) return;
        const keepNodes = new Set(nodeIds);
        const keepEdges = new Set();
        for (const id of nodeIds) {
            graphNetwork.getConnectedNodes(id).forEach(n => keepNodes.add(n));
            graphNetwork.getConnectedEdges(id).forEach(e => keepEdges.add(e));
        }

        const showNodeLabels = document.getElementById('graph-node-labels')?.checked ?? false;

        graphNodesDataSet.update(graphNodesDataSet.get().map(n => {
            const isHighlighted = keepNodes.has(n.id);
            const orig = currentGraphData ? currentGraphData.nodes.find(x => x.id === n.id) : null;
            const labelText = orig ? (orig.label || orig.name || orig.id) : n.id;
            return {
                id: n.id,
                opacity: isHighlighted ? 1 : 0.12,
                font: isHighlighted ? NODE_BASE_FONT : NODE_DIM_FONT,
                label: (showNodeLabels || isHighlighted) ? labelText : undefined
            };
        }));

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
        const showNodeLabels = document.getElementById('graph-node-labels')?.checked ?? false;
        graphNodesDataSet.update(graphNodesDataSet.get().map(n => {
            const orig = currentGraphData ? currentGraphData.nodes.find(x => x.id === n.id) : null;
            const labelText = orig ? (orig.label || orig.name || orig.id) : n.id;
            return {
                id: n.id,
                opacity: 1,
                font: NODE_BASE_FONT,
                label: showNodeLabels ? labelText : undefined
            };
        }));
        graphEdgesDataSet.update(graphEdgesDataSet.get().map(e => ({
            id: e.id, color: EDGE_BASE_COLOR, width: 1, font: EDGE_BASE_FONT,
        })));
    }

    // =====================================================================
    // Note Content Viewer — shared by the Vault Browser and the graph node
    // detail panel's "Source Notes" list, so both can show the actual
    // markdown/LaTeX content instead of just a filename.
    // =====================================================================
    const noteViewerOverlay = document.getElementById('note-viewer-overlay');
    const noteViewerTitle   = document.getElementById('note-viewer-title');
    const noteViewerBody    = document.getElementById('note-viewer-body');
    const btnCloseNoteViewer = document.getElementById('btn-close-note-viewer');

    async function openNoteViewer(path, fallbackTitle) {
        if (!noteViewerOverlay || !noteViewerBody) return;
        noteViewerTitle.textContent = fallbackTitle || 'Note';
        noteViewerBody.innerHTML = '<p style="color: var(--text-muted);">Loading…</p>';
        noteViewerOverlay.classList.remove('hidden');

        try {
            let title, content;
            if (STATIC_MODE) {
                const res = await fetch(path);
                if (!res.ok) {
                    noteViewerBody.innerHTML = `<p style="color: #ef4444;">Failed to load note: ${escapeHtml(res.statusText)}</p>`;
                    return;
                }
                title = fallbackTitle ? fallbackTitle.replace(/\.md$/, '') : path.split('/').pop().replace(/\.md$/, '');
                content = await res.text();
            } else {
                const res = await fetch(`/api/vault/note?path=${encodeURIComponent(path)}`);
                const data = await res.json();
                if (!res.ok) {
                    noteViewerBody.innerHTML = `<p style="color: #ef4444;">${escapeHtml(data.detail || 'Failed to load note.')}</p>`;
                    return;
                }
                title = data.title;
                content = data.content;
            }
            noteViewerTitle.textContent = `${title}.md`;
            noteViewerBody.innerHTML = marked.parse(content);
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
            noteViewerBody.innerHTML = `<p style="color: #ef4444;">Server connection error: ${escapeHtml(err.message)}</p>`;
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

    // Event delegation: the detail panel's innerHTML is fully replaced on
    // every node click, so bind once on the panel rather than per-item.
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
        const courseCheckboxes = document.querySelectorAll('.graph-course-filter');
        let activeCourses = null;
        if (courseCheckboxes.length > 0) {
            activeCourses = new Set();
            courseCheckboxes.forEach(cb => {
                if (cb.checked) activeCourses.add(cb.value.toLowerCase());
            });
        }

        const solver = document.getElementById('graph-layout-solver')?.value || 'forceAtlas2Based';
        const springLength = parseInt(document.getElementById('graph-spring-length')?.value || '250');
        const baseNodeSize = parseInt(document.getElementById('graph-node-scale')?.value || '10');
        const showNodeLabels = document.getElementById('graph-node-labels')?.checked ?? false;
        const showEdgeLabels = document.getElementById('graph-edge-labels')?.checked ?? false;
        const physicsEnabled = document.getElementById('graph-physics-toggle')?.checked ?? true;

        const filteredNodes = currentGraphData.nodes.filter(n => {
            const kind = n.kind || n.type || n.entity_type || 'Object';
            if (!activeTypes.has(kind)) return false;

            if (activeCourses !== null) {
                if (activeCourses.size === 0) return false;
                const nodeCourseIdentifiers = [];
                if (n.course) nodeCourseIdentifiers.push(n.course.toLowerCase());
                if (n.group) nodeCourseIdentifiers.push(n.group.toLowerCase());
                if (n.taxonomy && n.taxonomy.domain) nodeCourseIdentifiers.push(n.taxonomy.domain.toLowerCase());
                if (Array.isArray(n.provenance)) {
                    n.provenance.forEach(p => {
                        if (p.doc_path) nodeCourseIdentifiers.push(p.doc_path.toLowerCase());
                    });
                }
                const matchesCourse = Array.from(activeCourses).some(ac =>
                    nodeCourseIdentifiers.some(nc => nc.includes(ac) || ac.includes(nc))
                );
                if (!matchesCourse) return false;
            }
            return true;
        });
        const nodeIds = new Set(filteredNodes.map(n => n.id));

        const filteredEdges = currentGraphData.edges.filter(e => {
            const from = e.from || e.source;
            const to = e.to || e.target;
            return nodeIds.has(from) && nodeIds.has(to);
        });

        // Depths computed over the full graph (not just the filtered view)
        // so a node's color stays stable as filters toggle.
        const { depths, maxDepth } = computeNodeDepths(currentGraphData.nodes, currentGraphData.edges);

        const nodesArray = filteredNodes.map(n => {
            const domain = (n.taxonomy && n.taxonomy.domain) ? n.taxonomy.domain : 'Differential Equations';
            const role = n.role ? `${n.kind || n.type || 'Statement'} / ${n.role}` : (n.kind || n.type || n.entity_type || 'Object');
            const depth = depths.get(n.id) || 0;
            const fillColor = depthToColor(depth, maxDepth);
            const nodeSize = (n.kind === 'Statement' && n.role === 'Theorem') ? Math.round(baseNodeSize * 1.3) : baseNodeSize;

            return {
                id: n.id,
                label: showNodeLabels ? (n.label || n.name || n.id) : undefined,
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
                id: e.id || `${e.from || e.source}->${e.to || e.target}`,
                from: e.from || e.source,
                to: e.to || e.target,
                label: showEdgeLabels && rel !== 'links_to' ? rel : undefined,
                color: EDGE_BASE_COLOR,
                arrows: rel === 'EQUIVALENT_TO' ? undefined : 'to',
                font: EDGE_BASE_FONT
            };
        });

        if (graphNetwork && graphNodesDataSet && graphEdgesDataSet && currentSolverUsed === solver) {
            graphEdgesDataSet.clear();
            graphNodesDataSet.clear();
            graphNodesDataSet.add(nodesArray);
            graphEdgesDataSet.add(edgesArray);
            graphNetwork.setOptions({ physics: { enabled: physicsEnabled } });
            return;
        }

        currentSolverUsed = solver;
        if (graphNetwork) {
            try { graphNetwork.destroy(); } catch (e) {}
            graphNetwork = null;
        }
        container.innerHTML = '';

        graphNodesDataSet = new vis.DataSet(nodesArray);
        graphEdgesDataSet = new vis.DataSet(edgesArray);
        const networkData = {
            nodes: graphNodesDataSet,
            edges: graphEdgesDataSet
        };

        let options = {
            interaction: { hover: true, tooltipDelay: 150, hideEdgesOnDrag: true, hideEdgesOnZoom: true },
            edges: { smooth: { enabled: true, type: 'continuous', roundness: 0.15 } },
            layout: { improvedLayout: false },
            physics: {
                enabled: physicsEnabled,
                stabilization: { iterations: 150, fit: true }
            }
        };

        if (solver === 'hierarchical') {
            options.layout = {
                hierarchical: {
                    direction: 'DU',
                    sortMethod: 'directed',
                    levelSeparation: springLength,
                    nodeSpacing: springLength
                }
            };
            options.physics = {
                enabled: physicsEnabled,
                stabilization: { iterations: 150, fit: true },
                solver: 'hierarchicalRepulsion',
                hierarchicalRepulsion: {
                    nodeDistance: springLength,
                    centralGravity: 0.0,
                    springLength: springLength,
                    springConstant: 0.01,
                    damping: 0.12,
                    avoidOverlap: 1
                }
            };
        } else if (solver === 'forceAtlas2Based') {
            options.physics = {
                enabled: physicsEnabled,
                stabilization: { iterations: 150, fit: true },
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    gravitationalConstant: -60,
                    centralGravity: 0.008,
                    springLength: springLength,
                    springConstant: 0.06,
                    damping: 0.4,
                    avoidOverlap: 1
                }
            };
        } else if (solver === 'repulsion') {
            options.physics = {
                enabled: physicsEnabled,
                stabilization: { iterations: 150, fit: true },
                solver: 'repulsion',
                repulsion: {
                    nodeDistance: springLength,
                    centralGravity: 0.05,
                    springLength: springLength,
                    springConstant: 0.05,
                    damping: 0.12
                }
            };
        } else {
            options.physics = {
                enabled: physicsEnabled,
                stabilization: { iterations: 200, fit: true },
                solver: 'barnesHut',
                barnesHut: {
                    gravitationalConstant: -18000,
                    centralGravity: 0.05,
                    springLength: springLength,
                    springConstant: 0.04,
                    damping: 0.15,
                    avoidOverlap: 0.8
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

        // Automatically center the entire graph once loaded without forcing physics to freeze
        graphNetwork.once('stabilizationIterationsDone', () => {
            graphNetwork.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
            const currentPhysicsState = document.getElementById('graph-physics-toggle')?.checked ?? true;
            graphNetwork.setOptions({ physics: { enabled: currentPhysicsState } });
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
            const data = STATIC_MODE ? await getStaticVaultData() : await (await fetch('/api/vault')).json();

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
                    <h3>${ICONS.folder} ${course}</h3>
                    <div class="note-list">
                        ${notes.map(n => `<div class="note-item note-item-clickable" data-path="${escapeHtml(n.path)}" data-title="${escapeHtml(n.title)}.md">${ICONS.fileText} <span>${escapeHtml(n.title)}.md</span></div>`).join('')}
                    </div>
                `;
                container.appendChild(card);
            }
        } catch (err) {
            console.error('Failed to load vault notes:', err);
        }
    }

    // Event delegation: note-item cards are re-created on every refresh, so
    // bind once on the stable container rather than per-item.
    const vaultListContainer = document.getElementById('vault-list-container');
    if (vaultListContainer) {
        vaultListContainer.addEventListener('click', (e) => {
            const item = e.target.closest('.note-item-clickable');
            if (item) openNoteViewer(item.dataset.path, item.dataset.title);
        });
    }

    // =====================================================================
    // Settings Tab
    // =====================================================================
    const btnRebuildGraph   = document.getElementById('btn-rebuild-graph');
    const btnRebuildVectors = document.getElementById('btn-rebuild-vectors');
    const rebuildResult     = document.getElementById('rebuild-result');

    async function loadSystemSettings() {
        try {
            if (STATIC_MODE) {
                const [vaultData, graphData] = await Promise.all([
                    getStaticVaultData(),
                    fetch('data/graph.json').then(r => r.json()).catch(() => ({ nodes: [], edges: [] }))
                ]);
                const vault = vaultData.vault || {};
                const courses = Object.keys(vault);
                const totalNotes = courses.reduce((sum, c) => sum + (vault[c] || []).length, 0);

                setText('stat-vault-notes', totalNotes.toString());
                setText('stat-graph-nodes', (graphData.nodes || []).length.toString());
                setText('stat-graph-edges', (graphData.edges || []).length.toString());
                setText('stat-courses', courses.length > 0 ? courses.join(', ') : 'None');
                return;
            }

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
            btnRebuildGraph.textContent = 'Rebuilding...';
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
                btnRebuildGraph.innerHTML = `${ICONS.shareGraph} Rebuild Knowledge Graph`;
            }
        });
    }

    if (btnRebuildVectors) {
        btnRebuildVectors.addEventListener('click', async () => {
            btnRebuildVectors.disabled = true;
            btnRebuildVectors.textContent = 'Re-embedding...';
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
                btnRebuildVectors.innerHTML = `${ICONS.barChart} Rebuild Vector Index`;
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
            btnClearAllDbs.textContent = 'Clearing...';

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
                btnClearAllDbs.innerHTML = `${ICONS.trash} Clear All Databases`;
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
            const res = await fetch(STATIC_MODE ? 'data/graph.json' : '/api/graph');
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
                    tagsContainer.innerHTML = '<span class="catalog-table-empty">No tags extracted yet. Ingest a note to populate.</span>';
                } else {
                    for (const [tag, count] of Object.entries(tagCounts)) {
                        const badge = document.createElement('span');
                        badge.className = 'tag-badge';
                        const roleColor = ROLE_BORDER_COLORS[tag];
                        if (roleColor) {
                            badge.style.setProperty('--chip-color', roleColor);
                            badge.classList.add('tag-badge-role');
                        }
                        badge.textContent = `${tag}: ${count}`;
                        tagsContainer.appendChild(badge);
                    }
                }
            }

            renderBackendTable(currentBackendNodes);
        } catch (e) {
            console.error('Failed to load backend catalog:', e);
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="4" class="catalog-table-empty">Error loading catalog: ${escapeHtml(e.message)}</td></tr>`;
            }
        }
    }

    function renderBackendTable(nodes) {
        const tableBody = document.getElementById('backend-entity-table-body');
        if (!tableBody) return;

        tableBody.innerHTML = '';
        if (nodes.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="catalog-table-empty">Database is clean and empty. Ingest a note to populate!</td></tr>';
            return;
        }

        nodes.forEach(n => {
            const tr = document.createElement('tr');

            const role = n.type || n.entity_type || 'Concept';
            const roleColor = ROLE_BORDER_COLORS[role] || '#94a3b8';
            const domain = n.taxonomy ? `${n.taxonomy.domain} › ${n.taxonomy.subdomain}` : 'General';
            const desc = n.description || '—';

            tr.innerHTML = `
                <td class="catalog-entity-name" data-label="Entity Name">${escapeHtml(n.label || n.name || n.id)}</td>
                <td data-label="Role / Type"><span class="catalog-role-chip" style="--chip-color: ${roleColor};">${escapeHtml(role)}</span></td>
                <td class="catalog-domain" data-label="Domain Taxonomy">${escapeHtml(domain)}</td>
                <td class="catalog-description" data-label="Description" title="${escapeHtml(desc)}">${escapeHtml(desc)}</td>
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
            const orig = btn.innerHTML;
            btn.innerHTML = ICONS.check;
            setTimeout(() => { btn.innerHTML = orig; }, 1500);
        }
    }
}
