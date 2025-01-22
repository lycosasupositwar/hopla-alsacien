const express = require('express');
const router = express.Router();

// Données de test
const alsacienData = [
  { id: 1, word: "Guten Tach", translation: "Bonjour", audio: "/assets/audio/guten_tach.mp3" },
  { id: 2, word: "Wie geht's?", translation: "Comment ça va ?", audio: "/assets/audio/wie_gehts.mp3" },
  { id: 3, word: "Mache's guet", translation: "Au revoir", audio: "/assets/audio/maches_guet.mp3" }
];


router.get('/mots', (req, res) => {
  res.json(alsacienData);
});


module.exports = router;
