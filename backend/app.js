const express = require('express');
const cors = require('cors');
const apiRoutes = require('./routes/api');
const textToSpeech = require('@google-cloud/text-to-speech');


const app = express();
const port = 3000;

// Autoriser les requêtes CORS
app.use(cors());

// Utiliser les routes API
app.use('/api', apiRoutes);


// Route pour la page d'accueil
app.get('/', (req, res) => {
  res.send('Bienvenue sur le serveur Hopla Alsacien!');
});


// Fonction de synthèse vocale
async function generateAudio(text) {
   const client = new textToSpeech.TextToSpeechClient({
    keyFilename: './key.json' // Tu dois créer un fichier key.json avec la clé de ton API Google Cloud
  });
  const request = {
    input: {text: text},
    voice: {languageCode: 'de-DE', ssmlGender: 'MALE'}, // 'fr-FR' pour Français
    audioConfig: {audioEncoding: 'MP3'},
  };
  const [response] = await client.synthesizeSpeech(request);
  const audioData = Buffer.from(response.audioContent, 'base64').toString('base64');
  return `data:audio/mp3;base64,${audioData}`; // On renvoie un dataURI
}


app.locals.generateAudio = generateAudio;


app.listen(port, () => {
  console.log(`Serveur démarré sur http://localhost:${port}`);
});
