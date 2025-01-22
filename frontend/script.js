document.addEventListener('DOMContentLoaded', function() {
    const motsContainer = document.getElementById('mots-container');

    fetch('http://localhost:3000/api/mots') // Utilisation de l'API
        .then(response => response.json())
        .then(data => {
            data.forEach(mot => {
                const motCard = document.createElement('div');
                motCard.classList.add('mot-card');
                motCard.innerHTML = `
                    <h3>${mot.word}</h3>
                    <p>${mot.translation}</p>
                    <audio src="${mot.audio}" controls></audio>
                `;
                motsContainer.appendChild(motCard);
            });
        })
        .catch(error => console.error('Erreur lors du chargement des mots:', error));
});
