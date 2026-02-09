import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="UR Manager", page_icon="🛠️", layout="wide")

# --- STYLE CSS (Dla ładniejszego wyglądu) ---
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .status-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
    }
    .critical { border-left: 5px solid #ff4b4b; background-color: #fff5f5; }
    .warning { border-left: 5px solid #ffa421; background-color: #fffae5; }
    .ok { border-left: 5px solid #21c354; background-color: #f0fff4; }
    </style>
    """, unsafe_allow_html=True)

# --- DANE STARTOWE (JEŚLI BRAK PLIKU) ---
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

# --- OBSŁUGA DANYCH (SESSION STATE - PAMIĘĆ TYMCZASOWA) ---
# Uwaga: W wersji darmowej chmurowej dane resetują się po restarcie aplikacji. 
# Do trwałego zapisu należałoby podpiąć Google Sheets, tutaj wersja uproszczona na pliku CSV/Pamięci.

if 'df' not in st.session_state:
    st.session_state.df = get_initial_data()

# Funkcje pomocnicze dat
def str_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    return source_date.replace(year=year, month=month)

# --- PANEL GŁÓWNY (SIDEBAR) ---
st.sidebar.title("🔧 Menu Główne")
view = st.sidebar.radio("Wybierz widok:", ["Dashboard", "Szczegóły Maszyny", "Ustawienia"])

# --- WIDOK 1: DASHBOARD ---
if view == "Dashboard":
    st.title("Centrum Dowodzenia UR")
    
    # 1. Analiza stanu maszyn
    alerts = []
    
    for idx, row in st.session_state.df.iterrows():
        # Sprawdzanie cykli
        cycles_left = row['cycles_limit'] - row['cycles_current']
        cycle_status = "CRITICAL" if cycles_left <= 0 else "WARNING" if cycles_left <= (row['cycles_limit']*0.2) else "OK"
        
        # Sprawdzanie daty przeglądu okresowego
        last_fixed = str_to_date(row['last_fixed_service'])
        next_fixed = add_months(last_fixed, row['service_interval_months'])
        days_to_fixed = (next_fixed - datetime.now().date()).days
        
        time_status = "CRITICAL" if days_to_fixed <= 7 else "WARNING" if days_to_fixed <= 30 else "OK"
        
        # Generowanie alertów
        if cycle_status == "CRITICAL" or time_status == "CRITICAL":
            alerts.append({"name": row['name'], "reason": "WYMAGANY SERWIS!", "type": "critical"})
        elif cycle_status == "WARNING" or time_status == "WARNING":
            alerts.append({"name": row['name'], "reason": "Zbliża się termin", "type": "warning"})

    # 2. Wyświetlanie Alertów
    if alerts:
        st.subheader("🚨 Alerty na dziś")
        for alert in alerts:
            color = "red" if alert['type'] == "critical" else "orange"
            st.warning(f"**{alert['name']}**: {alert['reason']}", icon="⚠️")
    else:
        st.success("Wszystkie systemy sprawne. Brak pilnych serwisów.")

    st.divider()

    # 3. Kafelki Maszyn
    st.subheader("Stan Floty")
    cols = st.columns(3)
    
    for idx, row in st.session_state.df.iterrows():
        col = cols[idx % 3]
        with col:
            # Obliczenia do paska postępu
            progress = min(row['cycles_current'] / row['cycles_limit'], 1.0)
            status_color = "green"
            if progress == 1.0: status_color = "red"
            elif progress > 0.8: status_color = "orange"
            
            with st.container(border=True):
                st.markdown(f"### {row['name']}")
                st.write(f"Cykle: **:{status_color}[{row['cycles_current']} / {row['cycles_limit']}]**")
                st.progress(progress)
                
                # Info o przeglądzie czasowym
                last_fixed = str_to_date(row['last_fixed_service'])
                next_fixed = add_months(last_fixed, row['service_interval_months'])
                st.caption(f"📅 Przegląd okresowy: {next_fixed}")

                # Szybki przycisk serwisu
                if st.button("✅ Zgłoś Serwis", key=f"btn_serv_{idx}"):
                    st.session_state.df.at[idx, 'cycles_current'] = 0
                    st.session_state.df.at[idx, 'last_service_date'] = str(datetime.now().date())
                    st.toast(f"Wykonano serwis dla {row['name']}!")
                    st.rerun()

# --- WIDOK 2: SZCZEGÓŁY MASZYNY I KALENDARZ ---
elif view == "Szczegóły Maszyny":
    st.title("Szczegóły i Planowanie")
    
    selected_machine_name = st.selectbox("Wybierz maszynę:", st.session_state.df['name'])
    machine_row = st.session_state.df[st.session_state.df['name'] == selected_machine_name].iloc[0]
    idx = st.session_state.df[st.session_state.df['name'] == selected_machine_name].index[0]
    
    # Metryki
    c1, c2, c3 = st.columns(3)
    c1.metric("Aktualne Cykle", f"{machine_row['cycles_current']}", f"Limit: {machine_row['cycles_limit']}")
    
    days_to_service = "N/A"
    if machine_row['avg_daily_cycles'] > 0:
        cycles_left = machine_row['cycles_limit'] - machine_row['cycles_current']
        days_left = int(cycles_left / machine_row['avg_daily_cycles'])
        future_date = datetime.now().date() + timedelta(days=days_left)
        days_to_service = f"za {days_left} dni ({future_date})"
    
    c2.metric("Prognoza Serwisu (Cykle)", days_to_service)
    
    next_fixed = add_months(str_to_date(machine_row['last_fixed_service']), machine_row['service_interval_months'])
    c3.metric("Następny Przegląd Okresowy", f"{next_fixed}")

    st.divider()
    
    # --- PANEL STEROWANIA ---
    st.subheader("🎮 Panel Sterowania")
    
    col_input, col_cal = st.columns([1, 2])
    
    with col_input:
        st.info("Dodaj wykonane cykle")
        cycles_to_add = st.number_input("Liczba cykli", min_value=-100, max_value=1000, value=0, step=1)
        if st.button("Zatwierdź zmianę"):
            new_val = max(0, machine_row['cycles_current'] + cycles_to_add)
            st.session_state.df.at[idx, 'cycles_current'] = new_val
            st.success("Zaktualizowano stan licznika!")
            st.rerun()
            
        st.warning("Akcje Serwisowe")
        if st.button("🛠️ Wykonano Serwis CYKLICZNY"):
            st.session_state.df.at[idx, 'cycles_current'] = 0
            st.session_state.df.at[idx, 'last_service_date'] = str(datetime.now().date())
            st.success("Licznik wyzerowany!")
            st.rerun()
            
        if st.button("📅 Wykonano Przegląd OKRESOWY"):
            st.session_state.df.at[idx, 'last_fixed_service'] = str(datetime.now().date())
            st.success("Data przeglądu zaktualizowana!")
            st.rerun()

    with col_cal:
        st.subheader("📅 Kalendarz Prognoz (Najbliższe 7 dni)")
        # Prosta symulacja kalendarza
        forecast_data = []
        current_c = machine_row['cycles_current']
        avg = machine_row['avg_daily_cycles']
        limit = machine_row['cycles_limit']
        
        for i in range(7):
            day = datetime.now().date() + timedelta(days=i)
            # Symulacja przyrostu
            predicted_cycles = current_c + (avg * i)
            status = "🟢 OK"
            if predicted_cycles >= limit:
                status = "🔴 SERWIS!"
            elif predicted_cycles >= limit * 0.8:
                status = "🟡 Blisko"
            
            # Czy to data przeglądu okresowego?
            fixed_note = ""
            if day == next_fixed:
                fixed_note = "❗ PRZEGLĄD OKRESOWY"
                status = "🔴 SERWIS!"

            forecast_data.append({
                "Dzień": day.strftime("%A (%d.%m)"),
                "Przewidywane Cykle": int(predicted_cycles),
                "Status": status,
                "Uwagi": fixed_note
            })
            
        st.dataframe(pd.DataFrame(forecast_data), use_container_width=True, hide_index=True)

# --- WIDOK 3: USTAWIENIA (Podgląd bazy) ---
elif view == "Ustawienia":
    st.title("Baza Danych Maszyn")
    st.write("Tutaj możesz edytować parametry maszyn (np. limity).")
    
    edited_df = st.data_editor(st.session_state.df)
    
    if st.button("Zapisz zmiany w bazie"):
        st.session_state.df = edited_df
        st.success("Zapisano!")
