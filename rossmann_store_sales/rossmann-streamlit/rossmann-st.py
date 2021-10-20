##################### LIBRARIES #####################

import requests
import pickle
import json
import time
import pandas                   as pd
import streamlit                as st
import plotly.graph_objects     as go

##################### FUNCTIONS #####################

@st.cache( allow_output_mutation = True, suppress_st_warning = True )
def data_to_predict( ):
    """ 
    Load csv files with data to be sent to API for prediction.
    """
    
    # load data from test.csv
    df_test_extraction = pd.read_csv( 'data/test.csv', low_memory = False )

    # load data from store.csv
    df_store_supl_extraction = pd.read_csv( 'data/store.csv', low_memory = False )

    # merge dataframes on Store column
    df_deployment = pd.merge( df_test_extraction, 
                              df_store_supl_extraction,
                              how = 'left', 
                              on = 'Store'
                            )

    return df_deployment
    
@st.cache( allow_output_mutation = True, suppress_st_warning = True )   
def make_request( data_for_prediction ):
    """
    Send a API request to get predictions for the given data
    
    Args:
        data_for_prediction: data whose sales are to be predicted
        
    Return:
        df_predicted: dataframe with predictions
    """   
    
    # import necessary libraries
    import requests
    
    # convert Dataframe to json
    data = json.dumps( data_for_prediction.to_dict( orient = 'records' ) )

    # API url
    url = 'https://rossmann-six-weeks-prediction.herokuapp.com/rossmann/predict'
    # request header
    header = {'Content-type': 'application/json' } 
    # data
    data = data

    # make request
    r = requests.post( url, data = data, headers = header )

    # print request status message
    print( f'Status Code {r.status_code}' )
    # transform api response to pandas dataframe
    df_predicted = pd.DataFrame( r.json(), columns = r.json()[0].keys() )

    
    return df_predicted
    
@st.cache( allow_output_mutation = True, suppress_st_warning = True )
def get_date_filtered( dataframe ):
    """
    On API prediction, data is filtered so only open stores
    are considered for prediction. Therefore, we need to 
    filter 'Date' column to get prediction for every date.
    
    Args:
        dataframe: dataframe with date feature to be filtered on open stores
    
    Return:
        date_series: series with filtered dates
    """

    # filter open stores
    date_series = dataframe.loc[ (dataframe['Open'] == 1) , 'Date' ]
    
    # convert data series to date format, instead of string
    #date_series = pd.to_datetime( date_series, format = '%Y-%m-%d' )
    

    return date_series
    
@st.cache( allow_output_mutation = True, suppress_st_warning = True )    
def interactive_plot( data_predicted, store_number, filtered_dates, plot_scenarios ):
    """
    Plot a interactive line chart with predicted sales for the given store.

    Args:
        data_predicted: data predicted by API request.
        store_number: given store number the user wants to see results.
        filtered_dates: filtered dates according to get_date_filtered function.
    
    Return:
        None
    """
    
    # append date filtered
    data_predicted['date'] = filtered_dates

    # get prediction for the given store
    df_store_prediction = data_predicted[ data_predicted['store'] == store_number  ]

    # check if the chosen store exists
    if df_store_prediction.shape[0] == 0:
        return None
    
    else:
        # load mae_dict
        with open('data/mae_dict.pkl', 'rb') as file:
            mae_dict = pickle.load( file )
        
        # create column with best and worst scenarios with MAE value for the given store
        df_store_prediction['Best Scenario'] = round( df_store_prediction['predicted_sales'] + mae_dict[store_number], 2 )
        df_store_prediction['Worst Scenario'] = round( df_store_prediction['predicted_sales'] - mae_dict[store_number], 2 )       

        # create figure for chart
        fig = go.Figure()

        # check if user selected expected sales scenario
        if 'Expected Sales' in plot_scenarios:
            fig.add_trace( go.Scatter(
                x = df_store_prediction['date'],
                y = df_store_prediction['predicted_sales'],
                connectgaps = True,
                name = '<b>Expected Sales</b>'
            ))
        
        # check if user selected best scenario sales scenario
        if 'Best Scenario' in plot_scenarios:
            fig.add_trace( go.Scatter(
                x = df_store_prediction['date'],
                y = df_store_prediction['Best Scenario'],
                connectgaps = True,
                name = '<b>Best Scenario</b>'
            ))

        # check if user selected best scenario sales scenario
        if 'Worst Scenario' in plot_scenarios:
            fig.add_trace(go.Scatter(
                x = df_store_prediction['date'],
                y = df_store_prediction['Worst Scenario'],
                connectgaps = True,
                name = '<b>Worst Scenario</b>'
            ))
        

        return fig

