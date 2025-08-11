# MetalloBox Clone

Clone du logiciel MetalloBox pour l'analyse métallographique avec implémentation de la norme ASTM E112.

## Fonctionnalités

- Analyse automatique des grains
- Analyse des phases métallographiques
- Calcul de l'indice ASTM E112 (méthode planimétrique)
- Interface graphique intuitive
- Export des résultats vers Excel
- Correction manuelle des analyses

## Installation et utilisation

### Avec Docker (recommandé)

```bash
# Cloner le projet
git clone <repository-url>
cd metallobox-clone

# Lancer avec Docker
chmod +x run.sh
./run.sh
```

## Modifications et Améliorations (Projet de Correction)

Cette version du projet a été revue et corrigée pour améliorer la précision, la robustesse et la maintenabilité du code.

### Corrections Majeures
- **Calcul ASTM E112 Corrigé :** L'implémentation initiale du calcul de l'indice de grain ASTM E112 était une approximation incorrecte et reposait sur une échelle d'image codée en dur. Le calcul a été remplacé par une implémentation correcte de la **méthode planimétrique** comme décrit dans la norme.
- **Paramètre d'Échelle Obligatoire :** Pour garantir des mesures précises, l'analyse des grains nécessite désormais un paramètre d'échelle (en pixels par millimètre). Un champ de saisie a été ajouté à l'interface utilisateur pour permettre à l'utilisateur de fournir cette valeur cruciale.

### Améliorations Structurelles
- **Découplage :** La logique de calcul (`ASTM_E112`) a été découplée de la logique d'analyse d'image (`GrainAnalyzer`) en utilisant l'injection de dépendances.
- **Structure du Code :** Le code a été restructuré pour mieux séparer les couches (interface utilisateur, logique métier, utilitaires).
- **Suppression de Code Mort :** Les méthodes de calcul incorrectes ou factices ont été supprimées.

### Ajout de Tests
- Une suite de tests automatisés (`unittest`) a été ajoutée pour valider la correction du calcul ASTM E112 et assurer l'intégration correcte des composants.
