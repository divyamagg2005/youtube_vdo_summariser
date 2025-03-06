document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('videoForm');
    const videoUrlInput = document.getElementById('videoUrl');
    const submitBtn = document.getElementById('submitBtn');
    const errorDiv = document.getElementById('error');
    const errorMessage = errorDiv.querySelector('span');
    const mainContent = document.querySelector('main');

    let isLoading = false;

    const setLoading = (loading) => {
        isLoading = loading;
        submitBtn.disabled = loading;
        submitBtn.textContent = loading ? 'Processing...' : 'Generate Summary';
    };

    const showError = (message) => {
        errorMessage.textContent = message;
        errorDiv.style.display = 'flex';
    };

    const hideError = () => {
        errorDiv.style.display = 'none';
        errorMessage.textContent = '';
    };

    const isValidYouTubeUrl = (url) => {
        try {
            const urlObj = new URL(url);
            return (
                (urlObj.hostname === 'www.youtube.com' || 
                 urlObj.hostname === 'youtube.com' || 
                 urlObj.hostname === 'youtu.be') &&
                (urlObj.pathname.includes('/watch') || 
                 urlObj.hostname === 'youtu.be')
            );
        } catch {
            return false;
        }
    };

    const displaySummary = (summary) => {
        // Create summary container if it doesn't exist, otherwise update it
        let summaryContainer = document.getElementById('summaryContainer');
        
        if (!summaryContainer) {
            summaryContainer = document.createElement('div');
            summaryContainer.id = 'summaryContainer';
            summaryContainer.className = 'summary-container';
            
            // Create title
            const title = document.createElement('h2');
            title.textContent = 'Video Summary';
            summaryContainer.appendChild(title);
            
            // Create content container
            const content = document.createElement('div');
            content.id = 'summaryContent';
            content.className = 'summary-content';
            summaryContainer.appendChild(content);
            
            // Add to page after the form
            form.parentNode.insertBefore(summaryContainer, form.nextSibling);
        }
        
        // Update summary content with new summary
        const summaryContent = document.getElementById('summaryContent');
        summaryContent.innerHTML = summary.replace(/\n/g, '<br>');
        
        // Scroll to summary
        summaryContainer.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        hideError();

        const videoUrl = videoUrlInput.value.trim();

        if (!isValidYouTubeUrl(videoUrl)) {
            showError('Please enter a valid YouTube URL');
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ videoUrl }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate summary');
            }

            displaySummary(data.summary);
        } catch (error) {
            showError(error.message || 'An error occurred while generating the summary');
        } finally {
            setLoading(false);
        }
    };

    form.addEventListener('submit', handleSubmit);
    videoUrlInput.addEventListener('input', hideError);
});