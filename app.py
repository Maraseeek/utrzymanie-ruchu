import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Warsztat Ziołolek", 
    page_icon="🔧", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ZAAWANSOWANE STYLE CSS ---
st.markdown("""
    <style>
    /* Import profesjonalnej czcionki */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Tło aplikacji - gradient przemysłowy */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 100%);
    }
    
    /* Sidebar - panel kontrolny */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161b26 0%, #0d111c 100%);
        border-right: 2px solid #2a3142;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #4a9eff !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metryki - status indicators */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e2533 0%, #252d3d 100%);
        border: 2px solid #2d3748;
        border-left: 4px solid #4a9eff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-left-color: #60b0ff;
        box-shadow: 0 6px 12px rgba(74, 158, 255, 0.2);
        transform: translateY(-2px);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #8b95a8 !important;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    /* Kontenery z ramką */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, #1a1f2e 0%, #23293a 100%);
        border: 2px solid #2d3748;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Pasek postępu - wielokolorowy system */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4a9eff 0%, #60b0ff 100%);
        border-radius: 4px;
    }
    
    /* Przyciski - system hierarchiczny */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 12px 24px !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease;
        font-size: 0.9rem !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4a9eff 0%, #357abd 100%) !important;
        border-color: #4a9eff !important;
        box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #60b0ff 0%, #4a9eff 100%) !important;
        box-shadow: 0 6px 16px rgba(74, 158, 255, 0.5);
        transform: translateY(-2px);
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border-color: #4a9eff !important;
        color: #4a9eff !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(74, 158, 255, 0.1) !important;
        border-color: #60b0ff !important;
    }
    
    /* Nagłówki - hierarchia wizualna */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        border-bottom: 3px solid #4a9eff;
        padding-bottom: 10px;
        margin-bottom: 30px !important;
    }
    
    h2 {
        font-size: 1.8rem !important;
        color: #4a9eff !important;
        margin-top: 20px !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
        color: #60b0ff !important;
    }
    
    h4 {
        color: #8b95a8 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Tabele - profesjonalny wygląd */
    .stDataFrame {
        border: 2px solid #2d3748 !important;
        border-radius: 8px !important;
        overflow: hidden;
    }
    
    thead tr th {
        background: linear-gradient(135deg, #2d3748 0%, #3d4758 100%) !important;
        color: #4a9eff !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 15px !important;
        border-bottom: 2px solid #4a9eff !important;
    }
    
    tbody tr {
        background-color: #1a1f2e !important;
        transition: all 0.2s ease;
    }
    
    tbody tr:hover {
        background-color: #23293a !important;
        box-shadow: inset 0 0 0 2px #4a9eff;
    }
    
    tbody tr td {
        padding: 12px !important;
        color: #e2e8f0 !important;
        border-bottom: 1px solid #2d3748 !important;
    }
    
    /* Alerty - system kolorystyczny */
    .stAlert {
        border-radius: 8px !important;
        border-left: 5px solid !important;
        padding: 15px 20px !important;
        font-weight: 500 !important;
    }
    
    div[data-baseweb="notification"][kind="error"] {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-left-color: #ef4444 !important;
    }
    
    div[data-baseweb="notification"][kind="warning"] {
        background-color: rgba(251, 191, 36, 0.15) !important;
        border-left-color: #fbbf24 !important;
    }
    
    div[data-baseweb="notification"][kind="success"] {
        background-color: rgba(34, 197, 94, 0.15) !important;
        border-left-color: #22c55e !important;
    }
    
    div[data-baseweb="notification"][kind="info"] {
        background-color: rgba(74, 158, 255, 0.15) !important;
        border-left-color: #4a9eff !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #1a1f2e !important;
        border: 2px solid #2d3748 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        padding: 10px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #4a9eff !important;
        box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.2) !important;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-critical {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 2px solid #ef4444;
    }
    
    .badge-warning {
        background-color: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 2px solid #fbbf24;
    }
    
    .badge-ok {
        background-color: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 2px solid #22c55e;
    }
    
    /* Separator */
    hr {
        border: none;
        border-top: 2px solid #2d3748;
        margin: 30px 0;
    }
    
    /* Tooltips i caption */
    .stCaption {
        color: #8b95a8 !important;
        font-size: 0.85rem !important;
    }
    
    /* Radio buttons */
    div[role="radiogroup"] label {
        background-color: #1a1f2e !important;
        padding: 12px 20px !important;
        border-radius: 6px !important;
        border: 2px solid #2d3748 !important;
        margin: 5px 0 !important;
        transition: all 0.3s ease;
    }
    
    div[role="radiogroup"] label:hover {
        border-color: #4a9eff !important;
        background-color: #23293a !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1f2e !important;
        border: 2px solid #2d3748 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #4a9eff !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f2e;
        border: 2px solid #2d3748;
        border-radius: 6px 6px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        color: #8b95a8;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #23293a;
        border-color: #4a9eff;
        border-bottom: none;
        color: #4a9eff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KLASY DANYCH ---
@dataclass
class ServiceInterval:
    """Pojedynczy interwał serwisowy"""
    name: str
    type: str  # 'cycles' lub 'time'
    interval: int  # liczba cykli lub miesięcy
    current_value: int
    last_service: str
    enabled: bool = True
    
    def get_status(self):
        """Zwraca status: 0=OK, 1=Warning, 2=Critical"""
        if not self.enabled:
            return 0
            
        if self.type == 'cycles':
            remaining = self.interval - self.current_value
            if remaining <= 0:
                return 2
            elif remaining <= self.interval * 0.15:
                return 1
        else:  # time
            last = datetime.strptime(self.last_service, "%Y-%m-%d").date()
            next_date = add_months(last, self.interval)
            days_remaining = (next_date - datetime.now().date()).days
            if days_remaining <= 0:
                return 2
            elif days_remaining <= 7:
                return 1
        return 0
    
    def get_progress(self):
        """Zwraca postęp jako wartość 0-1"""
        if not self.enabled:
            return 0
        if self.type == 'cycles':
            return min(self.current_value / self.interval, 1.0)
        else:
            last = datetime.strptime(self.last_service, "%Y-%m-%d").date()
            next_date = add_months(last, self.interval)
            total_days = (next_date - last).days
            elapsed_days = (datetime.now().date() - last).days
            return min(elapsed_days / total_days, 1.0)

# --- FUNKCJE POMOCNICZE ---
def add_months(source_date, months):
    """Dodaje miesiące do daty"""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, [31,29,31,30,31,30,31,31,30,31,30,31][month-1])
    return source_date.replace(year=year, month=month, day=day)

# --- SYSTEM ZAPISU DANYCH (PERSISTENCE) ---
DATA_DIR = Path("warsztat_data")
DATABASE_FILE = DATA_DIR / "database.json"
HISTORY_FILE = DATA_DIR / "history.json"
BACKUP_DIR = DATA_DIR / "backups"

def ensure_data_directory():
    """Tworzy katalog na dane jeśli nie istnieje"""
    DATA_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

def create_backup():
    """Tworzy kopię zapasową bazy danych"""
    try:
        if DATABASE_FILE.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"database_backup_{timestamp}.json"
            
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Zachowaj tylko 10 ostatnich backupów
            backups = sorted(BACKUP_DIR.glob("database_backup_*.json"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
            
            return True
    except Exception as e:
        st.error(f"Błąd tworzenia backupu: {e}")
        return False

def save_database(data):
    """Zapisuje bazę danych do pliku JSON"""
    try:
        ensure_data_directory()
        
        # Walidacja danych przed zapisem
        if not isinstance(data, dict) or 'machines' not in data:
            st.error("Nieprawidłowa struktura danych!")
            return False
        
        # Zapisz dane
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Błąd zapisu bazy danych: {e}")
        return False

def load_database():
    """Wczytuje bazę danych z pliku JSON lub tworzy nową"""
    try:
        ensure_data_directory()
        
        if DATABASE_FILE.exists():
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Walidacja struktury
            if isinstance(data, dict) and 'machines' in data:
                return data
            else:
                st.warning("Nieprawidłowa struktura pliku database.json - tworzę nową bazę")
                return get_initial_data()
        else:
            # Pierwsza inicjalizacja - utwórz bazę
            initial_data = get_initial_data()
            save_database(initial_data)
            return initial_data
            
    except json.JSONDecodeError:
        st.error("Błąd odczytu database.json - plik uszkodzony. Tworzę nową bazę.")
        return get_initial_data()
    except Exception as e:
        st.error(f"Błąd wczytywania bazy danych: {e}")
        return get_initial_data()

def save_history(history):
    """Zapisuje historię operacji do pliku JSON"""
    try:
        ensure_data_directory()
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Błąd zapisu historii: {e}")
        return False

def load_history():
    """Wczytuje historię operacji z pliku JSON"""
    try:
        ensure_data_directory()
        
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history if isinstance(history, list) else []
        else:
            return []
            
    except json.JSONDecodeError:
        st.warning("Błąd odczytu history.json - tworzę nową historię")
        return []
    except Exception as e:
        st.error(f"Błąd wczytywania historii: {e}")
        return []

def get_status_color(status):
    """Zwraca kolor dla statusu"""
    colors = {0: "#22c55e", 1: "#fbbf24", 2: "#ef4444"}
    return colors.get(status, "#8b95a8")

def get_status_label(status):
    """Zwraca etykietę dla statusu"""
    labels = {0: "OK", 1: "OSTRZEŻENIE", 2: "KRYTYCZNY"}
    return labels.get(status, "NIEZNANY")

def get_initial_data():
    """Struktura danych z wieloma interwałami serwisowymi"""
    return {
        "machines": [
            {
                "id": "M01",
                "name": "Wtryskarka A1",
                "location": "Hala A",
                "model": "KraussMaffei KM250",
                "avg_daily_cycles": 15,
                "service_intervals": [
                    {"name": "Serwis 5-cyklowy", "type": "cycles", "interval": 5, "current_value": 4, "last_service": "2025-02-07", "enabled": True},
                    {"name": "Serwis 20-cyklowy", "type": "cycles", "interval": 20, "current_value": 18, "last_service": "2025-01-20", "enabled": True},
                    {"name": "Przegląd kwartalny", "type": "time", "interval": 3, "current_value": 0, "last_service": "2024-12-01", "enabled": True},
                    {"name": "Remont roczny", "type": "time", "interval": 12, "current_value": 0, "last_service": "2024-03-15", "enabled": True}
                ]
            },
            {
                "id": "M02",
                "name": "Prasa Hydrauliczna PH-500",
                "location": "Hala B",
                "model": "Schuler PH-500",
                "avg_daily_cycles": 30,
                "service_intervals": [
                    {"name": "Serwis 50-cyklowy", "type": "cycles", "interval": 50, "current_value": 45, "last_service": "2025-02-01", "enabled": True},
                    {"name": "Przegląd miesięczny", "type": "time", "interval": 1, "current_value": 0, "last_service": "2025-01-10", "enabled": True},
                    {"name": "Remont półroczny", "type": "time", "interval": 6, "current_value": 0, "last_service": "2024-09-01", "enabled": True}
                ]
            },
            {
                "id": "M03",
                "name": "Pakowarka Automatyczna Z-100",
                "location": "Hala C",
                "model": "Bosch Z-100",
                "avg_daily_cycles": 50,
                "service_intervals": [
                    {"name": "Serwis 100-cyklowy", "type": "cycles", "interval": 100, "current_value": 95, "last_service": "2025-02-05", "enabled": True},
                    {"name": "Serwis 500-cyklowy", "type": "cycles", "interval": 500, "current_value": 450, "last_service": "2024-12-20", "enabled": True},
                    {"name": "Przegląd kwartalny", "type": "time", "interval": 3, "current_value": 0, "last_service": "2024-11-15", "enabled": True}
                ]
            },
            {
                "id": "M04",
                "name": "Tokarka CNC TK-300",
                "location": "Hala A",
                "model": "DMG Mori NLX 2500",
                "avg_daily_cycles": 8,
                "service_intervals": [
                    {"name": "Przegląd miesięczny", "type": "time", "interval": 1, "current_value": 0, "last_service": "2025-01-15", "enabled": True},
                    {"name": "Remont roczny", "type": "time", "interval": 12, "current_value": 0, "last_service": "2024-02-20", "enabled": True}
                ]
            }
        ]
    }

# Inicjalizacja danych z automatycznym zapisem/odczytem
if 'data' not in st.session_state:
    st.session_state.data = load_database()
if 'history' not in st.session_state:
    st.session_state.history = load_history()
if 'unsaved_changes' not in st.session_state:
    st.session_state.unsaved_changes = False

# --- FUNKCJE OPERACYJNE ---
def add_cycle(machine_id, cycles):
    """Dodaje cykle do wszystkich interwałów cyklicznych"""
    for machine in st.session_state.data['machines']:
        if machine['id'] == machine_id:
            for interval in machine['service_intervals']:
                if interval['type'] == 'cycles' and interval['enabled']:
                    interval['current_value'] += cycles
            
            # Dodaj do historii
            st.session_state.history.insert(0, {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "machine": machine['name'],
                "action": f"Dodano {cycles} cykli",
                "user": "System"
            })
            
            # Automatyczny zapis
            save_database(st.session_state.data)
            save_history(st.session_state.history)
            break

def reset_service_interval(machine_id, interval_name):
    """Resetuje konkretny interwał serwisowy"""
    for machine in st.session_state.data['machines']:
        if machine['id'] == machine_id:
            for interval in machine['service_intervals']:
                if interval['name'] == interval_name:
                    interval['current_value'] = 0
                    interval['last_service'] = str(datetime.now().date())
                    
                    # Dodaj do historii
                    st.session_state.history.insert(0, {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "machine": machine['name'],
                        "action": f"Wykonano: {interval_name}",
                        "user": "System"
                    })
                    
                    # Automatyczny zapis
                    save_database(st.session_state.data)
                    save_history(st.session_state.history)
                    break
            break

def get_machine_critical_status(machine):
    """Zwraca najwyższy status krytyczny dla maszyny"""
    max_status = 0
    critical_intervals = []
    
    for interval_data in machine['service_intervals']:
        interval = ServiceInterval(**interval_data)
        status = interval.get_status()
        if status > max_status:
            max_status = status
        if status == 2:
            critical_intervals.append(interval.name)
    
    return max_status, critical_intervals

# --- SIDEBAR ---
st.sidebar.markdown("### 🔧 WARSZTAT ZIOŁOLEK")
st.sidebar.markdown("#### System Utrzymania Ruchu")
st.sidebar.markdown("---")

view = st.sidebar.radio(
    "NAWIGACJA",
    ["🏠 Panel Główny", "🔧 Karta Maszyny", "⚙️ Konfiguracja", "📊 Historia"],
    label_visibility="visible"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data systemu:** {datetime.now().strftime('%d.%m.%Y')}")
st.sidebar.markdown(f"**Godzina:** {datetime.now().strftime('%H:%M:%S')}")

# Liczniki alertów
critical_count = 0
warning_count = 0
for machine in st.session_state.data['machines']:
    status, _ = get_machine_critical_status(machine)
    if status == 2:
        critical_count += 1
    elif status == 1:
        warning_count += 1

st.sidebar.markdown("---")
st.sidebar.markdown("#### STATUS FLOTY")
if critical_count > 0:
    st.sidebar.error(f"🚨 Krytyczne: {critical_count}")
if warning_count > 0:
    st.sidebar.warning(f"⚠️ Ostrzeżenia: {warning_count}")
if critical_count == 0 and warning_count == 0:
    st.sidebar.success(f"✅ Wszystko OK")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 💾 SYSTEM ZAPISU")
if DATABASE_FILE.exists():
    file_time = datetime.fromtimestamp(DATABASE_FILE.stat().st_mtime)
    st.sidebar.caption(f"Ostatni zapis: {file_time.strftime('%d.%m %H:%M')}")
else:
    st.sidebar.caption("Brak zapisanej bazy")

# Przycisk tworzenia backupu
if st.sidebar.button("📦 Utwórz Backup", use_container_width=True):
    if create_backup():
        st.sidebar.success("✅ Backup utworzony!")
    else:
        st.sidebar.error("❌ Błąd backupu")

# --- WIDOK 1: PANEL GŁÓWNY ---
if view == "🏠 Panel Główny":
    st.title("DASHBOARD UTRZYMANIA RUCHU")
    
    # Sekcja alertów
    alerts_critical = []
    alerts_warning = []
    
    for machine in st.session_state.data['machines']:
        for interval_data in machine['service_intervals']:
            interval = ServiceInterval(**interval_data)
            status = interval.get_status()
            
            if status == 2:
                alerts_critical.append(f"**{machine['name']}** - {interval.name}")
            elif status == 1:
                alerts_warning.append(f"**{machine['name']}** - {interval.name}")
    
    # Wyświetlanie alertów
    col_alert1, col_alert2 = st.columns(2)
    
    with col_alert1:
        if alerts_critical:
            st.error(f"### 🚨 PILNE INTERWENCJE ({len(alerts_critical)})")
            for alert in alerts_critical:
                st.markdown(f"- {alert}")
        else:
            st.success("### ✅ Brak krytycznych alertów")
    
    with col_alert2:
        if alerts_warning:
            st.warning(f"### ⚠️ OSTRZEŻENIA ({len(alerts_warning)})")
            for alert in alerts_warning:
                st.markdown(f"- {alert}")
        else:
            st.info("### ℹ️ Brak ostrzeżeń")
    
    st.markdown("---")
    
    # Statystyki ogólne
    st.subheader("PRZEGLĄD FLOTY")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_machines = len(st.session_state.data['machines'])
    machines_ok = total_machines - critical_count - warning_count
    
    col1.metric("Maszyny w systemie", total_machines, delta=None)
    col2.metric("Stan sprawny", machines_ok, delta="OK" if machines_ok == total_machines else None)
    col3.metric("Ostrzeżenia", warning_count, delta="⚠️" if warning_count > 0 else None)
    col4.metric("Krytyczne", critical_count, delta="🚨" if critical_count > 0 else None)
    
    st.markdown("---")
    
    # Lista maszyn - kafelki
    st.subheader("STATUS MASZYN")
    
    cols = st.columns(2)
    for idx, machine in enumerate(st.session_state.data['machines']):
        col = cols[idx % 2]
        
        with col:
            with st.container(border=True):
                # Nagłówek z statusem
                machine_status, critical_intervals = get_machine_critical_status(machine)
                status_color = get_status_color(machine_status)
                status_label = get_status_label(machine_status)
                
                col_name, col_status = st.columns([3, 1])
                col_name.markdown(f"### {machine['name']}")
                col_status.markdown(f"<div class='status-badge badge-{'critical' if machine_status == 2 else 'warning' if machine_status == 1 else 'ok'}'>{status_label}</div>", unsafe_allow_html=True)
                
                st.caption(f"📍 {machine['location']} | 🏭 {machine['model']}")
                
                st.markdown("---")
                
                # Interwały serwisowe
                st.markdown("#### Interwały serwisowe:")
                
                for interval_data in machine['service_intervals']:
                    if interval_data['enabled']:
                        interval = ServiceInterval(**interval_data)
                        status = interval.get_status()
                        progress = interval.get_progress()
                        
                        col_label, col_value = st.columns([2, 1])
                        col_label.caption(interval.name)
                        
                        if interval.type == 'cycles':
                            col_value.write(f"{interval.current_value}/{interval.interval}")
                        else:
                            last = datetime.strptime(interval.last_service, "%Y-%m-%d").date()
                            next_date = add_months(last, interval.interval)
                            days = (next_date - datetime.now().date()).days
                            col_value.write(f"{days} dni")
                        
                        # Pasek postępu z kolorem
                        progress_color = get_status_color(status)
                        st.progress(progress)
                
                st.markdown("")
                
                # Przycisk akcji
                if st.button(f"Otwórz kartę", key=f"open_{machine['id']}", use_container_width=True, type="primary"):
                    st.session_state.selected_machine = machine['id']
                    st.rerun()

# --- WIDOK 2: KARTA MASZYNY ---
elif view == "🔧 Karta Maszyny":
    st.title("KARTA MASZYNY")
    
    # Wybór maszyny
    machine_names = [m['name'] for m in st.session_state.data['machines']]
    
    if 'selected_machine' in st.session_state:
        default_machine = next((m for m in st.session_state.data['machines'] if m['id'] == st.session_state.selected_machine), None)
        default_index = machine_names.index(default_machine['name']) if default_machine else 0
    else:
        default_index = 0
    
    selected_name = st.selectbox("**Wybierz maszynę:**", machine_names, index=default_index)
    machine = next(m for m in st.session_state.data['machines'] if m['name'] == selected_name)
    
    st.markdown("---")
    
    # Informacje podstawowe
    col1, col2, col3 = st.columns(3)
    col1.metric("ID Maszyny", machine['id'])
    col2.metric("Lokalizacja", machine['location'])
    col3.metric("Model", machine['model'])
    
    st.markdown("---")
    
    # Dwie kolumny: Operacje i Interwały
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 📝 OPERACJE")
        
        with st.container(border=True):
            st.markdown("#### Rejestracja cykli")
            cycles_to_add = st.number_input("Liczba wykonanych cykli:", min_value=1, step=1, value=1)
            
            if st.button("✅ Zatwierdź wpis", key="add_cycles", use_container_width=True, type="primary"):
                add_cycle(machine['id'], cycles_to_add)
                st.success(f"Dodano {cycles_to_add} cykli")
                st.rerun()
        
        st.markdown("")
        
        with st.container(border=True):
            st.markdown("#### Szybkie akcje")
            
            for interval_data in machine['service_intervals']:
                if interval_data['enabled']:
                    interval = ServiceInterval(**interval_data)
                    status = interval.get_status()
                    
                    button_type = "primary" if status == 2 else "secondary"
                    button_label = f"🛠️ {interval.name}"
                    
                    if st.button(button_label, key=f"reset_{machine['id']}_{interval.name}", use_container_width=True):
                        reset_service_interval(machine['id'], interval.name)
                        st.success(f"Wykonano: {interval.name}")
                        st.rerun()
    
    with col_right:
        st.markdown("### 📊 STATUS INTERWAŁÓW")
        
        # Szczegółowy widok każdego interwału
        for interval_data in machine['service_intervals']:
            if interval_data['enabled']:
                interval = ServiceInterval(**interval_data)
                status = interval.get_status()
                progress = interval.get_progress()
                
                with st.expander(f"**{interval.name}** - {get_status_label(status)}", expanded=(status == 2)):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if interval.type == 'cycles':
                            st.metric("Aktualny stan", f"{interval.current_value}/{interval.interval} cykli")
                            remaining = interval.interval - interval.current_value
                            st.metric("Pozostało", f"{remaining} cykli")
                        else:
                            last = datetime.strptime(interval.last_service, "%Y-%m-%d").date()
                            next_date = add_months(last, interval.interval)
                            days = (next_date - datetime.now().date()).days
                            st.metric("Następny termin", next_date.strftime("%d.%m.%Y"))
                            st.metric("Pozostało", f"{days} dni")
                    
                    with col_b:
                        st.metric("Ostatni serwis", interval.last_service)
                        st.metric("Status", get_status_label(status))
                    
                    st.progress(progress)
                    
                    # Prognoza
                    if interval.type == 'cycles' and machine['avg_daily_cycles'] > 0:
                        remaining = interval.interval - interval.current_value
                        days_to_service = int(remaining / machine['avg_daily_cycles'])
                        service_date = datetime.now().date() + timedelta(days=days_to_service)
                        st.info(f"📅 Estymowany termin serwisu: **{service_date.strftime('%d.%m.%Y')}** (za {days_to_service} dni)")
        
        st.markdown("---")
        
        # Prognoza 14-dniowa
        st.markdown("### 📈 PROGNOZA 14-DNIOWA")
        
        forecast_data = []
        for i in range(1, 15):
            day = datetime.now().date() + timedelta(days=i)
            day_status = "OK"
            events = []
            
            # Sprawdź cykle
            predicted_cycles = machine['avg_daily_cycles'] * i
            for interval_data in machine['service_intervals']:
                if interval_data['enabled'] and interval_data['type'] == 'cycles':
                    future_value = interval_data['current_value'] + predicted_cycles
                    if future_value >= interval_data['interval']:
                        events.append(interval_data['name'])
                        day_status = "SERWIS"
            
            # Sprawdź daty
            for interval_data in machine['service_intervals']:
                if interval_data['enabled'] and interval_data['type'] == 'time':
                    last = datetime.strptime(interval_data['last_service'], "%Y-%m-%d").date()
                    next_date = add_months(last, interval_data['interval'])
                    if day == next_date:
                        events.append(interval_data['name'])
                        day_status = "PRZEGLĄD"
            
            forecast_data.append({
                "Data": day.strftime("%d.%m (%a)"),
                "Status": day_status,
                "Zdarzenia": ", ".join(events) if events else "-"
            })
        
        df_forecast = pd.DataFrame(forecast_data)
        
        def highlight_forecast(val):
            if 'SERWIS' in str(val) or 'PRZEGLĄD' in str(val):
                return 'background-color: rgba(239, 68, 68, 0.3); color: #ef4444; font-weight: 600'
            return ''
        
        st.dataframe(
            df_forecast.style.map(highlight_forecast, subset=['Status']),
            use_container_width=True,
            hide_index=True,
            height=520
        )

# --- WIDOK 3: KONFIGURACJA ---
elif view == "⚙️ Konfiguracja":
    st.title("KONFIGURACJA SYSTEMU")
    
    # Ostrzeżenie o niezapisanych zmianach
    if st.session_state.unsaved_changes:
        st.warning("⚠️ **Masz niezapisane zmiany!** Kliknij 'Zapisz zmiany' aby je zachować.")
    
    # Przyciski akcji na górze
    col_save, col_backup, col_reset = st.columns(3)
    
    with col_save:
        if st.button("💾 Zapisz zmiany", type="primary", use_container_width=True):
            if save_database(st.session_state.data):
                st.session_state.unsaved_changes = False
                st.success("✅ Zmiany zapisane pomyślnie!")
                st.rerun()
            else:
                st.error("❌ Błąd zapisu!")
    
    with col_backup:
        if st.button("📦 Backup przed zmianami", use_container_width=True):
            if create_backup():
                st.success("✅ Backup utworzony!")
            else:
                st.error("❌ Błąd backupu!")
    
    with col_reset:
        if st.button("🔄 Odśwież dane", use_container_width=True):
            st.session_state.data = load_database()
            st.session_state.unsaved_changes = False
            st.success("✅ Dane odświeżone!")
            st.rerun()
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🏭 Zarządzanie maszynami", "🔧 Interwały serwisowe", "📁 Zarządzanie plikami"])
    
    with tab1:
        st.subheader("Lista maszyn")
        
        for idx, machine in enumerate(st.session_state.data['machines']):
            with st.expander(f"**{machine['name']}** ({machine['id']})", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Nazwa", machine['name'], key=f"name_{idx}")
                    new_location = st.text_input("Lokalizacja", machine['location'], key=f"loc_{idx}")
                    
                    if new_name != machine['name']:
                        machine['name'] = new_name
                        st.session_state.unsaved_changes = True
                    if new_location != machine['location']:
                        machine['location'] = new_location
                        st.session_state.unsaved_changes = True
                
                with col2:
                    new_model = st.text_input("Model", machine['model'], key=f"model_{idx}")
                    new_avg = st.number_input("Średnia dzienna cykli", machine['avg_daily_cycles'], key=f"avg_{idx}")
                    
                    if new_model != machine['model']:
                        machine['model'] = new_model
                        st.session_state.unsaved_changes = True
                    if new_avg != machine['avg_daily_cycles']:
                        machine['avg_daily_cycles'] = new_avg
                        st.session_state.unsaved_changes = True
                
                if st.button(f"🗑️ Usuń maszynę", key=f"del_machine_{idx}"):
                    if len(st.session_state.data['machines']) > 1:
                        deleted_name = machine['name']
                        st.session_state.data['machines'].pop(idx)
                        save_database(st.session_state.data)
                        
                        # Dodaj do historii
                        st.session_state.history.insert(0, {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "machine": deleted_name,
                            "action": "Usunięto maszynę z systemu",
                            "user": "System"
                        })
                        save_history(st.session_state.history)
                        
                        st.success(f"Usunięto maszynę: {deleted_name}")
                        st.rerun()
                    else:
                        st.error("Nie możesz usunąć ostatniej maszyny!")
        
        st.markdown("---")
        
        if st.button("➕ Dodaj nową maszynę", type="primary"):
            new_id = f"M{len(st.session_state.data['machines'])+1:02d}"
            new_machine = {
                "id": new_id,
                "name": f"Nowa maszyna {new_id}",
                "location": "Hala X",
                "model": "Model",
                "avg_daily_cycles": 10,
                "service_intervals": []
            }
            st.session_state.data['machines'].append(new_machine)
            save_database(st.session_state.data)
            
            # Dodaj do historii
            st.session_state.history.insert(0, {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "machine": new_machine['name'],
                "action": "Dodano nową maszynę do systemu",
                "user": "System"
            })
            save_history(st.session_state.history)
            
            st.success("Dodano nową maszynę!")
            st.rerun()
    
    with tab2:
        st.subheader("Konfiguracja interwałów serwisowych")
        
        selected_machine_name = st.selectbox("Wybierz maszynę:", [m['name'] for m in st.session_state.data['machines']], key="config_select")
        machine = next(m for m in st.session_state.data['machines'] if m['name'] == selected_machine_name)
        
        st.markdown("---")
        
        st.markdown("#### Istniejące interwały:")
        
        for idx, interval_data in enumerate(machine['service_intervals']):
            with st.expander(f"**{interval_data['name']}**", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_int_name = st.text_input("Nazwa interwału", interval_data['name'], key=f"int_name_{machine['id']}_{idx}")
                    new_enabled = st.checkbox("Włączony", interval_data['enabled'], key=f"int_en_{machine['id']}_{idx}")
                    
                    if new_int_name != interval_data['name']:
                        interval_data['name'] = new_int_name
                        st.session_state.unsaved_changes = True
                    if new_enabled != interval_data['enabled']:
                        interval_data['enabled'] = new_enabled
                        st.session_state.unsaved_changes = True
                
                with col2:
                    new_type = st.selectbox("Typ", ['cycles', 'time'], index=0 if interval_data['type']=='cycles' else 1, key=f"int_type_{machine['id']}_{idx}")
                    new_interval = st.number_input("Interwał" + (" (cykle)" if interval_data['type']=='cycles' else " (miesiące)"), 
                                                                 interval_data['interval'], min_value=1, key=f"int_val_{machine['id']}_{idx}")
                    
                    if new_type != interval_data['type']:
                        interval_data['type'] = new_type
                        st.session_state.unsaved_changes = True
                    if new_interval != interval_data['interval']:
                        interval_data['interval'] = new_interval
                        st.session_state.unsaved_changes = True
                
                with col3:
                    new_current = st.number_input("Bieżąca wartość", interval_data['current_value'], min_value=0, key=f"int_cur_{machine['id']}_{idx}")
                    new_last = st.date_input("Ostatni serwis", datetime.strptime(interval_data['last_service'], "%Y-%m-%d").date(), 
                                                                   key=f"int_date_{machine['id']}_{idx}").strftime("%Y-%m-%d")
                    
                    if new_current != interval_data['current_value']:
                        interval_data['current_value'] = new_current
                        st.session_state.unsaved_changes = True
                    if new_last != interval_data['last_service']:
                        interval_data['last_service'] = new_last
                        st.session_state.unsaved_changes = True
                
                if st.button(f"🗑️ Usuń interwał", key=f"del_int_{machine['id']}_{idx}"):
                    deleted_interval = interval_data['name']
                    machine['service_intervals'].pop(idx)
                    save_database(st.session_state.data)
                    
                    # Dodaj do historii
                    st.session_state.history.insert(0, {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "machine": machine['name'],
                        "action": f"Usunięto interwał: {deleted_interval}",
                        "user": "System"
                    })
                    save_history(st.session_state.history)
                    
                    st.success("Usunięto interwał")
                    st.rerun()
        
        st.markdown("---")
        
        st.markdown("#### Dodaj nowy interwał:")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            new_int_name = st.text_input("Nazwa", "Nowy interwał")
        with col_b:
            new_int_type = st.selectbox("Typ", ['cycles', 'time'])
        with col_c:
            new_int_interval = st.number_input("Interwał", 1, min_value=1)
        with col_d:
            st.write("")
            st.write("")
            if st.button("➕ Dodaj interwał", type="primary"):
                new_interval = {
                    "name": new_int_name,
                    "type": new_int_type,
                    "interval": new_int_interval,
                    "current_value": 0,
                    "last_service": str(datetime.now().date()),
                    "enabled": True
                }
                machine['service_intervals'].append(new_interval)
                save_database(st.session_state.data)
                
                # Dodaj do historii
                st.session_state.history.insert(0, {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "machine": machine['name'],
                    "action": f"Dodano interwał: {new_int_name}",
                    "user": "System"
                })
                save_history(st.session_state.history)
                
                st.success("Dodano nowy interwał")
                st.rerun()
    
    with tab3:
        st.subheader("Zarządzanie plikami danych")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("#### 📊 Baza danych")
            if DATABASE_FILE.exists():
                file_size = DATABASE_FILE.stat().st_size
                file_time = datetime.fromtimestamp(DATABASE_FILE.stat().st_mtime)
                st.info(f"**Plik:** `{DATABASE_FILE}`\n\n**Rozmiar:** {file_size} bajtów\n\n**Ostatnia modyfikacja:** {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Podgląd zawartości
                with st.expander("👁️ Podgląd JSON"):
                    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                        st.code(f.read(), language='json')
                
                # Pobieranie pliku
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="📥 Pobierz database.json",
                        data=f.read(),
                        file_name=f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.warning("Plik database.json nie istnieje")
        
        with col_info2:
            st.markdown("#### 📜 Historia")
            if HISTORY_FILE.exists():
                file_size = HISTORY_FILE.stat().st_size
                file_time = datetime.fromtimestamp(HISTORY_FILE.stat().st_mtime)
                st.info(f"**Plik:** `{HISTORY_FILE}`\n\n**Rozmiar:** {file_size} bajtów\n\n**Ostatnia modyfikacja:** {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Pobieranie pliku
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="📥 Pobierz history.json",
                        data=f.read(),
                        file_name=f"history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.warning("Plik history.json nie istnieje")
        
        st.markdown("---")
        
        st.markdown("#### 📦 Kopie zapasowe")
        
        backups = sorted(BACKUP_DIR.glob("database_backup_*.json"), reverse=True)
        
        if backups:
            st.info(f"Znaleziono {len(backups)} kopii zapasowych")
            
            for backup in backups[:5]:  # Pokaż tylko 5 ostatnich
                backup_time = datetime.strptime(backup.stem.replace("database_backup_", ""), "%Y%m%d_%H%M%S")
                col_b1, col_b2, col_b3 = st.columns([3, 1, 1])
                
                col_b1.caption(f"📦 {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                with open(backup, 'r', encoding='utf-8') as f:
                    col_b2.download_button(
                        label="📥",
                        data=f.read(),
                        file_name=backup.name,
                        mime="application/json",
                        key=f"download_{backup.name}"
                    )
                
                if col_b3.button("♻️", key=f"restore_{backup.name}"):
                    # Przywróć backup
                    with open(backup, 'r', encoding='utf-8') as f:
                        restored_data = json.load(f)
                    
                    st.session_state.data = restored_data
                    save_database(restored_data)
                    
                    st.success(f"Przywrócono backup z {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.rerun()
        else:
            st.warning("Brak kopii zapasowych")
        
        st.markdown("---")
        
        # Niebezpieczne operacje
        with st.expander("⚠️ OPERACJE NIEBEZPIECZNE", expanded=False):
            st.error("**UWAGA!** Te operacje są nieodwracalne!")
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                if st.button("🗑️ Wyczyść całą bazę danych", type="secondary"):
                    create_backup()  # Najpierw backup
                    st.session_state.data = get_initial_data()
                    save_database(st.session_state.data)
                    st.warning("Baza danych wyczyszczona! Utworzono backup.")
                    st.rerun()
            
            with col_d2:
                if st.button("🗑️ Wyczyść historię", type="secondary"):
                    st.session_state.history = []
                    save_history([])
                    st.warning("Historia wyczyszczona!")
                    st.rerun()

# --- WIDOK 4: HISTORIA ---
elif view == "📊 Historia":
    st.title("HISTORIA OPERACJI")
    
    if st.session_state.history:
        st.markdown(f"Pokazano **{len(st.session_state.history)}** ostatnich operacji")
        
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Wyczyść historię"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Brak zapisanych operacji w historii")

# --- FOOTER ---
st.markdown("---")
st.caption("🔧 Warsztat Ziołolek - System Utrzymania Ruchu | Powered by Claude | © 2025")
