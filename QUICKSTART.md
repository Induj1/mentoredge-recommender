# MentorEdge Quick Start Guide

## 🚀 Quick Start with Web Interface

### Step 1: Install Dependencies

```bash
cd mentoredge_recommender
pip install -r requirements.txt
```

### Step 2: Launch Web Interface

```bash
streamlit run frontend.py
```

The web interface will automatically open in your browser at `http://localhost:8501`

### Step 3: Configure Your Search

1. **Enter Your Profile** (in the sidebar):
   - Name: Your name (optional)
   - Research Interests: e.g., "Graph Neural Networks, Large Language Models"
   - Primary Keywords: e.g., "graph neural networks, transformer architecture, language models"
   - Minimum Year: e.g., 2020

2. **Adjust Scoring Weights** (optional):
   - Relevance: How much to prioritize search ranking (default: 0.5)
   - Citations: How much to prioritize citation count (default: 0.3)
   - Recency: How much to prioritize recent papers (default: 0.2)

3. **Set Search Parameters**:
   - Papers per Keyword: Number of papers to fetch per keyword (default: 50)
   - Top N Recommendations: Number of recommendations to return (default: 20)

4. **Optional: Add API Key**:
   - Enter your Semantic Scholar API key for higher rate limits
   - Or leave empty to use public rate limits (5 requests/second)

### Step 4: Generate Recommendations

Click the **"🚀 Generate Recommendations"** button and wait for results!

### Step 5: Explore Results

- View statistics in the dashboard
- Browse paper recommendations with full details
- Search/filter recommendations using the search box
- Download results as CSV with one click

## 📝 Example Configuration

**Name:** Dr. Jane Researcher

**Research Interests:** Graph Neural Networks, Large Language Models, Transformer Architecture

**Primary Keywords:** graph neural networks, transformer architecture, language models, graph learning

**Minimum Year:** 2020

**Scoring Weights:**
- Relevance: 0.5
- Citations: 0.3
- Recency: 0.2

## 💡 Tips

- **More Keywords**: Add more keywords to get a broader set of papers
- **Adjust Weights**: Tune scoring weights based on what matters most to you
- **Use API Key**: For faster searches, get a free API key from Semantic Scholar
- **Search Results**: Use the search box to filter recommendations by title, authors, or keywords

## 🔧 Troubleshooting

**Issue**: Streamlit not found
**Solution**: `pip install streamlit pandas`

**Issue**: Rate limit errors
**Solution**: Add a Semantic Scholar API key or reduce "Papers per Keyword"

**Issue**: No results found
**Solution**: Check your keywords and try broader search terms

## 📚 Need Help?

See the full README.md for detailed documentation and API usage examples.

