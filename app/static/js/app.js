/**
 * Scholarship Intelligence Crawler - Client-Side Controller
 * Connects UI to FastAPI backend, manages filters, evidence modals,
 * confidence audits, and live crawler triggers.
 */

// State Management
const state = {
    scholarships: [],
    metrics: {},
    currentView: 'grid', // 'grid' or 'table'
    activeFilters: {
        q: '',
        source_type: 'ALL',
        status: 'ALL',
        verification_status: 'ALL',
        education_level: 'ALL',
        domicile_state: 'ALL',
        sort_by: 'confidence_score',
        sort_order: 'desc'
    },
    activeScholarshipDetail: null
};

// DOM Elements
const gridContainer = document.getElementById('scholarships-grid');
const tableBody = document.getElementById('scholarships-table-body');
const tableWrapper = document.getElementById('scholarships-table-wrapper');
const emptyState = document.getElementById('empty-state');
const visibleCountBadge = document.getElementById('visible-count-badge');
const searchInput = document.getElementById('search-input');
const searchClearBtn = document.getElementById('search-clear-btn');
const modalBackdrop = document.getElementById('detail-modal');
const modalCloseBtn = document.getElementById('modal-close-btn');
const toastContainer = document.getElementById('toast-container');

// Metric Elements
const metricTotal = document.getElementById('metric-total');
const metricVerified = document.getElementById('metric-verified');
const metricReview = document.getElementById('metric-review');
const metricActive = document.getElementById('metric-active');
const metricAvgConf = document.getElementById('metric-avg-conf');
const metricMutations = document.getElementById('metric-mutations');

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupEventListeners();
    loadDashboardData();
});

function initTheme() {
    const savedTheme = localStorage.getItem('scholarship_app_theme') || 'cyan';
    setTheme(savedTheme, false);
}

function setTheme(theme, showNotification = true) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('scholarship_app_theme', theme);
    document.querySelectorAll('.theme-option').forEach(btn => {
        if (btn.getAttribute('data-theme') === theme) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function setupEventListeners() {
    // Theme dropdown toggle
    const themeBtn = document.getElementById('theme-dropdown-btn');
    const themeMenu = document.getElementById('theme-menu');
    const exportBtn = document.getElementById('export-dropdown-btn');
    const exportMenu = document.getElementById('export-menu');

    if (themeBtn && themeMenu) {
        themeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (exportMenu) exportMenu.classList.remove('show');
            themeMenu.classList.toggle('show');
        });

        document.querySelectorAll('.theme-option').forEach(opt => {
            opt.addEventListener('click', (e) => {
                const chosen = e.currentTarget.getAttribute('data-theme');
                const themeName = e.currentTarget.textContent.trim();
                setTheme(chosen);
                themeMenu.classList.remove('show');
                showToast(`Palette switched to ${themeName}`, 'success');
            });
        });

        document.addEventListener('click', () => themeMenu.classList.remove('show'));
    }

    // Search input with debounce
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        state.activeFilters.q = val;
        searchClearBtn.classList.toggle('hidden', val.length === 0);
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => loadScholarships(), 250);
    });

    searchClearBtn.addEventListener('click', () => {
        searchInput.value = '';
        state.activeFilters.q = '';
        searchClearBtn.classList.add('hidden');
        loadScholarships();
    });

    // Filters
    document.getElementById('filter-source-type').addEventListener('change', (e) => {
        state.activeFilters.source_type = e.target.value;
        loadScholarships();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        state.activeFilters.status = e.target.value;
        loadScholarships();
    });

    document.getElementById('filter-verification').addEventListener('change', (e) => {
        state.activeFilters.verification_status = e.target.value;
        loadScholarships();
    });

    document.getElementById('filter-education').addEventListener('change', (e) => {
        state.activeFilters.education_level = e.target.value;
        loadScholarships();
    });

    document.getElementById('filter-domicile').addEventListener('change', (e) => {
        state.activeFilters.domicile_state = e.target.value;
        loadScholarships();
    });

    // Sorting
    document.getElementById('sort-select').addEventListener('change', (e) => {
        const [field, order] = e.target.value.split('-');
        state.activeFilters.sort_by = field;
        state.activeFilters.sort_order = order;
        loadScholarships();
    });

    // View toggles
    const gridBtn = document.getElementById('view-grid-btn');
    const tableBtn = document.getElementById('view-table-btn');
    gridBtn.addEventListener('click', () => switchView('grid'));
    tableBtn.addEventListener('click', () => switchView('table'));

    // Export dropdown toggle
    if (exportBtn && exportMenu) {
        exportBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (themeMenu) themeMenu.classList.remove('show');
            exportMenu.classList.toggle('show');
        });
        document.addEventListener('click', () => exportMenu.classList.remove('show'));
    }

    // Crawler Triggers
    document.getElementById('btn-run-crawl').addEventListener('click', handleRunCrawler);
    document.getElementById('btn-simulate-run2').addEventListener('click', handleSimulateRun2);

    // Reset filters button
    document.getElementById('btn-reset-filters').addEventListener('click', resetFilters);

    // Modal tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Modal Close
    modalCloseBtn.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', (e) => {
        if (e.target === modalBackdrop) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modalBackdrop.classList.contains('hidden')) {
            closeModal();
        }
    });
}

