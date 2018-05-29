import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dte
from dash.dependencies import Input, Output, State, Event
from plotly.graph_objs import *
import os
import datetime as date
from AeroSpike_production import AerospikeClient
import time
import ipaddress
import flask
from datetime import datetime as dt
#------------------------------------------Settings --------------------------------------------------------------------

Accounts = [
    ['admin', 'admin'],
]

aero = AerospikeClient()
aero.connect()

app = dash.Dash('firewall-app')
app.config.supress_callback_exceptions = True
server = app.server
auth = dash_auth.BasicAuth(app, Accounts)
#------------------------------------------APP LAYOUT-------------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        html.H2("Elitnet1 HRPI Analyzer"),
        html.Img(src="/static/ktu.png"),
        html.Img(src="/static/elitnet.png"),
        html.Br(),
        dcc.Tabs(tabs=[ {'label': 'Live graph', 'value': True},
                        {'label': 'History graph', 'value': False}],
                        id='update-dropdown',
                        value=True,
                 style={'borderColor': "rgb(120,120,120)",
                        #'backgroundColor' : "rgb(165, 42, 42)",
                        "color": "rgb(20,20,20)",
                        "fontSize": "20px"}),
        html.Br(),
    ], className='banner'),
    # Live graph
    html.Div(id='live-graph-container', children=[
        html.Br(),
        dcc.Graph(id='live-graph', className='graph'),
        dcc.Interval(id='live-graph-update', interval=100),
        html.Div(id='live-table-container', className='table'),
        dcc.Interval(id='table-update', interval=100),
    ], className='graphDiv'),
    # Hystory graph
    html.Div(id='history-graph-container', children=[
        html.Br(),
        html.Div(id='history-inputs-container', children=[
            html.Label('Select date, time and hour to display'),
            html.Div(id='inputs', children=[
                dcc.DatePickerSingle(
                    id="date-input",
                    display_format="YYYY-M-D",
                    month_format='MMMM Y',
                    placeholder='MMMM Y',
                    date=date.date.today()),
            ], className='dateinput'),
            dcc.Dropdown(id='hour-dropdown', className='dropdown', value=dt.now().hour, options=
            [{'label': '00 h.', 'value': 0},
             {'label': '01 h.', 'value': 1},
             {'label': '02 h.', 'value': 2},
             {'label': '03 h.', 'value': 3},
             {'label': '04 h.', 'value': 4},
             {'label': '05 h.', 'value': 5},
             {'label': '06 h.', 'value': 6},
             {'label': '07 h.', 'value': 7},
             {'label': '08 h.', 'value': 8},
             {'label': '09 h.', 'value': 9},
             {'label': '10 h.', 'value': 10},
             {'label': '11 h.', 'value': 11},
             {'label': '12 h.', 'value': 12},
             {'label': '13 h.', 'value': 13},
             {'label': '14 h.', 'value': 14},
             {'label': '15 h.', 'value': 15},
             {'label': '16 h.', 'value': 16},
             {'label': '17 h.', 'value': 17},
             {'label': '18 h.', 'value': 18},
             {'label': '19 h.', 'value': 19},
             {'label': '20 h.', 'value': 20},
             {'label': '21 h.', 'value': 21},
             {'label': '22 h.', 'value': 22},
             {'label': '23 h.', 'value': 23}]),
            dcc.Dropdown(id='minute-dropdown', className='dropdown', value=int(dt.now().minute/5)*5, options=
            [{'label': '00-05 min.', 'value': 0},
             {'label': '05-10 min.', 'value': 5},
             {'label': '10-15 min.', 'value': 10},
             {'label': '15-20 min.', 'value': 15},
             {'label': '20-25 min.', 'value': 20},
             {'label': '25-30 min.', 'value': 25},
             {'label': '30-35 min.', 'value': 30},
             {'label': '35-40 min.', 'value': 35},
             {'label': '40-45 min.', 'value': 40},
             {'label': '45-50 min.', 'value': 45},
             {'label': '50-55 min.', 'value': 50},
             {'label': '55-60 min.', 'value': 55}]),
            ], className='inputs'),
        dcc.Graph(id='history-graph', className='graph'),
        html.Div(id='history-table-container', className='table'),
    ], className='graphDiv'),
    # Datatable graphical bug Fix
    html.Div(dte.DataTable(rows=[{}]), style={'display': 'none'}),
], className='window')
#----------------------------------------------Callback Functions-------------------------------------------------------

# Hides live graph
@app.callback(Output('live-graph-container', 'style'),
              [Input('update-dropdown', 'value')])
def toggle_container(toggle_value):
    if toggle_value == True:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# Hides history graph
@app.callback(Output('history-graph-container', 'style'),
              [Input('update-dropdown', 'value')])
def toggle_container(toggle_value):
    if toggle_value == True:
        return {'display': 'none'}
    else:
        return {'display': 'block'}
# Hides live graph update
@app.callback(Output('live-graph-update', 'interval'),
              [Input('update-dropdown', 'value')])
def toggle_container(toggle_value):
    if toggle_value == True:
        return 500
    else:
        return 2147483647

