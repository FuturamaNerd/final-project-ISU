# Named Entity Recognition (NER) for News Articles

This project now includes Named Entity Recognition (NER) functionality using spaCy to automatically extract location entities from news articles stored in your MongoDB database.

## 🌟 Features

- **Automatic Location Extraction**: Uses spaCy's NER to identify countries, cities, states, and other locations in article content
- **Location Statistics**: Provides analytics on the most common locations and location types found
- **Search by Location**: Find articles that mention specific locations
- **Web Interface**: View processed articles with extracted locations at `/locations`
- **API Endpoints**: RESTful APIs for processing and searching articles

## 🚀 Quick Start

### 1. Install Dependencies

Run the installation script to set up spaCy and required packages:

```bash
python install_spacy.py
```

Or install manually:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Process Your Articles

Run the NER processing script to analyze your existing articles:

```bash
python process_articles_with_ner.py
```

This will:
- Load all articles from your `news_by_location` collection
- Extract location entities using spaCy
- Update the database with location information
- Show statistics about found locations

### 3. Start Your Application

```bash
python app.py
```

### 4. View Results

Visit `http://localhost:5000/locations` to see:
- Articles with extracted locations
- Location statistics and analytics
- Search functionality for finding articles by location

## 📊 What Gets Extracted

The NER system identifies these types of location entities:

- **GPE** (Geo-Political Entity): Countries, cities, states
- **LOC** (Location): General locations, landmarks
- **FAC** (Facility): Buildings, airports, stadiums

## 🔧 API Endpoints

### Process Articles with NER
```
GET /api/ner/process
```
Processes all articles in the database with NER and returns statistics.

### Get Articles with Locations
```
GET /api/articles/locations
```
Returns all articles that have been processed with NER.

### Search Articles by Location
```
GET /api/articles/search?location=London
```
Finds articles that mention a specific location.

## 📁 File Structure

```
├── utility/
│   └── ner_processor.py          # Main NER processing logic
├── templates/
│   └── locations.html            # Web interface for viewing locations
├── process_articles_with_ner.py  # Script to process existing articles
├── install_spacy.py              # Installation helper script
└── app.py                        # Updated Flask app with NER routes
```

## 🎯 How It Works

1. **Text Analysis**: spaCy analyzes article title, description, and content
2. **Entity Recognition**: Identifies location entities with confidence scores
3. **Data Storage**: Stores extracted locations in MongoDB with metadata
4. **Web Display**: Shows locations with entity types and confidence levels

## 📈 Example Output

After processing, your articles will have these new fields:

```json
{
  "title": "Climate Summit in Paris Reaches Agreement",
  "extracted_locations": [
    {
      "text": "Paris",
      "label": "GPE",
      "confidence": 0.95,
      "description": "Country, City, or State"
    }
  ],
  "location_count": 1,
  "primary_location": "Paris",
  "ner_processed_at": "2025-01-15T10:30:00Z"
}
```

## 🔍 Search Examples

- Search for "London" to find articles mentioning London
- Search for "New York" to find articles about NYC
- Search for "Tokyo" to find articles about Japan's capital

## 🛠️ Troubleshooting

### spaCy Installation Issues
If you encounter installation problems:

1. **Windows**: Install Visual C++ build tools
2. **Update pip**: `python -m pip install --upgrade pip`
3. **Manual install**: `pip install spacy` then `python -m spacy download en_core_web_sm`

### MongoDB Connection Issues
Ensure MongoDB is running:
```bash
# Start MongoDB (Windows)
net start MongoDB

# Start MongoDB (macOS/Linux)
sudo systemctl start mongod
```

### Performance Tips
- Process articles in batches for large datasets
- The first run may be slower as spaCy loads the language model
- Consider using a larger spaCy model (`en_core_web_md` or `en_core_web_lg`) for better accuracy

## 🎉 Next Steps

1. **Enhance Location Mapping**: Add coordinates for extracted locations
2. **Visualization**: Create maps showing article locations
3. **Advanced Analytics**: Track location trends over time
4. **Multi-language Support**: Add support for other languages

## 📚 Resources

- [spaCy Documentation](https://spacy.io/usage)
- [Named Entity Recognition Guide](https://spacy.io/usage/linguistic-features#named-entities)
- [MongoDB with Python](https://pymongo.readthedocs.io/)

---

**Happy Location Extraction! 🌍📍** 