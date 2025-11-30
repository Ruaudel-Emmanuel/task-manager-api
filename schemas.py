"""
╔══════════════════════════════════════════════════════════════════════╗
║                      SCHÉMAS PYDANTIC (VALIDATION)                    ║
║                                                                      ║
║  Schémas de validation des données avec Pydantic V2                 ║
║  Gère la validation des entrées et la sérialisation des sorties     ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator


class PriorityEnum(str, Enum):
    """Énumération des niveaux de priorité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class StatusEnum(str, Enum):
    """Énumération des statuts de tâche"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskBase(BaseModel):
    """
    Schéma de base pour une tâche
    
    Utilisé comme classe parente pour les autres schémas
    """
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Titre de la tâche",
        examples=["Développer l'API REST"]
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Description détaillée de la tâche",
        examples=["Créer une API REST avec FastAPI incluant CRUD complet"]
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        description="Niveau de priorité de la tâche"
    )
    status: StatusEnum = Field(
        default=StatusEnum.TODO,
        description="Statut actuel de la tâche"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Date d'échéance de la tâche",
        examples=["2025-12-31T23:59:59"]
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Valide et nettoie le titre"""
        if not v or not v.strip():
            raise ValueError("Le titre ne peut pas être vide")
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Valide et nettoie la description"""
        if v:
            return v.strip()
        return v


class TaskCreate(TaskBase):
    """
    Schéma pour la création d'une tâche
    
    Hérite de TaskBase et peut ajouter des champs spécifiques à la création
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schéma pour la mise à jour d'une tâche
    
    Tous les champs sont optionnels pour permettre une mise à jour partielle
    """
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        description="Nouveau titre de la tâche"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Nouvelle description"
    )
    priority: Optional[PriorityEnum] = Field(
        None,
        description="Nouvelle priorité"
    )
    status: Optional[StatusEnum] = Field(
        None,
        description="Nouveau statut"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Nouvelle date d'échéance"
    )
    
    model_config = ConfigDict(
        # Permet de valider même si les champs sont None
        validate_assignment=True
    )


class TaskResponse(TaskBase):
    """
    Schéma pour la réponse contenant une tâche
    
    Inclut les champs auto-générés par la base de données
    """
    id: int = Field(
        ...,
        description="Identifiant unique de la tâche"
    )
    created_at: datetime = Field(
        ...,
        description="Date et heure de création"
    )
    updated_at: datetime = Field(
        ...,
        description="Date et heure de dernière modification"
    )
    
    model_config = ConfigDict(
        # Permet la compatibilité avec les modèles ORM
        from_attributes=True,
        # Exemple de réponse pour la documentation
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Développer l'API REST",
                "description": "Créer une API REST complète avec FastAPI",
                "priority": "high",
                "status": "in_progress",
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T15:45:00",
                "due_date": "2025-01-31T23:59:59"
            }
        }
    )


class TaskList(BaseModel):
    """
    Schéma pour une liste de tâches avec métadonnées de pagination
    """
    tasks: list[TaskResponse] = Field(
        ...,
        description="Liste des tâches"
    )
    total: int = Field(
        ...,
        description="Nombre total de tâches"
    )
    page: int = Field(
        default=1,
        description="Numéro de page actuel"
    )
    page_size: int = Field(
        default=20,
        description="Nombre de tâches par page"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Tâche exemple",
                        "description": "Description exemple",
                        "priority": "medium",
                        "status": "todo",
                        "created_at": "2025-01-15T10:00:00",
                        "updated_at": "2025-01-15T10:00:00",
                        "due_date": None
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20
            }
        }
    )


class MessageResponse(BaseModel):
    """Schéma pour les réponses simples avec message"""
    message: str = Field(
        ...,
        description="Message de réponse"
    )
    detail: Optional[str] = Field(
        None,
        description="Détails supplémentaires"
    )
