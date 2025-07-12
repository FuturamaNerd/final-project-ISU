// Parent class for all news events
class NewsEvent {
    constructor(data = {}) {
        // Core news properties (common to all sources)
        this.id = data._id || data.id || this.generateId();
        this.title = data.title || '';
        this.description = data.description || '';
        this.content = data.content || '';
        this.url = data.url || '';
        this.urlToImage = data.urlToImage || '';
        this.publishedAt = data.publishedAt || new Date().toISOString();
        
        // Source information
        this.source = {
            id: data.source?.id || '',
            name: data.source?.name || 'Unknown',
            url: data.source?.url || ''
        };
        
        // Basic location data
        this.sourceCountry = data.source_country || '';
        this.continent = data.continent || '';
        this.coordinates = data.coordinates || null;
        
        // NER (Named Entity Recognition) data
        this.extractedLocations = data.extracted_locations || [];
        this.locationCount = data.location_count || 0;
        this.primaryLocation = data.primary_location || '';
        
        // Metadata
        this.savedAt = data.saved_at || new Date().toISOString();
        this.nerProcessedAt = data.ner_processed_at || null;
        this.isProcessed = data.isProcessed || false;
        
        // Additional properties
        this.author = data.author || '';
        this.category = data.category || 'general';
        this.language = data.language || 'en';
        this.sentiment = data.sentiment || 'neutral';
        
        // Data source identification
        this.dataSource = data.data_source || 'unknown';
        this.locationPrecision = data.location_precision || 'country';
    }
    
