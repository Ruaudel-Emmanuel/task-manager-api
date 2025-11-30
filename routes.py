"""
╔══════════════════════════════════════════════════════════════════════╗
║                          ROUTES API (ENDPOINTS)                       ║
║                                                                      ║
║  Définition de tous les endpoints de l'API REST                     ║
║  Gère les requêtes HTTP et appelle les fonctions CRUD              ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskList,
    MessageResponse,
    StatusEnum,
    PriorityEnum
)

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router
router = APIRouter()


# ========================================
# ENDPOINTS CRUD PRINCIPAUX
# ========================================

@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle tâche",
    description="Crée une nouvelle tâche avec les informations fournies"
)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Créer une nouvelle tâche
    
    - **title**: Titre de la tâche (3-200 caractères)
    - **description**: Description détaillée (optionnelle)
    - **priority**: Niveau de priorité (low, medium, high, urgent)
    - **status**: Statut initial (todo, in_progress, completed, cancelled)
    - **due_date**: Date d'échéance (optionnelle)
    """
    try:
        db_task = crud.create_task(db, task)
        return db_task
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la tâche: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de la tâche"
        )


@router.get(
    "/tasks",
    response_model=TaskList,
    status_code=status.HTTP_200_OK,
    summary="Récupérer toutes les tâches",
    description="Récupère la liste de toutes les tâches avec pagination et filtres optionnels"
)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Nombre de tâches à sauter"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de tâches à retourner"),
    status: Optional[StatusEnum] = Query(None, description="Filtrer par statut"),
    priority: Optional[PriorityEnum] = Query(None, description="Filtrer par priorité"),
    db: Session = Depends(get_db)
) -> TaskList:
    """
    Récupérer toutes les tâches avec pagination
    
    - **skip**: Nombre de tâches à sauter (défaut: 0)
    - **limit**: Nombre maximum de tâches (défaut: 20, max: 100)
    - **status**: Filtre optionnel par statut
    - **priority**: Filtre optionnel par priorité
    """
    tasks = crud.get_all_tasks(
        db,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority
    )
    total = crud.get_tasks_count(db, status=status, priority=priority)
    
    return TaskList(
        tasks=tasks,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Récupérer une tâche par ID",
    description="Récupère les détails d'une tâche spécifique"
)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Récupérer une tâche par son ID
    
    - **task_id**: Identifiant unique de la tâche
    """
    db_task = crud.get_task_by_id(db, task_id)
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tâche avec l'ID {task_id} non trouvée"
        )
    
    return db_task


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Mettre à jour une tâche",
    description="Met à jour les informations d'une tâche existante"
)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Mettre à jour une tâche existante
    
    - **task_id**: Identifiant de la tâche à mettre à jour
    - Tous les champs sont optionnels (mise à jour partielle)
    """
    db_task = crud.update_task(db, task_id, task_update)
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tâche avec l'ID {task_id} non trouvée"
        )
    
    return db_task


@router.delete(
    "/tasks/{task_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Supprimer une tâche",
    description="Supprime définitivement une tâche"
)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Supprimer une tâche
    
    - **task_id**: Identifiant de la tâche à supprimer
    """
    success = crud.delete_task(db, task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tâche avec l'ID {task_id} non trouvée"
        )
    
    return MessageResponse(
        message=f"Tâche {task_id} supprimée avec succès"
    )


# ========================================
# ENDPOINTS SPÉCIALISÉS
# ========================================

@router.get(
    "/tasks/status/{status}",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Récupérer les tâches par statut",
    description="Récupère toutes les tâches d'un statut donné"
)
async def get_tasks_by_status(
    status: StatusEnum,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """
    Récupérer les tâches par statut
    
    - **status**: Statut à filtrer (todo, in_progress, completed, cancelled)
    """
    tasks = crud.get_tasks_by_status(db, status, skip=skip, limit=limit)
    return tasks


@router.get(
    "/tasks/priority/{priority}",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Récupérer les tâches par priorité",
    description="Récupère toutes les tâches d'une priorité donnée"
)
async def get_tasks_by_priority(
    priority: PriorityEnum,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """
    Récupérer les tâches par priorité
    
    - **priority**: Priorité à filtrer (low, medium, high, urgent)
    """
    tasks = crud.get_tasks_by_priority(db, priority, skip=skip, limit=limit)
    return tasks


@router.get(
    "/tasks/overdue/list",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Récupérer les tâches en retard",
    description="Récupère toutes les tâches dont la date d'échéance est dépassée"
)
async def get_overdue_tasks(
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """
    Récupérer les tâches en retard
    
    Retourne toutes les tâches dont la due_date est dépassée
    et qui ne sont pas complétées ou annulées
    """
    tasks = crud.get_overdue_tasks(db)
    return tasks


@router.patch(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Marquer une tâche comme complétée",
    description="Change le statut d'une tâche à 'completed'"
)
async def mark_task_completed(
    task_id: int,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Marquer une tâche comme complétée
    
    - **task_id**: Identifiant de la tâche à marquer comme complétée
    """
    db_task = crud.mark_task_as_completed(db, task_id)
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tâche avec l'ID {task_id} non trouvée"
        )
    
    return db_task


# ========================================
# ENDPOINTS DE STATISTIQUES
# ========================================

@router.get(
    "/stats/summary",
    status_code=status.HTTP_200_OK,
    summary="Récupérer les statistiques",
    description="Récupère un résumé statistique de toutes les tâches"
)
async def get_stats_summary(
    db: Session = Depends(get_db)
) -> dict:
    """
    Récupérer les statistiques globales
    
    Retourne un résumé des tâches par statut et priorité
    """
    total = crud.get_tasks_count(db)
    todo = crud.get_tasks_count(db, status=StatusEnum.TODO)
    in_progress = crud.get_tasks_count(db, status=StatusEnum.IN_PROGRESS)
    completed = crud.get_tasks_count(db, status=StatusEnum.COMPLETED)
    cancelled = crud.get_tasks_count(db, status=StatusEnum.CANCELLED)
    
    urgent = crud.get_tasks_count(db, priority=PriorityEnum.URGENT)
    high = crud.get_tasks_count(db, priority=PriorityEnum.HIGH)
    
    overdue = len(crud.get_overdue_tasks(db))
    
    return {
        "total_tasks": total,
        "by_status": {
            "todo": todo,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled
        },
        "by_priority": {
            "urgent": urgent,
            "high": high,
            "medium": crud.get_tasks_count(db, priority=PriorityEnum.MEDIUM),
            "low": crud.get_tasks_count(db, priority=PriorityEnum.LOW)
        },
        "overdue_tasks": overdue
    }
