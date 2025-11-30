"""
╔══════════════════════════════════════════════════════════════════════╗
║                 SCRIPT D'INITIALISATION DE LA BDD                     ║
║                                                                      ║
║  Crée les tables et peuple la base avec des données d'exemple       ║
║  Utile pour le développement et les démonstrations                  ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
║  Utilisation: python scripts/init_db.py                             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal, create_tables
from app.models import Task, PriorityEnum, StatusEnum


def create_sample_tasks():
    """Crée des tâches d'exemple pour démonstration"""
    db = SessionLocal()
    
    try:
        # Vérifier si des tâches existent déjà
        existing_tasks = db.query(Task).count()
        if existing_tasks > 0:
            print(f"⚠️  {existing_tasks} tâche(s) existante(s) trouvée(s).")
            response = input("Voulez-vous supprimer et recréer les données ? (o/N): ")
            if response.lower() != 'o':
                print("✋ Opération annulée.")
                return
            
            # Supprimer toutes les tâches existantes
            db.query(Task).delete()
            db.commit()
            print("🗑️  Tâches existantes supprimées.")
        
        # Tâches d'exemple
        sample_tasks = [
            Task(
                title="Développer l'API REST avec FastAPI",
                description="Créer une API complète avec CRUD, validation Pydantic et documentation automatique",
                priority=PriorityEnum.HIGH,
                status=StatusEnum.IN_PROGRESS,
                due_date=datetime.now() + timedelta(days=7)
            ),
            Task(
                title="Créer l'interface Streamlit",
                description="Développer une interface utilisateur interactive pour gérer les tâches",
                priority=PriorityEnum.HIGH,
                status=StatusEnum.TODO,
                due_date=datetime.now() + timedelta(days=10)
            ),
            Task(
                title="Écrire les tests unitaires",
                description="Couvrir tous les endpoints avec des tests pytest",
                priority=PriorityEnum.MEDIUM,
                status=StatusEnum.TODO,
                due_date=datetime.now() + timedelta(days=14)
            ),
            Task(
                title="Rédiger la documentation",
                description="Compléter le README et ajouter des exemples d'utilisation",
                priority=PriorityEnum.MEDIUM,
                status=StatusEnum.IN_PROGRESS,
                due_date=datetime.now() + timedelta(days=5)
            ),
            Task(
                title="Configurer CI/CD avec GitHub Actions",
                description="Automatiser les tests et le déploiement",
                priority=PriorityEnum.LOW,
                status=StatusEnum.TODO,
                due_date=datetime.now() + timedelta(days=21)
            ),
            Task(
                title="Optimiser les performances",
                description="Profiler l'API et optimiser les requêtes SQL",
                priority=PriorityEnum.MEDIUM,
                status=StatusEnum.TODO,
                due_date=datetime.now() + timedelta(days=30)
            ),
            Task(
                title="Ajouter l'authentification JWT",
                description="Implémenter un système d'authentification sécurisé",
                priority=PriorityEnum.URGENT,
                status=StatusEnum.TODO,
                due_date=datetime.now() + timedelta(days=3)
            ),
            Task(
                title="Migrer vers PostgreSQL",
                description="Préparer la migration de SQLite vers PostgreSQL pour la production",
                priority=PriorityEnum.HIGH,
                status=StatusEnum.TODO,
                due_date=datetime.now() + timedelta(days=15)
            ),
            Task(
                title="Mettre en place le monitoring",
                description="Intégrer Prometheus et Grafana pour le monitoring",
                priority=PriorityEnum.LOW,
                status=StatusEnum.TODO,
                due_date=datetime.now() + timedelta(days=45)
            ),
            Task(
                title="Première version déployée",
                description="Version 1.0.0 en production sur Render",
                priority=PriorityEnum.HIGH,
                status=StatusEnum.COMPLETED,
                due_date=datetime.now() - timedelta(days=2)
            ),
        ]
        
        # Ajouter les tâches à la base de données
        for task in sample_tasks:
            db.add(task)
        
        db.commit()
        print(f"✅ {len(sample_tasks)} tâches d'exemple créées avec succès !")
        
        # Afficher un résumé
        print("\n📊 Résumé des tâches créées:")
        print(f"   - TODO: {len([t for t in sample_tasks if t.status == StatusEnum.TODO])}")
        print(f"   - IN_PROGRESS: {len([t for t in sample_tasks if t.status == StatusEnum.IN_PROGRESS])}")
        print(f"   - COMPLETED: {len([t for t in sample_tasks if t.status == StatusEnum.COMPLETED])}")
        print(f"\n   - URGENT: {len([t for t in sample_tasks if t.priority == PriorityEnum.URGENT])}")
        print(f"   - HIGH: {len([t for t in sample_tasks if t.priority == PriorityEnum.HIGH])}")
        print(f"   - MEDIUM: {len([t for t in sample_tasks if t.priority == PriorityEnum.MEDIUM])}")
        print(f"   - LOW: {len([t for t in sample_tasks if t.priority == PriorityEnum.LOW])}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tâches: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Fonction principale"""
    print("🚀 Initialisation de la base de données...")
    print("=" * 60)
    
    try:
        # Créer les tables
        print("📁 Création des tables...")
        create_tables()
        print("✅ Tables créées avec succès !")
        
        # Créer des données d'exemple
        print("\n📝 Création des tâches d'exemple...")
        create_sample_tasks()
        
        print("\n" + "=" * 60)
        print("🎉 Initialisation terminée avec succès !")
        print("\n💡 Prochaines étapes:")
        print("   1. Lancer l'API: uvicorn main:app --reload")
        print("   2. Lancer le client: streamlit run client/streamlit_app.py")
        print("   3. Accéder à la doc: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
