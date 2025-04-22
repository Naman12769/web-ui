async function ingestUrls() {
    const urls = document.getElementById('urls').value.split('\n');
    const statusDiv = document.getElementById('ingestStatus');
    
    try {
        const response = await fetch('/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ urls: urls })
        });
        
        const data = await response.json();
        statusDiv.textContent = data.message;
        statusDiv.style.color = 'green';
    } catch (error) {
        statusDiv.textContent = 'Error processing URLs';
        statusDiv.style.color = 'red';
    }
}

async function askQuestion() {
    const question = document.getElementById('question').value;
    const answerDiv = document.getElementById('answer');
    
    if (!question) {
        answerDiv.textContent = 'Please enter a question';
        return;
    }

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        answerDiv.textContent = `Answer: ${data.answer}`;
        answerDiv.style.color = 'black';
    } catch (error) {
        answerDiv.textContent = 'Error getting answer';
        answerDiv.style.color = 'red';
    }
}
