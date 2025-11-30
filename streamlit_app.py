"""
╔══════════════════════════════════════════════════════════════════════╗
║                  INTERFACE CLIENT STREAMLIT                           ║
║                                                                      ║
║  Interface web interactive pour interagir avec l'API Task Manager    ║
║  Permet de créer, visualiser, modifier et supprimer des tâches      ║
║                                                                      ║
║  Auteur: Emmanuel Ruaudel                                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ========================================
# CONFIGURATION
# ========================================

# URL de l'API (à modifier selon votre configuration)
API_BASE_URL = "http://localhost:8000"

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .task-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .priority-urgent { border-left-color: #d62728 !important; }
    .priority-high { border-left-color: #ff7f0e !important; }
    .priority-medium { border-left-color: #2ca02c !important; }
    .priority-low { border-left-color: #7f7f7f !important; }
</style>
""", unsafe_allow_html=True)


# ========================================
# FONCTIONS D'API
# ========================================

def check_api_health() -> bool:
    """Vérifie si l'API est accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_all_tasks() -> List[Dict]:
    """Récupère toutes les tâches"""
    try:
        response = requests.get(f"{API_BASE_URL}/tasks?limit=100")
        if response.status_code == 200:
            data = response.json()
            return data.get("tasks", [])
        return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des tâches: {e}")
        return []


def create_task(task_data: Dict) -> Optional[Dict]:
    """Crée une nouvelle tâche"""
    try:
        response = requests.post(f"{API_BASE_URL}/tasks", json=task_data)
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Erreur: {response.json().get('detail', 'Erreur inconnue')}")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la création: {e}")
        return None


def update_task(task_id: int, task_data: Dict) -> Optional[Dict]:
    """Met à jour une tâche"""
    try:
        response = requests.put(f"{API_BASE_URL}/tasks/{task_id}", json=task_data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur: {response.json().get('detail', 'Erreur inconnue')}")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour: {e}")
        return None


def delete_task(task_id: int) -> bool:
    """Supprime une tâche"""
    try:
        response = requests.delete(f"{API_BASE_URL}/tasks/{task_id}")
        return response.status_code == 200
    except Exception as e:
        st.error(f"Erreur lors de la suppression: {e}")
        return False


def get_stats() -> Dict:
    """Récupère les statistiques"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats/summary")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}


def mark_as_completed(task_id: int) -> Optional[Dict]:
    """Marque une tâche comme complétée"""
    try:
        response = requests.patch(f"{API_BASE_URL}/tasks/{task_id}/complete")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Erreur: {e}")
        return None


# ========================================
# FONCTIONS D'INTERFACE
# ========================================

def render_header():
    """Affiche l'en-tête de l'application"""
    st.markdown('<h1 class="main-header">🚀 Task Manager Pro</h1>', unsafe_allow_html=True)
    
    # Vérification de l'API
    if check_api_health():
        st.success("✅ Connecté à l'API")
    else:
        st.error("❌ API non accessible - Vérifiez que le serveur est démarré")
        st.info("Lancez l'API avec: `uvicorn main:app --reload`")
        st.stop()


def render_sidebar():
    """Affiche la barre latérale avec les statistiques"""
    st.sidebar.title("📊 Tableau de bord")
    
    # Récupération des statistiques
    stats = get_stats()
    
    if stats:
        st.sidebar.metric("Total des tâches", stats.get("total_tasks", 0))
        
        st.sidebar.markdown("### Par statut")
        by_status = stats.get("by_status", {})
        st.sidebar.metric("À faire", by_status.get("todo", 0))
        st.sidebar.metric("En cours", by_status.get("in_progress", 0))
        st.sidebar.metric("Complétées", by_status.get("completed", 0))
        
        if stats.get("overdue_tasks", 0) > 0:
            st.sidebar.error(f"⚠️ {stats['overdue_tasks']} tâche(s) en retard")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔗 Liens utiles")
    st.sidebar.markdown(f"[📖 Documentation API]({API_BASE_URL}/docs)")
    st.sidebar.markdown(f"[📄 ReDoc]({API_BASE_URL}/redoc)")


def render_create_task_form():
    """Affiche le formulaire de création de tâche"""
    with st.expander("➕ Créer une nouvelle tâche", expanded=False):
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input(
                    "Titre *",
                    placeholder="Ex: Développer l'API REST"
                )
                priority = st.selectbox(
                    "Priorité",
                    options=["low", "medium", "high", "urgent"],
                    index=1
                )
            
            with col2:
                status = st.selectbox(
                    "Statut",
                    options=["todo", "in_progress", "completed", "cancelled"],
                    index=0
                )
                due_date = st.date_input(
                    "Date d'échéance",
                    min_value=datetime.now().date()
                )
            
            description = st.text_area(
                "Description",
                placeholder="Décrivez la tâche en détail..."
            )
            
            submitted = st.form_submit_button("🚀 Créer la tâche")
            
            if submitted:
                if not title or len(title) < 3:
                    st.error("Le titre doit contenir au moins 3 caractères")
                else:
                    task_data = {
                        "title": title,
                        "description": description if description else None,
                        "priority": priority,
                        "status": status,
                        "due_date": f"{due_date}T23:59:59" if due_date else None
                    }
                    
                    result = create_task(task_data)
                    if result:
                        st.success(f"✅ Tâche créée avec succès ! (ID: {result['id']})")
                        st.rerun()


