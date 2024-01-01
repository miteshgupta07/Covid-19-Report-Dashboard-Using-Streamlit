import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mplcyberpunk
from PIL import Image

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

img = Image.open("E:\Data Science\Project\Covid-19 Report\Image\img-1.jpeg")
st.image(img)
st.title('Covid-19 Report Dashboard for Berlin City')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

link = '[*©Developed by Mitesh Gupta*](https://www.linkedin.com/in/mitesh-gupta/)'
st.sidebar.markdown(link, unsafe_allow_html=True)
st.write('---')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

st.write("""
         
This dashboard provides daily updates of the following\n
• 7-day-incidence (number of cases per 100,000 inhabitants)\n
• The rolling 7-day-average number of new cases\n
• The raw number of new reported Covid-19 cases.\n 
         
You may select the cities to view and compare.

The data are the latest official figures provided by the Berlin government, sourced from [berlin.de](https://www.berlin.de/lageso/gesundheit/infektionsepidemiologie-infektionsschutz/corona/tabelle-bezirke-gesamtuebersicht/).

If you are viewing this on a mobile device, tap  "**>**"  in the top left corner to select City and timescale.
""")
st.write("---")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Getting Data
data=pd.read_csv("E:\Data Science\Project\Covid-19 Report\Dataset\Covid Case.csv",sep=';')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Adding a Total column for all Berlin
data['All Berlin'] = data.drop('Date',axis=1).sum(axis=1)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Convert 'Date' Column to datetime pandas format
data['Date'] = pd.to_datetime(data['Date'])

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Defining a list with the cities of Berlin, ensuring consistency of ordering and spelling, and a list with the corresponding populations
cities = ['All Berlin','Lichtenberg', 'Mitte', 'Charlottenburg-Wilmersdorf', 'Friedrichshain-Kreuzberg', 'Neukoelln', 'Tempelhof-Schoeneberg', 'Pankow', 'Reinickendorf', 'Steglitz-Zehlendorf', 'Spandau', 'Marzahn-Hellersdorf', 'Treptow-Koepenick']
populations = [37.54418, 2.91452, 3.84172, 3.42332, 2.89762, 3.29691, 3.51644, 4.07765, 2.65225, 3.08697, 2.43977, 2.68548, 2.71153]

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Creating a pandas DataFrame with the populations of the cities
pop_dict = {'City': cities,'Population': populations}
pop_data = pd.DataFrame(data=pop_dict)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Sidebar for User Input
# Creating a multi-select box to allow multiple cities to be compared
selected_cities = st.sidebar.multiselect('Select Cities:',cities,default=['All Berlin'])
if selected_cities == []:
    selected_cities = ['All Berlin']

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Creating a slider on the sidebar to adjust dates
no_of_days = st.sidebar.slider('Number of days to display:', 0, 365,365)
st.sidebar.write('---')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Creating a Checkbox in the sidebar to turn off the mplcyberpunk style
st.sidebar.write('Chart Presentation Settings:')
glow_effect_checkbox = st.sidebar.checkbox('Glow Effects')
gradient_fill_checkbox=st.sidebar.checkbox('Gradient Fill')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Manipulating Data based on User Input
# This is the simple metric of new reported cases on each day
new_cases = data['Date']

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Adding a new column for each City selected by the user
for i in selected_cities:
    new_cases = pd.concat([new_cases, data[i]], axis = 1)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Adding a  7-day-average column for the selected City to the existing dataframe ( moving average or rolling mean is simply a way to smooth out data fluctuations to help you distinguish between typical “noise” in data and the actual trend direction)
data_to_plot = data['Date']

for i in selected_cities:
    seven_day_average = data.rolling(window=7)[i].mean()
    new_col_name = ('7 Day Average for %s' % i)
    old_cases = data
    old_cases[new_col_name] = seven_day_average
    data_to_plot = pd.concat([data_to_plot, old_cases[new_col_name]], axis = 1)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Creating a 7 day rolling sum of cases per City
for i in selected_cities:
    new_cases['Seven Day Sum for %s' % i] = new_cases[i].rolling(7).sum()

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Getting the population for the selected cities, using that to calculate the 7-day-incidence
for i in selected_cities:
    city_pop = pop_data.loc[pop_data['City'] == i]
    get_pop = float(city_pop['Population'])
    new_cases['Seven Day Incidence for %s' % i] = new_cases['Seven Day Sum for %s' % i] / get_pop

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Creating a DataFrame containing only the 7-day-incidence data
incidence = new_cases['Date']

for i in selected_cities:
    incidence = pd.concat([incidence, new_cases['Seven Day Incidence for %s' % i]], axis = 1)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Output - Producing the plots
# Selecting the style for the plots
if glow_effect_checkbox:
    plt.style.use('cyberpunk')
else:
    plt.style.use('ggplot')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Plotting the 7 day incidence
