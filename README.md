# FEMS Dispatch Staffing Dashboard

This Streamlit app allows fire and aviation managers to configure and visualize FEMS NFDRS Outputs/Percentiles, Decision Classes (Staffing, Dispatch, Adjective, SFDI, Severe Fire Danger Index and R5 PAL using live FEMS index data. This is visualization work off of the work Kevin Osborne created.

## Features

- User input form to define SIG, fuel model, RAWS count, index types, and breakpoints
- Live data retrieval from the FEMS sample endpoint
- Color-coded graph of observed and forecasted fire danger indices
- Summary table of user input
- Download outputs as:
  - 📄 PDF (graph)
  - 🖼️ PNG (graph)
  - 📊 CSV (data)

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/your-username/fems-dashboard.git
cd fems-dashboard
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally:

```bash
streamlit run app.py
```

## Deployment

This app is ready to deploy on [Streamlit Cloud](https://streamlit.io/cloud):

- Connect your GitHub repo
- Select `app.py` as the main file
- Streamlit Cloud will auto-install from `requirements.txt`

## Credits

Developed by fire operations analysts and powered by live data from [FEMS](https://fems.fs2c.usda.gov).
