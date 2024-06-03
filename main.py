import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import mysql.connector

app = dash.Dash(__name__)

# MySQL database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="uptelemed_stqc"
)

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
                html.Div(className='form-label', children=[
                    html.Label('Select Option', className='form-label col-auto'),
                ]),
                html.Div(className='col-4', children=[
                    dcc.Dropdown(
                        id='selectOption',
                        options=[
                            {'label': 'All', 'value': 'ALL'},
                            {'label': 'New', 'value': 'NEW'},
                            {'label': 'Follow up', 'value': 'FOLLOWUP'}
                        ],
                        value='ALL',
                        className='form-select'
                    ),
                ]),
            ]),
            html.Div(className='form-group form-inline', children=[
                html.Div(className='form-label', children=[
                    html.Label('Select Type', className='form-label col-auto'),
                ]),
                html.Div(className='col-4', children=[
                    dcc.RadioItems(
                        id='selectType',
                        options=[
                            {'label': 'Graph 1', 'value': 'g1'},
                            {'label': 'Graph 2', 'value': 'g2'},
                            {'label': 'Graph 3', 'value': 'g3'}
                        ],
                        value='',
                        className='col-auto form-check-inline',
                        inputClassName='form-check-input',
                        labelClassName='form-check-label col-auto'
                    ),
                ]),
            ]),
            dcc.DatePickerRange(
                id='date-range-picker',
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                calendar_orientation='vertical',
                clearable=True,
                className='mt-3'
            )
        ]),
        html.Button('Submit', id='submit-val', n_clicks=0, className='btn btn-primary mt-3 float-right'),
    ]),
    dcc.Graph(id='plotlyGraph', className='mt-3')
])

@app.callback(
    Output('plotlyGraph', 'figure'),
    Input('submit-val', 'n_clicks'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('selectOption', 'value'),
    Input('selectType', 'value')
)
def update_graph(n_clicks, start_date, end_date, selectOption, selectType):
    print(n_clicks, start_date, end_date, selectOption, selectType)
    fig = go.Figure()

    ctx = dash.callback_context
    print('ctx triggered', ctx.triggered)

    if not ctx.triggered:
        # If no input is triggered, return the existing graph
        return dash.no_update

    # Get the ID of the triggered input
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'submit-val' and n_clicks > 0:
        if start_date and end_date:
            fig = plot_graph_1(start_date, end_date, selectOption)
    else:
        # If the Submit button is not clicked or has not been clicked yet, return the existing graph
        return dash.no_update
    
    return fig

def plot_graph_1(start_date, end_date, selectOption):
    cursor = db.cursor()
    if selectOption == 'ALL':
        query = "SELECT CaseType, COUNT(*) FROM TBL_Case \
                    WHERE CaseStartTime BETWEEN UNIX_TIMESTAMP(%s) AND UNIX_TIMESTAMP(%s) \
                    GROUP BY CaseType"
        cursor.execute(query, (start_date, end_date))
    else:
        query = "SELECT CaseType, COUNT(*) FROM TBL_Case \
                    WHERE CaseStartTime BETWEEN UNIX_TIMESTAMP(%s) AND UNIX_TIMESTAMP(%s) \
                    AND CaseType = %s \
                    GROUP BY CaseType"
        cursor.execute(query, (start_date, end_date, selectOption))

    rows = cursor.fetchall()
    print(rows)

    # Create plotly graph
    fig = go.Figure(data=go.Scatter(x=[row[0] for row in rows], y=[row[1] for row in rows]))

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
