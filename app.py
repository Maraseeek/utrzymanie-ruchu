import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="UR System", page_icon="⚙️", layout="wide")

# --- STYLE CSS (INDUSTRIAL DARK THEME) ---
st.markdown("""
    <style>
    /* Ogólne tło aplikacji */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Stylizacja Metryk (Liczników) - Naprawa białego tła */
    div[data-testid="stMetric"] {
        background-color: #262730; /* Ciemny grafit */
        border: 1px solid #41444e; /* Stalowa ramka */
        padding: 15px;
        border-radius: 4px; /* Bardziej kanciaste - techniczne */
        color: #ffffff;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #a3a8b8 !important; /* Szary techniczny dla etykiet */
        font-size: 0.9rem;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Roboto Mono', monospace; /* Czcionka techniczna */
    }

    /* Karty maszyn na Dashboardzie */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1c1e24;
        border-radius: 4px;
        padding: 10px;
    }

    /* Pasek postępu - zmiana kolorów */
    .stProgress > div > div > div > div {
        background-color: #4a90e2; /* Stalowy niebieski */
    }

    /* Przyciski - styl roboczy */
    button {
        border-radius: 4px !important;
        font-weight: 600 !important;
    }
    
    /* Nagłówki tabel */
    th {
        background-color: #262730 !important;
        color: #a3a8b8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DANE STARTOWE ---
def get_initial_data():
    return pd.DataFrame([
        {
            "id": "M01", "name": "Wtryskarka A1", "cycles_current": 18, "cycles_limit": 20,
            "last_service_date": "2023-10-01", "service_interval_months": 6, 
            "last_fixed_service": "2023-06-01", "avg_daily_cycles": 2
        },
        {
            "id": "M02", "name": "Prasa Hydrauliczna", "cycles_current": 5, "cycles_limit": 50,
            "last_service_date": "2023-10-15", "service_interval_months": 3, 
            "last_fixed_service": "2023-11-01", "avg_daily_cycles": 5
        },
        {
            "id": "M03", "name": "Pakowarka Z", "cycles_current": 195, "cycles_limit": 200,
            "last_service_date": "2023-09-20", "service_interval_months": 12, 
            "last_fixed_service": "2023-01-01", "avg_daily_cycles": 10
        }
    ])

if 'df' not in st.session_state:
    st.session_state.df = get_initial_data()

# Funkcje pomocnicze
def str_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    return source_date.replace(year=year, month=month)

# --- PANEL BOCZNY (MENU) ---
st.sidebar.header("SYSTEM UTRZYMANIA RUCHU")
st.sidebar.markdown("---")
view = st.sidebar.radio("Nawigacja:", ["Panel Główny", "Karta Maszyny", "Baza Danych"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption(f"Data systemu: {datetime.now().strftime('%d-%m-%Y')}")

# --- WIDOK 1: PANEL GŁÓWNY ---
if view == "Panel Główny":
    st.subheader("Podgląd Statusu Maszyn")
    
    # Logika statusów
    alerts_critical = []
    alerts_warning = []
    
    for idx, row in st.session_state.df.iterrows():
        # Cykle
        cycles_left = row['cycles_limit'] - row['cycles_current']
        cycle_status = 2 if cycles_left <= 0 else 1 if cycles_left <= (row['cycles_limit']*0.2) else 0
        
        # Czas
        last_fixed = str_to_date(row['last_fixed_service'])
        next_fixed = add_months(last_fixed, row['service_interval_months'])
        days_to_fixed = (next_fixed - datetime.now().date()).days
        time_status = 2 if days_to_fixed <= 7 else 1 if days_to_fixed <= 30 else 0
        
        if cycle_status == 2 or time_status == 2:
            alerts_critical.append(f"{row['name']} - WYMAGANA INTERWENCJA")
        elif cycle_status == 1 or time_status == 1:
            alerts_warning.append(f"{row['name']} - Zbliża się termin")

    # Sekcja powiadomień
    if alerts_critical:
        st.error(f"PILNE ({len(alerts_critical)}): " + ", ".join(alerts_critical))
    if alerts_warning:
        st.warning(f"OSTRZEŻENIA ({len(alerts_warning)}): " + ", ".join(alerts_warning))
    
    if not alerts_critical and not alerts_warning:
        st.success("Status floty: NORMA. Brak pilnych zleceń.")

    st.markdown("---")

    # Lista kafelkowa
    cols = st.columns(3)
    for idx, row in st.session_state.df.iterrows():
        col = cols[idx % 3]
        with col:
            with st.container(border=True):
                # Nagłówek kafelka
                st.markdown(f"#### {row['name']}")
                
                # Pasek postępu
                progress = min(row['cycles_current'] / row['cycles_limit'], 1.0)
                st.progress(progress)
                
                # Dane liczbowe
                c1, c2 = st.columns(2)
                c1.caption("Licznik cykli")
                c1.write(f"**{row['cycles_current']}** / {row['cycles_limit']}")
                
                # Obliczanie daty przeglądu
                last_fixed = str_to_date(row['last_fixed_service'])
                next_fixed = add_months(last_fixed, row['service_interval_months'])
                days_left = (next_fixed - datetime.now().date()).days
                
                c2.caption("Przegląd okresowy")
                color = "red" if days_left < 7 else "white"
                c2.markdown(f":{color}[{next_fixed}]")

                st.markdown("---")
                # Przycisk szybkiej akcji
                if st.button("Potwierdź Serwis", key=f"quick_serv_{idx}", use_container_width=True):
                    st.session_state.df.at[idx, 'cycles_current'] = 0
                    st.session_state.df.at[idx, 'last_service_date'] = str(datetime.now().date())
                    st.toast(f"Zarejestrowano serwis: {row['name']}")
                    st.rerun()

# --- WIDOK 2: KARTA MASZYNY ---
elif view == "Karta Maszyny":
    st.subheader("Operacje i Planowanie")
    
    col_select, col_empty = st.columns([1, 2])
    with col_select:
        selected_machine_name = st.selectbox("Wybierz urządzenie z listy:", st.session_state.df['name'])
    
    # Pobranie danych
    machine_row = st.session_state.df[st.session_state.df['name'] == selected_machine_name].iloc[0]
    idx = st.session_state.df[st.session_state.df['name'] == selected_machine_name].index[0]
    
    st.markdown("---")

    # Główne metryki - styl techniczny
    m1, m2, m3 = st.columns(3)
    m1.metric("Licznik Bieżący", f"{machine_row['cycles_current']}", delta=f"Limit: {machine_row['cycles_limit']}", delta_color="inverse")
    
    # Obliczenia prognozy
    days_to_service = "-"
    if machine_row['avg_daily_cycles'] > 0:
        cycles_left = machine_row['cycles_limit'] - machine_row['cycles_current']
        days_left = int(cycles_left / machine_row['avg_daily_cycles'])
        future_date = datetime.now().date() + timedelta(days=days_left)
        days_to_service = f"{days_left} dni"
    
    m2.metric("Estymacja Serwisu (Cykle)", days_to_service, f"Śr. dzienna: {machine_row['avg_daily_cycles']}")
    
    next_fixed = add_months(str_to_date(machine_row['last_fixed_service']), machine_row['service_interval_months'])
    m3.metric("Termin Przeglądu Okresowego", f"{next_fixed}")

    st.markdown("---")
    
    # Panel Operacyjny
    c_left, c_right = st.columns([1, 2])
    
    with c_left:
        st.markdown("#### Rejestracja Pracy")
        with st.container(border=True):
            cycles_to_add = st.number_input("Wprowadź liczbę wykonanych cykli:", step=1)
            if st.button("Zatwierdź wpis", type="primary", use_container_width=True):
                new_val = max(0, machine_row['cycles_current'] + cycles_to_add)
                st.session_state.df.at[idx, 'cycles_current'] = new_val
                st.toast("Zaktualizowano stan licznika")
                st.rerun()
        
        st.markdown("#### Raportowanie Serwisu")
        with st.container(border=True):
            if st.button("🛠️ Reset Licznika (Serwis Cykliczny)", use_container_width=True):
                st.session_state.df.at[idx, 'cycles_current'] = 0
                st.session_state.df.at[idx, 'last_service_date'] = str(datetime.now().date())
                st.toast("Zresetowano licznik cykli")
                st.rerun()
            
            st.write("") # odstęp
            
            if st.button("📅 Potwierdzenie Przeglądu (Okresowy)", use_container_width=True):
                st.session_state.df.at[idx, 'last_fixed_service'] = str(datetime.now().date())
                st.toast("Zaktualizowano datę przeglądu")
                st.rerun()

    with c_right:
        st.markdown("#### Prognoza Obciążenia (7 dni)")
        # Tabela prognoz
        forecast_data = []
        current_c = machine_row['cycles_current']
        avg = machine_row['avg_daily_cycles']
        limit = machine_row['cycles_limit']
        
        for i in range(1, 8):
            day = datetime.now().date() + timedelta(days=i)
            predicted_cycles = current_c + (avg * i)
            
            status_text = "OK"
            status_color = "" # default text color
            
            if predicted_cycles >= limit:
                status_text = "WYMAGANY SERWIS"
            elif predicted_cycles >= limit * 0.8:
                status_text = "Ostrzeżenie"
            
            # Kolizja z datą przeglądu okresowego
            if day == next_fixed:
                status_text = "PRZEGLĄD OKRESOWY"

            forecast_data.append({
                "Data": day.strftime("%d.%m.%Y (%A)"),
                "Symulowany stan": int(predicted_cycles),
                "Limit": limit,
                "Status": status_text
            })
            
        df_forecast = pd.DataFrame(forecast_data)
        
        # Kolorowanie tabeli
        def highlight_status(val):
            color = ''
            if 'SERWIS' in str(val) or 'PRZEGLĄD' in str(val):
                color = 'background-color: #3d1818; color: #ff4b4b'
            elif 'Ostrzeżenie' in str(val):
                color = 'color: #ffa421'
            return color

        st.dataframe(
            df_forecast.style.map(highlight_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )

# --- WIDOK 3: BAZA DANYCH ---
elif view == "Baza Danych":
    st.subheader("Edycja Parametrów Maszyn")
    st.info("Zmiany w tej tabeli wpływają bezpośrednio na funkcjonowanie systemu.")
    
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Zapisz zmiany", type="primary", use_container_width=True):
            st.session_state.df = edited_df
            st.success("Baza danych zaktualizowana.")
