# Étape de construction
FROM node:14 AS build
WORKDIR /app

# Copier les fichiers du frontend
COPY . .

# Installer les dépendances et construire l'application (si nécessaire)
# RUN npm install && npm run build

# Étape finale
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Copier uniquement les fichiers statiques depuis l'étape de construction
COPY --from=build /app .

EXPOSE 80
