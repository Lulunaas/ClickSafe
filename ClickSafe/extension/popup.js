document.getElementById('sendUrl').addEventListener('click', () => {
    // Show loading message
    const responseElement = document.getElementById('response');
    responseElement.innerText = 'Checking URL...';
    responseElement.style.color = 'black';

    // Get the current active tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs[0]) {
            responseElement.innerText = 'Error: No active tab found.';
            responseElement.style.color = 'red';
            return;
        }

        const url = tabs[0].url;

        // Send the URL to the Flask backend
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Display the prediction result
            if (data.prediction === 'phishing') {
                responseElement.innerText = `Warning: The URL "${url}" may be phishing!`;
                responseElement.style.color = 'red';
            } else {
                responseElement.innerText = `The URL "${url}" is safe.`;
                responseElement.style.color = 'green';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            responseElement.innerText = 'An error occurred. Please try again.';
            responseElement.style.color = 'red';
        });
    });
});