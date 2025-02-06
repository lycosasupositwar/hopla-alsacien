# Étape de construction
FROM node:14 AS build
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour installer les dépendances
COPY package.json package-lock.json ./
RUN npm install --production

# Copier le reste de l'application
COPY . .

# Étape finale
FROM node:14-alpine
WORKDIR /app

# Copier uniquement les fichiers nécessaires depuis l'étape de construction
COPY --from=build /app .

EXPOSE 3000
CMD ["node", "server.js"]
