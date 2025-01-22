const express = require('express');
const cors = require('cors');
const apiRoutes = require('./routes/api');

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

app.listen(port, () => {
  console.log(`Serveur démarré sur http://localhost:${port}`);
});
