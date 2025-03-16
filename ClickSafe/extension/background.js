// Log a message when the extension is installed
chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed');
});

// Monitor URLs visited by the user
chrome.webRequest.onBeforeRequest.addListener(
    (details) => {
        const url = details.url; // Capture the URL

        // Send the URL to the Flask backend for prediction
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.prediction === 'phishing') {
                // Notify the user if the URL is predicted as phishing
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'icons/icon48.png',
                    title: 'Phishing Warning',
                    message: `The URL "${url}" may be phishing!`,
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    },
    { urls: ['<all_urls>'] } // Monitor all URLs
);