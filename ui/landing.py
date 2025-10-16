import streamlit as st


def display_landing_page():
    """Display a formal and sophisticated landing page when no messages exist."""

    # Apply custom CSS for landing page
    st.markdown("""
    <style>
    /* Landing page specific styles */
    .landing-hero {
        text-align: center;
        padding: 1.5rem 1rem 1rem 1rem;
    }

    .landing-logo {
        font-size: 2.25rem; 
    }

    .landing-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f3f4f6;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }

    .landing-subtitle {
        font-size: 1rem;
        color: #9ca3af;
        margin: 0 auto 1rem auto;
        max-width: 700px;
        line-height: 1.5;
    }

    .feature-card {
        background: rgba(32, 35, 42, 0.6);
        border: 1px solid rgba(64, 68, 78, 0.3);
        border-radius: 0.875rem;
        padding: 1.25rem;
        height: 100%;
        transition: all 0.3s ease;
        backdrop-filter: blur(12px);
        margin-bottom: 1rem;
    }

    .feature-card:hover {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(91, 143, 212, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    .feature-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e5e7eb;
        margin-bottom: 0.5rem;
    }

    .feature-description {
        font-size: 0.875rem;
        color: #9ca3af;
        line-height: 1.5;
    }

    .cta-section {
        text-align: center;
        padding: 1rem 1rem 0.5rem 1rem;
    }

    .cta-text {
        font-size: 0.95rem;
        color: #6b7280;
    }

    .highlight {
        color: #60a5fa;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero section
    st.markdown("""
    <div class="landing-hero">
        <div class="landing-logo">💬</div>
        <h2 class="landing-title">SK Shieldus Chat Bot</h2>
 
    </div>
    """, unsafe_allow_html=True)

    # Feature cards in 2x2 grid
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔍</span>
            <div class="feature-title">Natural Language Queries</div>
            <div class="feature-description">
                Ask questions in plain language. Our AI understands context and generates precise SQL queries automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Advanced Visualizations</div>
            <div class="feature-description">
                Interactive charts, geospatial maps, and data tables rendered in real-time for comprehensive analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Second row
    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🗺️</span>
            <div class="feature-title">Geospatial Analysis</div>
            <div class="feature-description">
                Automatic detection and visualization of geographic data with polygon and point-based mapping.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <div class="feature-title">Real-time Processing</div>
            <div class="feature-description">
                Instant query execution with visual feedback and session persistence across conversations.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # CTA section
    st.markdown("""
    <div class="cta-section">
        <p class="cta-text">
            Start by typing your question below or explore <span class="highlight">sample queries</span> from the sidebar
        </p>
    </div>
    """, unsafe_allow_html=True)
