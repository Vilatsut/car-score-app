# Car Inspection Score Tool

This app calculates a quality score for a car based on make, model, year, and kilometers driven.  
It uses inspection failure rates and driving data from an Excel dataset. 

---

## How to use

1. Select the car make, model, and year from dropdowns.  
2. Enter the kilometers driven.  
3. Click the button to get a score between 1 (poor) and 10 (excellent).

---

## Live Demo

You can try the app online here:  
[https://car-score.streamlit.app/](https://car-score.streamlit.app/)

---

## Setup

To run locally:

1. Clone this repo.  
2. Install dependencies:
   `pip install streamlit pandas openpyxl`
3. Run the app:
   `streamlit run app.py`
   
---

## Notes

- Make sure your Excel dataset file is in the correct location. You can download the preferred one from [https://tieto.traficom.fi/fi/tilastot/katsastustilasto](https://tieto.traficom.fi/fi/tilastot/katsastustilasto)
- 
---

Feel free to contribute or report issues.
