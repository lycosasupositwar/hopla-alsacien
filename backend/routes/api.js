const express = require('express');
const router = express.Router();

// Données de test
const alsacienData = [
    { id: 1, word: "Guten Tach", translation: "Bonjour" },
    { id: 2, word: "Wie geht's?", translation: "Comment ça va ?" },
    { id: 3, word: "Mache's guet", translation: "Au revoir" }
];

router.get('/mots', async (req, res) => {
    const motsAvecAudio = await Promise.all(alsacienData.map(async mot => {
            const audioUrl = await req.app.locals.generateAudio(mot.word);
            return {...mot, audio: audioUrl};
        }));
    res.json(motsAvecAudio);
});

module.exports = router;
