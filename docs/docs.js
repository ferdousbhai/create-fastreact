// FastReact Documentation

// Documentation structure
const DOCS = [
    {
        slug: 'why-fastreact',
        title: 'Why FastReact?',
        file: 'docs/why-fastreact.md'
    },
    {
        slug: 'get-started',
        title: 'Quickstart',
        file: 'docs/get-started.md'
    },
    {
        slug: 'deploy-cloudflare',
        title: 'Deploy to Cloudflare',
        file: 'docs/deploy-cloudflare.md'
    },
    {
        slug: 'deploy-modal',
        title: 'Deploy to Modal',
        file: 'docs/deploy-modal.md'
    },
    {
        slug: 'add-ai',
        title: 'Add AI Features',
        file: 'docs/add-ai.md'
    }
];

// State
let currentDoc = 'why-fastreact';

// Initialize
async function init() {
    // Get doc from URL
    const params = new URLSearchParams(window.location.search);
    currentDoc = params.get('doc') || 'why-fastreact';

    // Load the document
    await loadDoc(currentDoc);

    // Set up navigation
    setupNavigation();

    // Set up mobile sidebar toggle
    setupMobileSidebar();
}

// Load a document
async function loadDoc(slug) {
    const doc = DOCS.find(d => d.slug === slug);
    if (!doc) {
        showError('Document not found');
        return;
    }

    const contentEl = document.getElementById('doc-content');

    try {
        // Use relative path for GitHub Pages compatibility
        const docPath = doc.file;
        const response = await fetch(docPath);
        if (!response.ok) throw new Error('Failed to fetch document');

        const markdown = await response.text();
        const html = marked.parse(markdown);

        contentEl.innerHTML = html;

        // Highlight code blocks
        document.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });

        // Update page title
        document.title = `${doc.title} - FastReact`;

        // Update sidebar active state
        updateSidebarActive(slug);

        // Update prev/next navigation
        updateDocNav(slug);

        // Scroll to top
        window.scrollTo(0, 0);

    } catch (error) {
        console.error('Error loading document:', error);
        showError('Failed to load documentation');
    }
}

// Show error message
function showError(message) {
    const contentEl = document.getElementById('doc-content');
    contentEl.innerHTML = `
        <div style="text-align: center; padding: 48px; color: var(--color-text-muted);">
            <p>${message}</p>
            <a href="/" style="color: var(--color-accent);">Go back to Quickstart</a>
        </div>
    `;
}

// Update sidebar active state
function updateSidebarActive(slug) {
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.doc === slug) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Update prev/next navigation
function updateDocNav(slug) {
    const navEl = document.getElementById('doc-nav');
    const currentIndex = DOCS.findIndex(d => d.slug === slug);

    const prevDoc = currentIndex > 0 ? DOCS[currentIndex - 1] : null;
    const nextDoc = currentIndex < DOCS.length - 1 ? DOCS[currentIndex + 1] : null;

    let html = '';

    if (prevDoc) {
        const prevUrl = prevDoc.slug === 'why-fastreact' ? '/' : `?doc=${prevDoc.slug}`;
        html += `
            <a href="${prevUrl}" class="doc-nav-link prev" data-doc="${prevDoc.slug}">
                <span class="doc-nav-label">← Previous</span>
                <span class="doc-nav-title">${prevDoc.title}</span>
            </a>
        `;
    } else {
        html += '<div></div>';
    }

    if (nextDoc) {
        html += `
            <a href="?doc=${nextDoc.slug}" class="doc-nav-link next" data-doc="${nextDoc.slug}">
                <span class="doc-nav-label">Next →</span>
                <span class="doc-nav-title">${nextDoc.title}</span>
            </a>
        `;
    } else {
        html += '<div></div>';
    }

    navEl.innerHTML = html;
}

// Set up navigation click handlers
function setupNavigation() {
    document.addEventListener('click', async (e) => {
        const link = e.target.closest('[data-doc]');
        if (!link) return;

        e.preventDefault();

        const slug = link.dataset.doc;
        if (slug === currentDoc) return;

        currentDoc = slug;

        // Update URL
        const url = slug === 'why-fastreact'
            ? '/'
            : `?doc=${slug}`;
        history.pushState({ doc: slug }, '', url);

        // Load the document
        await loadDoc(slug);

        // Close mobile sidebar
        document.querySelector('.sidebar').classList.remove('open');
    });

    // Handle browser back/forward
    window.addEventListener('popstate', async (e) => {
        const params = new URLSearchParams(window.location.search);
        const slug = params.get('doc') || 'why-fastreact';

        if (slug !== currentDoc) {
            currentDoc = slug;
            await loadDoc(slug);
        }
    });
}

// Set up mobile sidebar toggle
function setupMobileSidebar() {
    const toggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// Configure marked
marked.setOptions({
    breaks: true,
    gfm: true
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
