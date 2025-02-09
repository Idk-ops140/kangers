document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const videoListContainer = document.getElementById('videos-container');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const messageDiv = document.getElementById('message');

    // Function to fetch and display videos
    const fetchVideos = async (searchQuery = '') => {
        try {
            const response = await fetch(`/api/videos?search=${searchQuery}`); // Backend API endpoint
            const videos = await response.json();

            videoListContainer.innerHTML = ''; // Clear previous videos

            videos.forEach(video => {
                const videoItem = document.createElement('div');
                videoItem.classList.add('video-item');
                if (video.url.includes("youtube.com")) { //check if url is from youtube
                    // Extract YouTube video ID
                    const videoId = video.url.split('v=')[1].substring(0, 11);
                    videoItem.innerHTML = `
                        <h3>${video.title}</h3>
                        <iframe width="100%" height="200" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen></iframe>
                    `;
                } else { //if it is not from youtube.com
                    videoItem.innerHTML = `
                        <h3>${video.title}</h3>
                        <video controls>
                            <source src="${video.url}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    `;
                }
                videoListContainer.appendChild(videoItem);
            });
        } catch (error) {
            console.error('Error fetching videos:', error);
            messageDiv.textContent = 'Failed to load videos.';
        }
    };

    // Handle form submission (video upload)
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const title = document.getElementById('video-title').value;
        const url = document.getElementById('video-url').value;
        // const fileInput = document.getElementById('video-file'); // For direct file uploads
        // let file = null;
        // if (fileInput.files.length > 0) {
        //    file = fileInput.files[0];
        //}

        // Basic validation
        if (!title || !url) {
            messageDiv.textContent = 'Please enter both title and URL.';
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('url', url);
        // if (file) {
        //     formData.append('file', file);
        // }

        try {
            const response = await fetch('/api/videos', {  // Backend API endpoint
                method: 'POST',
                body: formData,  //  Send as FormData
            });

            if (response.ok) {
                messageDiv.textContent = 'Video uploaded successfully!';
                uploadForm.reset();
                fetchVideos(); // Refresh the video list
            } else {
                const data = await response.json();
                messageDiv.textContent = `Error: ${data.message || 'Failed to upload video.'}`;
            }
        } catch (error) {
            console.error('Error uploading video:', error);
            messageDiv.textContent = 'Failed to upload video.';
        }
    });

    // Handle search
    searchButton.addEventListener('click', () => {
        const searchQuery = searchInput.value;
        fetchVideos(searchQuery);
    });

    // Initial video load
    fetchVideos();
});
