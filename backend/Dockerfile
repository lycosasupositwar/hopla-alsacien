# Étape de construction
FROM node:14 AS build
WORKDIR /app

# Copier uniquement package.json
COPY package.json ./
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
