function getSuggestions(query) {
    if (query.length < 5) {
        document.getElementById('suggestions').innerHTML = "";
        return;
    }
    
    fetch(`/autocomplete-athlete?query=${query}`)
        .then(response => response.json())
        .then(data => {
            let suggestions = data.suggestions.map(s => `<div>${s}</div>`).join('');
            document.getElementById('suggestions').innerHTML = suggestions;
        });
}
