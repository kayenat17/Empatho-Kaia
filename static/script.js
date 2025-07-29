// VoiceLens - Interactive JavaScript

class VoiceLens {
    constructor() {
        this.currentAnalysis = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadStats();
    }

    initializeElements() {
        // Text input elements
        this.textInput = document.getElementById('textInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        
        // Analysis elements
        this.analysisResults = document.getElementById('analysisResults');
        this.emotionIcon = document.getElementById('emotionIcon');
        this.emotionText = document.getElementById('emotionText');
        this.confidenceText = document.getElementById('confidenceText');
        this.emotionScores = document.getElementById('emotionScores');
        this.recommendationText = document.getElementById('recommendationText');
        this.saveEntryBtn = document.getElementById('saveEntryBtn');
        
        // Stats elements
        this.streakDays = document.getElementById('streakDays');
        this.weeklyEntries = document.getElementById('weeklyEntries');
        this.dominantEmotion = document.getElementById('dominantEmotion');
        this.emotionChart = document.getElementById('emotionChart');
        
        // Modal elements
        this.wellnessModal = document.getElementById('wellnessModal');
        this.wellnessText = document.getElementById('wellnessText');
        this.checkWellnessBtn = document.getElementById('checkWellnessBtn');
        this.wellnessResults = document.getElementById('wellnessResults');
    }

    bindEvents() {
        // Text analysis events
        this.analyzeBtn.addEventListener('click', () => this.analyzeText());
        this.saveEntryBtn.addEventListener('click', () => this.saveEntry());
        
        // Modal events
        document.querySelector('.close').addEventListener('click', () => this.closeModal());
        this.checkWellnessBtn.addEventListener('click', () => this.performWellnessCheck());
        
        // Close modal when clicking outside
        this.wellnessModal.addEventListener('click', (e) => {
            if (e.target === this.wellnessModal) {
                this.closeModal();
            }
        });
    }



    async analyzeText() {
        const text = this.textInput.value.trim();
        if (!text) {
            this.showNotification('Please enter some text to analyze', 'error');
            return;
        }

        this.showNotification('Analyzing emotions...', 'info');
        
        try {
            const response = await fetch('/api/journal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    entry: text,
                    voice_data: null // In real implementation, this would contain audio features
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.currentAnalysis = data.analysis;
                this.displayAnalysis(data.analysis);
                this.showNotification('Analysis complete!', 'success');
            } else {
                throw new Error(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Analysis failed. Please try again.', 'error');
        }
    }

    displayAnalysis(analysis) {
        const emotion = analysis.text_analysis.dominant_emotion;
        const confidence = analysis.text_analysis.confidence;
        const recommendation = analysis.recommendation;

        // Update emotion display
        this.emotionIcon.className = `emotion-icon ${emotion}`;
        this.emotionIcon.innerHTML = this.getEmotionIcon(emotion);
        this.emotionText.textContent = this.capitalizeFirst(emotion);
        this.confidenceText.textContent = `Confidence: ${(confidence * 100).toFixed(1)}%`;

        // Update emotion scores
        this.displayEmotionScores(analysis.text_analysis.emotion_scores);

        // Update recommendation
        this.recommendationText.textContent = recommendation;

        // Show results
        this.analysisResults.classList.remove('hidden');
    }

    displayEmotionScores(scores) {
        this.emotionScores.innerHTML = '';
        
        Object.entries(scores)
            .sort(([,a], [,b]) => b - a)
            .forEach(([emotion, score]) => {
                if (score > 0) {
                    const scoreElement = document.createElement('div');
                    scoreElement.className = 'emotion-score';
                    scoreElement.innerHTML = `
                        <strong>${this.capitalizeFirst(emotion)}</strong><br>
                        ${(score * 100).toFixed(1)}%
                    `;
                    this.emotionScores.appendChild(scoreElement);
                }
            });
    }

    getEmotionIcon(emotion) {
        const icons = {
            joy: '<i class="fas fa-laugh"></i>',
            sadness: '<i class="fas fa-sad-tear"></i>',
            anger: '<i class="fas fa-angry"></i>',
            fear: '<i class="fas fa-fearful"></i>',
            surprise: '<i class="fas fa-surprise"></i>',
            disgust: '<i class="fas fa-dizzy"></i>',
            trust: '<i class="fas fa-heart"></i>',
            anticipation: '<i class="fas fa-star"></i>',
            neutral: '<i class="fas fa-meh"></i>'
        };
        return icons[emotion] || icons.neutral;
    }

    async saveEntry() {
        if (!this.currentAnalysis) {
            this.showNotification('Please analyze some text first', 'error');
            return;
        }

        try {
            this.saveEntryBtn.disabled = true;
            this.saveEntryBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            
            // Entry is already saved during analysis, just update UI
            this.showNotification('Entry saved successfully!', 'success');
            this.loadStats();
            
            // Reset form
            this.textInput.value = '';
            this.analysisResults.classList.add('hidden');
            this.currentAnalysis = null;
            
        } catch (error) {
            console.error('Save error:', error);
            this.showNotification('Failed to save entry', 'error');
        } finally {
            this.saveEntryBtn.disabled = false;
            this.saveEntryBtn.innerHTML = '<i class="fas fa-save"></i> Save Entry';
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            this.streakDays.textContent = stats.streak_days;
            this.weeklyEntries.textContent = stats.weekly_entries;
            this.dominantEmotion.textContent = this.capitalizeFirst(stats.most_common_emotion);
            
            this.displayEmotionChart(stats.emotion_distribution);
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    displayEmotionChart(emotionDistribution) {
        if (Object.keys(emotionDistribution).length === 0) {
            this.emotionChart.innerHTML = '<p>No data available yet. Start journaling to see your emotional patterns!</p>';
            return;
        }

        const chartHTML = Object.entries(emotionDistribution)
            .map(([emotion, count]) => `
                <div class="chart-item">
                    <div class="chart-bar" style="height: ${count * 20}px; background: ${this.getEmotionColor(emotion)}"></div>
                    <span>${this.capitalizeFirst(emotion)}</span>
                    <small>${count}</small>
                </div>
            `).join('');

        this.emotionChart.innerHTML = `
            <div class="chart-grid">
                ${chartHTML}
            </div>
        `;
    }

    getEmotionColor(emotion) {
        const colors = {
            joy: '#10b981',
            sadness: '#64748b',
            anger: '#ef4444',
            fear: '#f59e0b',
            surprise: '#8b5cf6',
            disgust: '#06b6d4',
            trust: '#6366f1',
            anticipation: '#f97316',
            neutral: '#94a3b8'
        };
        return colors[emotion] || '#94a3b8';
    }

    openWellnessCheck() {
        this.wellnessModal.classList.remove('hidden');
        this.wellnessText.focus();
    }

    closeModal() {
        this.wellnessModal.classList.add('hidden');
        this.wellnessText.value = '';
        this.wellnessResults.classList.add('hidden');
    }

    async performWellnessCheck() {
        const text = this.wellnessText.value.trim();
        if (!text) {
            this.showNotification('Please enter some text for wellness check', 'error');
            return;
        }

        try {
            this.checkWellnessBtn.disabled = true;
            this.checkWellnessBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

            const response = await fetch('/api/wellness-check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.displayWellnessResults(data);
            } else {
                throw new Error(data.error || 'Wellness check failed');
            }
        } catch (error) {
            console.error('Wellness check error:', error);
            this.showNotification('Wellness check failed. Please try again.', 'error');
        } finally {
            this.checkWellnessBtn.disabled = false;
            this.checkWellnessBtn.innerHTML = '<i class="fas fa-brain"></i> Analyze';
        }
    }

    displayWellnessResults(data) {
        const intensityClass = data.intensity === 'high' ? 'high-intensity' : 
                              data.intensity === 'medium' ? 'medium-intensity' : 'low-intensity';
        
        this.wellnessResults.innerHTML = `
            <div class="wellness-result ${intensityClass}">
                <h4>Emotion: ${this.capitalizeFirst(data.emotion)}</h4>
                <p><strong>Sentiment:</strong> ${this.capitalizeFirst(data.sentiment)}</p>
                <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                <p><strong>Intensity:</strong> ${this.capitalizeFirst(data.intensity)}</p>
                <hr>
                <p><strong>Recommendation:</strong></p>
                <p>${data.recommendation}</p>
            </div>
        `;
        
        this.wellnessResults.classList.remove('hidden');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Navigation functions
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Add active class to clicked nav link
    event.target.classList.add('active');
    
    // Load stats when showing insights
    if (sectionName === 'insights') {
        voiceLens.loadStats();
    }
}

// Placeholder functions for future features
function openCommunity() {
    voiceLens.showNotification('Community feature coming soon!', 'info');
}

function openTherapistPortal() {
    voiceLens.showNotification('Therapist portal feature coming soon!', 'info');
}

// Initialize VoiceLens when DOM is loaded
let voiceLens;
document.addEventListener('DOMContentLoaded', () => {
    voiceLens = new VoiceLens();
});

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid #10b981;
        color: #065f46;
    }
    
    .notification-error {
        border-left: 4px solid #ef4444;
        color: #991b1b;
    }
    
    .notification-warning {
        border-left: 4px solid #f59e0b;
        color: #92400e;
    }
    
    .notification-info {
        border-left: 4px solid #6366f1;
        color: #3730a3;
    }
    
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        gap: 1rem;
        align-items: end;
        height: 200px;
    }
    
    .chart-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chart-bar {
        width: 100%;
        min-height: 20px;
        border-radius: 4px;
        transition: height 0.3s ease;
    }
    
    .wellness-result {
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    
    .wellness-result.high-intensity {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
    }
    
    .wellness-result.medium-intensity {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
    }
    
    .wellness-result.low-intensity {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
    }
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet); 