def render_task_card(task: Dict):
    """Affiche une carte de tâche"""
    priority_class = f"priority-{task['priority']}"
    
    with st.container():
        st.markdown(f'<div class="task-card {priority_class}">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"### {task['title']}")
            if task.get('description'):
                st.markdown(task['description'])
        
        with col2:
            # Badge de priorité
            priority_colors = {
                "urgent": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "⚪"
            }
            st.markdown(f"{priority_colors.get(task['priority'], '⚪')} {task['priority'].upper()}")
        
        with col3:
            # Badge de statut
            status_emoji = {
                "todo": "📝",
                "in_progress": "⚙️",
                "completed": "✅",
                "cancelled": "❌"
            }
            st.markdown(f"{status_emoji.get(task['status'], '📝')} {task['status'].replace('_', ' ').title()}")
        
        with col4:
            # Actions
            if st.button("✅", key=f"complete_{task['id']}", help="Marquer comme complété"):
                if mark_as_completed(task['id']):
                    st.success("Tâche complétée !")
                    st.rerun()
            
            if st.button("🗑️", key=f"delete_{task['id']}", help="Supprimer"):
                if delete_task(task['id']):
                    st.success("Tâche supprimée !")
                    st.rerun()
        
        # Informations supplémentaires
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            created = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
            st.caption(f"📅 Créée le: {created.strftime('%d/%m/%Y %H:%M')}")
        
        with col_info2:
            if task.get('due_date'):
                due = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                st.caption(f"⏰ Échéance: {due.strftime('%d/%m/%Y')}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_tasks_list(tasks: List[Dict]):
    """Affiche la liste des tâches"""
    if not tasks:
        st.info("Aucune tâche à afficher. Créez-en une pour commencer !")
        return
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.multiselect(
            "Filtrer par statut",
            options=["todo", "in_progress", "completed", "cancelled"],
            default=["todo", "in_progress"]
        )
    
    with col2:
        filter_priority = st.multiselect(
            "Filtrer par priorité",
            options=["urgent", "high", "medium", "low"],
            default=["urgent", "high", "medium", "low"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Trier par",
            options=["Date de création", "Priorité", "Échéance"]
        )
    
    # Application des filtres
    filtered_tasks = [
        task for task in tasks
        if task['status'] in filter_status and task['priority'] in filter_priority
    ]
    
    # Tri
    if sort_by == "Priorité":
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        filtered_tasks.sort(key=lambda x: priority_order.get(x['priority'], 4))
    elif sort_by == "Échéance":
        filtered_tasks.sort(key=lambda x: x.get('due_date') or '9999-12-31')
    else:  # Date de création
        filtered_tasks.sort(key=lambda x: x['created_at'], reverse=True)
    
    st.markdown(f"### 📋 {len(filtered_tasks)} tâche(s)")
    
    # Affichage des tâches
    for task in filtered_tasks:
        render_task_card(task)


def render_analytics():
    """Affiche les graphiques analytiques"""
    st.markdown("## 📊 Analyse des tâches")
    
    tasks = get_all_tasks()
    if not tasks:
        st.info("Aucune donnée à analyser")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique par statut
        df_status = pd.DataFrame([
            {"Statut": task['status'].replace('_', ' ').title(), "Count": 1}
            for task in tasks
        ])
        status_counts = df_status.groupby('Statut').sum().reset_index()
        
        fig_status = px.pie(
            status_counts,
            values='Count',
            names='Statut',
            title="Répartition par statut"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Graphique par priorité
        df_priority = pd.DataFrame([
            {"Priorité": task['priority'].upper(), "Count": 1}
            for task in tasks
        ])
        priority_counts = df_priority.groupby('Priorité').sum().reset_index()
        
        fig_priority = px.bar(
            priority_counts,
            x='Priorité',
            y='Count',
            title="Répartition par priorité",
            color='Priorité',
            color_discrete_map={
                "URGENT": "#d62728",
                "HIGH": "#ff7f0e",
                "MEDIUM": "#2ca02c",
                "LOW": "#7f7f7f"
            }
        )
        st.plotly_chart(fig_priority, use_container_width=True)


# ========================================
# APPLICATION PRINCIPALE
# ========================================

def main():
    """Fonction principale de l'application"""
    render_header()
    render_sidebar()
    
    # Onglets de navigation
    tab1, tab2, tab3 = st.tabs(["📝 Tâches", "📊 Analyse", "ℹ️ À propos"])
    
    with tab1:
        render_create_task_form()
        st.markdown("---")
        tasks = get_all_tasks()
        render_tasks_list(tasks)
    
    with tab2:
        render_analytics()
    
    with tab3:
        st.markdown("""
        # 🚀 Task Manager Pro
        
        ## À propos
        
        Application de gestion de tâches moderne construite avec:
        - **Backend**: FastAPI + SQLAlchemy
        - **Frontend**: Streamlit
        - **Base de données**: SQLite (extensible vers PostgreSQL)
        
        ## Fonctionnalités
        
        ✅ Créer, modifier, supprimer des tâches  
        ✅ Filtrer par statut et priorité  
        ✅ Visualiser les statistiques  
        ✅ Graphiques interactifs  
        ✅ Interface intuitive et responsive  
        
        ## Auteur
        
        **Emmanuel Ruaudel**  
        📧 ruaudel.emmanuel@orange.fr  
        🔗 [GitHub](https://github.com/Ruaudel-Emmanuel)  
        🌐 [Portfolio](https://ruaudel-emmanuel.github.io/RuaudelEmmanuel.github.io/)
        
        ## Version
        
        v1.0.0 - 2025
        """)


if __name__ == "__main__":
    main()
