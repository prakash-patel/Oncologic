# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import operator
import math
import os
import datetime
from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import requests
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io as io
from io import BytesIO
import statsmodels.api as sm
import seaborn as sns
import tensorflow as tf
import re
import json
import http.client, urllib.parse

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

# thank you to @kinghelix and @trevormarburger for this idea
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

@blueprint.route('/index')
@login_required
def index():

    return render_template('dashboard.html', segment='index')

@blueprint.route('/dashboard')
@login_required
def dashboard():
    # # Register converters to avoid warnings
    # pd.plotting.register_matplotlib_converters()
    # plt.rc("figure", figsize=(16,8))
    # plt.rc("font", size=14)

    # url="https://api.covidtracking.com/v1/states/daily.csv"
    # s=requests.get(url).content
    # #print(s)
    # c=pd.read_csv(io.StringIO(s.decode('utf-8')))
    # #print(c)
    # predictorList = []
    # for state in c['state'].unique():
    #     df = c.loc[c['state'] == state]
    #     #df['DateTime'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d')
    #     df = df[::-1]
    #     mod = sm.tsa.statespace.SARIMAX(df['positive'], trend='c', order=(1,1,1),simple_differencing=True)
    #     res = mod.fit(disp=False)
    #     result = res.forecast()
    #     result = re.search(r"[\u0030-\u0039]+\u002E[\u0030-\u0039]+", str(result))
    #     result = result.group()
    #     predictorList.append([state,str(result)])
    #     # print(res.summary())
    #     print("State: "+str(state)+" , predicted next day positive cases : "+str(result))#.format(state, res.forecast()))

    return render_template('dashboard.html', segment='dashboard')

@blueprint.route('/predictTomorrow', methods=['GET'])
def predictCasesTomorrow():
    # Register converters to avoid warnings
    pd.plotting.register_matplotlib_converters()
    plt.rc("figure", figsize=(16,8))
    plt.rc("font", size=14)
    stateUrl = "https://gist.githubusercontent.com/meiqimichelle/7727723/raw/0109432d22f28fd1a669a3fd113e41c4193dbb5d/USstates_avg_latLong"
    stateData = requests.get(stateUrl).content
    #print(stateData)
    stateLatLong = json.loads(stateData)
    #print(stateLatLong)

    basedir = os.path.abspath(os.path.dirname(__file__))
    data_file = os.path.join(basedir, 'uscities.csv')

    df = pd.read_csv(data_file)
    df_state = df.groupby('state_id')

    data = []
    for state in df_state['state_id'].unique():
        cur_state = df_state.get_group(state[0]) 
        cur_state_copy = cur_state.copy()
        cur_state['weighted_average'] = (cur_state_copy['population'] / cur_state_copy.population.sum()) * cur_state_copy['density']
        data.append([str(state[0]),cur_state.weighted_average.sum()])

    state_df = pd.DataFrame(data, columns=['state', 'weight'])
    url="https://api.covidtracking.com/v1/states/daily.csv"
    s=requests.get(url).content
    c=pd.read_csv(io.StringIO(s.decode('utf-8')))
    predictorList = []
    predictorListUpdated = []
    needVac = []
    #print(c)
    for state in c['state'].unique():
        #print(state)
        stateName = abbrev_us_state[state]
        #print(stateName)
        for keyval in stateLatLong:
            if stateName.lower() == keyval['state'].lower():
                sLatLong = keyval
                
        # conn = http.client.HTTPConnection('api.positionstack.com')
        # params = urllib.parse.urlencode({
        #     'access_key': '57a81ef8942f6d890be16b36b5a41f1d',
        #     'query': abbrev_us_state[state],
        #     "country": "US",
        #     "region": abbrev_us_state[state],
        #     'limit': 1
        #     })

        # conn.request('GET', '/v1/forward?{}'.format(params))

        # res = conn.getresponse()
        # data = res.read()
        # latlong = json.loads(data.decode('utf-8'))
        #print(latlong)
        #print("lat/long" + data.decode('utf-8'))

        df = c.loc[c['state'] == state]
        #df['DateTime'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d')
        df = df[::-1]
        mod = sm.tsa.statespace.SARIMAX(df['positive'], trend='c', order=(1,1,1),simple_differencing=True)
        res = mod.fit(disp=False)
        result = res.forecast()
        result = re.search(r"[\u0030-\u0039]+\u002E[\u0030-\u0039]+", str(result))
        result = result.group()
        predictorList.append([state,str(result)])
        a_dictionary = {"predication": str(result), "stateAbbreviation" : state}
        sLatLong.update(a_dictionary)
        #print(sLatLong)
        predictorListUpdated.append(sLatLong)
        # print(res.summary())
        #print("State: "+str(state)+" , predicted next day positive cases : "+str(result))#.format(state, res.forecast()))
        #print("State: "+ state + "Predicted next day positive cases"+res.forecast())
        js = json.dumps(predictorListUpdated)
    # data = {}
    # dfObj = pd.DataFrame(predictorList ,columns = ['state' , 'PredictedNextDayCase'] ) 
    # dfObj = dfObj.join(state_df.set_index('state'), on='state')
    # for index,row in dfObj.iterrows():
    #     cur_state = str(row['state'])
    #     if not math.isnan(float(row['weight'])) :
    #         cur_val = float(row['PredictedNextDayCase']) / float(row['weight'])
    #         data[cur_state]=cur_val
    # needVacine = dict(sorted(data.items(), key=operator.itemgetter(1), reverse=True)[:5])
    # print(needVacine)
    #newJs = {"vaccineNeed": needVacine}
    return js

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  
