
// ============================================
// AI RECOMMENDATIONS FUNCTIONS
// ============================================

function loadAIDashboard() {
    // Load AI dashboard
    fetch("/ai/api/global-recommendations/")
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('AI Error:', data.error);
                return;
            }
            displayRecommendations(data.recommendations);
            displayGlobalStats(data.global_stats);
        })
        .catch(error => console.error('Error loading AI recommendations:', error));
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('ai-recommendations');
    if (!container) return;
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No recommendations available</div>';
        return;
    }
    
    let html = '';
    recommendations.forEach(rec => {
        const priorityClass = rec.priority === 'HIGH' ? 'danger' : 
                             rec.priority === 'MEDIUM' ? 'warning' : 'info';
        html += `
            <div class="card mb-3 border-left-${priorityClass}">
                <div class="card-body">
                    <h5 class="card-title">${rec.action}</h5>
                    <p class="card-text">${rec.details}</p>
                    <span class="badge bg-${priorityClass}">${rec.priority}</span>
                    <ul class="mt-2">
                        ${rec.steps.map(step => `<li>${step}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function displayGlobalStats(stats) {
    const container = document.getElementById('ai-stats');
    if (!container) return;
    
    if (!stats) {
        container.innerHTML = '<div class="text-center text-muted">No stats available</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="row">
            <div class="col-4">
                <div class="card bg-primary text-white">
                    <div class="card-body text-center">
                        <h4>${stats.total_students || 0}</h4>
                        <small>Total Students</small>
                    </div>
                </div>
            </div>
            <div class="col-4">
                <div class="card bg-danger text-white">
                    <div class="card-body text-center">
                        <h4>${stats.critical_count || 0}</h4>
                        <small>Critical</small>
                    </div>
                </div>
            </div>
            <div class="col-4">
                <div class="card bg-warning text-white">
                    <div class="card-body text-center">
                        <h4>${stats.warning_count || 0}</h4>
                        <small>Warning</small>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Load AI dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('ai-dashboard-content')) {
        loadAIDashboard();
    }
});
