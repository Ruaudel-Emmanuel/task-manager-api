"""
╔══════════════════════════════════════════════════════════════════════╗
║                   CONFIGURATION BASE DE DONNÉES                       ║
║                                                                      ║
║  Configuration de SQLAlchemy pour la gestion de la base de données  ║
║  Supporte SQLite (dev) et PostgreSQL (prod)                         ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import logging
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement de la configuration
CONFIG_PATH = Path("config.json")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    DATABASE_URL = config["database"]["url"]
except (FileNotFoundError, KeyError) as e:
    logger.warning(f"⚠️ Erreur de configuration: {e}. Utilisation de SQLite par défaut.")
    DATABASE_URL = "sqlite:///./tasks.db"

# Création du moteur de base de données
# check_same_thread=False nécessaire uniquement pour SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Création de la session locale
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base pour les modèles SQLAlchemy
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session de base de données
    
    À utiliser comme dépendance FastAPI pour injecter une session DB
    La session est automatiquement fermée après utilisation
    
    Yields:
        Session: Session SQLAlchemy
        
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crée toutes les tables définies dans les modèles
    
    Cette fonction doit être appelée au démarrage de l'application
    Elle vérifie si les tables existent et les crée si nécessaire
    """
    try:
        # Import des modèles pour que SQLAlchemy les connaisse
        from app.models import Task
        
        # Création des tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables de la base de données créées/vérifiées avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des tables: {e}")
        raise
