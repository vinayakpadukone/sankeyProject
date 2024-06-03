from logging.config import dictConfig
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import mysql.connector
import random
from app.database.repositories import CaseRepository
from app.service.services import CaseService
from config.logging_config import LOGGING_CONFIG
from config.settings import *
import logging
import urllib.parse


# Set up logging
def setup_logging():
    dictConfig(LOGGING_CONFIG)

# Get the logger for the main module
logger = logging.getLogger(__name__)

# Initialize repositories with database configuration
case_repository = CaseRepository(DATABASE_CONFIG)

# Initialize services with repositories
case_service = CaseService(case_repository)

# MySQL database configuration
db = mysql.connector.connect(**DATABASE_CONFIG)

# Initialize dash app
app = dash.Dash(__name__)

# Dash app UI layout
app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
    ),
    html.Div(className='container mt-3 clearfix', children=[
        html.Div(className='row justify-content-center', children=[
            html.Img(src='https://televital.com/images/logo.png', className='img-fluid'),
        ]),
        html.Div(className='form mt-4', children=[
            html.Div(className='form-group form-inline', children=[
                html.Div(className='col-3 form-label', children=[
                    html.Label('Select Speciality', className='form-label col-auto justify-content-end'),
                ]),
                html.Div(className='col-4', children=[
                    dcc.Dropdown(
                        id='selectedSpeciality',
                        options=[
                            {'label': 'Cardiology', 'value': '10'},
                            {'label': 'Dermatology', 'value': '9'},
                            {'label': 'Endocrinology', 'value': '8'},
                            {'label': 'Gastroenterology', 'value': '6'},
                            {'label': 'General Medicine', 'value': '1'},
                            {'label': 'Nephrology', 'value': '11'},
                            {'label': 'Neurology', 'value': '12'},
                            {'label': 'Obstetrics & Gynaecology', 'value': '2'},
                            {'label': 'Oncologist', 'value': '7'},
                            {'label': 'Orthopaedics', 'value': '4'},
                            {'label': 'Paediatrics', 'value': '3'},
                            {'label': 'Physical Medicine and Rehabilitation', 'value': '5'},
                            {'label': 'Urology', 'value': '13'}
                        ],
                        value='1',
                        className='form-select'
                    ),
                ]),
            ]),
            html.Div(className='form-group form-inline', children=[
                html.Div(className='col-3 form-label', children=[
                    html.Label('Filter by Symptoms', className='form-label col-auto justify-content-end'),
                ]),
                html.Div(className='col-4', children=[
                    dcc.Input(
                        id='searchSymptoms',
                        type="text",
                        className='form-control',
                        placeholder="Type Symptom Name",
                        value=''
                    )
                ]),
            ]),
            html.Div(className='form-group form-inline', children=[
                html.Div(className='col-3 form-label', children=[
                    html.Label('Select Date Range', className='form-label col-auto justify-content-end'),
                ]),
                html.Div(className='col-4', children=[
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        # calendar_orientation='vertical',
                        clearable=True,
                        # className='mt-3'
                    )
                ]),
            ]),
        ]),
        html.Button('Load Graph', id='submit-val', n_clicks=0, className='btn btn-outline-primary mt-3 float-right'),
    ]),
    dcc.Loading(
        id="loading",
        type="default",
        children=[
            dcc.Graph(id='plotlyGraph', className='mt-3')
        ]
    ),
    dcc.Location(id='url', refresh=False),
    #html.Div(id='page-content')
])

@app.callback(
    Output('date-range-picker', 'start_date'),
    Output('date-range-picker', 'end_date'),
    Output('selectedSpeciality', 'value'),
    Output('searchSymptoms', 'value'),
    Input('url', 'search')
)
def update_date_picker(search):
    if search:
        query_params = urllib.parse.parse_qs(search.lstrip('?'))
        _from_date = query_params.get('fromDate', [''])[0]
        _to_date = query_params.get('toDate', [''])[0]
        _selectedSpeciality = query_params.get('speciality', [''])[0]
        _searchSymptoms = query_params.get('symptoms', [''])[0]
        if _from_date:
            from_date=_from_date
        else:
            from_date=''

        if _to_date:
            to_date=_to_date
        else:
            to_date=''

        if _selectedSpeciality:
            selectedSpeciality=_selectedSpeciality
        else:
            selectedSpeciality=1

        if _searchSymptoms:
            searchSymptoms= _searchSymptoms
        else:
            searchSymptoms=''

        return from_date, to_date, selectedSpeciality,searchSymptoms
    return None, None, 1, None

