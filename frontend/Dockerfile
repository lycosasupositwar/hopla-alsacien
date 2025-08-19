# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
# Using --legacy-peer-deps to avoid issues with dependency versions
RUN npm install --legacy-peer-deps

# Copy the rest of the application source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the static files with a lightweight server
FROM node:18-alpine

WORKDIR /app

# Install a simple static server
RUN npm install -g serve

# Copy the build output from the build stage
COPY --from=build /app/dist ./dist

# Expose the port the server will run on
EXPOSE 8080

# The command to run the server
# The -s flag is important; it serves the app on all routes, which is needed for client-side routing
CMD ["serve", "-s", "dist", "-l", "8080"]