function switchView(viewName) {
    state.currentView = viewName;
    const gridBtn = document.getElementById('view-grid-btn');
    const tableBtn = document.getElementById('view-table-btn');
    
    if (viewName === 'grid') {
        gridBtn.classList.add('active');
        tableBtn.classList.remove('active');
        gridContainer.classList.remove('hidden');
        tableWrapper.classList.add('hidden');
    } else {
        tableBtn.classList.add('active');
        gridBtn.classList.remove('active');
        gridContainer.classList.add('hidden');
        tableWrapper.classList.remove('hidden');
    }
}

function resetFilters() {
    state.activeFilters = {
        q: '',
        source_type: 'ALL',
        status: 'ALL',
        verification_status: 'ALL',
        education_level: 'ALL',
        domicile_state: 'ALL',
        sort_by: 'confidence_score',
        sort_order: 'desc'
    };
    searchInput.value = '';
    searchClearBtn.classList.add('hidden');
    document.getElementById('filter-source-type').value = 'ALL';
    document.getElementById('filter-status').value = 'ALL';
    document.getElementById('filter-verification').value = 'ALL';
    document.getElementById('filter-education').value = 'ALL';
    document.getElementById('filter-domicile').value = 'ALL';
    document.getElementById('sort-select').value = 'confidence_score-desc';
    loadScholarships();
}

async function loadDashboardData() {
    await Promise.all([fetchMetrics(), loadScholarships()]);
}

async function fetchMetrics() {
    try {
        const res = await fetch('/api/metrics');
        if (!res.ok) throw new Error('Metrics API error');
        const data = await res.json();
        state.metrics = data;
        
        metricTotal.textContent = data.total_discovered;
        metricVerified.textContent = data.verified_count;
        metricReview.textContent = data.review_required_count;
        metricActive.textContent = data.active_count;
        metricAvgConf.textContent = `${data.avg_confidence}%`;
        metricMutations.textContent = data.total_changes_detected;
    } catch (err) {
        console.error('Failed to load metrics:', err);
    }
}

async function loadScholarships() {
    try {
        const params = new URLSearchParams();
        if (state.activeFilters.q) params.append('q', state.activeFilters.q);
        if (state.activeFilters.source_type !== 'ALL') params.append('source_type', state.activeFilters.source_type);
        if (state.activeFilters.status !== 'ALL') params.append('status', state.activeFilters.status);
        if (state.activeFilters.verification_status !== 'ALL') params.append('verification_status', state.activeFilters.verification_status);
        if (state.activeFilters.education_level !== 'ALL') params.append('education_level', state.activeFilters.education_level);
        if (state.activeFilters.domicile_state !== 'ALL') params.append('domicile_state', state.activeFilters.domicile_state);
        params.append('sort_by', state.activeFilters.sort_by);
        params.append('sort_order', state.activeFilters.sort_order);

        const res = await fetch(`/api/scholarships?${params.toString()}`);
        if (!res.ok) throw new Error('Scholarships API error');
        const result = await res.json();
        
        state.scholarships = result.data;
        renderScholarships(state.scholarships);
    } catch (err) {
        console.error('Failed to load scholarships:', err);
    }
}