# Stops live container update
@app.callback(Output('table-update', 'interval'),
              [Input('update-dropdown', 'value')])
def toggle_container(toggle_value):
    if toggle_value == True:
        return 1500
    else:
        return 2147483647

# Updates graph-live figure
@app.callback(Output('live-graph', 'figure'),
              [Input('live-graph-update', 'n_intervals'),
               Input('update-dropdown', 'value')])
def display_page(intervals, graphStatus):
   #print("live-graph")
    if(graphStatus == True):
        ltime = int(time.time() * 10)
        dataSpike = aero.getData(timeFrom=ltime - 101, timeTo=ltime)
        hrpi_array = []
        eval_array = []
        time_array = []
        for record in dataSpike:
            time_array.append(int(ltime) * 100)
            if (record[1] != None):
                hrpi_array.append(record[2].get('data'))
                eval_array.append(record[2].get('eval'))
            else:
                hrpi_array.append(0)
                eval_array.append(0)
            ltime += 1
        trace = Scatter(
            x=time_array,
            y=hrpi_array,
            hovertext=hrpi_array,
            name="HRPI",
            mode='markers+lines',
            visible=True,
            marker=dict(
                size='7',
                cmin=0,
                cmax=2,
                cauto=False,
                color=eval_array,
                showscale=True,
                colorscale=[
                    [0, 'rgb(0,255,0)'],
                    [0.33, 'rgb(0,255,0)'],

                    [0.33, 'rgb(255,255,0)'],
                    [0.66, 'rgb(255,255,0)'],

                    [0.66, 'rgb(255,0,0)'],
                    [1, 'rgb(255,0,0)'],
                ],
                colorbar=dict(
                    tickmode='array',
                    title='Danger Level',
                    titleside='top',
                    tickvals=[0.4, 1, 1.6],
                    ticktext=['Safe', 'Alert', 'Danger'],
                    dtick=(1),
                )
            ),
            line=dict(
                width='1',
                color='rgb(192,192,192)',
            )
        )
        layout = dict(
            title='Real-Time HRPI statistics graph',
            height=500,
            autosize=True,
            xaxis=dict(
                constrain='range',
                constraintoward='right',
                fixedrange=True,
                rangemode='normal',
                range=[time_array[0], time_array[-1]],
                type='date'
            ),
            yaxis=dict(
                fixedrange=True,
                range=list([0, 3]),
                autorange=False,
                nticks=6,
            )
        )
        return Figure(data=[trace], layout=layout)
    else:
        return Figure()

# Updates history-graph figure
@app.callback(Output('history-graph', 'figure'),
              [Input('update-dropdown', 'value'),
               Input('hour-dropdown', 'value'),
               Input('minute-dropdown', 'value'),
               Input('date-input', 'date'),])
def display_history(graphStatus, valueHours, valueMinutes, valueDate):
    #print("history-graph")
    update_time = int(time.mktime(dt.strptime(valueDate, "%Y-%m-%d").timetuple()))
    timeReadFrom = (update_time + int(valueHours) * 3600 + int(valueMinutes) * 60) * 10
    timeReadTo = (update_time + int(valueHours) * 3600 + (int(valueMinutes) + 5) * 60) * 10
    dataSpike = aero.getData(timeFrom=timeReadFrom, timeTo=timeReadTo+1)
    
    hrpi_array = []
    eval_array = []
    time_array = []
    for record in dataSpike:
        time_array.append(timeReadFrom * 100)
        if (record[1] != None):
            hrpi_array.append(record[2].get('data'))
            eval_array.append(record[2].get('eval'))
        else:
            hrpi_array.append(0)
            eval_array.append(0)
        timeReadFrom += 1
    trace = Scatter(
        x=time_array,
        y=hrpi_array,
        name="HRPI",
        mode='markers+lines',
        visible=True,
        marker=dict(
            size='7',
            cmin=0,
            cmax=2,
            cauto=False,
            color=eval_array,
            showscale=True,
            colorscale=[
                [0, 'rgb(0,255,0)'],
                [0.33, 'rgb(0,255,0)'],

                [0.33, 'rgb(255,255,0)'],
                [0.66, 'rgb(255,255,0)'],

                [0.66, 'rgb(255,0,0)'],
                [1, 'rgb(255,0,0)'],
            ],
            colorbar=dict(
                tickmode='array',
                title='Danger Level',
                titleside='top',
                tickvals=[0.4, 1, 1.6],
                ticktext=['Safe', 'Suspicious', 'Dangerous'],
                dtick=(1),
            )
        ),
        line=dict(
            width='1',
            color='rgb(192,192,192)',
        )
    )
    layout = dict(
        title='History time graph',
        height=500,
        autosize=True,
        xaxis=dict(
            constrain='range',
            constraintoward='right',
            range=[time_array[0], time_array[-1]],

            rangeslider=dict(
                autorange=False,
                range=[time_array[0], time_array[-1]],
                yaxis=dict(
                    rangemode='match'
                )
            ),
            type='date'
        ),
        yaxis=dict(
            fixedrange=True,
            range=list([0, 3]),
            autorange=False,
            nticks=6,
        )
    )
    return Figure(data=[trace], layout=layout)

