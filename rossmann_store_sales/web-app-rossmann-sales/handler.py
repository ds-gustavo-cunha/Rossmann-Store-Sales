############## LIBRARIES ##############


import pickle
import os
import lightgbm
import pandas              as pd
from   rossmann.Rossmann   import Rossmann
from   flask               import Flask, request, Response


############## API ##############


# loading model
with open('./model/model_rossmann_sales.pkl', 'rb') as file:
    model = pickle.load( file )


# Create the app object
app = Flask( __name__ )

# create endpoint for request
@app.route( '/rossmann/predict', methods=['POST'] )
def rossmann_predict():
    # get json data on request
    test_json = request.get_json()   

    # check if data was sent on request
    if test_json:
    # unique row given on the request made: json = dictionary
        if isinstance( test_json, dict ): 
            test_raw = pd.DataFrame( test_json, index = [0] )

        # multiple rows given on the request made
        else:
            test_raw = pd.DataFrame( test_json, columns=test_json[0].keys() )
       
        # create a copy of original data
        original_data = test_raw.copy()

        # Instantiate Rossmann class
        pipeline = Rossmann()

        # clean data
        df_dc_done = pipeline.data_cleaning( test_raw )

        # engineer data
        df_fe_done = pipeline.feature_engineering( df_dc_done )

        # filter data
        df_df_done = pipeline.data_filtering( df_fe_done )
               
        # prepare data
        df_dp_done = pipeline.data_preparation( df_df_done )
       
        # make prediction
        df_response = pipeline.get_prediction( model, original_data, df_dp_done )

        
        return df_response


    # data was not sent on request
    else:
        # mimetype -> from a json application
        return Response( '{}', status = 200, mimetype = 'application/json' )


# when handler.py script is run, run flask
if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    # '0.0.0.0' is the local host
    app.run( host = '0.0.0.0', port = port, debug = True )