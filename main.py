"""
MentorEdge - Academic Paper Recommendation Engine

Main entry point demonstrating usage of the recommendation system.
"""

from semantic_scholar_client import SemanticScholarClient
from recommender import PaperRecommender, UserProfile


def main():
    """Demonstrate the MentorEdge recommendation system."""
    
    print("=" * 70)
    print("MentorEdge - Academic Paper Recommendation Engine")
    print("=" * 70)
    print()
    
    # Initialize the Semantic Scholar API client
    # Note: API key is optional but recommended for higher rate limits
    # Set SEMANTIC_SCHOLAR_API_KEY environment variable if you have one
    import os
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", None)
    
    if api_key:
        print("✓ API key found - using authenticated requests")
    else:
        print("ℹ No API key found - using public rate limits (5 req/sec)")
        print("  Set SEMANTIC_SCHOLAR_API_KEY environment variable for higher limits")
    
    print()
    
    client = SemanticScholarClient(
        api_key=api_key,
        requests_per_second=5.0,  # Conservative rate limiting
        timeout=30
    )
    
    # Create a sample user profile
    # Example: AI researcher interested in Graph Neural Networks and LLMs
    user_profile = UserProfile(
        name="Dr. Jane Researcher",
        research_interests=[
            "Graph Neural Networks",
            "Large Language Models",
            "Transformer Architecture",
            "Graph Representation Learning"
        ],
        primary_keywords=[
            "graph neural networks",
            "transformer architecture",
            "language models",
            "graph learning"
        ],
        min_year=2020,  # Only papers from 2020 onwards
        scoring_weights={
            "relevance": 0.5,   # Emphasize search ranking
            "citations": 0.3,   # Consider impact
            "recency": 0.2      # Slight preference for recent work
        }
    )
    
    print("User Profile:")
    print(f"  Name: {user_profile.name}")
    print(f"  Research Interests: {', '.join(user_profile.research_interests)}")
    print(f"  Primary Keywords: {', '.join(user_profile.primary_keywords)}")
    print(f"  Minimum Year: {user_profile.min_year}")
    print(f"  Scoring Weights: {user_profile.scoring_weights}")
    print()
    
    # Initialize the recommender
    recommender = PaperRecommender(
        client=client,
        user_profile=user_profile
    )
    
    # Build personalized recommendations
    print("=" * 70)
    print("Building Recommendations...")
    print("=" * 70)
    
    try:
        recommendations = recommender.build_personalized_recommendations(
            papers_per_keyword=50,  # Fetch 50 papers per keyword
            top_n=20                # Return top 20 recommendations
        )
        
        if not recommendations:
            print("\nNo recommendations generated. Please check your keywords.")
            return
        
        # Display top recommendations
        print("\n" + "=" * 70)
        print(f"Top {len(recommendations)} Recommendations")
        print("=" * 70)
        print()
        
        for idx, scored_paper in enumerate(recommendations, 1):
            paper = scored_paper.paper
            print(f"{idx}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}" + 
                  (f" + {len(paper.authors) - 3} more" if len(paper.authors) > 3 else ""))
            print(f"   Year: {paper.year or 'N/A'} | "
                  f"Citations: {paper.citationCount or 0} | "
                  f"Score: {scored_paper.score:.4f}")
            print(f"   Matched Keywords: {', '.join(scored_paper.matched_keywords)}")
            if paper.url:
                print(f"   URL: {paper.url}")
            print(f"   Score Breakdown: "
                  f"Relevance={scored_paper.relevance_norm:.3f}, "
                  f"Citations={scored_paper.citations_norm:.3f}, "
                  f"Recency={scored_paper.recency_norm:.3f}")
            print()
        
        # Export to CSV
        print("=" * 70)
        recommender.export_to_csv(recommendations, "sample_output.csv")
        print("=" * 70)
        print()
        print("✓ Recommendations successfully generated and exported!")
        
    except Exception as e:
        print(f"\n❌ Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

