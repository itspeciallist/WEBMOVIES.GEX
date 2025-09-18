// Enhanced Georgian Movie Website JavaScript - Universal Video Player & Admin Functions

// Universal Video Player Functions
function openVideoPlayer(videoUrl, title) {
    const modal = document.getElementById('videoPlayerModal');
    const titleElement = document.getElementById('videoPlayerTitle');
    const contentElement = document.getElementById('videoPlayerContent');
    
    titleElement.textContent = title;
    modal.style.display = 'flex';
    
    // Clear previous content
    contentElement.innerHTML = '';
    
    try {
        if (isYouTubeURL(videoUrl)) {
            embedYouTube(videoUrl, contentElement);
        } else if (isVimeoURL(videoUrl)) {
            embedVimeo(videoUrl, contentElement);
        } else if (isDailymotionURL(videoUrl)) {
            embedDailymotion(videoUrl, contentElement);
        } else if (isDirectVideoURL(videoUrl)) {
            embedDirectVideo(videoUrl, contentElement);
        } else {
            // Fallback: try to embed as iframe or direct video
            embedFallback(videoUrl, contentElement);
        }
    } catch (error) {
        console.error('Error loading video:', error);
        contentElement.innerHTML = `
            <div style="color: white; text-align: center; padding: 2rem;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h3>ვიდეოს ჩატვირთვისას მოხდა შეცდომა</h3>
                <p>გთხოვთ შეამოწმოთ ვიდეოს ლინკი</p>
                <a href="${videoUrl}" target="_blank" class="btn btn-primary" style="margin-top: 1rem;">
                    <i class="fas fa-external-link-alt"></i>
                    ახალ ფანჯარაში გახსნა
                </a>
            </div>
        `;
    }
    
    // Close on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeVideoPlayer();
        }
    });
    
    // Close on background click
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeVideoPlayer();
        }
    });
}

function closeVideoPlayer() {
    const modal = document.getElementById('videoPlayerModal');
    const contentElement = document.getElementById('videoPlayerContent');
    
    modal.style.display = 'none';
    contentElement.innerHTML = '';
    
    // Remove event listeners
    document.removeEventListener('keydown', closeVideoPlayerHandler);
}

function closeVideoPlayerHandler(event) {
    if (event.key === 'Escape') {
        closeVideoPlayer();
    }
}