##################### PREPARATION #####################

####### NOTE: this step was made on jupyter notebook.
####### To fully understand these codes, check 1.0.gcj.rossmann_store_sales.ipynb

####### get store number and mae from generalization performance
# # get store number and mae from generalization performance
# df_mae = final_report[ ['store', 'MAE'] ]
# # create a dictionary with store index and mae values
# mae_dict = { int(row['store']): row['MAE'] for index, row in df_mae.iterrows() }

# # save mae_dict
# with open('mae_dict.pkl', 'wb') as file:
#     pickle.dump( mae_dict, file )

# load mae_dict
# with open('mae_dict.pkl', 'rb') as file:
#     mae_dict = pickle.load( file )
# mae_dict

##################### STREAMLIT APP #####################

# set page layout
st.set_page_config( layout='wide' )

# set title
st.title( 'Rossmann six weeks sales prediction' )

# set subheader
st.header('Six weeks prediction chart')

# set widget to select store number
store_number = st.sidebar.number_input(
                                        label = 'Choose store number', 
                                        min_value = 1, 
                                        max_value = 1115,
                                        value = 500,
                                        step = 1
                                        )

# display selected store for the user
st.write('The current store is ', store_number)

# set widget to select prediction scenario
plot_scenarios = st.sidebar.multiselect(
                                        label = 'Choose prediction scenarios',
                                        options = ['Expected Sales', 'Best Scenario', 'Worst Scenario'],
                                        default = ['Expected Sales', 'Best Scenario', 'Worst Scenario']

                                        )

# display selected scenarios for the user 
st.write('You selected the following scenarios: ', tuple(plot_scenarios) )

# help user to change store number
st.write('')
st.caption('You can change the store number and the scenario on the sidebar to the left.')
st.write('')

# if user don't select any scenario
if plot_scenarios == []:
    # display message 
    st.write('')
    st.caption('Please choose at least one scenario')
    st.write('')
    st.write('')



# if user select at least one scenario
else:
    # create a progress bar
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.1)
        progress_bar.progress( percent_complete + 1 )

    # load data
    df_data_loaded = data_to_predict( )
        
    # request predictions via API
    df_data_predicted = make_request( df_data_loaded )
        
    # get filtered dates
    dates_filtered = get_date_filtered( df_data_loaded )
        
    # plot interactive line chart
    fig = interactive_plot( df_data_predicted, store_number, dates_filtered, plot_scenarios )

    # if chosen store doesn't exist
    if fig is None:
        st.write( "" )
        st.caption( "The chosen store doesn't exist on databases. Try another one :) ..." )
        st.write( "" )

    # if chosen store exists
    else:
        # plot interactive chart
        st.plotly_chart( fig )


# widget to display README.md
project_overview = st.checkbox( 
                        label = 'Show me the project overview ;) ...',
                        value = False
                            )

