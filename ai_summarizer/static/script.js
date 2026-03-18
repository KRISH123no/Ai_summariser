let selectedFile = null;

document.addEventListener('DOMContentLoaded', function() {
    initDropZone();
    initFileInput();
    initYoutubeInput();
});

function initDropZone() {
    const dropZone = document.getElementById('drop-zone');
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
}

function initFileInput() {
    const fileInput = document.getElementById('pdf-input');
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
}

function handleFile(file) {
    if (file.type !== 'application/pdf') {
        showError('Please upload a PDF file');
        return;
    }
    
    selectedFile = file;
    
    document.getElementById('drop-zone').style.display = 'none';
    document.getElementById('file-info').style.display = 'flex';
    document.getElementById('file-name').textContent = file.name;
    
    hideError();
}

function removeFile() {
    selectedFile = null;
    document.getElementById('pdf-input').value = '';
    document.getElementById('drop-zone').style.display = 'block';
    document.getElementById('file-info').style.display = 'none';
    document.getElementById('file-name').textContent = '';
}

function initYoutubeInput() {
    const urlInput = document.getElementById('youtube-url');
    
    urlInput.addEventListener('input', (e) => {
        const url = e.target.value.trim();
        if (url) {
            const videoId = extractVideoId(url);
            if (videoId) {
                document.getElementById('url-preview').innerHTML = 
                    `<img src="https://img.youtube.com/vi/${videoId}/mqdefault.jpg" alt="Video preview">`;
            } else {
                document.getElementById('url-preview').innerHTML = '';
            }
        } else {
            document.getElementById('url-preview').innerHTML = '';
        }
    });
}

function extractVideoId(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
        /youtube\.com\/shorts\/([^&\n?#]+)/
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) return match[1];
    }
    return null;
}

async function generateContent() {
    hideError();
    
    const features = Array.from(document.querySelectorAll('input[name="features"]:checked'))
        .map(cb => cb.value);
    
    if (!selectedFile && !document.getElementById('youtube-url').value.trim()) {
        showError('Please upload a PDF or enter a YouTube URL');
        return;
    }
    
    if (features.length === 0) {
        showError('Please select at least one feature');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    
    if (selectedFile) {
        formData.append('pdf', selectedFile);
    }
    
    formData.append('youtube_url', document.getElementById('youtube-url').value.trim());
    
    features.forEach(f => formData.append('features', f));
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        
        hideLoading();
        
        if (!response.ok) {
            const data = await response.json();
            showError(data.error || 'An error occurred');
        } else {
            const html = await response.text();
            document.documentElement.innerHTML = html;
        }
    } catch (error) {
        hideLoading();
        showError('AI generation failed. Please try again');
    }
}

function showLoading() {
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('generate-btn').disabled = true;
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('generate-btn').disabled = false;
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}
