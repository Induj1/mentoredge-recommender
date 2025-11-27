"""
MentorEdge Frontend - Web Interface

A Streamlit-based web interface for easy interaction with the recommendation engine.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

from semantic_scholar_client import SemanticScholarClient
from recommender import PaperRecommender, UserProfile


# Page configuration
st.set_page_config(
    page_title="MentorEdge - Paper Recommendation Engine",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .paper-card {
        background-color: #ffffff;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .paper-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .paper-authors {
        color: #666;
        font-style: italic;
        margin-bottom: 0.5rem;
    }
    .paper-meta {
        display: flex;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    .score-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


def create_user_profile_from_input():
    """Create UserProfile from form inputs."""
    name = st.session_state.get('name', '')
    interests = [x.strip() for x in st.session_state.get('interests', '').split(',') if x.strip()]
    keywords = [x.strip() for x in st.session_state.get('keywords', '').split(',') if x.strip()]
    
    min_year = st.session_state.get('min_year', None)
    if min_year == '' or min_year is None:
        min_year = None
    else:
        min_year = int(min_year)
    
    weights = {
        "relevance": float(st.session_state.get('weight_relevance', 0.5)),
        "citations": float(st.session_state.get('weight_citations', 0.3)),
        "recency": float(st.session_state.get('weight_recency', 0.2))
    }
    
    return UserProfile(
        name=name if name else "User",
        research_interests=interests,
        primary_keywords=keywords,
        min_year=min_year,
        scoring_weights=weights
    )


def display_paper_card(paper, score, relevance, citations, recency, keywords_matched, index):
    """Display a paper recommendation card."""
    paper_id = paper.paperId or "N/A"
    title = paper.title or "No title"
    authors = ', '.join(paper.authors[:3])
    if len(paper.authors) > 3:
        authors += f" + {len(paper.authors) - 3} more"
    
    year = paper.year or "N/A"
    citation_count = paper.citationCount or 0
    abstract = paper.abstract or "No abstract available"
    url = paper.url or ""
    
    # Truncate abstract if too long
    if len(abstract) > 300:
        abstract = abstract[:300] + "..."
    
    st.markdown(f"""
    <div class="paper-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <div class="paper-title">{index}. {title}</div>
                <div class="paper-authors">{authors}</div>
                <div class="paper-meta">
                    <span><strong>Year:</strong> {year}</span>
                    <span><strong>Citations:</strong> {citation_count:,}</span>
                    <span class="score-badge">Score: {score:.4f}</span>
                </div>
                <div style="margin-top: 0.5rem; margin-bottom: 0.5rem;">
                    <strong>Matched Keywords:</strong> {', '.join(keywords_matched)}
                </div>
                <div style="margin-top: 0.5rem; color: #555; font-size: 0.95rem;">
                    {abstract}
                </div>
                <div style="margin-top: 0.5rem;">
                    <strong>Score Breakdown:</strong> 
                    Relevance={relevance:.3f}, 
                    Citations={citations:.3f}, 
                    Recency={recency:.3f}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if url:
        st.markdown(f"[🔗 View Paper on Semantic Scholar]({url})")
    
    st.markdown("---")


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">📚 MentorEdge</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Academic Paper Recommendation Engine</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key
        st.subheader("API Settings")
        api_key = st.text_input(
            "Semantic Scholar API Key (Optional)",
            value=os.getenv("SEMANTIC_SCHOLAR_API_KEY", ""),
            type="password",
            help="Leave empty to use public rate limits (5 req/sec). Get a key from https://www.semanticscholar.org/product/api"
        )
        
        st.divider()
        
        # User Profile Input
        st.subheader("User Profile")
        
        name = st.text_input(
            "Your Name",
            value="",
            key="name",
            placeholder="Mr Induj Gupta"
        )
        
        interests_input = st.text_area(
            "Research Interests (comma-separated)",
            value="",
            key="interests",
            placeholder="Graph Neural Networks, Large Language Models, Transformer Architecture",
            help="Enter your research interests, separated by commas"
        )
        
        keywords_input = st.text_area(
            "Primary Keywords for Search (comma-separated)",
            value="",
            key="keywords",
            placeholder="graph neural networks, transformer architecture, language models",
            help="Enter keywords to search for papers, separated by commas"
        )
        
        min_year = st.number_input(
            "Minimum Publication Year",
            min_value=1900,
            max_value=datetime.now().year,
            value=2020,
            key="min_year",
            help="Only show papers published on or after this year"
        )
        
        st.divider()
        
        # Scoring Weights
        st.subheader("Scoring Weights")
        st.caption("Adjust how much each factor influences recommendations")
        
        weight_relevance = st.slider(
            "Relevance Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            key="weight_relevance",
            help="How much to prioritize search ranking position"
        )
        
        weight_citations = st.slider(
            "Citations Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            key="weight_citations",
            help="How much to prioritize citation count"
        )
        
        weight_recency = st.slider(
            "Recency Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.1,
            key="weight_recency",
            help="How much to prioritize recent publications"
        )
        
        # Normalize weights
        total_weight = weight_relevance + weight_citations + weight_recency
        if total_weight > 0:
            normalized_relevance = weight_relevance / total_weight
            normalized_citations = weight_citations / total_weight
            normalized_recency = weight_recency / total_weight
            
            st.caption(f"Normalized: Relevance={normalized_relevance:.2f}, "
                      f"Citations={normalized_citations:.2f}, "
                      f"Recency={normalized_recency:.2f}")
        
        st.divider()
        
        # Search Parameters
        st.subheader("Search Parameters")
        papers_per_keyword = st.number_input(
            "Papers per Keyword",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="Number of papers to fetch for each keyword"
        )
        
        top_n = st.number_input(
            "Top N Recommendations",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            help="Number of top recommendations to return"
        )
        
        st.divider()
        
        # Generate Button
        generate_btn = st.button(
            " Generate Recommendations",
            type="primary",
            use_container_width=True
        )
        
        # Clear Button
        if st.button(" Clear Results", use_container_width=True):
            st.session_state.recommendations = None
            st.rerun()
    
    # Main content area
    if generate_btn:
        # Validate inputs
        if not keywords_input or not keywords_input.strip():
            st.error(" Please enter at least one keyword for search.")
            return
        
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        if not keywords:
            st.error(" Please enter valid keywords (comma-separated).")
            return
        
        # Create user profile
        user_profile = create_user_profile_from_input()
        # Normalize weights
        total = sum(user_profile.scoring_weights.values())
        if total > 0:
            user_profile.scoring_weights = {
                k: v / total
                for k, v in user_profile.scoring_weights.items()
            }
        
        # Initialize client and recommender
        with st.spinner("Initializing recommendation engine..."):
            client = SemanticScholarClient(
                api_key=api_key if api_key else None,
                requests_per_second=5.0,
                timeout=30
            )
            
            recommender = PaperRecommender(client, user_profile)
        
        # Generate recommendations
        st.session_state.processing = True
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text(" Searching for papers...")
            progress_bar.progress(10)
            
            recommendations = recommender.build_personalized_recommendations(
                papers_per_keyword=papers_per_keyword,
                top_n=top_n
            )
            
            progress_bar.progress(100)
            status_text.text("Recommendations generated successfully!")
            
            st.session_state.recommendations = recommendations
            st.session_state.user_profile = user_profile
            
            # Small delay then clear progress
            import time
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f" Error generating recommendations: {str(e)}")
            st.exception(e)
            st.session_state.processing = False
            return
    
    # Display results
    if st.session_state.recommendations:
        recommendations = st.session_state.recommendations
        
        # Statistics
        st.header("📊 Recommendation Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Recommendations", len(recommendations))
        
        avg_score = sum(r.score for r in recommendations) / len(recommendations) if recommendations else 0
        with col2:
            st.metric("Average Score", f"{avg_score:.4f}")
        
        total_citations = sum(r.paper.citationCount or 0 for r in recommendations)
        with col3:
            st.metric("Total Citations", f"{total_citations:,}")
        
        avg_year = sum(r.paper.year or 0 for r in recommendations if r.paper.year) / len([r for r in recommendations if r.paper.year]) if recommendations else 0
        with col4:
            st.metric("Average Year", f"{avg_year:.0f}" if avg_year > 0 else "N/A")
        
        st.divider()
        
        # Export to CSV
        st.header("📥 Export Options")
        csv_data = []
        for r in recommendations:
            paper = r.paper
            csv_data.append({
                'paperId': paper.paperId or '',
                'title': paper.title or '',
                'authors': '; '.join(paper.authors) if paper.authors else '',
                'year': paper.year or '',
                'abstract': paper.abstract or '',
                'citationCount': paper.citationCount or 0,
                'url': paper.url or '',
                'score': f"{r.score:.4f}",
                'relevance_norm': f"{r.relevance_norm:.4f}",
                'citations_norm': f"{r.citations_norm:.4f}",
                'recency_norm': f"{r.recency_norm:.4f}",
                'matched_keywords': ', '.join(r.matched_keywords)
            })
        
        df = pd.DataFrame(csv_data)
        
        csv_string = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_string,
            file_name=f"mentoredge_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.divider()
        
        # Display papers
        st.header(f"📚 Top {len(recommendations)} Recommendations")
        
        # Search/filter box
        search_query = st.text_input(
            "🔍 Search recommendations",
            placeholder="Search by title, authors, or keywords..."
        )
        
        # Filter recommendations
        filtered_recommendations = recommendations
        if search_query:
            query_lower = search_query.lower()
            filtered_recommendations = [
                r for r in recommendations
                if (query_lower in r.paper.title.lower() if r.paper.title else False) or
                   any(query_lower in author.lower() for author in r.paper.authors) or
                   any(query_lower in kw.lower() for kw in r.matched_keywords)
            ]
        
        if not filtered_recommendations:
            st.info("No recommendations match your search query.")
        else:
            st.caption(f"Showing {len(filtered_recommendations)} of {len(recommendations)} recommendations")
            
            # Display each paper
            for idx, scored_paper in enumerate(filtered_recommendations, 1):
                display_paper_card(
                    scored_paper.paper,
                    scored_paper.score,
                    scored_paper.relevance_norm,
                    scored_paper.citations_norm,
                    scored_paper.recency_norm,
                    scored_paper.matched_keywords,
                    idx
                )
    else:
        # Welcome message
        st.info("""
         **Welcome to MentorEdge!**
        
        Get started by:
        1.  Enter your research interests and keywords in the sidebar
        2. Configure your preferences (min year, scoring weights)
        3.  Click "Generate Recommendations" to get personalized paper suggestions
        
        The system will search for papers matching your keywords and rank them based on:
        - **Relevance**: How well they match your search terms
        - **Citations**: Impact measured by citation count
        - **Recency**: Publication date (newer papers preferred)
        """)
        
        # Example profile
        with st.expander("See Example Configuration"):
            st.markdown("""
            **Name:** Dr. Jane Researcher
            
            **Research Interests:** Graph Neural Networks, Large Language Models, Transformer Architecture
            
            **Primary Keywords:** graph neural networks, transformer architecture, language models, graph learning
            
            **Minimum Year:** 2020
            
            **Scoring Weights:**
            - Relevance: 0.5
            - Citations: 0.3
            - Recency: 0.2
            """)


if __name__ == "__main__":
    main()

