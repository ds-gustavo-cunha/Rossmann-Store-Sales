############## LIBRARIES ##############


import pickle
import re
import numpy  as np
import pandas as pd
import sklearn


############## CLASS AND ITS FUNCTIONS ##############


# NOTE: features that won't be used for prediction will have 
# their codes commented. The feature transformations for these
# features will be kept on this code to make code tracking easier
# for future CRISP cycles. 


class Rossmann:
    def __init__( self ): # class constructor

        # load scalers
        with open( './parameter/competition_distance_inputter.pkl', 'rb' ) as competition_distance_inputter:
            self.competition_distance_inputter = pickle.load( competition_distance_inputter )       
        with open( './parameter/competition_open_since_month_inputter.pkl', 'rb' ) as competition_open_since_month_inputter:
            self.competition_open_since_month_inputter = pickle.load( competition_open_since_month_inputter )
        with open( './parameter/competition_open_since_month_scaler.pkl', 'rb' ) as competition_open_since_month_scaler:
            self.competition_open_since_month_scaler = pickle.load( competition_open_since_month_scaler )
        with open( './parameter/competition_open_since_year_inputter.pkl', 'rb' ) as competition_open_since_year_inputter:
            self.competition_open_since_year_inputter = pickle.load( competition_open_since_year_inputter )
        with open( './parameter/promo2_since_week_inputter.pkl', 'rb' ) as promo2_since_week_inputter:
            self.promo2_since_week_inputter = pickle.load( promo2_since_week_inputter )
        with open( './parameter/promo2_since_week_scaler.pkl', 'rb' ) as promo2_since_week_scaler:
            self.promo2_since_week_scaler = pickle.load( promo2_since_week_scaler )
        with open( './parameter/promo2_since_year_inputter.pkl', 'rb' ) as promo2_since_year_inputter:
            self.promo2_since_year_inputter = pickle.load( promo2_since_year_inputter )
        with open( './parameter/promo2_since_year_scaler.pkl', 'rb' ) as promo2_since_year_scaler:
            self.promo2_since_year_scaler = pickle.load( promo2_since_year_scaler )
        # with open( './parameter/promo_interval_inputter.pkl', 'rb' ) as promo_interval_inputter:
        #     self.promo_interval_inputter = pickle.load( promo_interval_inputter )
        with open( './parameter/store_scaler.pkl', 'rb' ) as store_scaler:
            self.store_scaler = pickle.load( store_scaler )
        # with open( './parameter/year_scaler.pkl', 'rb' ) as year_scaler:
        #     self.year_scaler = pickle.load( year_scaler )


    def data_cleaning( self, df_to_clean ):
        """df_to_clean is the data(frame) to be cleaned"""
  
        # change from Pascal case to snake case
        snake_case = [ '_'.join( re.findall('([A-Z][a-z0-9]+)', column) ).lower()
                        for column in df_to_clean.columns ]
        df_to_clean.columns = snake_case

        # convert data column to date format, instead of string
        df_to_clean['date'] = pd.to_datetime( df_to_clean['date'], format = '%Y-%m-%d' )

        # transform given column with fitted inputter
        df_to_clean[ 'competition_distance' ] = self.competition_distance_inputter.transform( df_to_clean[ 'competition_distance' ].values.reshape(-1, 1) )

        # Data Cleaning is done -> df_dc_done
        df_dc_done = df_to_clean
        
        return df_dc_done


    def feature_engineering( self, df_to_fe ):
        """df_to_fe is the data(frame) to be engineered"""

        # convert float columns to integer columns 
        # as they have interger values
        # df_to_fe['competition_distance'] = df_to_fe['competition_distance'].astype( int )
        # df_to_fe['competition_open_since_month'] = df_to_fe['competition_open_since_month'].astype( int )
        # df_to_fe['competition_open_since_year'] = df_to_fe['competition_open_since_year'].astype( int )
        # df_to_fe['promo2_since_week'] = df_to_fe['promo2_since_week'].astype( int )
        # df_to_fe['promo2_since_year'] = df_to_fe['promo2_since_year'].astype( int )


        # create a column for day of month
        df_to_fe['day_of_month'] = df_to_fe['date'].dt.day

        # create day of year
        df_to_fe['day_of_year'] = df_to_fe['date'].dt.strftime('%j')
        df_to_fe['day_of_year'] = df_to_fe['day_of_year'].astype( 'int' )

        # create a column for month
        df_to_fe['month'] = df_to_fe['date'].dt.month

        # create a column for year
        # df_to_fe['year'] = df_to_fe['date'].dt.year

        # make day_of_week start from 0 -> (sunday = 0)
        df_to_fe['day_of_week'] = df_to_fe['day_of_week'].apply( lambda x: 0 if x == 7 else x )

        # create a column for week number 
        # sunday = 0 to match day_of_week column
        # df_to_fe['week_number'] = df_to_fe['date'].dt.strftime('%U')
        # df_to_fe['week_number'] = df_to_fe['week_number'].astype( 'int' );


        # # get season data
        # spring = range(3, 5)
        # summer = range(6, 8)
        # autumn = range(9, 11)
        # # winter = everything else

        # create season column
        # df_to_fe['season'] = df_to_fe['month'].apply( lambda x: 'spring' if x in spring else
        #                                                         'summer' if x in summer else
        #                                                         'autumn' if x in autumn else
        #                                                         'winter')

        # Feature Engineering is done -> df_fe_done
        df_fe_done = df_to_fe


        return df_fe_done


    def data_filtering( self, df_to_filter ):
        """df_to_filter is the data(frame) be (data) filtered"""

        # remove rows where store is closed
        df_to_filter = df_to_filter[ df_to_filter['open'] == 1 ]
        
        # remove open column
        df_to_filter.drop(columns = ['open'], 
                          axis = 'columns',
                          inplace = True)    
        
        # Data Filtering is done -> df_df_done
        df_df_done = df_to_filter


        return df_df_done
        
        
    def data_preparation( self, df_to_dp ):
        """df_to_dp is the data(frame) be (data) prepared"""

        # map assortment column according to database information
        # Assortment -> a = basic, b = extra, c = extended
        df_to_dp['assortment'] = df_to_dp['assortment'].apply(lambda x: 'basic' if x == 'a' else
                                                                    'extra' if x == 'b' else
                                                                    'extended'
                                                             )       
                
        # columns not available in production environment
        # 'customers' not in production data -> no need to be removed
        cols_to_remove = ['state_holiday', 'school_holiday', 'promo']
        # drop columns to be removed
        df_to_dp.drop( columns = cols_to_remove, axis = 'columns', inplace = True )
   

        # iterate over columns
        for column in df_to_dp:

            ####################
            dict_inputter = {'competition_open_since_month': self.competition_open_since_month_inputter,
                            'competition_open_since_year': self.competition_open_since_year_inputter,
                            'promo2_since_week': self.promo2_since_week_inputter,
                            'promo2_since_year': self.promo2_since_year_inputter,
                            # 'promo_interval': self.promo_interval_inputter
                            }            
            
            # check if MISSING VALUE INPUTATION is required                      
            if column in dict_inputter.keys():
                # load inputter
                inputter = dict_inputter[ column ]
                # transform given column with inputter
                df_to_dp[ column ] = inputter.transform( df_to_dp[ column ].values.reshape(-1, 1) )


            ####################    
            # no NORMALIZATION yet


            ####################
            dict_scaler = {'store': self.store_scaler, 
                           'competition_open_since_month': self.competition_open_since_month_scaler,
                           'promo2_since_week': self.promo2_since_week_scaler, 
                           'promo2_since_year': self.promo2_since_year_scaler, 
                        #    'year': self.year_scaler
                          }           

            # check if RESCALING is required
            if column in dict_scaler.keys():

                # load scaler 
                scaler = dict_scaler[ column ]
                # transform col_outlier
                df_to_dp[ column ] = scaler.transform( df_to_dp[ column ].values.reshape(-1,1) )


            ####################
            # check if DISCRETIZATION is required
            if column in ['competition_open_since_year',
                          'competition_distance'
                         ]:

                # dictionary with feateres and their bins
                dict_bins = {'competition_open_since_year': [1989, 1990, 1995, 2000, 2005, 2008, 2010, 2012, 2014, 2016],
                             'competition_distance': [0, 50, 100, 500, 1000, 5000, 15000, 100000]
                            }

                # discretize column
                df_to_dp[ column ] = pd.cut( df_to_dp[ column ], bins = dict_bins[ column ] )
                # convert categoric dtype to integer
                df_to_dp[ column ] = pd.Categorical( df_to_dp[ column ] ).codes
                # make category labels range from 0 to 2
                df_to_dp[ column ] = df_to_dp[ column ] / ( ( len( dict_bins[ column ] ) - 2 ) / 2 )



             ####################       
            # check if ENCODING is required
            if column in ['store_type', 
                          'assortment', 
                        #   'promo_interval'
                         ]:

                # auxiliary list to encode
                aux_dict = {'store_type': {'a': 0, 'd': 1, 'c': 2, 'b': 3},
                            'assortment': {'basic': 0, 'extended': 1, 'extra': 2},
                            # 'promo_interval': {'Mar,Jun,Sept,Dec': 0,
                            #                     'Feb,May,Aug,Nov': 1,
                            #                     'Jan,Apr,Jul,Oct': 2 }
                           }

                # map feature
                df_to_dp[ column ] = df_to_dp[ column ].map( aux_dict[ column ] )


            ####################
            # check if NATURE TRANSFORMATION is required
            if column in [#'season',
                          'day_of_month',
                          'day_of_year',
                          'month',
                        #   'week_number',
                          'day_of_week'
                         ]:

                # # check season especific engineering
                # if column == 'season':
                #     # create season dictionary for mapping
                #     season_map = {
                #         'winter': 0, 
                #         'spring': 1, 
                #         'autumn': 2, 
                #         'summer': 3
                #     }

                #     # map season feature
                #     df_to_dp['season'] = df_to_dp['season'].map( season_map )

                # dict with feature and its cycle
                cyclic_dict = {
                    # 'season': 4,
                    'day_of_month': 30,
                    'day_of_year': 365,
                    'month': 12,
                    'week_number': 52,
                    'day_of_week': 7
                }

                # apply sin and cos transformation on features    
                df_to_dp[ f'{column}_sin' ] = df_to_dp[ column ].apply( lambda x: np.sin( x * ( 2. * np.pi/ cyclic_dict[ column ] ) ) )
                df_to_dp[ f'{column}_cos' ] = df_to_dp[ column ].apply( lambda x: np.cos( x * ( 2. * np.pi/ cyclic_dict[ column ] ) ) )
                # remove cyclic column from dataframe
                df_to_dp.drop( columns = [ column ], axis = 'columns', inplace = True )


        cols_selected = [
            'store',
            'store_type',
            'assortment',
            'competition_distance',
            'competition_open_since_month',
            'competition_open_since_year',
            'promo2_since_week',
            'promo2_since_year',
            'day_of_month_sin',
            'day_of_month_cos',
            'day_of_year_sin',
            'day_of_year_cos',
            'month_cos',
            'day_of_week_sin',
            'day_of_week_cos'
        ]

        # select columns
        df_to_dp = df_to_dp[ cols_selected ]
        
        # Data Preparation (and feature selection) is is done -> df_dp_done
        df_dp_done = df_to_dp


        return df_dp_done


    def get_prediction( self, ml_model, original_data, prepared_data):
        """
        Args:
            ml_model: model trained
            original_data: original data sent on request
            prepared_data: transformed data, ready for prediction
        
        Return:        
            pred: sales prediction in the next 6 weeks
        """

        # make ML model predict sales on prepared data
        prediction = ml_model.predict( prepared_data )

        # convert prediction to normal scale (instead of log scale)
        # and join prediction as a column onto original dataframe
        prepared_data['predicted_sales'] = np.expm1( prediction )

        # note that store number is scaled once data was prepared
        # to get original store number -> reverse scaling
        prepared_data[ 'store' ] = self.store_scaler.inverse_transform( prepared_data[ 'store' ].values.reshape(-1,1) )

        # # calculate sales prediction for each store in the last 6 weeks
        # stores_prediction = prepared_data[ ['store', 
        #                                     'predicted_sales'] ].groupby('store').sum().reset_index()

        # convert the result to json (API transferring format)
        # df_prediction = stores_prediction.to_json( orient='records', date_format='iso' )
        df_prediction = prepared_data.to_json( orient='records', date_format='iso' )


        return df_prediction