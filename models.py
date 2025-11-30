"""
╔══════════════════════════════════════════════════════════════════════╗
║                       MODÈLES DE BASE DE DONNÉES                      ║
║                                                                      ║
║  Définition des modèles SQLAlchemy pour la persistance des données  ║
║  Modèle Task: Représente une tâche avec ses propriétés             ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
import enum

from app.database import Base


class PriorityEnum(str, enum.Enum):
    """Énumération des niveaux de priorité d'une tâche"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class StatusEnum(str, enum.Enum):
    """Énumération des statuts possibles d'une tâche"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(Base):
    """
    Modèle représentant une tâche dans la base de données
    
    Attributes:
        id (int): Identifiant unique auto-incrémenté
        title (str): Titre de la tâche (requis, max 200 caractères)
        description (str): Description détaillée (optionnelle)
        priority (PriorityEnum): Niveau de priorité (défaut: medium)
        status (StatusEnum): Statut actuel (défaut: todo)
        created_at (datetime): Date de création (auto-générée)
        updated_at (datetime): Date de dernière modification (auto-mise à jour)
        due_date (datetime): Date d'échéance (optionnelle)
    """
    
    __tablename__ = "tasks"
    
    # Clé primaire
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Identifiant unique de la tâche"
    )
    
    # Champs principaux
    title = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Titre de la tâche"
    )
    
    description = Column(
        String(1000),
        nullable=True,
        comment="Description détaillée de la tâche"
    )
    
    priority = Column(
        SQLEnum(PriorityEnum),
        nullable=False,
        default=PriorityEnum.MEDIUM,
        index=True,
        comment="Niveau de priorité: low, medium, high, urgent"
    )
    
    status = Column(
        SQLEnum(StatusEnum),
        nullable=False,
        default=StatusEnum.TODO,
        index=True,
        comment="Statut: todo, in_progress, completed, cancelled"
    )
    
    # Champs de dates
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Date et heure de création"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Date et heure de dernière modification"
    )
    
    due_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date d'échéance de la tâche"
    )
    
    def __repr__(self) -> str:
        """Représentation string du modèle pour le debugging"""
        return (
            f"<Task(id={self.id}, "
            f"title='{self.title}', "
            f"status={self.status}, "
            f"priority={self.priority})>"
        )
    
    def to_dict(self) -> dict:
        """
        Convertit le modèle en dictionnaire Python
        
        Returns:
            dict: Représentation dictionnaire de la tâche
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value if self.priority else None,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }
