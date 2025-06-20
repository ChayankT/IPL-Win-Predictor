import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt

# Load model safely
try:
    pipe = pickle.load(open('pipe.pkl', 'rb'))
except FileNotFoundError:
    st.error("Model file not found. Please ensure 'pipe.pkl' is in the same directory.")
    st.stop()

# Team and city options
teams = ['Sunrisers Hyderabad',
         'Mumbai Indians',
         'Royal Challengers Bangalore',
         'Kolkata Knight Riders',
         'Kings XI Punjab',
         'Chennai Super Kings',
         'Rajasthan Royals',
         'Delhi Capitals']

cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
          'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
          'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
          'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
          'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
          'Sharjah', 'Mohali', 'Bengaluru']
overs=0
balls_left = 120 - (overs * 6)

st.title('🏏 IPL Win Predictor')

col1, col2 = st.columns(2)

with col1:
    batting_team = st.selectbox('Select the Batting Team', sorted(teams))
with col2:
    filtered_bowling_teams = [team for team in sorted(teams) if team != batting_team]
    bowling_team = st.selectbox('Select the Bowling Team', filtered_bowling_teams)

selected_city = st.selectbox('Select Host City', sorted(cities))

target = st.number_input('Target Score', min_value=1, max_value=300)

col3, col4, col5 = st.columns(3)

with col3:
    score = st.number_input('Current Score', min_value=0, max_value=target)
with col4:
    overs = st.number_input('Overs Completed', min_value=0.0, max_value=20.0, step=0.1)
with col5:
    wickets = st.number_input('Wickets Fallen', min_value=0, max_value=10)

input_valid = True
error_messages = []

if batting_team == bowling_team:
    input_valid = False
    error_messages.append("Batting and Bowling teams cannot be the same.")

if overs == 0 and score == 0:
    input_valid = False
    error_messages.append("Overs and score both cannot be zero. Please enter valid match progress.")

if score > target:
    input_valid = False
    error_messages.append("Score cannot exceed the target.")

if balls_left <= 0:
    input_valid = False
    error_messages.append("Overs cannot exceed 20. Match should have balls left.")

# Prediction button
if st.button('Predict Probability'):
    if not input_valid:
        for msg in error_messages:
            st.warning(msg)
        st.stop()
    runs_left = target - score
    balls_left = 120 - (overs * 6)
    wickets_left = 10 - wickets

    # Avoid division by zero
    crr = score / overs if overs > 0 else 0
    rrr = (runs_left * 6) / balls_left if balls_left > 0 else 0

    input_df = pd.DataFrame({
        'batting_team': [batting_team],
        'bowling_team': [bowling_team],
        'city': [selected_city],
        'runs_left': [runs_left],
        'balls_left': [balls_left],
        'wickets': [wickets_left],
        'total_runs_x': [target],
        'crr': [crr],
        'rrr': [rrr]
    })

    # Predict
    result = pipe.predict_proba(input_df)
    loss = result[0][0]
    win = result[0][1]

    # Output
    st.markdown("### 🧠 Win Prediction")
    st.success(f"📣 {batting_team} - **{round(win * 100)}%** chance to win")
    st.error(f"🎯 {bowling_team} - **{round(loss * 100)}%** chance to win")
    st.progress(int(win * 100))

    # Pie chart
    fig, ax = plt.subplots()
    ax.pie([win, loss],
           labels=[batting_team, bowling_team],
           colors=['#00b894', '#d63031'],
           autopct='%1.1f%%',
           startangle=90,
           wedgeprops={'edgecolor': 'white'})
    ax.axis('equal')  # Equal aspect ratio makes the pie chart a circle

    st.pyplot(fig)