# check if user wants to see project overview
if project_overview:      
    # create a progress bar
    progress_bar = st.progress(0)
    
    for percent_complete in range(100):
        time.sleep(0.1)
        progress_bar.progress( percent_complete + 1 )

    # # display project README.md
    # st.markdown( project_readme )
    st.markdown( """# **BUSINESS UNDERSTANDING**

## What is the company?

Rossmann.

## What is its business model?

Rossmann operates over 3,000 drug stores in 7 European countries. Its products range includes up to 21,700 items and can vary depending on the size of the shop and the location. In addition to drugstore goods with a focus on skin, hair, body, baby and health, Rossmann also offers promotional items ("World of Ideas"), pet food, a photo service and a wide range of natural foods and wines. 

## What is the business problem the company is facing?

Rossmann store managers need daily sales predictions for up to six weeks in advance so as to plan infrastructure investments in their stores (will next six weeks sales be high enough to balance infrastructure investment?).

## What is the business solution that this project has to deliver?

For each store, the daily sales predictions for the next six weeks.

REFERENCES:

https://www.kaggle.com/c/rossmann-store-sales

https://en.wikipedia.org/wiki/Rossmann_(company)

# **BUSINESS ASSUMPTIONS**

## Hypothesis

In order to make predictions for the next six weeks, Rossmann company has to provide data about its stores for this time interval. Such data, for each store, must include: store model, store assortment level and if the given store will be on continuous promotion.

References:

https://www.kaggle.com/c/rossmann-store-sales

# **SOLUTION STRATEGY**""")

    st.image( 'images/crisp-ds.png' )

    st.markdown("""## Step 01. Data Extraction:
For the available data, check files and data fields description. Then load data from CSV files and merge different tables.

## Step 02. Data Description:
Rename columns and check the number of rows in the table (does it requires big data tools?). Convert data types for some columns and fill out NA (not-available) values. Then use statistics metrics to identify data outside the scope of business.

## Step 03. Feature Engineering:
Create a hypothesis list to check on the fifth step (EDA). Then apply data transformations on the required columns.

## Step 04. Data Filtering:
Filter rows and select columns that do not contain information for modelling or do not match the scope of the business, such as predict sales for a closed store.

## Step 05. Exploratory Data Analysis:
Analyse each variable alone and then the relationship among variables. Then, explore the data further to validate the hypothesis list and raise insights.

## Step 06. Data Preparation:
Split data into train and validation and test. Then, prepare data so that the Machine Learning models can more easily learn and perform more accurately.

## Step 07. Feature Selection:
Select the most signiﬁcant attributes for training the model.

## Step 08. Machine Learning Modelling:
Test different Machine Learning models and select the one with the best performance in prediction sales according to the selected attributes.

## Step 09. Hyperparameter Fine Tuning:
Choose the best values for each parameter of the selected ML model.

## Step 10. Performance Evaluation and Interpretation:
Compare the training and the learning performance (overfitting vs underfitting). Then test the ML model on data equivalent to production data (generalization performance) and convert the ML performance into business results.

## Step 11. Deployment:
Create APIs (Application Programming Interface) to make predictions available on internet requests. Then, for the final user, create a Telegram bot where the user types the number of store and the bot answer with the sales prediction for this given store in the next six weeks. Finally, create a data app where the user could check the sales prediction over these six weeks and also read the entire project overview.

# **TOP 3 INSIGHTS**

## H1. Different store assortments contribute differently to sales revenue.

> H1 IS TRUE. Different store assortments contribute differently to sales revenue and **'extra' assortment has higher median sales**.""")
    
    st.image( 'images/h1_hypothesis.png' )
    
    st.markdown("""## H2. The nearer to competitors, the lower the sales revenue.

> H2 IS FALSE. The nearer to competitors, the higher the sales revenue tends to be.""")

    st.image( 'images/h2_hypothesis.png' )

    st.markdown( """## H3. The sales revenue is higher on weekends.

> H3 IS FALSE. From Monday till Thursday, the sales revenue is higher than from Friday till Sunday.""")

    st.image( 'images/h9_hypothesis.png' )

    st.markdown( """# **BUSINESS RESULTS**

**You can check the Telegram bot at the following link**

https://www.youtube.com/watch?v=6yQgYIjbQog

**You can check the data App at the following link**

https://rossmann-sales-streamlit.herokuapp.com/

# **DEPLOYMENT**

**Telegram Bot**

To make predictions more straightforward for the final user, a Telegram bot was created so the user just needs to type the number of the store and the bot will quickly answer the sales prediction for this given store in the next six weeks. 

You can check how easy is to get predictions via this Telegram bot by watching the following video:

https://www.youtube.com/watch?v=6yQgYIjbQog

**Streamlit**

If the final user wants more detailed information about this six weeks prediction, he (she) could get further details on a data App. This data App has information on sales prediction over these six weeks. Besides, the user can also read the entire project overview to understand further how this prediction is made.

You can check this data App at the following link:

https://rossmann-sales-streamlit.herokuapp.com/

**GitHub**

You can check the whole project repository at the following link:

https://github.com/ds-gustavo-cunha/Rossmann-Store-Sales

# **CONCLUSIONS**

It took me a while to go from the very beginning till the very end of the project (actually, it took me about two weeks). 

Even within just two weeks, we can easily see that **Data Science projects can deploy straightforward solutions to support business team decisions, making these decisions not only more precise but also easier to be made.**


# - LESSONS LEARNED

**How to do an end-to-end Data Science project.**

How to build a Flask API, data App, Telegram bot and host all of them on Heroku cloud so that the solution is available online.

**It's important to focus on the business solution** and don't get lost in 'playing' with different tools.

**The most important thing is the business solution so**, if one tool is not working or if it is taking too much time to implement, find another one that will **keep the project pacing forward.**

**On the first project cycle, it's important to keep things simple** and not try to get the best solution because this can only be achieved through many project cycles.

# **NEXT STEPS TO IMPROVE**

**Streamlit**: make App run faster and create more options for the user to further analyse prediction data.

**Telegram Bot**: create more options for the user so, for example, the user could get a chart with sales predictions besides the single value prediction.

**Features**: try different variables, scalers and encodings so that ML performance improves.

**API**: implement data validation on API requests to make it less error-prone and more easily debugged in case of error.

**Machine Learning Models**: test more ML models to find one with better results. 

**Code**: review the whole code once more to make it clearer and more efficient (faster and less resource-intensive).

""" )