st.write('## 7 Day Incidence')
st.write('This chart shows the 7 day incidence of cases per 100,000 inhabitants for the selected City(s)')
incidence_data = incidence.iloc[-no_of_days:,:]

fig, ax = plt.subplots()
for i in selected_cities:
    plt.plot(incidence_data['Date'], incidence_data['Seven Day Incidence for %s' % i])

ax.legend(selected_cities)
plt.xticks(rotation=40,
    horizontalalignment='right',
    fontweight='normal',
    fontsize='small',
    color= '1')
plt.yticks(color = '1')
plt.ylim((0))
plt.title('Seven Day Incidence - Last ' + str(no_of_days) + ' Days', color = '1')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#mplcyberpunk glow effects if checkbox selected

legend = plt.legend(selected_cities,loc='upper right')
if (glow_effect_checkbox and gradient_fill_checkbox):
    mplcyberpunk.add_glow_effects()
    mplcyberpunk.add_gradient_fill()
elif glow_effect_checkbox:
    mplcyberpunk.add_glow_effects()
elif gradient_fill_checkbox:
    mplcyberpunk.add_gradient_fill()
    plt.setp(legend.get_texts(), color='k')
else:
    plt.setp(legend.get_texts(), color='k')

st.pyplot(fig)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Displaying the plot and the last 7 days' values
    
st.write("#### Last 7 Days Incedence")
st.table(incidence.iloc[-7:,:])

st.write('---')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

st.write('## New reported cases - Rolling 7 Day Average')
st.write('This chart shows a [rolling 7-day-average](https://en.wikipedia.org/wiki/Moving_average) of newly reported cases for the selected City(s).')
st.write('This smoothes out the spikes somewhat and makes it easier to identify the real trend in cases.')

# Plotting the 7 day average

data = data_to_plot.iloc[-no_of_days:,:]

fig, ax = plt.subplots()

for i in selected_cities:
    plt.plot(data['Date'], data['7 Day Average for %s' % i])

ax.legend(selected_cities)
plt.xticks(rotation=45,
    horizontalalignment='right',
    fontweight='light',
    fontsize='small',
    color= '1')
plt.yticks(color = '1')
plt.title('Rolling 7-day-average - Last ' + str(no_of_days) + ' Days', color = '1')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# mplcyberpunk glow effects if checkbox selected

legend = plt.legend(selected_cities,loc='upper right')
if (glow_effect_checkbox and gradient_fill_checkbox):
    mplcyberpunk.add_glow_effects()
    mplcyberpunk.add_gradient_fill()
elif glow_effect_checkbox:
    mplcyberpunk.add_glow_effects()
elif gradient_fill_checkbox:
    mplcyberpunk.add_gradient_fill()
    plt.setp(legend.get_texts(), color='k')
else:
    plt.setp(legend.get_texts(), color='k')

st.pyplot(fig)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Displaying the plot and the last 7 days' values
st.write("#### Last 7 Days Incedence")
st.table(data_to_plot.iloc[-7:,:])

st.write('---')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Plotting the new cases

st.write('## Newly Reported Cases')
st.write('This chart shows the raw number of new reported cases in the selected City(s).')
st.write("This will show larger variance and generally be 'noisier' than the 7-day-average chart.")
st.write('Notice that the numbers tend to dip to near zero on weekends and spike on Mondays. This is an artifact of the data collection process and not a real trend - new cases are generally not recorded / reported over weekends.')

new_cases = new_cases.iloc[-no_of_days:,:]

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

fig, ax = plt.subplots()

for i in selected_cities:
    plt.plot(new_cases['Date'], new_cases[i])

ax.legend(selected_cities)
plt.xticks(rotation=45, 
    horizontalalignment='right',
    fontweight='light',
    fontsize='small',
    color= '1')
plt.yticks(color = '1')
plt.title('New Reported Cases - Last ' + str(no_of_days) + ' Days', color='1')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# mplcyberpunk glow effects if checkbox selected

legend = plt.legend(selected_cities,loc='upper right')
if (glow_effect_checkbox and gradient_fill_checkbox):
    mplcyberpunk.add_glow_effects()
    mplcyberpunk.add_gradient_fill()
elif glow_effect_checkbox:
    mplcyberpunk.add_glow_effects()
elif gradient_fill_checkbox:
    mplcyberpunk.add_gradient_fill()
    plt.setp(legend.get_texts(), color='k')
else:
    plt.setp(legend.get_texts(), color='k')

st.pyplot(fig)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Displaying the plot and the last 7 days' values

number_to_limit_table = len(selected_cities) + 1 
st.table(new_cases.iloc[-7:,:number_to_limit_table])

st.write('---')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

st.write('''
    Dashboard created by [Mitesh Gupta](https://linkedin.com/in/mitesh-gupta), with [Streamlit](https://www.streamlit.io).
''')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
