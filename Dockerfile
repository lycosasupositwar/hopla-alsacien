# Utilise une image de base Node.js
FROM node:18-alpine

# Définis le répertoire de travail dans le conteneur
WORKDIR /app

# Copie les fichiers package.json et package-lock.json pour installer les dépendances
COPY package*.json ./

# Installe les dépendances
RUN npm install

# Copie le reste du code de l'application
COPY . .

# Expose le port sur lequel l'application tourne (par exemple 3000)
EXPOSE 3000

# Commande pour démarrer l'application
CMD ["npm", "start"]
