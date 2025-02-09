async function fetchVideoStream() {
  const response = await fetch("http://127.0.0.1:5000/stream");
  const data = await response.json();
  console.log(data.scores); // Display anomaly scores
}

fetchVideoStream();
