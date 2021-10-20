############## LIBRARIES ##############


import os
import requests
import json
import pandas as pd
from flask import Flask, request, Response


############## FUNCTIONS ##############

# send message to user
def send_message( chat_id, text ):
    # construct url to sent text
    url = f'https://api.telegram.org/bot{TOKEN}/' 
    url = url + f'sendMessage?chat_id={chat_id}'

    # send text to given url
    r = requests.post( url, json = {'text': text } )
    print( f'Status Code {r.status_code}' )


    return None


 # load data to make prediction
def load_dataset( store_id ):
    # loading test dataset  
    home_path = ''    
    df_test = pd.read_csv( f'{home_path}test.csv' )
    df_store_supl = pd.read_csv( f'{home_path}store.csv' )

    # merge test dataset + store suplementary info
    df_test = pd.merge( df_test, df_store_supl, 
						how = 'left', on = 'Store' )

    # choose store for prediction
    df_test = df_test[ df_test['Store'] == store_id ]

	# check if there is data to make prediction
    if not df_test.empty:
        
		# convert Dataframe to json
        data = json.dumps( df_test.to_dict( orient = 'records' ) )
		
		# there is no data to be predicted
    else:
        data = 'error: there is no data for this store'


    return data


 # API call
def predict( data ):
    # API url for prediction
    url = 'https://rossmann-six-weeks-prediction.herokuapp.com/rossmann/predict'
    # request header
    header = {'Content-type': 'application/json' }
    # data to be be predicted
    data = data

	# make post request to API -> get prediction for given data
    r = requests.post( url, data = data, headers = header )
    print( f'Status Code {r.status_code}' )

	# construct dataframe for the prediction made
    df_predicted = pd.DataFrame( r.json(), columns = r.json()[0].keys() )


    return df_predicted


 # get store id the user wants prediction
def parse_message( message ):
    # get chat id from conversation
    chat_id = message['message']['chat']['id']
    # get message the user sent 
    store_id = message['message']['text']

    # remove / on store id message
    store_id = store_id.replace( '/', '' )

    try: 
		# check if user send a number as store id
        store_id = int( store_id )

    except ValueError: 
		# if user doesn't sent a number as store id
        store_id = 'error'


    return chat_id, store_id


############## API ##############


# constants
TOKEN = 'TOKEN'


# create the app object
app = Flask( __name__ )

# create endpoint for request
@app.route( '/', methods=['GET', 'POST'] )
def index():
    if request.method == 'POST':
        # get message sent on request as json
        message = request.get_json()

        # extract chat_id and store_id from
        # message sent to bot
        chat_id, store_id = parse_message( message )

		# if user sent a store id as a number
        if store_id != 'error':
            # load data for the given store
            data = load_dataset( store_id )

            if data != 'error: there is no data for this store':
                # get prediction for the given store via api request
                df_predicted = predict( data )

                # calculation
                sales = df_predicted[ df_predicted[ 'store' ] == store_id ]

                # calculate sales prediction for each store in the last 6 weeks
                stores_prediction = sales[ ['store', 
                                            'predicted_sales'] ].groupby('store').sum().reset_index()               

                # create message for user
                msg = 'Store Number {} will sell U$ {:,.2f} in the next 6 weeks'.format(
                            int(stores_prediction['store'].values[0]),
                            stores_prediction['predicted_sales'].values[0] ) 

                # send message to user
                send_message( chat_id, msg )

                # response to API
                return Response( 'Ok', status = 200 )

            else: # if there is no data for the given store
                send_message( chat_id, 'Store ID is wrong. Try another id ;)' )

                # response to API
                # always send status, otherwise API will loop forever
                return Response( 'Ok', status=200 )

        else: # if user sent a store id as a number
            # send message to user
            send_message( chat_id, 'Store ID is Wrong. Try another id ;)' )

            # response to API
            return Response( 'Ok', status=200 )

    else: # if request.method = GET               

        return '<h1> Rossmann Telegram BOT </h1>'


# when this script is run, run flask
if __name__ == '__main__':
    # set port number
    port = os.environ.get( 'PORT', 5000 )
    app.run( host = '0.0.0.0', port = port, debug = True )