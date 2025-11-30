"""
╔══════════════════════════════════════════════════════════════════════╗
║                         TESTS UNITAIRES API                           ║
║                                                                      ║
║  Tests complets pour vérifier le bon fonctionnement de l'API        ║
║  Couvre tous les endpoints CRUD et cas d'erreur                     ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
║  Lancer: pytest tests/test_api.py -v                                ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from app.database import Base, get_db
from app.models import Task

# ========================================
# CONFIGURATION DES TESTS
# ========================================

# Base de données de test en mémoire
TEST_DATABASE_URL = "sqlite:///./test_tasks.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dépendance get_db pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override de la dépendance
app.dependency_overrides[get_db] = override_get_db

# Client de test
client = TestClient(app)


# ========================================
# FIXTURES
# ========================================

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Créer et nettoyer la base de données pour chaque test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_task_data():
    """Données exemple pour créer une tâche"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "medium",
        "status": "todo",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat()
    }


# ========================================
# TESTS DES ENDPOINTS PRINCIPAUX
# ========================================

def test_root_endpoint():
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test du health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_get_version():
    """Test de l'endpoint version"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "app_name" in data


# ========================================
# TESTS CRUD - CREATE
# ========================================

def test_create_task_success(sample_task_data):
    """Test de création d'une tâche avec succès"""
    response = client.post("/tasks", json=sample_task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_task_data["title"]
    assert data["description"] == sample_task_data["description"]
    assert data["priority"] == sample_task_data["priority"]
    assert data["status"] == sample_task_data["status"]
    assert "id" in data
    assert "created_at" in data


def test_create_task_minimal():
    """Test de création d'une tâche avec données minimales"""
    minimal_data = {
        "title": "Minimal Task",
        "priority": "low",
        "status": "todo"
    }
    response = client.post("/tasks", json=minimal_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == minimal_data["title"]
    assert data["description"] is None


def test_create_task_invalid_title():
    """Test de création avec titre invalide (trop court)"""
    invalid_data = {
        "title": "Ab",  # Moins de 3 caractères
        "priority": "medium",
        "status": "todo"
    }
    response = client.post("/tasks", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_create_task_invalid_priority():
    """Test de création avec priorité invalide"""
    invalid_data = {
        "title": "Valid Title",
        "priority": "invalid_priority",
        "status": "todo"
    }
    response = client.post("/tasks", json=invalid_data)
    assert response.status_code == 422


# ========================================
# TESTS CRUD - READ
# ========================================

def test_get_all_tasks_empty():
    """Test de récupération quand aucune tâche n'existe"""
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["tasks"]) == 0


def test_get_all_tasks_with_data(sample_task_data):
    """Test de récupération avec des tâches existantes"""
    # Créer quelques tâches
    client.post("/tasks", json=sample_task_data)
    client.post("/tasks", json=sample_task_data)
    
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["tasks"]) == 2


def test_get_all_tasks_with_pagination(sample_task_data):
    """Test de la pagination"""
    # Créer 5 tâches
    for i in range(5):
        client.post("/tasks", json=sample_task_data)
    
    # Récupérer avec limit=2
    response = client.get("/tasks?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 2
    assert data["total"] == 5
    assert data["page_size"] == 2


def test_get_task_by_id_success(sample_task_data):
    """Test de récupération d'une tâche par ID"""
    # Créer une tâche
    create_response = client.post("/tasks", json=sample_task_data)
    task_id = create_response.json()["id"]
    
    # Récupérer par ID
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == sample_task_data["title"]


def test_get_task_by_id_not_found():
    """Test de récupération d'une tâche inexistante"""
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert "non trouvée" in response.json()["detail"]


# ========================================
# TESTS CRUD - UPDATE
# ========================================

def test_update_task_success(sample_task_data):
    """Test de mise à jour d'une tâche"""
    # Créer une tâche
    create_response = client.post("/tasks", json=sample_task_data)
    task_id = create_response.json()["id"]
    
    # Mettre à jour
    update_data = {
        "title": "Updated Title",
        "status": "in_progress"
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"


def test_update_task_partial(sample_task_data):
    """Test de mise à jour partielle"""
    # Créer une tâche
    create_response = client.post("/tasks", json=sample_task_data)
    task_id = create_response.json()["id"]
    original_title = create_response.json()["title"]
    
    # Mettre à jour seulement le statut
    update_data = {"status": "completed"}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == original_title  # Titre inchangé
    assert data["status"] == "completed"  # Statut modifié


def test_update_task_not_found():
    """Test de mise à jour d'une tâche inexistante"""
    update_data = {"title": "New Title"}
    response = client.put("/tasks/9999", json=update_data)
    assert response.status_code == 404


# ========================================
# TESTS CRUD - DELETE
# ========================================

def test_delete_task_success(sample_task_data):
    """Test de suppression d'une tâche"""
    # Créer une tâche
    create_response = client.post("/tasks", json=sample_task_data)
    task_id = create_response.json()["id"]
    
    # Supprimer
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert "supprimée avec succès" in response.json()["message"]
    
    # Vérifier qu'elle n'existe plus
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found():
    """Test de suppression d'une tâche inexistante"""
    response = client.delete("/tasks/9999")
    assert response.status_code == 404


# ========================================
# TESTS DES ENDPOINTS SPÉCIALISÉS
# ========================================

def test_get_tasks_by_status(sample_task_data):
    """Test du filtrage par statut"""
    # Créer des tâches avec différents statuts
    data1 = {**sample_task_data, "status": "todo"}
    data2 = {**sample_task_data, "status": "completed"}
    
    client.post("/tasks", json=data1)
    client.post("/tasks", json=data2)
    
    # Récupérer seulement les tâches "todo"
    response = client.get("/tasks/status/todo")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"


def test_get_tasks_by_priority(sample_task_data):
    """Test du filtrage par priorité"""
    # Créer des tâches avec différentes priorités
    data1 = {**sample_task_data, "priority": "high"}
    data2 = {**sample_task_data, "priority": "low"}
    
    client.post("/tasks", json=data1)
    client.post("/tasks", json=data2)
    
    # Récupérer seulement les tâches "high"
    response = client.get("/tasks/priority/high")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "high"


def test_mark_task_as_completed(sample_task_data):
    """Test de marquage d'une tâche comme complétée"""
    # Créer une tâche
    create_response = client.post("/tasks", json=sample_task_data)
    task_id = create_response.json()["id"]
    
    # Marquer comme complétée
    response = client.patch(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_get_stats_summary(sample_task_data):
    """Test de l'endpoint de statistiques"""
    # Créer quelques tâches
    client.post("/tasks", json={**sample_task_data, "status": "todo", "priority": "high"})
    client.post("/tasks", json={**sample_task_data, "status": "completed", "priority": "low"})
    
    response = client.get("/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_tasks" in data
    assert "by_status" in data
    assert "by_priority" in data
    assert data["total_tasks"] == 2


def test_get_overdue_tasks():
    """Test de récupération des tâches en retard"""
    # Créer une tâche avec une date d'échéance passée
    past_date = (datetime.now() - timedelta(days=5)).isoformat()
    overdue_task = {
        "title": "Overdue Task",
        "priority": "high",
        "status": "todo",
        "due_date": past_date
    }
    client.post("/tasks", json=overdue_task)
    
    response = client.get("/tasks/overdue/list")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1


# ========================================
# TESTS DE VALIDATION
# ========================================

def test_title_too_long():
    """Test avec un titre trop long"""
    long_title = "A" * 201  # Plus de 200 caractères
    data = {
        "title": long_title,
        "priority": "medium",
        "status": "todo"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422


def test_description_too_long():
    """Test avec une description trop longue"""
    long_description = "A" * 1001  # Plus de 1000 caractères
    data = {
        "title": "Valid Title",
        "description": long_description,
        "priority": "medium",
        "status": "todo"
    }
    response = client.post("/tasks", json=data)
    assert response.status_code == 422


# ========================================
# EXÉCUTION DES TESTS
# ========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
