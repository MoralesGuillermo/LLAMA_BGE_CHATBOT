// Speech to Text Service connection with the backend

// Returns a promise to transcribe the given audio blob
export default async function transcribe(audioBlob){
    const apiUrl = import.meta.env.VITE_API_URL;
    const requestBody = new FormData();
    requestBody.append('audio', audioBlob);
    fetch(`${apiUrl}/transcribe`, {
        method: 'POST',
        body: requestBody,
    })
    .then(response => response.json())
    .then(data => {
        return data.text;
    }
    )
    .catch(error => {
        console.log("Error al realizar la transcripción: ", error);
        return null;
    })
};