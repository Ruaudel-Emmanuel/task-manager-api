"""
╔══════════════════════════════════════════════════════════════════════╗
║                    SCRIPT DE LANCEMENT RAPIDE                         ║
║                                                                      ║
║  Lance l'API et l'interface Streamlit en un seul clic               ║
║  Utile pour le développement et les démonstrations                  ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
║  Utilisation: python start.py                                       ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    try:
        import fastapi
        import streamlit
        import uvicorn
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("\n💡 Installez les dépendances avec:")
        print("   pip install -r requirements.txt")
        return False


def check_database():
    """Vérifie si la base de données existe"""
    db_path = Path("tasks.db")
    if not db_path.exists():
        print("⚠️  Base de données non trouvée")
        response = input("Voulez-vous initialiser la base de données ? (O/n): ")
        if response.lower() != 'n':
            print("\n🔧 Initialisation de la base de données...")
            subprocess.run([sys.executable, "scripts/init_db.py"])
            return True
        return False
    return True


def start_api():
    """Démarre l'API FastAPI"""
    print("\n🚀 Démarrage de l'API FastAPI...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return api_process


def start_streamlit():
    """Démarre l'interface Streamlit"""
    print("🎨 Démarrage de l'interface Streamlit...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "client/streamlit_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return streamlit_process


def main():
    """Fonction principale"""
    print("=" * 70)
    print("  🚀 TASK MANAGER API - LANCEMENT AUTOMATIQUE".center(70))
    print("=" * 70)
    
    # Vérifications préalables
    if not check_dependencies():
        sys.exit(1)
    
    if not check_database():
        print("\n⚠️  Impossible de continuer sans base de données")
        sys.exit(1)
    
    # Lancement des services
    print("\n" + "=" * 70)
    print("  LANCEMENT DES SERVICES".center(70))
    print("=" * 70)
    
    try:
        # Démarrer l'API
        api_process = start_api()
        time.sleep(3)  # Attendre que l'API démarre
        
        # Démarrer Streamlit
        streamlit_process = start_streamlit()
        time.sleep(3)  # Attendre que Streamlit démarre
        
        # Afficher les informations
        print("\n" + "=" * 70)
        print("  ✅ SERVICES DÉMARRÉS AVEC SUCCÈS".center(70))
        print("=" * 70)
        print("\n📌 URLs d'accès:")
        print("   • API FastAPI:          http://localhost:8000")
        print("   • Documentation Swagger: http://localhost:8000/docs")
        print("   • Documentation ReDoc:   http://localhost:8000/redoc")
        print("   • Interface Streamlit:   http://localhost:8501")
        
        print("\n💡 Commandes utiles:")
        print("   • Ctrl+C pour arrêter tous les services")
        print("   • Logs de l'API affichés ci-dessous")
        
        # Ouvrir automatiquement dans le navigateur
        print("\n🌐 Ouverture automatique dans le navigateur...")
        time.sleep(2)
        webbrowser.open("http://localhost:8501")
        
        print("\n" + "=" * 70)
        print("  📊 LOGS DES SERVICES".center(70))
        print("=" * 70)
        print("\n(Appuyez sur Ctrl+C pour arrêter)\n")
        
        # Garder les processus actifs
        api_process.wait()
        streamlit_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt des services en cours...")
        api_process.terminate()
        streamlit_process.terminate()
        print("✅ Services arrêtés proprement")
        print("\n👋 À bientôt !")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("Arrêt des services...")
        if 'api_process' in locals():
            api_process.terminate()
        if 'streamlit_process' in locals():
            streamlit_process.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
