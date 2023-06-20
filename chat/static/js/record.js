let audioChunks = [];
let mediaRecorder;


function startRecording() {
    audioChunks = [];
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (stream) {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.addEventListener('dataavailable', function (event) {
                audioChunks.push(event.data);
            });
            mediaRecorder.start();
            document.getElementById('recordButton').classList.add('recording');
            document.getElementById('recordButton').textContent = 'Recording';
        });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.addEventListener('stop', function () {
            const audioBlob = new Blob(audioChunks, { 'type': 'audio/webm; codecs=opus' });
            const audioUrl = URL.createObjectURL(audioBlob);
            document.getElementById('audioElement').src = audioUrl;

            // Send audio to the server
            uploadAudio(audioBlob);
        });

        mediaRecorder.stop();
        document.getElementById('recordButton').classList.remove('recording');
        document.getElementById('recordButton').textContent = 'Record';
    }
}

function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio', blob);

    // Get the CSRF token from the cookie
    const csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/upload/',  // Replace with the server endpoint for audio upload
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function (response) {
            console.log('Audio uploaded successfully!');
            $('#transcription').html(response.transcription)
            $('#answer').html(response.answer)
        },
        error: function (error) {
            console.error('Error uploading audio:', error);
        }
    });
}

// Function to retrieve the CSRF token from the cookie
function getCookie(name) {
    const cookieValue = document.cookie.match('(^|;)\\s*' + name + '=([^;]*)');
    return cookieValue ? cookieValue.pop() : '';
}
