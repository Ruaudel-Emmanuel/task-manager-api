"""
╔══════════════════════════════════════════════════════════════════════╗
║                    TASK MANAGER API - MAIN                           ║
║                                                                      ║
║  Point d'entrée principal de l'application FastAPI                  ║
║  Configure l'API, les routes, CORS et la documentation              ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
║  Date: 2025                                                         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import create_tables, engine
from app.routes import router as task_router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Chargement de la configuration
CONFIG_PATH = Path("config.json")

def load_config() -> Dict:
    """Charge la configuration depuis config.json"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info("✅ Configuration chargée avec succès")
        return config
    except FileNotFoundError:
        logger.error("❌ Fichier config.json non trouvé")
        raise
    except json.JSONDecodeError:
        logger.error("❌ Erreur de parsing du fichier config.json")
        raise

# Chargement de la configuration
config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    - Startup: Création des tables de la base de données
    - Shutdown: Nettoyage des ressources
    """
    # Startup
    logger.info("🚀 Démarrage de l'application...")
    create_tables()
    logger.info("✅ Tables de la base de données créées/vérifiées")
    yield
    # Shutdown
    logger.info("🛑 Arrêt de l'application...")
    engine.dispose()
    logger.info("✅ Ressources libérées")


# Création de l'application FastAPI
app = FastAPI(
    title=config["api"]["title"],
    description=config["api"]["description"],
    version=config["api"]["version"],
    contact=config["api"]["contact"],
    license_info=config["api"]["license_info"],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuration CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["cors"]["allow_origins"],
    allow_credentials=config["cors"]["allow_credentials"],
    allow_methods=config["cors"]["allow_methods"],
    allow_headers=config["cors"]["allow_headers"],
)

# Inclusion des routes
app.include_router(task_router, prefix="", tags=["tasks"])


# ========================================
# ROUTES PRINCIPALES
# ========================================

@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> Dict[str, str]:
    """
    Route racine de l'API
    
    Returns:
        Dict contenant les informations de bienvenue
    """
    return {
        "message": f"Bienvenue sur {config['app_name']} v{config['version']}",
        "documentation": "/docs",
        "redoc": "/redoc",
        "status": "operational",
        "author": config["author"]
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """
    Endpoint de vérification de santé de l'API
    
    Returns:
        Dict contenant le statut de l'API et de la base de données
    """
    try:
        # Vérification de la connexion à la base de données
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "api": "operational",
            "database": "connected",
            "version": config["version"]
        }
    except Exception as e:
        logger.error(f"❌ Erreur lors du health check: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "api": "operational",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/version", status_code=status.HTTP_200_OK)
async def get_version() -> Dict[str, str]:
    """
    Récupère la version de l'API
    
    Returns:
        Dict contenant la version et les informations de l'application
    """
    return {
        "app_name": config["app_name"],
        "version": config["version"],
        "description": config["description"],
        "author": config["author"],
        "license": config["license"]
    }


# ========================================
# GESTIONNAIRES D'ERREURS GLOBAUX
# ========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Gestionnaire personnalisé pour les erreurs HTTP"""
    logger.error(f"❌ HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Gestionnaire personnalisé pour les erreurs générales"""
    logger.error(f"❌ Exception non gérée: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Une erreur interne s'est produite",
            "detail": str(exc)
        }
    )


# ========================================
# POINT D'ENTRÉE
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    # Récupération de la configuration depuis le fichier config.json
    host = "0.0.0.0"
    port = 8000
    
    logger.info(f"🚀 Démarrage du serveur sur http://{host}:{port}")
    logger.info(f"📖 Documentation disponible sur http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload en mode développement
        log_level="info"
    )
