/**
 * Lucky Stories Module
 * Handles the "I'm feeling lucky" functionality for random story selection
 */

let currentModal = null;

/**
 * Fetch and display a random story from a specific continent
 * @param {string} continent - The continent name (Americas, Africa, Asia, Europe, Oceania)
 */
export function getLuckyStory(continent) {
    // Show loading state
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    fetch(`/api/lucky/${continent}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const story = data.story;
                
                // Clean up any existing modal first
                cleanupModal();
                
                // Create modal content
                let modalContent = `
                    <div class="modal fade" id="luckyModal" tabindex="-1" aria-labelledby="luckyModalLabel" aria-hidden="true">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="luckyModalLabel">Random Story from ${continent}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <h6 class="card-title">${story.title || story.translated_title || 'No title available'}</h6>
                                    <p class="card-text">${story.description || story.translated_content || 'No description available'}</p>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <small class="text-muted">
                                                <strong>Source:</strong> ${story.data_source.toUpperCase()}<br>
                                                ${story.location_name ? `<strong>Location:</strong> ${story.location_name}<br>` : ''}
                                                ${story.source_country ? `<strong>Country:</strong> ${story.source_country}<br>` : ''}
                                                ${story.actor1_country ? `<strong>Actor 1:</strong> ${story.actor1_country}<br>` : ''}
                                                ${story.actor2_country ? `<strong>Actor 2:</strong> ${story.actor2_country}<br>` : ''}
                                            </small>
                                        </div>
                                        <div class="col-md-6">
                                            <small class="text-muted">
                                                ${story.sentiment_score ? `<strong>Sentiment:</strong> ${story.sentiment_score}<br>` : ''}
                                                ${story.goldstein ? `<strong>Goldstein:</strong> ${story.goldstein}<br>` : ''}
                                                ${story.event_code ? `<strong>Event Code:</strong> ${story.event_code}<br>` : ''}
                                                ${story.date ? `<strong>Date:</strong> ${story.date}<br>` : ''}
                                            </small>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                    ${story.url && story.url !== '#' ? `<a href="${story.url}" target="_blank" class="btn btn-primary">Read Full Article</a>` : ''}
                                    <button type="button" class="btn btn-success" onclick="window.luckyStories.getLuckyStory('${continent}')">Try Another</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Add new modal to body
                document.body.insertAdjacentHTML('beforeend', modalContent);
                
                // Create and show modal
                const modalElement = document.getElementById('luckyModal');
                currentModal = new bootstrap.Modal(modalElement);
                
                // Add event listener to clean up when modal is hidden
                modalElement.addEventListener('hidden.bs.modal', function() {
                    cleanupModal();
                });
                
                currentModal.show();
                
                // Reset button
                button.textContent = originalText;
                button.disabled = false;
            } else {
                alert(`No stories found for ${continent}. Please try again later.`);
                button.textContent = originalText;
                button.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error fetching lucky story:', error);
            alert('Error fetching random story. Please try again.');
            button.textContent = originalText;
            button.disabled = false;
        });
}

/**
 * Clean up modal elements and Bootstrap state
 */
function cleanupModal() {
    // Hide and dispose of current modal if it exists
    if (currentModal) {
        currentModal.hide();
        currentModal.dispose();
        currentModal = null;
    }
    
    // Remove any existing modal elements
    const existingModals = document.querySelectorAll('#luckyModal');
    existingModals.forEach(modal => {
        modal.remove();
    });
    
    // Remove any modal backdrops
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => {
        backdrop.remove();
    });
    
    // Remove modal-open class from body
    document.body.classList.remove('modal-open');
    
    // Remove any inline styles added by Bootstrap
    document.body.style.removeProperty('padding-right');
    document.body.style.removeProperty('overflow');
}

// Make functions available globally for onclick handlers
window.luckyStories = {
    getLuckyStory: getLuckyStory
}; 