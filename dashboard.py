import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import os 
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title= 'Super Store ', page_icon=':bar_chart:', layout='wide')
st.title(':bar_chart: SuperStore EDA Project')

file = st.file_uploader('Upload your file ', type= (['csv','xlsx','xls','text']))

if file is not None:
    file_name = file.name
    st.write(f"Active File: {file_name}")
    if file_name.endswith('.csv'):
        data = pd.read_csv(file, encoding='ISO-8859-1')
    else:
        data = pd.read_excel(file)
else:
    try:
        data = pd.read_excel('Sample - Superstore.xls')
    except Exception as e:
        st.error("Default file not found! Please upload a file.")
        st.stop() 
    
col1, col2 = st.columns((2))
data['Order Date'] = pd.to_datetime(data['Order Date'])



# Getting max and min date 
start_date = data['Order Date'].min()
end_date = data['Order Date'].max()


with col1:
    date1 = pd.to_datetime(st.date_input("Start date" , start_date))
with col2:
    date2  = pd.to_datetime(st.date_input('End date ', end_date) )

data = data[(data["Order Date"] >= date1) & (data["Order Date"] <= date2)].copy()



# create for Region 
st.sidebar.header('Choose your filter : ')
region = st.sidebar.multiselect('Pick the region', data['Region'].unique())

if not region:
    data2 = data.copy()
else:
    data2 = data[data['Region'].isin(region)]
    
    
# create for state 
state = st.sidebar.multiselect('Pick the  state ', data2['State'].unique())

if not state:
    data3 = data2.copy()
else:
    data3 = data2[data2['State'].isin(state)]
    
# create for city

city = st.sidebar.multiselect('Pick the city', data3['City'].unique())



# Filter the data based on Region,State and City

if not region and not state and not city:
    filtered_data = data
elif not state and not city:
    filtered_data = data[data['Region'].isin(region)]
elif not region and not city:
    filtered_data = data[data['State'].isin(state)]
elif state and city:
    filtered_data = data3[data3['State'].isin(state) & data3['City'].isin(city)]
elif region and city:
    filtered_data = data3[data3['Region'].isin(region) & data3['City'].isin(city)]
elif region and state:
    filtered_data = data3[data3['Region'].isin(region) & data3['State'].isin(state)]
elif city:
    filtered_data = data3[data3['City'].isin(city)]
else:
    filtered_data = data3[data3['Region'].isin(region) & data3['State'].isin(state) & data3['City'].isin(city)]



category_wise_sales = filtered_data.groupby(by = ['Category'], as_index= False)['Sales'].sum()
region_wise_sales =  filtered_data.groupby(by = ['Region'], as_index = False)['Sales'].sum()


with col1:
    st.subheader('Category wise Sales')
    fig = px.bar(data_frame= category_wise_sales , x= 'Category',  y='Sales', text=['${:,.2f}'.format(x) for x in category_wise_sales['Sales']],
                 template='plotly_dark')
    fig.update_xaxes(showgrid = False)
    fig.update_yaxes(showgrid = False ,zeroline = False)
    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig,use_container_width=True, height=500)

with col2:
    st.subheader('Region wise Sales')
    fig =  px.pie(data_frame= filtered_data, values= 'Sales', names= 'Region', hole= 0.5)
    fig.update_traces(textinfo='percent+label', textposition='outside')
    st.plotly_chart(fig,use_container_width=True)
    
    
col1 , col2 = st.columns(2)

with col1:
    with st.expander('Category_wise_sales_view_data'):
        st.write(category_wise_sales.style.background_gradient(cmap='Blues').format(precision = 2))
        csv = category_wise_sales.to_csv(index = False).encode('utf-8')
        st.download_button("Download data", data= csv, mime= 'text/csv', help= 'click here to download the data as  a CSV file',key= 'Category data')
    
    
with col2:
    with st.expander('Region_wise_sales_view_data'):
        st.write(region_wise_sales.style.background_gradient(cmap='Oranges').format(precision =2))
        csv = region_wise_sales.to_csv(index = False).encode('utf-8')
        st.download_button("Download data", data= csv, mime= 'text/csv', key='Region data',help= 'click here to download the data as  a CSV file')
        
        
filtered_data['month_year'] =filtered_data['Order Date'].dt.to_period('M')

st.subheader('Time Series Analysis')

line_chart = filtered_data.groupby('month_year')['Sales'].sum().reset_index()
line_chart['month_year']  = line_chart['month_year'].dt.strftime('%Y - %b')
fig2 = px.line(data_frame= line_chart, x= 'month_year', y= 'Sales', labels= {'Sales':'Amount','month_year ':'Month'}, height= 500 , width= 1000 , template= 'gridon')

st.plotly_chart(fig2, use_container_width=True)


with st.expander('View data of Time Series '):
        st.write(line_chart.T.style.background_gradient(cmap='Oranges').format(precision = 2))
        csv = line_chart.to_csv(index = False).encode('utf-8')
        st.download_button("Download data", data= csv, mime= 'text/csv', help= 'click here to download the data as  a CSV file',key= 'Time series')
        
    
    
# create a tree map base on category , sub_category and Region


st.subheader('Hierarchical view of Sales using Treemap')
fig3 = px.treemap(data_frame= filtered_data,values= 'Sales',path= ['Region' ,'Category', 'Sub-Category'], hover_data= 'Sales', color='Profit')
st.plotly_chart(fig3, use_container_width=True)

# Create pie chart for Segment  and Category wise sales  

chart_1, chart_2 = st.columns((2))

with chart_1:
    st.subheader('Segment wise Sales')
    fig =  px.pie(filtered_data,  values= 'Sales', names='Segment',template='plotly_dark')
    fig.update_traces(textinfo='percent+label', textposition='inside')
    st.plotly_chart(fig,use_container_width=True)

with chart_2:
    st.subheader('Category wise Sales')
    fig =  px.pie(filtered_data,  values= 'Sales', names='Category',template='plotly_dark')
    fig.update_traces(textinfo='percent+label', textposition='inside')
    st.plotly_chart(fig,use_container_width=True)

st.subheader(":point_right: Month wise Sub_Category Sales Summary")
with st.expander('Summary Table'):
    sample_data = data[0:5][['Region','State','City','Category','Sales','Profit','Quantity']].round(2)
    fig = ff.create_table(sample_data, colorscale= 'Viridis')
    st.plotly_chart(fig,use_container_width=True)
    
    st.markdown('Mothly wise Sub_Category Table')
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    filtered_data['Month'] = filtered_data['Order Date'].dt.month_name().str[:3]
    filtered_data['Month'] = pd.Categorical(filtered_data['Month'], categories= month_order, ordered=True)
    filtered_data = filtered_data.sort_values('Month')
    sub_category_year = pd.pivot_table(filtered_data, values= 'Sales', index= 'Sub-Category', columns='Month')
    st.write(sub_category_year.style.background_gradient(cmap='Oranges').format(precision =2))



# Create a scatter plot 


data_4 = px.scatter(data_frame= filtered_data , x= 'Sales',  y='Profit', size='Quantity')
data_4.update_layout(title = 'Relationship between Sales and Profit Using Scatter plot',
                     title_font_size = 20 ,
                     xaxis_title = 'Sales',
                     xaxis_title_font_size = 19,
                     yaxis_title = 'Profit',
                     yaxis_title_font_size = 19,
                     template = 'plotly_white')
st.plotly_chart(data_4,use_container_width=True )

with st.expander('View Data'):
    st.write((filtered_data.iloc[:500,1:20:2]).style.background_gradient(cmap='Oranges').format(precision =2))

