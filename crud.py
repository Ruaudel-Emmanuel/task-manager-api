"""
╔══════════════════════════════════════════════════════════════════════╗
║                    OPÉRATIONS CRUD (Base de données)                  ║
║                                                                      ║
║  Fonctions pour Create, Read, Update, Delete sur les tâches         ║
║  Séparation de la logique métier et des routes API                  ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Task, StatusEnum, PriorityEnum
from app.schemas import TaskCreate, TaskUpdate

# Configuration du logging
logger = logging.getLogger(__name__)


def create_task(db: Session, task: TaskCreate) -> Task:
    """
    Crée une nouvelle tâche dans la base de données
    
    Args:
        db: Session de base de données
        task: Données de la tâche à créer (TaskCreate schema)
    
    Returns:
        Task: Tâche créée avec son ID généré
        
    Raises:
        Exception: En cas d'erreur lors de la création
    """
    try:
        # Création de l'objet Task
        db_task = Task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            status=task.status,
            due_date=task.due_date
        )
        
        # Ajout et commit à la base de données
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        logger.info(f"✅ Tâche créée: ID={db_task.id}, Titre='{db_task.title}'")
        return db_task
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la création de la tâche: {e}")
        raise


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """
    Récupère une tâche par son ID
    
    Args:
        db: Session de base de données
        task_id: ID de la tâche à récupérer
    
    Returns:
        Task | None: Tâche trouvée ou None si inexistante
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if task:
        logger.info(f"✅ Tâche trouvée: ID={task_id}")
    else:
        logger.warning(f"⚠️ Tâche non trouvée: ID={task_id}")
    
    return task


def get_all_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[StatusEnum] = None,
    priority: Optional[PriorityEnum] = None
) -> List[Task]:
    """
    Récupère toutes les tâches avec pagination et filtres optionnels
    
    Args:
        db: Session de base de données
        skip: Nombre de tâches à sauter (pour pagination)
        limit: Nombre maximum de tâches à retourner
        status: Filtre optionnel par statut
        priority: Filtre optionnel par priorité
    
    Returns:
        List[Task]: Liste des tâches correspondant aux critères
    """
    query = db.query(Task)
    
    # Application des filtres
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    # Tri par date de création (plus récent en premier)
    query = query.order_by(Task.created_at.desc())
    
    # Pagination
    tasks = query.offset(skip).limit(limit).all()
    
    logger.info(f"✅ {len(tasks)} tâche(s) récupérée(s)")
    return tasks


def get_tasks_count(
    db: Session,
    status: Optional[StatusEnum] = None,
    priority: Optional[PriorityEnum] = None
) -> int:
    """
    Compte le nombre total de tâches (avec filtres optionnels)
    
    Args:
        db: Session de base de données
        status: Filtre optionnel par statut
        priority: Filtre optionnel par priorité
    
    Returns:
        int: Nombre total de tâches
    """
    query = db.query(func.count(Task.id))
    
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    count = query.scalar()
    return count or 0


def update_task(
    db: Session,
    task_id: int,
    task_update: TaskUpdate
) -> Optional[Task]:
    """
    Met à jour une tâche existante
    
    Args:
        db: Session de base de données
        task_id: ID de la tâche à mettre à jour
        task_update: Données de mise à jour (TaskUpdate schema)
    
    Returns:
        Task | None: Tâche mise à jour ou None si inexistante
        
    Raises:
        Exception: En cas d'erreur lors de la mise à jour
    """
    try:
        # Récupération de la tâche
        db_task = get_task_by_id(db, task_id)
        
        if not db_task:
            return None
        
        # Mise à jour des champs modifiés uniquement
        update_data = task_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        # Mise à jour du timestamp
        db_task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_task)
        
        logger.info(f"✅ Tâche mise à jour: ID={task_id}")
        return db_task
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la mise à jour de la tâche: {e}")
        raise


def delete_task(db: Session, task_id: int) -> bool:
    """
    Supprime une tâche
    
    Args:
        db: Session de base de données
        task_id: ID de la tâche à supprimer
    
    Returns:
        bool: True si suppression réussie, False si tâche inexistante
        
    Raises:
        Exception: En cas d'erreur lors de la suppression
    """
    try:
        db_task = get_task_by_id(db, task_id)
        
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        
        logger.info(f"✅ Tâche supprimée: ID={task_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la suppression de la tâche: {e}")
        raise


def get_tasks_by_status(
    db: Session,
    status: StatusEnum,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """
    Récupère toutes les tâches d'un statut donné
    
    Args:
        db: Session de base de données
        status: Statut à filtrer
        skip: Nombre de tâches à sauter
        limit: Nombre maximum de tâches
    
    Returns:
        List[Task]: Liste des tâches avec le statut spécifié
    """
    return get_all_tasks(db, skip=skip, limit=limit, status=status)


def get_tasks_by_priority(
    db: Session,
    priority: PriorityEnum,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """
    Récupère toutes les tâches d'une priorité donnée
    
    Args:
        db: Session de base de données
        priority: Priorité à filtrer
        skip: Nombre de tâches à sauter
        limit: Nombre maximum de tâches
    
    Returns:
        List[Task]: Liste des tâches avec la priorité spécifiée
    """
    return get_all_tasks(db, skip=skip, limit=limit, priority=priority)


def get_overdue_tasks(db: Session) -> List[Task]:
    """
    Récupère toutes les tâches en retard (due_date dépassée)
    
    Args:
        db: Session de base de données
    
    Returns:
        List[Task]: Liste des tâches en retard
    """
    now = datetime.utcnow()
    tasks = db.query(Task).filter(
        Task.due_date < now,
        Task.status != StatusEnum.COMPLETED,
        Task.status != StatusEnum.CANCELLED
    ).all()
    
    logger.info(f"⚠️ {len(tasks)} tâche(s) en retard trouvée(s)")
    return tasks


def mark_task_as_completed(db: Session, task_id: int) -> Optional[Task]:
    """
    Marque une tâche comme complétée
    
    Args:
        db: Session de base de données
        task_id: ID de la tâche à marquer comme complétée
    
    Returns:
        Task | None: Tâche mise à jour ou None si inexistante
    """
    task_update = TaskUpdate(status=StatusEnum.COMPLETED)
    return update_task(db, task_id, task_update)
