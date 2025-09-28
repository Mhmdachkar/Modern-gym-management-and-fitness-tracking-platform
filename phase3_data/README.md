# PHASE 3: ADVANCED INSIGHTS & MODELING

This phase focuses on advanced analytics including sentiment analysis, topic clustering, intent recognition, and member segmentation.

## 📁 Project Structure

```
phase3_data/
├── data/                           # Datasets for Phase 3
│   └── feedback_data.csv          # Synthetic feedback dataset for sentiment analysis
├── notebooks/                      # Analysis notebooks and scripts
│   └── 01_Feedback_Sentiment_Analysis.py  # Complete sentiment analysis script
├── outputs/                        # Generated analysis results and visualizations
└── requirements.txt                # Python dependencies for Phase 3
```

## 🎯 Phase 3 Components

### 8. Feedback Sentiment Analysis ✅ COMPLETED
- **Dataset**: `feedback_data.csv` - 50 synthetic feedback entries
- **Features**: 
  - Member ID, feedback type, rating (1-5), feedback text
  - Sentiment score (0-1), timestamp, coach/session/package IDs
  - Feedback types: class_review, facility_review, service_review, coach_review, package_review
- **Analysis**: 
  - Multi-method sentiment analysis (TextBlob + VADER)
  - Temporal trends (daily, weekly, monthly)
  - Coach performance correlation
  - Package satisfaction analysis
- **Outputs**: Comprehensive visualizations and trend analysis

### 9. Topic Clustering (Next Step)
- **Goal**: Group user queries into thematic clusters
- **Data Needed**: Query text data or feedback text analysis
- **Methods**: TF-IDF, word embeddings, clustering algorithms

### 10. Intent Recognition Improvement (Next Step)
- **Goal**: Enhance intent classification for member queries
- **Data Needed**: Labeled query data with intent categories
- **Methods**: Supervised learning, NLP techniques

### 11. Member Segmentation (Next Step)
- **Goal**: Segment members by behavior and characteristics
- **Data Needed**: Member data + session/package data from Phase 2
- **Methods**: Clustering, RFM analysis, demographic segmentation

## 🚀 Getting Started

### Installation
```bash
cd phase3_data
pip install -r requirements.txt
```

### Running Sentiment Analysis
```bash
python notebooks/01_Feedback_Sentiment_Analysis.py
```

## 📊 Dataset Details

### feedback_data.csv
- **Size**: 50 records
- **Time Range**: January 15-27, 2024
- **Coverage**: 
  - 20 unique members
  - 10 coaches
  - 30 sessions
  - 5 packages
  - 5 feedback types

**Key Fields:**
- `id`: Unique feedback identifier
- `member_id`: Member who provided feedback
- `feedback_type`: Type of feedback (class, facility, service, coach, package)
- `rating`: 1-5 star rating
- `feedback_text`: Detailed feedback text
- `sentiment_score`: Pre-calculated sentiment score (0-1)
- `timestamp`: When feedback was provided
- `coach_id`: Associated coach (if applicable)
- `session_id`: Associated session (if applicable)
- `package_id`: Associated package (if applicable)

## 📈 Analysis Features

### Sentiment Analysis Methods
1. **TextBlob**: General-purpose sentiment analysis
2. **VADER**: Valence Aware Dictionary and sEntiment Reasoner
3. **Correlation Analysis**: Compare different sentiment methods

### Trend Detection
- Daily sentiment trends
- Weekly patterns by day
- Monthly aggregation
- Moving averages for trend smoothing

### Performance Analysis
- Coach sentiment correlation
- Package satisfaction metrics
- Session quality assessment
- Facility and service ratings

## 🎨 Visualizations Generated

1. **Sentiment Analysis Dashboard** (6-panel comprehensive view)
2. **Coach Performance Analysis** (top performers + correlations)
3. **Weekly Trends Analysis** (sentiment + rating trends with moving averages)
4. **Export Files**: All processed data and analysis results

## 🔄 Next Steps

1. **Install Dependencies**: Run `pip install -r requirements.txt`
2. **Execute Analysis**: Run the sentiment analysis script
3. **Review Results**: Check outputs directory for generated files
4. **Continue with Phase 3**: Move to topic clustering (Step 9)

## 📝 Notes

- The feedback dataset is synthetic but realistic, designed to demonstrate various sentiment patterns
- All timestamps are in 2024 for consistency with the project timeline
- The analysis includes both numerical ratings and text-based sentiment scores
- Results are automatically exported to the outputs directory for further analysis

## 🤝 Contributing

This phase builds upon the data structures and insights from Phases 1 and 2. Each component is designed to be modular and can be enhanced with additional data sources or analysis methods.
