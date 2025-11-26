# MentorEdge – Academic Paper Recommendation Engine

A intelligent Python-based recommendation system that helps researchers discover relevant academic papers using the Semantic Scholar API. MentorEdge combines relevance ranking, citation impact, and recency to generate personalized paper recommendations.

## Overview

MentorEdge is designed for AI researchers and academics who need to stay up-to-date with the latest publications in their field. The system intelligently scores papers based on multiple signals:

- **Relevance**: Position-based ranking from search results
- **Citations**: Log-scaled normalization of citation counts
- **Recency**: Year-based normalization favoring recent publications

The recommendation engine can be customized through user profiles that define research interests, keywords, publication year filters, and scoring weights.

## Features

- ✅ **Web Interface**: Beautiful Streamlit-based frontend for easy interaction
- ✅ **Semantic Scholar API Integration**: Clean, production-ready client with rate limiting and error handling
- ✅ **Intelligent Scoring Algorithm**: Multi-factor scoring combining relevance, citations, and recency
- ✅ **Personalized Recommendations**: User profile-based customization
- ✅ **Paper Deduplication**: Automatic removal of duplicate papers across multiple keyword searches
- ✅ **CSV Export**: Structured export with full metadata and scoring breakdown
- ✅ **Type Safety**: Full type hints and dataclasses throughout
- ✅ **Rate Limiting**: Built-in throttling to respect API limits
- ✅ **Error Handling**: Robust error handling with informative messages

## Project Structure

```
mentoredge_recommender/
│── semantic_scholar_client.py  # API client with Paper dataclass
│── recommender.py               # Recommendation engine with scoring logic
│── main.py                      # Command-line demo usage example
│── frontend.py                  # Streamlit web interface
│── sample_output.csv            # Output CSV file (generated)
│── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   cd mentoredge_recommender
   pip install -r requirements.txt
   ```

3. **(Optional) Set up API key**:
   The Semantic Scholar API works without an API key, but you'll have rate limits (5 requests/second). For higher limits, you can obtain a free API key from [Semantic Scholar](https://www.semanticscholar.org/product/api) and set it as an environment variable:
   
   **Windows (PowerShell)**:
   ```powershell
   $env:SEMANTIC_SCHOLAR_API_KEY="your-api-key-here"
   ```
   
   **Windows (CMD)**:
   ```cmd
   set SEMANTIC_SCHOLAR_API_KEY=your-api-key-here
   ```
   
   **Linux/Mac**:
   ```bash
   export SEMANTIC_SCHOLAR_API_KEY="your-api-key-here"
   ```

## Running Instructions

### Web Interface (Recommended)

The easiest way to use MentorEdge is through the web interface:

```bash
cd mentoredge_recommender
streamlit run frontend.py
```

This will:
1. Open your web browser automatically
2. Show an intuitive interface with:
   - Sidebar configuration for user profile, keywords, and scoring weights
   - Real-time paper search and recommendations
   - Beautiful paper cards with full details
   - Statistics dashboard
   - One-click CSV download
   - Search/filter functionality

The interface allows you to:
- Enter research interests and keywords
- Adjust scoring weights with sliders
- Set minimum publication year
- Configure search parameters (papers per keyword, top N results)
- View recommendations in a user-friendly format
- Download results as CSV

**Note**: The web interface will open at `http://localhost:8501` by default.

### Command-Line Interface

Run the main script for command-line usage:

```bash
python main.py
```

This will:
1. Initialize the Semantic Scholar API client
2. Create a sample user profile (AI researcher interested in GNNs and LLMs)
3. Fetch papers for each keyword
4. Score and rank recommendations
5. Display top recommendations in the console
6. Export results to `sample_output.csv`

### Custom Usage

You can customize the recommendation system by modifying the user profile in `main.py`:

```python
user_profile = UserProfile(
    name="Your Name",
    research_interests=["Topic 1", "Topic 2"],
    primary_keywords=["keyword1", "keyword2"],
    min_year=2020,  # Filter papers before this year
    scoring_weights={
        "relevance": 0.5,
        "citations": 0.3,
        "recency": 0.2
    }
)
```

### Programmatic Usage

