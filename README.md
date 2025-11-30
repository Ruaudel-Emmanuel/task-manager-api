 🚀 Task Manager API - Projet Python Full-Stack



!\[Python](https://img.shields.io/badge/Python-3.11+-blue.svg)

!\[FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)

!\[Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)

!\[License](https://img.shields.io/badge/License-MIT-yellow.svg)



\## 📋 Description



API REST moderne construite avec \*\*FastAPI\*\* pour la gestion de tâches, accompagnée d'une interface client interactive en \*\*Streamlit\*\*. Ce projet démontre les compétences essentielles pour un développeur Python Full-Stack junior/intermédiaire.



\## ✨ Fonctionnalités



\- ✅ \*\*API REST complète\*\* avec FastAPI (CRUD)

\- 🎨 \*\*Interface client intuitive\*\* avec Streamlit

\- 🗃️ \*\*Base de données SQLite\*\* (extensible vers PostgreSQL)

\- 🔐 \*\*Validation des données\*\* avec Pydantic V2

\- 📝 \*\*Documentation API automatique\*\* (Swagger/ReDoc)

\- ✅ \*\*Tests unitaires\*\* avec pytest

\- 🔧 \*\*Configuration flexible\*\* (JSON + .env)

\- 📦 \*\*Architecture modulaire\*\* et extensible



\## 🛠️ Technologies Utilisées



| Catégorie | Technologie | Rôle |

|-----------|-------------|------|

| \*\*Framework API\*\* | FastAPI 0.115+ | Backend REST API |

| \*\*Interface Client\*\* | Streamlit 1.40+ | Dashboard interactif |

| \*\*Validation\*\* | Pydantic V2 | Validation de données |

| \*\*Base de données\*\* | SQLite / SQLAlchemy | Persistance des données |

| \*\*Tests\*\* | pytest | Tests unitaires |

| \*\*HTTP Client\*\* | httpx | Requêtes asynchrones |



\## 📦 Installation



\### Prérequis



\- Python 3.11 ou supérieur

\- pip (gestionnaire de paquets Python)

\- Git



\### Étapes d'installation



1\. \*\*Cloner le repository\*\*



2\. \*\*Créer un environnement virtuel\*\*

Windows

python -m venv venv

venv\\Scripts\\activate



Linux/Mac

python3 -m venv venv

source venv/bin/activate



text



3\. \*\*Installer les dépendances\*\*

pip install -r requirements.txt



text



4\. \*\*Configurer les variables d'environnement\*\*

Copier le template

cp .env.example .env



Éditer .env avec vos paramètres

text



5\. \*\*Initialiser la base de données\*\*

python scripts/init\_db.py



text



\## 🚀 Utilisation



\### Lancer l'API (Backend)



Mode développement avec rechargement automatique

uvicorn main:app --reload --host 0.0.0.0 --port 8000



Mode production

uvicorn main:app --host 0.0.0.0 --port 8000



text



L'API sera accessible à : `http://localhost:8000`



\*\*Documentation interactive :\*\*

\- Swagger UI : `http://localhost:8000/docs`

\- ReDoc : `http://localhost:8000/redoc`



\### Lancer l'Interface Client (Frontend)



Dans un nouveau terminal (avec l'API en cours d'exécution)

streamlit run client/streamlit\_app.py



text



L'interface sera accessible à : `http://localhost:8501`



\### Lancer les Tests



Tous les tests

pytest



Avec couverture de code

pytest --cov=app tests/



Mode verbeux

pytest -v



text



\## 📚 Endpoints API



| Méthode | Endpoint | Description |

|---------|----------|-------------|

| `GET` | `/` | Page d'accueil de l'API |

| `GET` | `/health` | Vérification de l'état de l'API |

| `GET` | `/tasks` | Liste toutes les tâches |

| `GET` | `/tasks/{id}` | Récupère une tâche par ID |

| `POST` | `/tasks` | Crée une nouvelle tâche |

| `PUT` | `/tasks/{id}` | Met à jour une tâche |

| `DELETE` | `/tasks/{id}` | Supprime une tâche |

| `GET` | `/tasks/status/{status}` | Filtre les tâches par statut |



\## 🔧 Configuration



\### Fichier `config.json`



{

"app\_name": "Task Manager API",

"version": "1.0.0",

"database\_url": "sqlite:///./tasks.db",

"api\_prefix": "/api/v1",

"cors\_origins": \["http://localhost:8501", "http://127.0.0.1:8501"]

}



text



\### Fichier `.env`



Configuration de l'environnement

ENVIRONMENT=development

DEBUG=True

DATABASE\_URL=sqlite:///./tasks.db

SECRET\_KEY=your-secret-key-here-change-in-production

API\_HOST=0.0.0.0

API\_PORT=8000



text



\## 📁 Structure du Projet



task-manager-api/

├── .env.example # Template des variables d'environnement

├── .gitignore # Fichiers à ignorer

├── README.md # Documentation (ce fichier)

├── requirements.txt # Dépendances Python

├── config.json # Configuration JSON

├── main.py # Point d'entrée FastAPI

├── app/

│ ├── init.py # Package app

│ ├── models.py # Modèles SQLAlchemy

│ ├── database.py # Configuration DB

│ ├── crud.py # Opérations CRUD

│ ├── routes.py # Routes API

│ └── schemas.py # Schémas Pydantic

├── client/

│ └── streamlit\_app.py # Interface Streamlit

├── tests/

│ ├── init.py # Package tests

│ └── test\_api.py # Tests unitaires

└── scripts/

└── init\_db.py # Initialisation DB



text



\## 🧪 Exemples d'Utilisation



\### Créer une tâche (cURL)



curl -X POST "http://localhost:8000/tasks"

-H "Content-Type: application/json"

-d '{

"title": "Apprendre FastAPI",

"description": "Suivre le tutoriel officiel",

"priority": "high",

"status": "todo"

}'



text



\### Créer une tâche (Python)



import requests



url = "http://localhost:8000/tasks"

task = {

"title": "Développer une API",

"description": "Utiliser FastAPI et Pydantic",

"priority": "high",

"status": "in\_progress"

}



response = requests.post(url, json=task)

print(response.json())



text



\## 🔐 Sécurité



\- Validation stricte des entrées avec Pydantic

\- Protection contre les injections SQL (SQLAlchemy ORM)

\- Variables sensibles dans `.env` (non versionnées)

\- CORS configuré pour limiter les origines



\## 🚀 Déploiement



\### Déploiement sur Render.com



1\. Créer un compte sur \[Render](https://render.com)

2\. Créer un nouveau Web Service

3\. Connecter votre dépôt GitHub

4\. Configurer les variables d'environnement

5\. Déployer !



\### Déploiement sur Railway



Installer Railway CLI

npm install -g @railway/cli



Se connecter

railway login



Initialiser et déployer

railway init

railway up



text



\## 📈 Évolutions Futures



\- \[ ] Authentification JWT

\- \[ ] Gestion des utilisateurs

\- \[ ] Notifications par email

\- \[ ] Export PDF des tâches

\- \[ ] Migration vers PostgreSQL

\- \[ ] API GraphQL alternative

\- \[ ] Conteneurisation Docker

\- \[ ] CI/CD avec GitHub Actions



\## 🤝 Contribution



Les contributions sont les bienvenues ! Voici comment procéder :



1\. Forkez le projet

2\. Créez une branche (`git checkout -b feature/AmazingFeature`)

3\. Committez vos changements (`git commit -m 'Add AmazingFeature'`)

4\. Pushez vers la branche (`git push origin feature/AmazingFeature`)

5\. Ouvrez une Pull Request



\## 📝 License



Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.



\## 👨‍💻 Auteur



\*\*Emmanuel Ruaudel\*\*

\- GitHub: \[@Ruaudel-Emmanuel](https://github.com/Ruaudel-Emmanuel)

\- Email: ruaudel.emmanuel@orange.fr

\- Portfolio: \[https://ruaudel-emmanuel.github.io](https://ruaudel-emmanuel.github.io/RuaudelEmmanuel.github.io/)



\## 🙏 Remerciements



\- \[FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne

\- \[Streamlit](https://streamlit.io/) - Framework d'interface simple

\- \[Pydantic](https://docs.pydantic.dev/) - Validation de données

\- \[SQLAlchemy](https://www.sqlalchemy.org/) - ORM Python



---



⭐ \*\*Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile !\*\*