# Updates Live Table
@app.callback(Output('live-table-container', 'children'),
              [Input('update-dropdown', 'value'),
              Input('table-update', 'n_intervals')])
def compute_value(graphStatus, intervals):
   #print("live-table")
    if (graphStatus == True):
        ltime = int(time.time() * 10)
        records = aero.getDataIP(timeFrom=ltime - 101, timeTo=ltime)
        ip_requests = {}
        request_sum = 0
        for record in records:
            if (record[1] != None):
                IPlist = record[2]
                if IPlist is not None:
                    for IP in IPlist.items():
                        IP_address = (str(ipaddress.IPv4Address(int(IP[0]))))
                        ip_requests[IP_address] = ip_requests.get(IP_address, 0) + IP[1]
                        request_sum += IP[1]

        ip_count = len(ip_requests)
        ip_table = list()
        for IP, count in ip_requests.items():
            ip_table.append({'IP address': IP, 'Request amount': count})
        ip_table.sort(key=lambda x: -x['Request amount'])
        return [
            html.Div([
                        html.H2("IP statistics"),
                        html.H3("Active IP's: " + str(ip_count) + " Total requests: " + str(request_sum)),
                    ], className='tableHeader'),
            dte.DataTable(
                id='live-iptable',
                rows=ip_table,
                columns=['IP address', 'Request amount'],
                max_rows_in_viewport=1000,
                row_height=32,
                resizable=False,
                editable=False,
                row_selectable=False,
                filterable=False,
                sortable=False,
                enable_drag_and_drop=False,
            ),
        ]
    else:
        return []

# Updates History Table
@app.callback(Output('history-table-container', 'children'),
              [Input('update-dropdown', 'value'),
               Input('hour-dropdown', 'value'),
               Input('minute-dropdown', 'value'),
               Input('date-input', 'date'),
               Input('history-graph', 'relayoutData'),])
def compute_value(graphStatus, valueHours, valueMinutes, valueDate, relayout):
    if (graphStatus == False):
        # Selecting range input
        if relayout is None or 'autosize' in relayout:
            update_time = int(time.mktime(dt.strptime(valueDate, "%Y-%m-%d").timetuple()))
            timeReadFrom = (update_time + int(valueHours) * 3600 + int(valueMinutes) * 60) * 10
            timeReadTo = (update_time + int(valueHours) * 3600 + (int(valueMinutes) + 5) * 60) * 10
        else:
            # Selecting graph
            if 'xaxis.range' in relayout:
                timeReadFrom = int(
                    time.mktime(dt.strptime(relayout['xaxis.range'][0], "%Y-%m-%d %H:%M:%S.%f").timetuple()) * 10)
                timeReadTo = int(
                    time.mktime(dt.strptime(relayout['xaxis.range'][1], "%Y-%m-%d %H:%M:%S.%f").timetuple()) * 10)
            # Selecting slider
            else:

                timeReadFrom = int(
                    time.mktime(dt.strptime(relayout['xaxis.range[0]'], "%Y-%m-%d %H:%M:%S.%f").timetuple()) * 10)
                timeReadTo = int(
                    time.mktime(dt.strptime(relayout['xaxis.range[1]'], "%Y-%m-%d %H:%M:%S.%f").timetuple()) * 10)
        ip_requests = {}
        request_sum = 0
        records = aero.getDataIP(timeFrom=timeReadFrom, timeTo=timeReadTo)
        for record in records:
            if (record[1] != None):
                IPlist = record[2]
                if IPlist is not None:
                    for IP in IPlist.items():
                        IP_address = (str(ipaddress.IPv4Address(int(IP[0]))))
                        ip_requests[IP_address] = ip_requests.get(IP_address, 0) + IP[1]
                        request_sum += IP[1]

        ip_count = len(ip_requests)
        ip_table = list()
        for IP, count in ip_requests.items():
            ip_table.append({'IP address': IP, 'Request amount': count})
        ip_table.sort(key=lambda x: -x['Request amount'])

        return [
            html.Div([
                html.H2("IP statistics"),
                html.H3("Active IP's: " + str(ip_count) + " Total requests: " + str(request_sum)),
            ], className='tableHeader'),
            dte.DataTable(
                id='histoy-iptable',
                rows=ip_table,
                columns=['IP address', 'Request amount'],
                max_rows_in_viewport=1000,
                row_height=32,
                resizable=False,
                editable=False,
                row_selectable=False,
                filterable=False,
                sortable=False,
                enable_drag_and_drop=False,
            ),
        ]
    else:
        return []

#-----------------------------------------------CSS files---------------------------------------------------------------
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
@app.server.route('/static/<resource>')
def serve_static(resource):
    return flask.send_from_directory(STATIC_PATH, resource)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i",
                "/static/GUIstyle.css",
                ]


for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    #app.run_server(debug=False, host='0.0.0.0')
    app.run_server(debug=False, host='0.0.0.0', processes=3, threaded=False)