// Video URL Detection Functions
function isYouTubeURL(url) {
    return /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([^&\n?#]+)/.test(url);
}

function isVimeoURL(url) {
    return /vimeo\.com\/(\d+)/.test(url);
}

function isDailymotionURL(url) {
    return /dailymotion\.com\/video\/([^_]+)/.test(url);
}

function isDirectVideoURL(url) {
    return /\.(mp4|webm|ogg|avi|mov|wmv|flv|mkv)(\?.*)?$/i.test(url);
}

// Video Embedding Functions
function embedYouTube(url, container) {
    const videoId = extractYouTubeID(url);
    if (videoId) {
        const iframe = document.createElement('iframe');
        iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`;
        iframe.width = '100%';
        iframe.height = '600';
        iframe.frameBorder = '0';
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        iframe.allowFullscreen = true;
        container.appendChild(iframe);
    }
}

function embedVimeo(url, container) {
    const videoId = extractVimeoID(url);
    if (videoId) {
        const iframe = document.createElement('iframe');
        iframe.src = `https://player.vimeo.com/video/${videoId}?autoplay=1&color=e50914`;
        iframe.width = '100%';
        iframe.height = '600';
        iframe.frameBorder = '0';
        iframe.allow = 'autoplay; fullscreen; picture-in-picture';
        iframe.allowFullscreen = true;
        container.appendChild(iframe);
    }
}

function embedDailymotion(url, container) {
    const videoId = extractDailymotionID(url);
    if (videoId) {
        const iframe = document.createElement('iframe');
        iframe.src = `https://www.dailymotion.com/embed/video/${videoId}?autoplay=1`;
        iframe.width = '100%';
        iframe.height = '600';
        iframe.frameBorder = '0';
        iframe.allow = 'autoplay; fullscreen';
        iframe.allowFullscreen = true;
        container.appendChild(iframe);
    }
}

function embedDirectVideo(url, container) {
    const video = document.createElement('video');
    video.src = url;
    video.controls = true;
    video.autoplay = true;
    video.style.width = '100%';
    video.style.height = 'auto';
    video.style.maxHeight = '600px';
    container.appendChild(video);
}

function embedFallback(url, container) {
    // Try iframe first
    const iframe = document.createElement('iframe');
    iframe.src = url;
    iframe.width = '100%';
    iframe.height = '600';
    iframe.frameBorder = '0';
    iframe.allow = 'autoplay; fullscreen';
    iframe.allowFullscreen = true;
    
    iframe.onerror = function() {
        // If iframe fails, show link
        container.innerHTML = `
            <div style="color: white; text-align: center; padding: 2rem;">
                <i class="fas fa-play-circle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h3>ვიდეოს ყურება</h3>
                <p>ამ ვიდეოს ყურება შესაძლებელია გარე ლინკით</p>
                <a href="${url}" target="_blank" class="btn btn-primary" style="margin-top: 1rem;">
                    <i class="fas fa-external-link-alt"></i>
                    ვიდეოს ყურება
                </a>
            </div>
        `;
    };
    
    container.appendChild(iframe);
}

// ID Extraction Functions
function extractYouTubeID(url) {
    const match = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([^&\n?#]+)/);
    return match ? match[1] : null;
}

function extractVimeoID(url) {
    const match = url.match(/vimeo\.com\/(\d+)/);
    return match ? match[1] : null;
}

function extractDailymotionID(url) {
    const match = url.match(/dailymotion\.com\/video\/([^_]+)/);
    return match ? match[1] : null;
}

// Admin Delete Functions
function confirmDelete(movieId, movieTitle) {
    const modal = document.getElementById('deleteModal');
    const titleElement = document.getElementById('movieToDelete');
    const form = document.getElementById('deleteForm');
    
    if (modal && titleElement && form) {
        titleElement.textContent = movieTitle;
        form.action = `/movie/${movieId}/delete`;
        modal.style.display = 'flex';
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Favorite Functions
function toggleFavorite(movieId) {
    fetch(`/movie/${movieId}/favorite`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update button state
            const buttons = document.querySelectorAll(`[data-movie-id="${movieId}"]`);
            buttons.forEach(button => {
                const icon = button.querySelector('i');
                if (data.is_favorite) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    button.classList.add('active');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    button.classList.remove('active');
                }
            });
            
            // Show notification
            showNotification(data.message, 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('შეცდომა მოხდა', 'error');
    });
}

// Notification Function
function showNotification(message, type = 'success') {
    const container = document.querySelector('.alert-container') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-icon">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        </span>
        <span class="alert-message">${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container';
    document.body.appendChild(container);
    return container;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Close modals on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const videoModal = document.getElementById('videoPlayerModal');
            const deleteModal = document.getElementById('deleteModal');
            
            if (videoModal && videoModal.style.display === 'flex') {
                closeVideoPlayer();
            }
            if (deleteModal && deleteModal.style.display === 'flex') {
                closeDeleteModal();
            }
        }
    });
    
    // Close modals on background click
    const modals = document.querySelectorAll('.modal, .video-player-modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                if (modal.id === 'videoPlayerModal') {
                    closeVideoPlayer();
                } else if (modal.id === 'deleteModal') {
                    closeDeleteModal();
                }
            }
        });
    });
    
    // Auto-hide alerts
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.animation = 'slideOutRight 0.3s ease-out forwards';
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Enhanced search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Could implement live search here
            }, 300);
        });
    }
    
    // Rating stars interaction
    const starInputs = document.querySelectorAll('.stars-input input[type="radio"]');
    const starLabels = document.querySelectorAll('.star-label');
    
    starLabels.forEach((label, index) => {
        label.addEventListener('mouseenter', () => {
            highlightStars(index + 1);
        });
        
        label.addEventListener('mouseleave', () => {
            const checkedStar = document.querySelector('.stars-input input[type="radio"]:checked');
            if (checkedStar) {
                highlightStars(parseInt(checkedStar.value));
            } else {
                highlightStars(0);
            }
        });
        
        label.addEventListener('click', () => {
            highlightStars(index + 1);
        });
    });
    
    function highlightStars(rating) {
        starLabels.forEach((label, index) => {
            const star = label.querySelector('i');
            if (index < rating) {
                star.style.color = '#ffd700';
            } else {
                star.style.color = '#666';
            }
        });
    }
    
    // Initialize star ratings
    const checkedStar = document.querySelector('.stars-input input[type="radio"]:checked');
    if (checkedStar) {
        highlightStars(parseInt(checkedStar.value));
    }
});

// Add slideOutRight animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);