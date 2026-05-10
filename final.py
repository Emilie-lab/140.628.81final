import streamlit as st
import pandas as pd
import numpy as np
import datetime


st.title("Interactive COVID-19 Dashboard for Case Counts")

confirmed_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/refs/heads/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
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

##select a country (selectbox)
country = st.selectbox(
    'Select a country:',
    (country_list)
)

##select a data type (radio)
datatype = st.radio(
    "Choose daily or cumulative case counts to view:",
    ("daily", "cumulative")
)


##select a data (date_input)
selected_date = st.date_input(
    "Select a date:",
    min_value=datetime.date(2020, 1, 22),
    max_value=datetime.date(2023, 3, 9))

#format the selected_date to be m/d/yy
#for the date format, I googled "transform data format in python st.date_input (2020/01/01) into m/d/yy format like 1/1/20" and followed the steps recommended by AI overview
formatted_selected_date = f"{selected_date.month}/{selected_date.day}/{selected_date.strftime('%y')}"


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


#if user choose cumulative
if datatype == "cumulative": 
    answer_c = cumulative_confirmed
    answer_d = cumulative_deaths
    answer_r = cumulative_recovered

    st.success(f"The {datatype} number of confirmed cases in **{country}** until **{selected_date}** was **{answer_c:,}**.")
    st.success(f"The {datatype} number of deaths in **{country}** until **{selected_date}** was **{answer_d:,}**.")
    st.success(f"The {datatype} number of recovered in **{country}** until **{selected_date}** was **{answer_r:,}**.")



#if user choose daily        
elif datatype == "daily": ##cumulative (today) - cumulative (yesterday)
    previous = selected_date - datetime.timedelta(days=1) 
    formatted_previous = f"{previous.month}/{previous.day}/{previous.strftime('%y')}"
    if formatted_previous in country_data_c.columns:
        previous_deaths = country_data_d.iloc[0][formatted_previous]
        answer_d = cumulative_deaths - previous_deaths
        previous_confirmed = country_data_c.iloc[0][formatted_previous]
        answer_c = cumulative_confirmed - previous_confirmed
        previous_recovered = country_data_r.iloc[0][formatted_previous]
        answer_r = cumulative_recovered - previous_recovered

    else: #if user select the 1st day of the data
        answer_d = cumulative_deaths 
        answer_c = cumulative_confirmed
        answer_r = cumulative_recovered


    st.success(f"The {datatype} number of confirmed cases in **{country}** on **{selected_date}** was **{answer_c:,}**.")
    st.success(f"The {datatype} number of deaths in **{country}** on **{selected_date}** was **{answer_d:,}**.")
    st.success(f"The {datatype} number of recovered in **{country}** on **{selected_date}** was **{answer_r:,}**.")




##
plot_dat_c = country_data_c.drop(columns=['Country/Region']).T
plot_dat_c = plot_dat_c.reset_index()
plot_dat_c.columns = ['Date', 'Confirmed']
plot_dat_c['Date'] = pd.to_datetime(plot_dat_c['Date'])


plot_dat_d = country_data_d.drop(columns=['Country/Region']).T
plot_dat_d = plot_dat_d.reset_index()
plot_dat_d.columns = ['Date', 'Deaths']
plot_dat_d['Date'] = pd.to_datetime(plot_dat_d['Date'])


#plot_dat_r = country_data_r.drop(columns=['Country/Region']).T
#plot_dat_r = plot_dat_r.reset_index()
#plot_dat_r.columns = ['Date', 'Recovered']
#plot_dat_r['Date'] = pd.to_datetime(plot_dat_r['Date'])


combined_plot = pd.merge(plot_dat_c, plot_dat_d, on='Date')
#combined_plot = pd.merge(combined_plot, plot_dat_r, on='Date')

if datatype == "daily":
    combined_plot['Confirmed'] = combined_plot['Confirmed'].diff().fillna(0)
    combined_plot['Deaths'] = combined_plot['Deaths'].diff().fillna(0)

    combined_plot = combined_plot
else:
    combined_plot = combined_plot

st.line_chart(combined_plot, x='Date', y=['Confirmed', 'Deaths'] )
