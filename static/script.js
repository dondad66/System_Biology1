document.getElementById('accession-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const accessionNumber = document.getElementById('accession-number').value;
    fetch(`/fetch_data?accession_number=${accessionNumber}`)
        .then(response => response.json())
        .then(data => {
            let output = '<h2>Results:</h2>';
            output += `<p><strong>Ensembl:</strong> ${JSON.stringify(data.ensembl)}</p>`;
            output += `<p><strong>NCBI:</strong> ${JSON.stringify(data.ncbi)}</p>`;
            document.getElementById('results').innerHTML = output;
        })
        .catch(error => {
            document.getElementById('results').innerHTML = '<p>Error fetching data.</p>';
            console.error('Error:', error);
        });
});

document.getElementById('chromosome-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const chromosomeNumber = document.getElementById('chromosome-number').value;
    window.location.href = `/download_chromosome?chromosome=${chromosomeNumber}`;
});