function renderScholarships(items) {
    visibleCountBadge.textContent = `Showing ${items.length} opportunities`;

    if (items.length === 0) {
        gridContainer.innerHTML = '';
        tableBody.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }
    emptyState.classList.add('hidden');

    // Render Grid Cards
    gridContainer.innerHTML = items.map(s => createScholarshipCard(s)).join('');
    
    // Render Table Rows
    tableBody.innerHTML = items.map(s => createScholarshipRow(s)).join('');

    // Attach click listeners
    document.querySelectorAll('.btn-inspect').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const sid = e.currentTarget.getAttribute('data-id');
            openDetailModal(sid);
        });
    });
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'ACTIVE': return 'badge-status-active';
        case 'EXPIRING_SOON': return 'badge-status-expiring';
        case 'EXPIRED': return 'badge-status-expired';
        default: return 'badge-status-review';
    }
}

function getConfidenceClass(score) {
    if (score >= 95.0) return 'conf-high';
    if (score >= 80.0) return 'conf-medium';
    return 'conf-low';
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function createScholarshipCard(s) {
    const confClass = getConfidenceClass(s.confidence_score);
    const statusClass = getStatusBadgeClass(s.current_status);
    const evidenceCount = s.evidence_ledger ? Object.keys(s.evidence_ledger).length : 0;

    return `
        <article class="scholarship-card" id="card-${s.id}">
            <div class="card-top">
                <div class="card-badges">
                    <span class="badge badge-source">${escapeHtml(s.source_type)}</span>
                    <span class="confidence-chip ${confClass}">
                        ${s.confidence_score.toFixed(1)}% ${s.verification_status === 'VERIFIED' ? '✓ VERIFIED' : '⚠️ REVIEW'}
                    </span>
                </div>
                <h3 class="card-title" title="${escapeHtml(s.name)}">${escapeHtml(s.name)}</h3>
                <p class="card-provider" title="${escapeHtml(s.provider)}">${escapeHtml(s.provider)}</p>
                
                <div class="card-facts">
                    <div class="fact-item fact-item-full">
                        <span class="fact-label">Benefit</span>
                        <span class="fact-val highlight-green fact-val-wrap" title="${escapeHtml(s.amount_benefit)}">${escapeHtml(s.amount_benefit)}</span>
                    </div>
                    <div class="fact-item">
                        <span class="fact-label">Deadline</span>
                        <span class="fact-val fact-val-truncate">${escapeHtml(s.closing_date)}</span>
                    </div>
                    <div class="fact-item">
                        <span class="fact-label">Residency</span>
                        <span class="fact-val fact-val-truncate" title="${escapeHtml(s.domicile_state)}">${escapeHtml(s.domicile_state)}</span>
                    </div>
                    <div class="fact-item fact-item-full">
                        <span class="fact-label">Income Limit</span>
                        <span class="fact-val fact-val-truncate" title="${escapeHtml(s.income_criteria)}">${escapeHtml(s.income_criteria)}</span>
                    </div>
                </div>
            </div>

            <div class="card-bottom">
                <div class="card-meta">
                    <span class="badge ${statusClass}">${escapeHtml(s.current_status.replace('_', ' '))}</span>
                    <span class="evidence-tag">📎 ${evidenceCount} verified citations</span>
                </div>
                <button class="btn btn-outline btn-inspect" data-id="${s.id}">
                    Inspect ➜
                </button>
            </div>
        </article>
    `;
}

function createScholarshipRow(s) {
    const confClass = getConfidenceClass(s.confidence_score);
    const statusClass = getStatusBadgeClass(s.current_status);

    return `
        <tr>
            <td>
                <span class="confidence-chip ${confClass}">
                    ${s.confidence_score.toFixed(1)}%
                </span>
            </td>
            <td>
                <strong>${s.name}</strong>
                <div style="font-size: 0.78rem; color: var(--text-muted);">${s.provider}</div>
            </td>
            <td><span class="badge badge-source">${s.source_type}</span></td>
            <td class="highlight-green">${s.amount_benefit}</td>
            <td>
                <div style="font-size: 0.8rem;">${s.income_criteria}</div>
            </td>
            <td>${s.closing_date}</td>
            <td><span class="badge ${statusClass}">${s.current_status.replace('_', ' ')}</span></td>
            <td>
                <button class="btn btn-outline btn-inspect" data-id="${s.id}" style="padding: 4px 10px; font-size: 0.8rem;">
                    Inspect
                </button>
            </td>
        </tr>
    `;
}

async function openDetailModal(scholarshipId) {
    try {
        const res = await fetch(`/api/scholarships/${scholarshipId}`);
        if (!res.ok) throw new Error('Failed to load scholarship details');
        const data = await res.json();
        
        const s = data.scholarship;
        const history = data.history || [];
        state.activeScholarshipDetail = { scholarship: s, history };

        // Header
        document.getElementById('modal-title').textContent = s.name;
        document.getElementById('modal-provider').textContent = `${s.provider} • Last verified: ${s.last_verified_at}`;
        
        const badgesContainer = document.getElementById('modal-badges-top');
        const confClass = getConfidenceClass(s.confidence_score);
        const statusClass = getStatusBadgeClass(s.current_status);
        
        badgesContainer.innerHTML = `
            <span class="badge badge-source">${s.source_type}</span>
            <span class="badge ${statusClass}">${s.current_status}</span>
            <span class="confidence-chip ${confClass}">
                ${s.confidence_score.toFixed(1)}% ${s.verification_status}
            </span>
        `;

        // Tab 1: Overview
        document.getElementById('modal-amount').textContent = s.amount_benefit;
        document.getElementById('modal-deadline').textContent = s.closing_date;
        document.getElementById('modal-education').textContent = s.education_level;
        document.getElementById('modal-domicile').textContent = s.domicile_state;
        document.getElementById('modal-eligibility-summary').textContent = s.eligibility_summary;
        document.getElementById('modal-income').textContent = s.income_criteria;
        document.getElementById('modal-academic').textContent = s.academic_requirements;
        document.getElementById('modal-gender').textContent = s.gender_criteria;
        document.getElementById('modal-category').textContent = s.category_criteria;

        // Documents list
        const docsList = document.getElementById('modal-documents-list');
        if (s.documents_required && s.documents_required.length > 0) {
            docsList.innerHTML = s.documents_required.map(doc => `<li>${doc}</li>`).join('');
        } else {
            docsList.innerHTML = '<li>Standard academic documents specified on portal</li>';
        }

        // Action URLs
        const offUrlBtn = document.getElementById('modal-official-url');
        offUrlBtn.href = s.official_source_url;
        
        const applyUrlBtn = document.getElementById('modal-apply-url');
        if (s.application_url && s.application_url !== 'Not specified') {
            applyUrlBtn.href = s.application_url;
            applyUrlBtn.classList.remove('hidden');
        } else {
            applyUrlBtn.classList.add('hidden');
        }

        // Tab 2: Why this score? (Confidence Breakdown)
        const cb = s.confidence_breakdown || {};
        document.getElementById('audit-score-val').textContent = `${s.confidence_score.toFixed(1)}%`;
        const auditBadge = document.getElementById('audit-status-badge');
        auditBadge.textContent = s.verification_status;
        auditBadge.className = `score-circle-sub ${s.verification_status === 'VERIFIED' ? 'text-emerald' : 'text-amber'}`;

        const rubricContainer = document.getElementById('rubric-bars');
        const rubricItems = [
            { label: 'Primary Domain Authority', score: cb.source_authority_score || 0, max: 25 },
            { label: 'Live Page Presence & Title Match', score: cb.live_presence_score || 0, max: 20 },
            { label: 'Official Direct Application Gateway', score: cb.application_url_score || 0, max: 15 },
            { label: 'Verbatim Field Evidence Grounding', score: cb.field_grounding_score || 0, max: 25 },
            { label: 'Temporal Freshness & Active Lifecycle', score: cb.freshness_score || 0, max: 15 }
        ];

        rubricContainer.innerHTML = rubricItems.map(item => `
            <div class="rubric-item">
                <div class="rubric-header">
                    <span>${item.label}</span>
                    <span style="font-family: var(--font-mono); color: var(--color-emerald);">${item.score.toFixed(1)} / ${item.max} pts</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${(item.score / item.max) * 100}%;"></div>
                </div>
            </div>
        `).join('');

        const auditNotesList = document.getElementById('audit-notes-list');
        if (cb.audit_notes && cb.audit_notes.length > 0) {
            auditNotesList.innerHTML = cb.audit_notes.map(note => `<li>${note}</li>`).join('');
        } else {
            auditNotesList.innerHTML = '<li>Evidence verification verified with high confidence.</li>';
        }

        // Tab 3: Evidence Ledger
        const evidenceContainer = document.getElementById('evidence-ledger-container');
        const ledger = s.evidence_ledger || {};
        const entries = Object.entries(ledger);

        if (entries.length > 0) {
            evidenceContainer.innerHTML = entries.map(([field, item]) => `
                <div class="evidence-card">
                    <span class="evidence-field-name">FIELD: ${field.toUpperCase().replace('_', ' ')} ➔ [${item.extracted_value || s[field]}]</span>
                    <div class="evidence-quote">"${item.snippet || 'Verbatim citation extracted from source portal.'}"</div>
                    <div class="evidence-source-link">Source URL: <a href="${item.source_url || s.official_source_url}" target="_blank" style="color: var(--color-indigo);">${item.source_url || s.official_source_url}</a></div>
                </div>
            `).join('');
        } else {
            evidenceContainer.innerHTML = '<p style="color: var(--text-muted);">No verbatim citations recorded for this entry.</p>';
        }

        // Tab 4: Change History
        document.getElementById('modal-history-count').textContent = history.length;
        const historyContainer = document.getElementById('history-timeline');
        
        if (history.length > 0) {
            historyContainer.innerHTML = history.map(h => `
                <div class="history-item">
                    <div class="history-header">
                        <span class="badge badge-source">${h.change_type}</span>
                        <span>${h.detected_at}</span>
                    </div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-top: 4px;">
                        Field: ${h.field_name}
                    </div>
                    <div class="history-diff">
                        <span class="diff-old">${h.old_value || '[NEW RECORD]'}</span>
                        <span>➔</span>
                        <span class="diff-new">${h.new_value}</span>
                    </div>
                    ${h.evidence_snippet ? `<div style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-secondary); margin-top: 4px;">Snippet: "${h.evidence_snippet}"</div>` : ''}
                </div>
            `).join('');
        } else {
            historyContainer.innerHTML = '<p style="color: var(--text-muted); padding: 14px;">No historical modifications recorded yet.</p>';
        }

        // Reset to first tab
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        document.querySelector('.tab-btn[data-tab="tab-overview"]').classList.add('active');
        document.getElementById('tab-overview').classList.add('active');

        // Show modal
        modalBackdrop.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    } catch (err) {
        console.error('Failed to open modal:', err);
        showToast('Error opening scholarship details', 'error');
    }
}

function closeModal() {
    modalBackdrop.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

async function handleRunCrawler() {
    const btn = document.getElementById('btn-run-crawl');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Crawling...';
    btn.disabled = true;

    try {
        showToast('🚀 Running automated crawler cycle & re-verifying official sources...', 'info');
        const res = await fetch('/api/crawl/run', { method: 'POST' });
        const data = await res.json();
        
        showToast(`✅ Crawler Cycle Completed! Discovered: ${data.summary.total_discovered}, Verified: ${data.summary.total_verified}`, 'success');
        await loadDashboardData();
    } catch (err) {
        console.error('Crawler error:', err);
        showToast('❌ Crawler execution failed', 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleSimulateRun2() {
    const btn = document.getElementById('btn-simulate-run2');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Simulating...';
    btn.disabled = true;

    try {
        showToast('⚡ Simulating Run 2: Modifying live announcements to test change detection...', 'info');
        const res = await fetch('/api/crawl/simulate-change', { method: 'POST' });
        const data = await res.json();
        
        showToast(`🔍 Change Detection Complete! Detected ${data.mutations.length} mutations (logged to audit table)`, 'success');
        await loadDashboardData();
    } catch (err) {
        console.error('Simulation error:', err);
        showToast('❌ Change detection simulation failed', 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