    /**
     * Generate a unique ID for the event
     */
    generateId() {
        return 'event_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * Get formatted date string
     */
    getFormattedDate() {
        const date = new Date(this.publishedAt);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    /**
     * Get time since publication
     */
    getTimeAgo() {
        const now = new Date();
        const published = new Date(this.publishedAt);
        const diffInSeconds = Math.floor((now - published) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        return `${Math.floor(diffInSeconds / 2592000)}mo ago`;
    }
    
    /**
     * Get truncated title
     */
    getTruncatedTitle(maxLength = 60) {
        // Use scraped title if available (for GDELT events)
        const titleToUse = this.scrapedTitle || this.title;
        if (titleToUse.length <= maxLength) return titleToUse;
        return titleToUse.substring(0, maxLength) + '...';
    }
    
    /**
     * Get truncated description
     */
    getTruncatedDescription(maxLength = 100) {
        if (this.description.length <= maxLength) return this.description;
        return this.description.substring(0, maxLength) + '...';
    }
    
    /**
     * Check if event has image
     */
    hasImage() {
        return this.urlToImage && this.urlToImage.trim() !== '';
    }
    
    /**
     * Check if event has location data
     */
    hasLocation() {
        return this.coordinates && this.coordinates.length === 2;
    }
    
    /**
     * Get location coordinates for map (to be overridden by child classes)
     */
    getMapCoordinates() {
        console.log(`NewsEvent getMapCoordinates called for event:`, {
            coordinates: this.coordinates,
            sourceCountry: this.sourceCountry,
            locationPrecision: this.locationPrecision
        });
        
        // Priority 1: Direct coordinates (from country mapping)
        if (this.coordinates && this.coordinates.length === 2) {
            console.log(`Using direct coordinates: [${this.coordinates[0]}, ${this.coordinates[1]}]`);
            return this.coordinates;
        }
        
        // Priority 2: Fallback to country coordinates if available
        if (this.sourceCountry) {
            const countryCoords = this.getCountryCoordinates(this.sourceCountry);
            console.log(`Using country coordinates for ${this.sourceCountry}: [${countryCoords[0]}, ${countryCoords[1]}]`);
            return countryCoords;
        }
        
        // Default fallback
        console.log(`Using default US coordinates`);
        return [39.8283, -98.5795];
    }
    
    /**
     * Get country coordinates (basic mapping)
     */
    getCountryCoordinates(countryCode) {
        const coords = {
            'US': [39.8283, -98.5795],
            'CA': [56.1304, -106.3468],
            'BR': [-14.2350, -51.9253],
            'MX': [23.6345, -102.5528],
            'AR': [-38.4161, -63.6167],
            'CL': [-35.6751, -71.5430],
            'CO': [4.5709, -74.2973],
            'PE': [-9.1900, -75.0152],
            'VE': [6.4238, -66.5897],
            'AU': [-25.2744, 133.7751],
            'NZ': [-40.9006, 174.8860],
            'FJ': [-17.7134, 178.0650],
            'PG': [-6.3150, 143.9555],
            'WS': [-13.7590, -172.1046],
            'GB': [55.3781, -3.4360],
            'DE': [51.1657, 10.4515],
            'FR': [46.2276, 2.2137],
            'IT': [41.8719, 12.5674],
            'ES': [40.4637, -3.7492],
            'CN': [35.8617, 104.1954],
            'JP': [36.2048, 138.2529],
            'IN': [20.5937, 78.9629],
            'KR': [35.9078, 127.7669],
            'ZA': [-30.5595, 22.9375],
            'EG': [26.8206, 30.8025],
            'NG': [9.0820, 8.6753],
            'KE': [-0.0236, 37.9062]
        };
        
        return coords[countryCode] || [39.8283, -98.5795]; // Default to US
    }
    
    /**
     * Create map marker for this event
     */
    createMapMarker(map) {
        if (!map) return null;
        
        const coords = this.getMapCoordinates();
        if (!coords) return null;
        
        const marker = L.marker(coords).addTo(map);
        
        // Create popup content
        const popupContent = this.createPopupContent();
        marker.bindPopup(popupContent);
        
        return marker;
    }
    
    /**
     * Create popup content for map marker (to be overridden by child classes)
     */
    createPopupContent() {
        const title = this.getTruncatedTitle(50);
        const source = this.source.name;
        const country = this.sourceCountry;
        const timeAgo = this.getTimeAgo();
        
        return `
            <div class="news-popup">
                <h6><strong>${title}</strong></h6>
                <small class="text-muted">${country} - ${source}</small><br>
                <small class="text-muted">${timeAgo}</small><br>
                ${this.url ? `<a href="${this.url}" target="_blank" class="btn btn-sm btn-primary mt-2">Read Article</a>` : ''}
            </div>
        `;
    }
    
    /**
     * Create HTML card for this event
     */
    createCard() {
        const cardHtml = `
            <div class="card h-100 news-card" data-event-id="${this.id}" data-source="${this.dataSource}">
                ${this.hasImage() ? `
                    <img src="${this.urlToImage}" class="card-img-top" alt="News Image" 
                         style="height: 200px; object-fit: cover;" onerror="this.style.display='none'">
                ` : ''}
                <div class="card-body">
                    <h5 class="card-title">${this.getTruncatedTitle()}</h5>
                    <p class="card-text">${this.getTruncatedDescription()}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            ${this.author ? this.author : ''}
                            ${this.author && this.sourceCountry ? ' | ' : ''}
                            ${this.sourceCountry || ''}
                        </small>
                        <small class="text-muted">${this.getFormattedDate()}</small>
                    </div>
                    ${this.getSourceBadge()}
                </div>
                <div class="card-footer">
                    ${this.url ? `<a href="${this.url}" target="_blank" class="btn btn-primary btn-sm">Read More</a>` : ''}
                    ${this.hasLocation() ? `<button class="btn btn-outline-secondary btn-sm ms-2" onclick="showOnMap('${this.id}')">Show on Map</button>` : ''}
                </div>
            </div>
        `;
        
        return cardHtml;
    }
    
    /**
     * Get source badge for display
     */
    getSourceBadge() {
        return `<span class="badge bg-secondary ms-2">${this.dataSource}</span>`;
    }
    
    /**
     * Get location precision level
     */
    getLocationPrecision() {
        if (this.locationPrecision) return this.locationPrecision;
        if (this.coordinates) return 'country';
        return 'unknown';
    }
    
    /**
     * Convert event to JSON
     */
    toJSON() {
        return {
            id: this.id,
            title: this.title,
            description: this.description,
            content: this.content,
            url: this.url,
            urlToImage: this.urlToImage,
            publishedAt: this.publishedAt,
            source: this.source,
            sourceCountry: this.sourceCountry,
            continent: this.continent,
            coordinates: this.coordinates,
            extractedLocations: this.extractedLocations,
            locationCount: this.locationCount,
            primaryLocation: this.primaryLocation,
            savedAt: this.savedAt,
            nerProcessedAt: this.nerProcessedAt,
            isProcessed: this.isProcessed,
            author: this.author,
            category: this.category,
            language: this.language,
            sentiment: this.sentiment,
            dataSource: this.dataSource,
            locationPrecision: this.locationPrecision
        };
    }
    
    /**
     * Validate event data
     */
    isValid() {
        return this.title && this.title.trim() !== '' && 
               this.description && this.description.trim() !== '';
    }
    
    /**
     * Get event summary
     */
    getSummary() {
        return {
            id: this.id,
            title: this.getTruncatedTitle(),
            source: this.source.name,
            country: this.sourceCountry,
            continent: this.continent,
            timeAgo: this.getTimeAgo(),
            hasImage: this.hasImage(),
            hasLocation: this.hasLocation(),
            locationPrecision: this.getLocationPrecision(),
            dataSource: this.dataSource
        };
    }
    
    /**
     * Get all locations associated with this event
     */
    getAllLocations() {
        const locations = [];
        
        if (this.coordinates) {
            locations.push({
                type: 'general',
                coordinates: this.coordinates,
                precision: 'general'
            });
        }
        
        if (this.extractedLocations.length > 0) {
            locations.push(...this.extractedLocations.map(loc => ({
                ...loc,
                type: 'ner'
            })));
        }
        
        return locations;
    }
}

// Child class for NewsAPI events
class NewsAPIEvent extends NewsEvent {
    constructor(data = {}) {
        super(data);
        this.dataSource = 'newsapi';
        
        // NewsAPI specific properties
        this.newsApiId = data.newsApiId || null;
        this.newsApiSourceId = data.newsApiSourceId || null;
        this.newsApiSourceName = data.newsApiSourceName || null;
    }
    
    /**
     * Create NewsAPI event from API response
     */
    static fromAPIResponse(apiData) {
        return new NewsAPIEvent({
            title: apiData.title,
            description: apiData.description,
            content: apiData.content,
            url: apiData.url,
            urlToImage: apiData.urlToImage,
            publishedAt: apiData.publishedAt,
            source: apiData.source,
            author: apiData.author,
            newsApiId: apiData.id,
            newsApiSourceId: apiData.source?.id,
            newsApiSourceName: apiData.source?.name,
            // Add location data
            sourceCountry: apiData.source_country,
            continent: apiData.continent,
            coordinates: apiData.coordinates,
            locationPrecision: apiData.location_precision,
            dataSource: apiData.data_source || 'newsapi'
        });
    }
    
    /**
     * Get source badge for NewsAPI
     */
    getSourceBadge() {
        return `<span class="badge bg-primary ms-2">NewsAPI</span>`;
    }
}

// Child class for GDELT events
class GDELTEvent extends NewsEvent {
    constructor(data = {}) {
        super(data);
        this.dataSource = 'gdelt';
        
        // GDELT-specific location data
        this.gdeltLocations = data.gdelt_locations || [];
        this.actor1Location = data.actor1_location || null;
        this.actor2Location = data.actor2_location || null;
        this.actionLocation = data.action_location || null;
        this.mentionedLocations = data.mentioned_locations || [];
        this.exactCoordinates = data.exactCoordinates || data.exact_coordinates || null;
        
        // GDELT-specific properties
        this.gkgRecordId = data.gkg_record_id || null;
        this.eventId = data.event_id || null;
        this.eventCode = data.event_code || null;
        this.eventBaseCode = data.event_base_code || null;
        this.eventRootCode = data.event_root_code || null;
        this.quadClass = data.quad_class || null;
        this.goldsteinScale = data.goldstein_scale || null;
        this.numMentions = data.num_mentions || 0;
        this.numSources = data.num_sources || 0;
        this.numArticles = data.num_articles || 0;
        this.avgTone = data.avg_tone || 0;
        
        // Translation-specific properties
        this.translatedTitle = data.translated_title || null;
        this.translatedContent = data.translated_content || null;
        this.sourceLanguage = data.source_language || null;
        this.targetLanguage = data.target_language || null;
        this.translationConfidence = data.translation_confidence || null;
        this.sentimentScore = data.sentiment_score || null;
        this.sentimentMagnitude = data.sentiment_magnitude || null;
        
        // Scraped title (highest priority)
        this.scrapedTitle = data.scraped_title || null;
        this.actor1Type1Code = data.actor1_type1_code || null;
        this.actor1Type2Code = data.actor1_type2_code || null;
        this.actor1Type3Code = data.actor1_type3_code || null;
        this.actor2Type1Code = data.actor2_type1_code || null;
        this.actor2Type2Code = data.actor2_type2_code || null;
        this.actor2Type3Code = data.actor2_type3_code || null;
        this.isRootEvent = data.is_root_event || false;
        this.eventTimeDate = data.event_time_date || null;
        this.eventMonthYear = data.event_month_year || null;
        this.eventYear = data.event_year || null;
    }
    
    /**
     * Get location coordinates for map (GDELT-specific priority)
     */
    getMapCoordinates() {
        console.log(`GDELT getMapCoordinates called for event:`, {
            exactCoordinates: this.exactCoordinates,
            coordinates: this.coordinates,
            sourceCountry: this.sourceCountry
        });
        
        // Priority 1: Exact GDELT coordinates
        if (this.exactCoordinates && this.exactCoordinates.length === 2) {
            console.log(`Using exact coordinates: [${this.exactCoordinates[0]}, ${this.exactCoordinates[1]}]`);
            return this.exactCoordinates;
        }
        
        // Priority 2: General coordinates
        if (this.coordinates && this.coordinates.length === 2) {
            console.log(`Using general coordinates: [${this.coordinates[0]}, ${this.coordinates[1]}]`);
            return this.coordinates;
        }
        
        // Priority 3: GDELT locations (take first one with coordinates)
        if (this.gdeltLocations.length > 0) {
            const locationWithCoords = this.gdeltLocations.find(loc => 
                loc.coordinates && loc.coordinates.length === 2
            );
            if (locationWithCoords) {
                console.log(`Using GDELT location coordinates: [${locationWithCoords.coordinates[0]}, ${locationWithCoords.coordinates[1]}]`);
                return locationWithCoords.coordinates;
            }
        }
        
        // Priority 4: Actor locations
        if (this.actor1Location && this.actor1Location.coordinates) {
            console.log(`Using actor1 location coordinates: [${this.actor1Location.coordinates[0]}, ${this.actor1Location.coordinates[1]}]`);
            return this.actor1Location.coordinates;
        }
        if (this.actor2Location && this.actor2Location.coordinates) {
            console.log(`Using actor2 location coordinates: [${this.actor2Location.coordinates[0]}, ${this.actor2Location.coordinates[1]}]`);
            return this.actor2Location.coordinates;
        }
        if (this.actionLocation && this.actionLocation.coordinates) {
            console.log(`Using action location coordinates: [${this.actionLocation.coordinates[0]}, ${this.actionLocation.coordinates[1]}]`);
            return this.actionLocation.coordinates;
        }
        
        // Fallback to country coordinates if available
        const countryCoords = this.getCountryCoordinates(this.sourceCountry);
        console.log(`Falling back to country coordinates for ${this.sourceCountry}: [${countryCoords[0]}, ${countryCoords[1]}]`);
        return countryCoords;
    }
    
    /**
     * Get location precision level (GDELT-specific)
     */
    getLocationPrecision() {
        if (this.exactCoordinates) return 'exact';
        if (this.gdeltLocations.length > 0) return 'gdelt';
        if (this.coordinates) return 'general';
        return 'country';
    }
    
    /**
     * Get GDELT-specific summary
     */
    getGDELTSummary() {
        return {
            eventId: this.eventId,
            eventCode: this.eventCode,
            eventRootCode: this.eventRootCode,
            quadClass: this.quadClass,
            goldsteinScale: this.goldsteinScale,
            avgTone: this.avgTone,
            numMentions: this.numMentions,
            numSources: this.numSources,
            numArticles: this.numArticles,
            locationPrecision: this.getLocationPrecision(),
            exactCoordinates: this.exactCoordinates,
            actor1Location: this.actor1Location,
            actor2Location: this.actor2Location,
            actionLocation: this.actionLocation,
            mentionedLocations: this.mentionedLocations
        };
    }
    
    /**
     * Get all locations associated with this event (GDELT-specific)
     */
    getAllLocations() {
        const locations = [];
        
        if (this.exactCoordinates) {
            locations.push({
                type: 'exact',
                coordinates: this.exactCoordinates,
                precision: 'exact'
            });
        }
        
        if (this.gdeltLocations.length > 0) {
            locations.push(...this.gdeltLocations.map(loc => ({
                ...loc,
                type: 'gdelt'
            })));
        }
        
        if (this.actor1Location) {
            locations.push({
                ...this.actor1Location,
                type: 'actor1'
            });
        }
        
        if (this.actor2Location) {
            locations.push({
                ...this.actor2Location,
                type: 'actor2'
            });
        }
        
        if (this.actionLocation) {
            locations.push({
                ...this.actionLocation,
                type: 'action'
            });
        }
        
        if (this.mentionedLocations.length > 0) {
            locations.push(...this.mentionedLocations.map(loc => ({
                ...loc,
                type: 'mentioned'
            })));
        }
        
        // Add parent class locations
        locations.push(...super.getAllLocations());
        
        return locations;
    }
    
    /**
     * Get GDELT event classification
     */
    getEventClassification() {
        const classifications = {
            '01': 'MAKE PUBLIC STATEMENT',
            '02': 'APPEAL',
            '03': 'EXPRESS INTENT TO COOPERATE',
            '04': 'CONSULT',
            '05': 'ENGAGE IN DIPLOMATIC COOPERATION',
            '06': 'ENGAGE IN MATERIAL COOPERATION',
            '07': 'PROVIDE AID',
            '08': 'YIELD',
            '09': 'INVESTIGATE',
            '10': 'DEMAND',
            '11': 'DISAPPROVE',
            '12': 'REJECT',
            '13': 'THREATEN',
            '14': 'PROTEST',
            '15': 'EXHIBIT FORCE POSTURE',
            '16': 'REDUCE RELATIONS',
            '17': 'EXPEL',
            '18': 'SEIZE OR DESTROY PROPERTY',
            '19': 'MASS VIOLENCE',
            '20': 'USE UNCONVENTIONAL MASS VIOLENCE'
        };
        
        return {
            code: this.eventCode,
            description: classifications[this.eventCode] || 'Unknown',
            rootCode: this.eventRootCode,
            quadClass: this.getQuadClassDescription()
        };
    }
    
    /**
     * Get quad class description
     */
    getQuadClassDescription() {
        const quadClasses = {
            1: 'Verbal Cooperation',
            2: 'Material Cooperation', 
            3: 'Verbal Conflict',
            4: 'Material Conflict'
        };
        
        return {
            code: this.quadClass,
            description: quadClasses[this.quadClass] || 'Unknown'
        };
    }
    
    /**
     * Get tone analysis
     */
    getToneAnalysis() {
        let toneCategory = 'neutral';
        if (this.avgTone > 5) toneCategory = 'positive';
        else if (this.avgTone < -5) toneCategory = 'negative';
        
        return {
            score: this.avgTone,
            category: toneCategory,
            description: this.getToneDescription(this.avgTone)
        };
    }
    
    /**
     * Get tone description
     */
    getToneDescription(tone) {
        if (tone >= 10) return 'Very Positive';
        if (tone >= 5) return 'Positive';
        if (tone >= 0) return 'Slightly Positive';
        if (tone >= -5) return 'Slightly Negative';
        if (tone >= -10) return 'Negative';
        return 'Very Negative';
    }
    
    /**
     * Create enhanced popup content with GDELT data
     */
    createPopupContent() {
        // Use scraped title if available, then translated title, otherwise fall back to generated title
        const title = this.scrapedTitle || this.translatedTitle || this.getTruncatedTitle(50);
        const source = this.source.name;
        const country = this.sourceCountry;
        const timeAgo = this.getTimeAgo();
        const eventClass = this.getEventClassification();
        const precision = this.getLocationPrecision();
        
        // Only show available GDELT data
        let gdeltInfo = `<small><strong>Event:</strong> ${eventClass.description}</small><br>`;
        gdeltInfo += `<small><strong>Precision:</strong> ${precision}</small><br>`;
        
        if (this.goldsteinScale !== null && this.goldsteinScale !== undefined) {
            gdeltInfo += `<small><strong>Goldstein Scale:</strong> ${this.goldsteinScale.toFixed(2)}</small><br>`;
        }
        
        if (this.actor1Name) {
            gdeltInfo += `<small><strong>Actor 1:</strong> ${this.actor1Name} (${this.actor1Country || 'Unknown'})</small><br>`;
        }
        
        if (this.actor2Name) {
            gdeltInfo += `<small><strong>Actor 2:</strong> ${this.actor2Name} (${this.actor2Country || 'Unknown'})</small><br>`;
        }
        
        // Add translation and sentiment info if available
        if (this.sourceLanguage) {
            gdeltInfo += `<small><strong>Language:</strong> ${this.sourceLanguage}</small><br>`;
        }
        
        if (this.sentimentScore !== null && this.sentimentScore !== undefined) {
            gdeltInfo += `<small><strong>Sentiment:</strong> ${this.sentimentScore.toFixed(2)}</small><br>`;
        }
        
        if (this.numSources) {
            gdeltInfo += `<small><strong>Sources:</strong> ${this.numSources}</small><br>`;
        }
        
        return `
            <div class="news-popup gdelt-popup">
                <h6><strong>${title}</strong></h6>
                <small class="text-muted">${country || 'Unknown'} - ${source}</small><br>
                <small class="text-muted">${timeAgo}</small><br>
                <div class="gdelt-info">
                    ${gdeltInfo}
                </div>
                ${this.url ? `<a href="${this.url}" target="_blank" class="btn btn-sm btn-primary mt-2">Read Article</a>` : ''}
            </div>
        `;
    }
    
    /**
     * Get source badge for GDELT
     */
    getSourceBadge() {
        return `<span class="badge bg-success ms-2">GDELT</span>`;
    }
    
    /**
     * Create GDELT event from raw GDELT data
     */
    static fromGDELTData(gdeltData) {
        return new GDELTEvent({
            eventId: gdeltData.GLOBALEVENTID,
            eventCode: gdeltData.EventCode,
            eventBaseCode: gdeltData.EventBaseCode,
            eventRootCode: gdeltData.EventRootCode,
            quadClass: gdeltData.QuadClass,
            goldsteinScale: gdeltData.GoldsteinScale,
            numMentions: gdeltData.NumMentions,
            numSources: gdeltData.NumSources,
            numArticles: gdeltData.NumArticles,
            avgTone: gdeltData.AvgTone,
            actor1Type1Code: gdeltData.Actor1Type1Code,
            actor1Type2Code: gdeltData.Actor1Type2Code,
            actor1Type3Code: gdeltData.Actor1Type3Code,
            actor2Type1Code: gdeltData.Actor2Type1Code,
            actor2Type2Code: gdeltData.Actor2Type2Code,
            actor2Type3Code: gdeltData.Actor2Type3Code,
            isRootEvent: gdeltData.IsRootEvent === 1,
            eventTimeDate: gdeltData.EventTimeDate,
            eventMonthYear: gdeltData.EventMonthYear,
            eventYear: gdeltData.EventYear,
            // Location data
            exactCoordinates: gdeltData.ActionGeo_Lat && gdeltData.ActionGeo_Long ? 
                [parseFloat(gdeltData.ActionGeo_Lat), parseFloat(gdeltData.ActionGeo_Long)] : null,
            locationPrecision: gdeltData.ActionGeo_Type || 'country',
            // Additional processing can be added here
            publishedAt: gdeltData.EventTimeDate ? 
                new Date(gdeltData.EventTimeDate).toISOString() : new Date().toISOString()
        });
    }
    
    /**
     * Create GDELT event from SQLite data
     */
    static fromSQLiteData(sqliteData) {
        // Parse GDELT date format (YYYYMMDD)
        let publishedAt = new Date().toISOString(); // Default to now
        if (sqliteData.date) {
            try {
                // GDELT date format is YYYYMMDD (e.g., "20240705")
                const dateStr = sqliteData.date.toString();
                if (dateStr.length === 8) {
                    const year = parseInt(dateStr.substring(0, 4));
                    const month = parseInt(dateStr.substring(4, 6)) - 1; // Month is 0-indexed
                    const day = parseInt(dateStr.substring(6, 8));
                    const date = new Date(year, month, day);
                    if (!isNaN(date.getTime())) {
                        publishedAt = date.toISOString();
                    }
                }
            } catch (error) {
                console.warn('Could not parse GDELT date:', sqliteData.date, error);
            }
        }
        
        // Calculate exact coordinates - check both direct properties and nested structure
        let exactCoords = null;
        if (sqliteData.latitude && sqliteData.longitude) {
            const lat = parseFloat(sqliteData.latitude);
            const lng = parseFloat(sqliteData.longitude);
            if (!isNaN(lat) && !isNaN(lng)) {
                exactCoords = [lat, lng];
                console.log(`GDELT fromSQLiteData: Setting exact coordinates to [${lat}, ${lng}]`);
            } else {
                console.log(`GDELT fromSQLiteData: Invalid coordinates - lat: ${sqliteData.latitude}, lng: ${sqliteData.longitude}`);
            }
        } else {
            console.log(`GDELT fromSQLiteData: No coordinates found - lat: ${sqliteData.latitude}, lng: ${sqliteData.longitude}`);
        }
        
        // Determine source country - use actor countries or derive from coordinates
        let sourceCountry = sqliteData.actor1_country || sqliteData.actor2_country;
        if (!sourceCountry && exactCoords) {
            // If no country specified but we have coordinates, try to determine country
            const [lat, lng] = exactCoords;
            if (lat >= 24 && lat <= 49 && lng >= -125 && lng <= -66) {
                sourceCountry = 'US'; // Continental US
            } else if (lat >= 49 && lat <= 84 && lng >= -141 && lng <= -52) {
                sourceCountry = 'CA'; // Canada
            } else if (lat >= -56 && lat <= 12 && lng >= -81 && lng <= -34) {
                sourceCountry = 'BR'; // Brazil
            }
        }
        
        const eventData = {
            eventId: sqliteData.event_id,
            eventCode: sqliteData.event_code,
            goldsteinScale: sqliteData.goldstein,
            actor1Name: sqliteData.actor1_name,
            actor1Country: sqliteData.actor1_country,
            actor2Name: sqliteData.actor2_name,
            actor2Country: sqliteData.actor2_country,
            exactCoordinates: exactCoords,
            sourceCountry: sourceCountry,
            continent: sqliteData.continent,
            url: sqliteData.source_url,
            title: `${sqliteData.actor1_name || 'Unknown'} - ${sqliteData.actor2_name || 'Event'}`,
            description: `Event involving ${sqliteData.actor1_name || 'Unknown'} and ${sqliteData.actor2_name || 'others'}`,
            publishedAt: publishedAt,
            source: {
                name: 'GDELT',
                id: 'gdelt',
                url: 'https://www.gdeltproject.org/'
            },
            // Translation fields
            translatedTitle: sqliteData.translated_title || null,
            translatedContent: sqliteData.translated_content || null,
            sourceLanguage: sqliteData.source_language || null,
            targetLanguage: sqliteData.target_language || null,
            translationConfidence: sqliteData.translation_confidence || null,
            sentimentScore: sqliteData.sentiment_score || null,
            sentimentMagnitude: sqliteData.sentiment_magnitude || null,
            scrapedTitle: sqliteData.scraped_title || null,
            // Set default values for missing properties
            numMentions: sqliteData.num_mentions || 0,
            numSources: sqliteData.num_sources || 0,
            numArticles: 0,
            avgTone: sqliteData.avg_tone || 0,
            quadClass: null,
            eventBaseCode: null,
            eventRootCode: null
        };
        
        console.log(`GDELT fromSQLiteData: Creating event with exactCoordinates:`, eventData.exactCoordinates);
        
        return new GDELTEvent(eventData);
    }
    
    /**
     * Override toJSON to include GDELT-specific properties
     */
    toJSON() {
        const baseJson = super.toJSON();
        return {
            ...baseJson,
            gdeltLocations: this.gdeltLocations,
            actor1Location: this.actor1Location,
            actor2Location: this.actor2Location,
            actionLocation: this.actionLocation,
            mentionedLocations: this.mentionedLocations,
            exactCoordinates: this.exactCoordinates,
            gkgRecordId: this.gkgRecordId,
            eventId: this.eventId,
            eventCode: this.eventCode,
            eventBaseCode: this.eventBaseCode,
            eventRootCode: this.eventRootCode,
            quadClass: this.quadClass,
            goldsteinScale: this.goldsteinScale,
            numMentions: this.numMentions,
            numSources: this.numSources,
            numArticles: this.numArticles,
            avgTone: this.avgTone,
            actor1Type1Code: this.actor1Type1Code,
            actor1Type2Code: this.actor1Type2Code,
            actor1Type3Code: this.actor1Type3Code,
            actor2Type1Code: this.actor2Type1Code,
            actor2Type2Code: this.actor2Type2Code,
            actor2Type3Code: this.actor2Type3Code,
            isRootEvent: this.isRootEvent,
            eventTimeDate: this.eventTimeDate,
            eventMonthYear: this.eventMonthYear,
            eventYear: this.eventYear
        };
    }
}

// Utility functions for working with events
const EventUtils = {
    /**
     * Filter events by continent
     */
    filterByContinent(events, continent) {
        return events.filter(event => event.continent === continent);
    },
    
    /**
     * Filter events by country
     */
    filterByCountry(events, country) {
        return events.filter(event => event.sourceCountry === country);
    },
    
    /**
     * Sort events by date (newest first)
     */
    sortByDate(events, ascending = false) {
        return events.sort((a, b) => {
            const dateA = new Date(a.publishedAt);
            const dateB = new Date(b.publishedAt);
            return ascending ? dateA - dateB : dateB - dateA;
        });
    },
    
    /**
     * Search events by title or description
     */
    searchEvents(events, query) {
        const searchTerm = query.toLowerCase();
        return events.filter(event => 
            event.title.toLowerCase().includes(searchTerm) ||
            event.description.toLowerCase().includes(searchTerm) ||
            event.content.toLowerCase().includes(searchTerm)
        );
    },
    
    /**
     * Group events by continent
     */
    groupByContinent(events) {
        return events.reduce((groups, event) => {
            const continent = event.continent || 'Unknown';
            if (!groups[continent]) {
                groups[continent] = [];
            }
            groups[continent].push(event);
            return groups;
        }, {});
    },
    
    /**
     * Get unique continents from events
     */
    getUniqueContinents(events) {
        return [...new Set(events.map(event => event.continent).filter(Boolean))];
    },
    
    /**
     * Filter events by data source
     */
    filterByDataSource(events, dataSource) {
        return events.filter(event => event.dataSource === dataSource);
    },
    
    /**
     * Get events by data source
     */
    getEventsBySource(events) {
        return events.reduce((groups, event) => {
            const source = event.dataSource || 'unknown';
            if (!groups[source]) {
                groups[source] = [];
            }
            groups[source].push(event);
            return groups;
        }, {});
    },
    
    /**
     * Filter events by location precision
     */
    filterByLocationPrecision(events, precision) {
        return events.filter(event => event.getLocationPrecision() === precision);
    },
    
    /**
     * Get events with exact coordinates
     */
    getEventsWithExactCoordinates(events) {
        return events.filter(event => event.getLocationPrecision() === 'exact');
    },
    
    /**
     * Get location precision statistics
     */
    getLocationPrecisionStats(events) {
        const precisions = events.map(event => event.getLocationPrecision());
        const stats = {};
        
        precisions.forEach(precision => {
            stats[precision] = (stats[precision] || 0) + 1;
        });
        
        return stats;
    },
    
    /**
     * GDELT-specific utility functions
     */
    gdelt: {
        /**
         * Filter events by GDELT event code
         */
        filterByEventCode(events, eventCode) {
            return events.filter(event => 
                event instanceof GDELTEvent && event.eventCode === eventCode
            );
        },
        
        /**
         * Filter events by quad class
         */
        filterByQuadClass(events, quadClass) {
            return events.filter(event => 
                event instanceof GDELTEvent && event.quadClass === quadClass
            );
        },
        
        /**
         * Filter events by tone range
         */
        filterByToneRange(events, minTone, maxTone) {
            return events.filter(event => 
                event instanceof GDELTEvent && 
                event.avgTone >= minTone && event.avgTone <= maxTone
            );
        },
        
        /**
         * Get events by Goldstein scale range
         */
        filterByGoldsteinScale(events, minScale, maxScale) {
            return events.filter(event => 
                event instanceof GDELTEvent && 
                event.goldsteinScale >= minScale && event.goldsteinScale <= maxScale
            );
        },
        
        /**
         * Get events with high mention count
         */
        getHighMentionEvents(events, threshold = 10) {
            return events.filter(event => 
                event instanceof GDELTEvent && event.numMentions >= threshold
            );
        },
        
        /**
         * Group events by event code
         */
        groupByEventCode(events) {
            const gdeltEvents = events.filter(event => event instanceof GDELTEvent);
            return gdeltEvents.reduce((groups, event) => {
                const code = event.eventCode || 'Unknown';
                if (!groups[code]) {
                    groups[code] = [];
                }
                groups[code].push(event);
                return groups;
            }, {});
        },
        
        /**
         * Get tone statistics
         */
        getToneStatistics(events) {
            const gdeltEvents = events.filter(event => event instanceof GDELTEvent);
            const tones = gdeltEvents.map(event => event.avgTone).filter(tone => tone !== null);
            if (tones.length === 0) return null;
            
            const avg = tones.reduce((sum, tone) => sum + tone, 0) / tones.length;
            const min = Math.min(...tones);
            const max = Math.max(...tones);
            
            return {
                average: avg,
                minimum: min,
                maximum: max,
                count: tones.length
            };
        }
    },
    
    /**
     * NewsAPI-specific utility functions
     */
    newsapi: {
        /**
         * Filter events by NewsAPI source
         */
        filterBySource(events, sourceName) {
            return events.filter(event => 
                event instanceof NewsAPIEvent && event.source.name === sourceName
            );
        },
        
        /**
         * Get events by NewsAPI source
         */
        groupBySource(events) {
            const newsApiEvents = events.filter(event => event instanceof NewsAPIEvent);
            return newsApiEvents.reduce((groups, event) => {
                const source = event.source.name || 'Unknown';
                if (!groups[source]) {
                    groups[source] = [];
                }
                groups[source].push(event);
                return groups;
            }, {});
        }
    }
};

function addNewsApiLayer(map, newsData) {
    newsData.forEach(article => {
        // Only add if both latitude and longitude are present
        if (article.latitude != null && article.longitude != null) {
            // Use a larger, transparent circle for NewsAPI data
            L.circle([article.latitude, article.longitude], {
                color: 'blue',
                fillColor: 'blue',
                fillOpacity: 0.25,
                radius: 20000, // Adjust for your map's scale (meters)
                weight: 2
            }).addTo(map)
            .bindPopup(`<b>${article.title}</b><br>${article.location_name || ''}`);
        }
    });
}


// Export for use in other modules (ES6 modules)
export { NewsEvent, NewsAPIEvent, GDELTEvent, EventUtils, addNewsApiLayer };