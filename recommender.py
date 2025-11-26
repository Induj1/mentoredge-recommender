"""
Intelligent paper recommendation engine.

This module provides personalized paper recommendations based on user profiles,
combining relevance, citation impact, and recency scoring.
"""

import csv
import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

from semantic_scholar_client import Paper, SemanticScholarClient


@dataclass
class UserProfile:
    """User profile for personalized recommendations."""
    name: str
    research_interests: List[str]
    primary_keywords: List[str]
    min_year: Optional[int] = None
    scoring_weights: Dict[str, float] = field(default_factory=lambda: {
        "relevance": 0.5,
        "citations": 0.3,
        "recency": 0.2
    })
    
    def __post_init__(self):
        """Validate scoring weights sum to approximately 1.0."""
        total = sum(self.scoring_weights.values())
        if abs(total - 1.0) > 0.01:
            # Normalize weights if they don't sum to 1.0
            self.scoring_weights = {
                k: v / total
                for k, v in self.scoring_weights.items()
            }


@dataclass
class ScoredPaper:
    """Paper with recommendation scores."""
    paper: Paper
    score: float
    relevance_norm: float
    citations_norm: float
    recency_norm: float
    matched_keywords: List[str]  # Keywords that matched this paper


class PaperRecommender:
    """
    Intelligent paper recommendation engine.
    
    Combines multiple signals (relevance, citations, recency) to generate
    personalized recommendations for researchers.
    """
    
    def __init__(
        self,
        client: SemanticScholarClient,
        user_profile: UserProfile
    ):
        """
        Initialize the recommender with a client and user profile.
        
        Args:
            client: SemanticScholarClient instance
            user_profile: UserProfile with preferences and weights
        """
        self.client = client
        self.user_profile = user_profile
    
    def _normalize_relevance(
        self,
        position: int,
        total_results: int
    ) -> float:
        """
        Normalize relevance score based on ranking position.
        
        Higher-ranked papers (lower position index) get higher scores.
        Uses a logarithmic decay to emphasize top results.
        
        Args:
            position: Position in search results (0-indexed)
            total_results: Total number of results
            
        Returns:
            Normalized relevance score [0.0, 1.0]
        """
        if total_results == 0:
            return 0.0
        
        # Normalize position to [0, 1]
        normalized_position = position / max(total_results - 1, 1)
        
        # Use exponential decay: higher rank = higher score
        # Top result gets 1.0, bottom gets ~0.1
        relevance = math.exp(-2 * normalized_position)
        
        return relevance
    
    def _normalize_citations(
        self,
        citation_count: Optional[int],
        max_citations: int
    ) -> float:
        """
        Normalize citation count using log scaling.
        
        Citation counts can vary wildly (0 to thousands), so we use
        log scaling to compress the range while maintaining relative order.
        
        Args:
            citation_count: Number of citations (None treated as 0)
            max_citations: Maximum citation count in the dataset
            
        Returns:
            Normalized citation score [0.0, 1.0]
        """
        if citation_count is None or citation_count == 0:
            return 0.0
        
        if max_citations == 0:
            return 0.0
        
        # Log scaling: log(1 + citations) / log(1 + max_citations)
        # +1 prevents log(0) and gives some credit to low-citation papers
        log_citations = math.log(1 + citation_count)
        log_max = math.log(1 + max_citations)
        
        return log_citations / log_max
    
    def _normalize_recency(
        self,
        year: Optional[int],
        current_year: Optional[int] = None
    ) -> float:
        """
        Normalize year for recency scoring.
        
        More recent papers get higher scores. Papers older than
        the user's min_year get penalized.
        
        Args:
            year: Publication year (None treated as very old)
            current_year: Current year for normalization (defaults to 2024)
            
        Returns:
            Normalized recency score [0.0, 1.0]
        """
        if current_year is None:
            current_year = datetime.now().year
        
        if year is None:
            # Papers without year get minimum score
            return 0.1
        
        # Filter out papers before min_year
        if self.user_profile.min_year and year < self.user_profile.min_year:
            return 0.0
        
        # Normalize: (year - oldest_year) / (current_year - oldest_year)
        # Use last 20 years as reference range
        oldest_year = max(current_year - 20, 2000)
        
        if year < oldest_year:
            return 0.1  # Very old papers get minimal score
        
        recency = (year - oldest_year) / (current_year - oldest_year)
        
        # Ensure score is in [0.1, 1.0] range
        return max(0.1, min(1.0, recency))
    
    def _deduplicate_papers(
        self,
        papers: List[Paper]
    ) -> List[Paper]:
        """
        Remove duplicate papers based on paperId.
        
        Args:
            papers: List of papers that may contain duplicates
            
        Returns:
            Deduplicated list of papers
        """
        seen = set()
        unique_papers = []
        
        for paper in papers:
            if paper.paperId and paper.paperId not in seen:
                seen.add(paper.paperId)
                unique_papers.append(paper)
        
        return unique_papers
    
    def build_personalized_recommendations(
        self,
        papers_per_keyword: int = 50,
        top_n: int = 20
    ) -> List[ScoredPaper]:
        """
        Build personalized recommendations for the user profile.
        
        Process:
        1. Fetch papers for each keyword in primary_keywords
        2. Deduplicate papers across keywords
        3. Score each paper using weighted combination of:
           - Relevance (based on search ranking)
           - Citations (log-scaled impact)
           - Recency (year normalization)
        4. Return top N papers sorted by score
        
        Args:
            papers_per_keyword: Number of papers to fetch per keyword
            top_n: Number of top recommendations to return
            
        Returns:
            List of ScoredPaper objects, sorted by score (highest first)
        """
        print(f"Building recommendations for {self.user_profile.name}...")
        print(f"Keywords: {', '.join(self.user_profile.primary_keywords)}")
        
        # Step 1: Fetch papers for each keyword
        all_papers = []
        keyword_positions = {}  # Track position for relevance scoring
        
        for keyword in self.user_profile.primary_keywords:
            print(f"\nFetching papers for keyword: '{keyword}'")
            try:
                papers = self.client.search_papers(
                    query=keyword,
                    limit=papers_per_keyword,
                    min_citations=0,
                    year_range=(
                        self.user_profile.min_year,
                        datetime.now().year
                    ) if self.user_profile.min_year else None
                )
                
                # Store position information for relevance scoring
                for idx, paper in enumerate(papers):
                    if paper.paperId not in keyword_positions:
                        keyword_positions[paper.paperId] = []
                    keyword_positions[paper.paperId].append({
                        'keyword': keyword,
                        'position': idx,
                        'total': len(papers)
                    })
                
                all_papers.extend(papers)
                print(f"  Found {len(papers)} papers")
                
            except Exception as e:
                print(f"  Error fetching papers for '{keyword}': {e}")
                continue
        
        # Step 2: Deduplicate papers
        print(f"\nTotal papers fetched: {len(all_papers)}")
        unique_papers = self._deduplicate_papers(all_papers)
        print(f"Unique papers after deduplication: {len(unique_papers)}")
        
        if not unique_papers:
            print("No papers found. Please check your keywords.")
            return []
        
        # Step 3: Calculate normalization factors
        max_citations = max(
            (p.citationCount or 0 for p in unique_papers),
            default=1
        )
        current_year = datetime.now().year
        
        # Step 4: Score each paper
        scored_papers = []
        weights = self.user_profile.scoring_weights
        
        for paper in unique_papers:
            # Calculate relevance: use best (highest) ranking across keywords
            relevance_scores = []
            matched_keywords = []
            
            for match_info in keyword_positions.get(paper.paperId, []):
                relevance = self._normalize_relevance(
                    match_info['position'],
                    match_info['total']
                )
                relevance_scores.append(relevance)
                matched_keywords.append(match_info['keyword'])
            
            relevance_norm = max(relevance_scores) if relevance_scores else 0.0
            
            # Calculate citation score
            citations_norm = self._normalize_citations(
                paper.citationCount,
                max_citations
            )
            
            # Calculate recency score
            recency_norm = self._normalize_recency(
                paper.year,
                current_year
            )
            
            # Combined weighted score
            score = (
                weights.get("relevance", 0.5) * relevance_norm +
                weights.get("citations", 0.3) * citations_norm +
                weights.get("recency", 0.2) * recency_norm
            )
            
            scored_paper = ScoredPaper(
                paper=paper,
                score=score,
                relevance_norm=relevance_norm,
                citations_norm=citations_norm,
                recency_norm=recency_norm,
                matched_keywords=matched_keywords
            )
            
            scored_papers.append(scored_paper)
        
        # Step 5: Sort by score and return top N
        scored_papers.sort(key=lambda x: x.score, reverse=True)
        top_papers = scored_papers[:top_n]
        
        print(f"\nReturning top {len(top_papers)} recommendations")
        print("\nScoring breakdown:")
        print(f"  Weights: Relevance={weights.get('relevance', 0):.2f}, "
              f"Citations={weights.get('citations', 0):.2f}, "
              f"Recency={weights.get('recency', 0):.2f}")
        
        return top_papers
    
    def export_to_csv(
        self,
        scored_papers: List[ScoredPaper],
        filename: str = "sample_output.csv"
    ) -> None:
        """
        Export scored recommendations to CSV file.
        
        Args:
            scored_papers: List of ScoredPaper objects to export
            filename: Output CSV filename
        """
        if not scored_papers:
            print("No papers to export.")
            return
        
        print(f"\nExporting {len(scored_papers)} recommendations to {filename}...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'paperId',
                'title',
                'authors',
                'year',
                'abstract',
                'citationCount',
                'url',
                'score',
                'relevance_norm',
                'citations_norm',
                'recency_norm',
                'matched_keywords'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for scored_paper in scored_papers:
                paper = scored_paper.paper
                writer.writerow({
                    'paperId': paper.paperId or '',
                    'title': paper.title or '',
                    'authors': '; '.join(paper.authors) if paper.authors else '',
                    'year': paper.year or '',
                    'abstract': paper.abstract or '',
                    'citationCount': paper.citationCount or 0,
                    'url': paper.url or '',
                    'score': f"{scored_paper.score:.4f}",
                    'relevance_norm': f"{scored_paper.relevance_norm:.4f}",
                    'citations_norm': f"{scored_paper.citations_norm:.4f}",
                    'recency_norm': f"{scored_paper.recency_norm:.4f}",
                    'matched_keywords': ', '.join(scored_paper.matched_keywords)
                })
        
        print(f"Successfully exported to {filename}")

