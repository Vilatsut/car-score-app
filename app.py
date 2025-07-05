import streamlit as st
import pandas as pd

def get_model(df, make, model, year):
    row = df[(df['Merkki'] == make) & (df['Malli'] == model) & (df['Käyttöönottovuosi'] == year)]
    if not row.empty:
        return row['Hylkäys-%'].values[0], row['Katsastusten\nlukumäärä'].values[0], row['Ajettujen\nkilometrien\nmediaani'].values[0]
    else:
        return None, None, None

def get_make(df, make, year):
    row = df[(df['Merkki'] == make) & (df['Malli'] == 'Mallit yhteensä') & (df['Käyttöönottovuosi'] == year)]
    if not row.empty:
        return row['Hylkäys-%'].values[0], row['Katsastusten\nlukumäärä'].values[0], row['Ajettujen\nkilometrien\nmediaani'].values[0]
    else:
        return None, None, None

def get_all(df, year):
    row = df[(df['Merkki'] == 'Merkit\nyhteensä') & (df['Käyttöönottovuosi'] == year)]
    if not row.empty:
        return row['Hylkäys-%'].values[0], row['Ajettujen\nkilometrien\nmediaani'].values[0]
    else:
        return None, None


def calculate_score(model_fail, make_avg_fail, all_avg_fail,
                    median_km_model, median_km_make, median_km_all,
                    input_km,
                    model_inspections, make_inspections):

    def relative_improvement(base, compare):
        if base == 0:
            return 1.0 if compare == 0 else 0.0
        diff = (base - compare) / base  # positive if compare is better (lower failure)
        return max(0, min(1, diff))
        
    model_vs_make = relative_improvement(make_avg_fail, model_fail)
    make_vs_all = relative_improvement(all_avg_fail, make_avg_fail)

    # km scores
    def km_score(input_km, median_km):
        if input_km <= median_km:
            return 1.0  # best score if km is at or below median
        else:
            # Penalize proportionally if km is higher than median
            diff_ratio = (input_km - median_km) / median_km
            score = max(0, 1 - diff_ratio)
            return score

    km_score_model = km_score(input_km, median_km_model)
    km_score_make = km_score(input_km, median_km_make)
    km_score_all = km_score(input_km, median_km_all)

    combined_km_score = 0.5 * km_score_model + 0.3 * km_score_make + 0.2 * km_score_all

    # inspection weight
    inspection_weight = min(1.0, model_inspections / 500)
    model_vs_make *= inspection_weight

    # combine all
    combined = 0.45 * model_vs_make + 0.25 * make_vs_all + 0.2 * combined_km_score + 0.1 * inspection_weight

    return round(combined * 9 + 1, 1)

def score_car(make, model, year, input_km, df):

    model_fail, model_inspections, model_median_km = get_model(df, make, model, year)
    make_avg_fail, make_inspections, make_median_km = get_make(df, make, year)
    all_avg_fail, all_median_km = get_all(df, year)

    if all(x is not None for x in [ model_fail, make_avg_fail, all_avg_fail, 
                                    model_median_km, make_median_km, all_median_km,
                                    input_km,
                                    model_inspections, make_inspections]):
        score = calculate_score(model_fail, make_avg_fail, all_avg_fail,
                                model_median_km, make_median_km, all_median_km, 
                                input_km,
                                model_inspections, make_inspections)
        return score
    else:
        return None

st.title("Car Inspection Score Tool")
st.header("Select Your Car Details")
st.subheader("Then click \"Score this car\" to calculate the score based on Traficom 2024 inspection data for that year.")

@st.cache_data
def load_data():
    df = pd.read_excel("cars_data_2024.xlsx") 
    df = df.iloc[5:]
    df.columns = df.iloc[0]
    df = df[1:]
    return df
df = load_data()

makes = sorted(df['Merkki'].dropna().unique())
models = df['Malli'].dropna().unique()
years = sorted(df['Käyttöönottovuosi'].dropna().unique())

make = st.selectbox("Select Car Make", makes)
filtered_models = df[df['Merkki'] == make]['Malli'].dropna().unique()
model = st.selectbox("Select Car Model", filtered_models)

filtered_years = df[(df['Merkki'] == make) & (df['Malli'] == model)]['Käyttöönottovuosi'].dropna().unique()
year = st.selectbox("Select Year", sorted(filtered_years, reverse=True))

km = st.number_input("Driven Kilometers", min_value=0)

if "score_history" not in st.session_state:
    st.session_state.score_history = []

# --- Scoring ---
if st.button("Score This Car"):
    score = score_car(make, model, year, km, df)
    st.write(f"Score: {score}/10")

    st.session_state.score_history.insert(0, {
        "Make": make,
        "Model": model,
        "Year": year,
        "Kilometers": km,
        "Score": score,
    })

st.markdown("## Score History")
for record in st.session_state.score_history:
    st.write(f"{record['Make']} — {record['Model']} — {record['Year']} — "
             f"{record['Kilometers']} km — Score: {record['Score']}/10")