```python
from semantic_scholar_client import SemanticScholarClient
from recommender import PaperRecommender, UserProfile

# Initialize client
client = SemanticScholarClient(api_key="your-key-optional")

# Create user profile
profile = UserProfile(
    name="Dr. Researcher",
    research_interests=["Machine Learning"],
    primary_keywords=["deep learning", "neural networks"],
    min_year=2022
)

# Create recommender
recommender = PaperRecommender(client, profile)

# Get recommendations
recommendations = recommender.build_personalized_recommendations(
    papers_per_keyword=50,
    top_n=20
)

# Export to CSV
recommender.export_to_csv(recommendations, "output.csv")
```

## Environment Variables

- `SEMANTIC_SCHOLAR_API_KEY`: (Optional) Your Semantic Scholar API key for higher rate limits. Without it, the client uses public rate limits (5 requests/second).

## Output Description

The system generates a CSV file (`sample_output.csv` by default) with the following columns:

- `paperId`: Unique Semantic Scholar paper ID
- `title`: Paper title
- `authors`: Semicolon-separated list of authors
- `year`: Publication year
- `abstract`: Paper abstract
- `citationCount`: Number of citations
- `url`: Link to the paper
- `score`: Combined weighted score (0.0 to 1.0)
- `relevance_norm`: Normalized relevance score
- `citations_norm`: Normalized citation score
- `recency_norm`: Normalized recency score
- `matched_keywords`: Comma-separated list of keywords that matched

Papers are sorted by `score` in descending order.

## Scoring Algorithm

The recommendation score is calculated as:

```
score = w1 × relevance_norm + w2 × citations_norm + w3 × recency_norm
```

Where:
- **relevance_norm**: Based on paper's position in search results, using exponential decay (top results get higher scores)
- **citations_norm**: Log-scaled citation count normalization to handle wide ranges
- **recency_norm**: Year-based normalization favoring recent papers (last 20 years)

Default weights are:
- Relevance: 0.5
- Citations: 0.3
- Recency: 0.2

You can customize these weights in the `UserProfile`.

## Code Quality

The project follows best practices:

- ✅ Type hints throughout
- ✅ Dataclasses for structured data
- ✅ Comprehensive error handling
- ✅ Clear method documentation
- ✅ Modular, extensible design
- ✅ PEP 8 compliant formatting

## Bonus Ideas & Future Enhancements

### Caching
- Implement local caching of API responses to reduce redundant requests
- Cache recommendations with TTL (time-to-live) based on user profile

### Async Support
- Convert to `asyncio`/`aiohttp` for concurrent API requests
- Significant speedup for multiple keyword searches

### Web Interface Enhancements
- ✅ **Implemented**: Streamlit-based web interface for easy interaction
- Future: RESTful API endpoint with FastAPI
- Future: User authentication and saved profiles
- Future: Real-time collaboration features

### Docker
- Containerize the application with Docker
- Include environment variable configuration
- Easy deployment to cloud platforms

### Advanced Features
- **Collaborative Filtering**: Recommend papers based on similar researchers
- **Paper Clustering**: Group related papers by topic
- **Abstract Summarization**: Generate summaries using NLP models
- **Citation Network Analysis**: Visualize paper relationships
- **Email Alerts**: Periodic email notifications for new papers

## API Notes

- **Rate Limits**: Without API key: 5 requests/second. With API key: 100 requests/second (check Semantic Scholar docs for current limits)
- **Rate Limiting**: The client automatically throttles requests to respect limits
- **Error Handling**: Network errors, rate limits, and API errors are handled gracefully

## License

This project is created for an AI App Developer assessment.

## Frontend Features

The Streamlit web interface provides:

- **Interactive Configuration**: Easy-to-use sidebar with all settings
- **Real-time Recommendations**: Generate and view recommendations instantly
- **Beautiful Paper Cards**: Readable, organized display of paper information
- **Statistics Dashboard**: Quick overview of recommendation metrics
- **CSV Export**: One-click download of results
- **Search & Filter**: Filter recommendations by keywords, title, or authors
- **Responsive Design**: Works on desktop and tablet devices

### Using the Web Interface

1. Launch the interface: `streamlit run frontend.py`
2. Configure your profile in the sidebar:
   - Enter your name (optional)
   - Add research interests (comma-separated)
   - Enter primary keywords for search (comma-separated)
   - Set minimum publication year
   - Adjust scoring weights using sliders
3. Set search parameters:
   - Papers per keyword (10-200)
   - Top N recommendations (5-100)
4. Click "Generate Recommendations"
5. View results, search/filter, and download CSV

## Contact

For questions or issues, please refer to the Semantic Scholar API documentation: https://api.semanticscholar.org/api-docs/