# # Update URL based on DatePickerRange changes
# @app.callback(
#     Output('url', 'search'),
#     Input('submit-val', 'n_clicks'),
#     State('date-range-picker', 'start_date'),
#     State('date-range-picker', 'end_date'),
#     State('selectedSpeciality', 'value'),
#     State('searchSymptoms', 'value'),
#     State('url', 'search')
# )
# def update_url(n_clicks, start_date, end_date,selectedSpeciality,searchSymptoms, current_search):
#     query_params = urllib.parse.parse_qs(current_search[1:]) if current_search else {}
#     if start_date:
#         query_params['fromDate'] = start_date
#     if end_date:
#         query_params['toDate'] = end_date
#     if selectedSpeciality:
#         query_params['specality'] = selectedSpeciality
#     if searchSymptoms:
#         query_params['symptoms'] = searchSymptoms
#     new_search = '?' + urllib.parse.urlencode(query_params, doseq=True)
#     return new_search

@app.callback(
    Output('plotlyGraph', 'figure'),
    Input('submit-val', 'n_clicks'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('selectedSpeciality', 'value'),
    Input('searchSymptoms', 'value'),
    Input('url', 'search')
)
def update_graph(n_clicks, start_date, end_date, selectedSpeciality, searchSymptoms,search):
    logger.info(f"in update_graph: {n_clicks}, {start_date}, {end_date}, {selectedSpeciality}, {searchSymptoms}")
    fig = go.Figure()

    ctx = dash.callback_context
    logger.info(f"ctx triggered {ctx.triggered}")

    # Reading from URL
    query_params = urllib.parse.parse_qs(search.lstrip('?'))
    symptom_name = query_params.get('symptomName', [''])[0]
    from_date = query_params.get('fromDate', [''])[0]
    to_date = query_params.get('toDate', [''])[0]
    speciality = query_params.get('speciality', [''])[0]

    # print(symptom_name)

    if not ctx.triggered:
        # If no input is triggered, return the existing graph
        return dash.no_update

    # Get the ID of the triggered input
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'submit-val' and n_clicks > 0:
        if start_date and end_date and selectedSpeciality:
            # fig = plot_graph_1(start_date, end_date, selectedSpeciality)
            fig = plot_sankey(start_date, end_date, selectedSpeciality, searchSymptoms)
    
    else:
        if start_date and end_date and selectedSpeciality:
            # fig = plot_graph_1(start_date, end_date, selectedSpeciality)
            fig = plot_sankey(start_date, end_date, selectedSpeciality, searchSymptoms)
        else:
            # If the Submit button is not clicked or has not been clicked yet, return the existing graph
            return dash.no_update
    
    return fig



def plot_graph_1(start_date, end_date, selectedSpeciality):
    logger.info(f"in plot_graph_1: {start_date}, {end_date}, {selectedSpeciality}")

    cursor = db.cursor()

    query = "SELECT FROM_UNIXTIME(cs.CompletedTime, '%Y-%M') AS YearMonth, COUNT(*) FROM TBL_Case cs \
                LEFT JOIN TBL_Doctor sshdoc ON cs.CompletedBy = sshdoc.DoctorId \
                WHERE cs.CompletedTime BETWEEN UNIX_TIMESTAMP(%s) AND UNIX_TIMESTAMP(%s) and sshdoc.DocSpecalityId=%s \
                GROUP BY FROM_UNIXTIME(cs.CompletedTime, '%Y-%m')"
    cursor.execute(query, (start_date, end_date, selectedSpeciality))

    rows = cursor.fetchall()
    logger.debug(f"rows: {rows}")
    logger.debug(f"columns: {cursor.description}")

    # Create plotly graph
    fig = go.Figure(data=go.Scatter(x=[row[0] for row in rows], y=[row[1] for row in rows]))

    return fig


# def plot_sankey(start_date, end_date, Specality, searchSymptoms):
def plot_sankey(start_date, end_date, speciality, searchSymptoms):
    logger.info(f"in plot_sankey: {start_date}, {end_date}, {speciality}, {searchSymptoms}")

    # get all symptoms between dates and by speciality
    response = case_service.get_symptoms_by_case_speciality_and_bw_dates(start_date, end_date, speciality)
    logger.debug(f"qry get_symptoms_by_case_speciality_and_bw_dates: {response}")

    # extract data and column headings
    data = response['rows']
    column_names = response['cols']

    # convert to dataframe obj
    df1 = pd.DataFrame(data, columns=column_names)
    logger.debug(f"df1: pd.DataFrame: {df1}")

    if df1.empty:
        return go.Figure()


    ###
    # filter symptoms, extract diagnosis list & fetch medicines for that diagnosis prescribed b/w dates
    ###
    # filter symptoms
    if searchSymptoms:
        f_df1 = df1[df1["Src"].str.contains(searchSymptoms)]
        logger.debug(f"filtered dataframe by symptom: {f_df1}")
    else:
        f_df1 = df1

    if f_df1.empty:
        return go.Figure()
    
    # f_df1.sort_values(by=["Count"],ascending=False)

    # extract Trgt from filtered dataframe
    d_list = list(set(f_df1['Trgt'].unique()))
    logger.debug(f"Trgt from f_df1: {d_list}")

    # get all medicines for above filtered diagnosis 
    diag_med_response = case_service.get_medicine_bw_dates_by_diagnosis_list(start_date, end_date, d_list)
    logger.debug(f"qry get_medicine_bw_dates_by_diagnosis_list: {diag_med_response}")

    # extract data and column headings
    data2 = diag_med_response['rows']
    column_names2 = diag_med_response['cols']

    # convert to dataframe obj
    df2 = pd.DataFrame(data2, columns=column_names2)
    logger.debug(f"df2: pd.DataFrame: {df2}")

    ###
    # fetch caseids matching symptom & fetch medicines of those cases prescribed b/w dates
    ###
    # get caseids of symptoms between dates and by speciality
    symp_caseid_list = case_service.get_symptoms_caseid_by_case_speciality_and_bw_dates(start_date, end_date, speciality, searchSymptoms)
    logger.debug(f"qry get_symptoms_caseid_by_case_speciality_and_bw_dates: {symp_caseid_list}")

    # extract data and column headings
    data3 = symp_caseid_list['rows']
    column_names3 = symp_caseid_list['cols']

    # convert to dataframe obj
    df3 = pd.DataFrame(data3, columns=column_names3)
    logger.debug(f"df3: pd.DataFrame: {df3}")
    
    # extract CaseId from dataframe
    caseid_list = list(set(df3['CaseId'].unique()))
    logger.debug(f"CaseId from df3: {caseid_list}")

    # FIXME handel empty caseid_list
    # get all medicines for above filtered diagnosis 
    diag_med_response = case_service.get_medicine_bw_dates_by_caseid_list(start_date, end_date, caseid_list)
    logger.debug(f"qry get_medicine_bw_dates_by_caseid_list: {diag_med_response}")

    # extract data and column headings
    data4 = diag_med_response['rows']
    column_names4 = diag_med_response['cols']

    # convert to dataframe obj
    df4 = pd.DataFrame(data4, columns=column_names4)
    logger.debug(f"df4: pd.DataFrame: {df4}")

    # concat both the dataframes
    df = pd.concat([f_df1, df4])
    logger.debug(f"df: pd.DataFrame: {df}")
    print(df)
    df.sort_values(by=["Count"],ascending=False)
    logger.debug(f"df: pd.DataFrame sorted by count desc: {df}")
    # Define unique nodes
    nodes = list(set(df['Src'].unique()) | set(df['Trgt'].unique()))

    total_counts = df['Count'].sum()
    print(total_counts)
    df['Average'] = df['Count'] / total_counts * 100
    print(df['Average'])
    

    hover_text = [f'Percentage: {value}%' for value in df['Average']]

    # Define Sankey trace
    trace = go.Sankey(
        node=dict(
            pad=15,
            thickness=50,
            line=dict(color='black', width=0.5),
            label=nodes,
            x= [0.1, 0.5, 0.9],
            # y= [0.7, 0.5, 0.2],
            color=[f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})" for _ in range(len(df))]
        ),
        link=dict(
            source=df['Src'].apply(lambda x: nodes.index(x)),
            target=df['Trgt'].apply(lambda x: nodes.index(x)),
            value=df['Count'],
            customdata=hover_text,
            hovertemplate='Source: %{source.label}<br>Target: %{target.label}<br>%{customdata}<extra></extra>',
            color=[f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})" for _ in range(len(df))]
        )
    )
    
    # Calculate height based on the number of rows
    height = max(len(df) * 15, 400)  # Minimum height is 400

    # Define layout with dynamic height
    layout = go.Layout(
        # title='Sankey Chart - Oncologist - 2022-2023',
        font=dict(size=10),
        height=height
    )

    return {
        'data': [trace],
        'layout': layout
    }



if __name__ == '__main__':
    setup_logging()
    app.run_server(debug=True, port=runtime_port)
