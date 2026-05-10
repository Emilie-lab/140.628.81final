import streamlit as st
import pandas as pd
import numpy as np
import datetime


st.title("Interactive COVID-19 Dashboard for Case Counts")

##(1) Data manipulation

#Imported the .csv files
confirmed_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/refs/heads/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
#Aggregated data for countries reporting at the province/state level into one row. 
confirmed_df_1 = confirmed_df.drop(columns=['Province/State', 'Lat', 'Long'])
confirmed_df_1 = confirmed_df_1.groupby('Country/Region').sum()
confirmed_df_1 = confirmed_df_1.reset_index()

death_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/refs/heads/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
death_df_1 = death_df.drop(columns=['Province/State', 'Lat', 'Long'])
death_df_1 = death_df_1.groupby('Country/Region').sum()
death_df_1 = death_df_1.reset_index()

recovered_df  = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/refs/heads/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
recovered_df_1 = recovered_df.drop(columns=['Province/State', 'Lat', 'Long'])
recovered_df_1 = recovered_df_1.groupby('Country/Region').sum()
recovered_df_1 = recovered_df_1.reset_index()


#create a list of countries
country_list = confirmed_df_1['Country/Region'].tolist()

##(2) Construct Interactive User Input Elements

#drop-down menu (st.selectbox) for the country selection
country = st.selectbox(
    "Select a country:",
    (country_list))

#button (st.radio) to choose between daily or cumulative data
datatype = st.radio(
    "Choose daily or cumulative case counts to view:",
    ("daily", "cumulative"))


#pop-up calendar (st.date_input) to select a date between 1/22/20 and 3/9/23
selected_date = st.date_input(
    "Select a date:",
    min_value=datetime.date(2020, 1, 22),
    max_value=datetime.date(2023, 3, 9))

#format the selected_date to be m/d/yy
#for the date format, I googled "transform data format in python st.date_input (2020/01/01) into m/d/yy format like 1/1/20" and followed the steps recommended by AI overview
formatted_selected_date = f"{selected_date.month}/{selected_date.day}/{selected_date.strftime('%y')}"


##(3) Connect the user input elements to the data

#pick the country user choose (confirmed)
country_data_c = confirmed_df_1[confirmed_df_1['Country/Region'] == country]
#check the cumulatice confirmed cases on the day user select
cumulative_confirmed = country_data_c.iloc[0][formatted_selected_date]

#pick the country user choose (death)
country_data_d = death_df_1[death_df_1['Country/Region'] == country]
#check the cumulatice deaths on the day user select
cumulative_deaths = country_data_d.iloc[0][formatted_selected_date]

#pick the country user choose (recover)
country_data_r = recovered_df_1[recovered_df_1['Country/Region'] == country]
#check the cumulatice recovered cases on the day user select
cumulative_recovered = country_data_r.iloc[0][formatted_selected_date]


#when user choose daily        
if datatype == "daily": ##cumulative (today) - cumulative (yesterday)
    previous = selected_date - datetime.timedelta(days=1) 
    formatted_previous = f"{previous.month}/{previous.day}/{previous.strftime('%y')}"
    if formatted_previous in country_data_c.columns: 
        previous_confirmed = country_data_c.iloc[0][formatted_previous] #confirmed
        answer_c = cumulative_confirmed - previous_confirmed 
        previous_deaths = country_data_d.iloc[0][formatted_previous] #deaths
        answer_d = cumulative_deaths - previous_deaths
        previous_recovered = country_data_r.iloc[0][formatted_previous] #recovered
        answer_r = cumulative_recovered - previous_recovered

    else: #if user select the 1st day of the data
        answer_c = cumulative_confirmed
        answer_d = cumulative_deaths 
        answer_r = cumulative_recovered

    #output message
    st.success(f"The {datatype} number of confirmed cases in **{country}** on **{selected_date}** was **{answer_c:,}**.")
    st.success(f"The {datatype} number of deaths in **{country}** on **{selected_date}** was **{answer_d:,}**.")
    st.success(f"The {datatype} number of recovered in **{country}** on **{selected_date}** was **{answer_r:,}**.")

#when user choose cumulative
else:
    answer_c = cumulative_confirmed
    answer_d = cumulative_deaths
    answer_r = cumulative_recovered

    #output message
    st.success(f"The {datatype} number of confirmed cases in **{country}** until **{selected_date}** was **{answer_c:,}**.")
    st.success(f"The {datatype} number of deaths in **{country}** until **{selected_date}** was **{answer_d:,}**.")
    st.success(f"The {datatype} number of recovered in **{country}** until **{selected_date}** was **{answer_r:,}**.")



##(4) Generate Data Visualization

#combine confirmed cases and deaths datasets, reshape the data into a long format
combined_dat = pd.concat([country_data_c, country_data_d])
combined_dat = combined_dat.drop(columns=['Country/Region']).T
combined_dat = combined_dat.reset_index()
combined_dat.columns = ['Date', 'Confirmed', 'Deaths']
combined_dat['Date'] = pd.to_datetime(combined_dat['Date'])



if datatype == "daily":
    #grab the number on day 1 in selected country
    day1_confirmed = combined_dat.iloc[0]['Confirmed']
    day1_deaths = combined_dat.iloc[0]['Deaths']

    ##Calculate the daily cases: cumulative (today) - cumulative (yesterday)
    combined_dat['Confirmed'] = combined_dat['Confirmed'].diff()
    combined_dat['Deaths'] = combined_dat['Deaths'].diff()

    #put the number on day 1 back
    combined_dat.iloc[0]['Confirmed'] = day1_confirmed
    combined_dat.iloc[0]['Deaths'] = day1_deaths

    combined_plot = combined_dat

else:
    combined_plot = combined_dat

#make the line chart
st.line_chart(combined_plot, x='Date', y=['Confirmed', 'Deaths'] )
