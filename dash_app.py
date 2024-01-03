import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import json
import pandas as pd
from datetime import datetime

# Load and preprocess data
with open("declarations.json", "r") as f:
    declarations_data = json.load(f)['FemaWebDisasterDeclarations']

with open("summaries.json", "r") as f:
    summaries_data = json.load(f)['FemaWebDisasterSummaries']

merged_data = []
for declaration in declarations_data:
    for summary in summaries_data:
        if declaration["disasterNumber"] == summary["disasterNumber"]:
            try:
                begin_date = datetime.strptime(declaration["incidentBeginDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
                end_date = datetime.strptime(declaration["incidentEndDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
                duration_days = (end_date - begin_date).days
                duration_months = round(duration_days / 30, 2)  # Approximate conversion to months
            except:
                duration_months = None

            funding = summary.get("totalObligatedAmountHmgp", 0)
            
            # Handling None value for funding
            if funding is not None:
                formatted_funding = "${:,.2f}".format(funding)
            else:
                formatted_funding = "N/A"

            merged_data.append({
                "Disaster Type": declaration["incidentType"],
                "Funding": formatted_funding,
                "State": declaration["stateCode"],
                "Duration (months)": duration_months
            })

df = pd.DataFrame(merged_data)

# Create Dash app
app = dash.Dash(__name__)

# External CSS for a better look
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# Layout of the app
app.layout = html.Div([
    html.H1("Disaster Analysis", style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Label("Select State:"),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in ['All'] + list(df['State'].unique())],
                value='All'
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Select Metric:"),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[{'label': metric, 'value': metric} for metric in ['Funding', 'Duration (months)']],
                value='Funding'
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Select Disaster Type:"),
            dcc.Dropdown(
                id='disaster-dropdown',
                options=[{'label': d_type, 'value': d_type} for d_type in ['All'] + list(df['Disaster Type'].unique())],
                value='All'
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
    ], style={'padding': '20px'}),
    dcc.Graph(id='bar-chart')
])

# Callback for updating the visualization
@app.callback(
    Output('bar-chart', 'figure'),
    [
        Input('state-dropdown', 'value'),
        Input('metric-dropdown', 'value'),
        Input('disaster-dropdown', 'value')
    ]
)
def update_graph(state, metric, disaster_type):
    filtered_df = df
    if state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == state]
    if disaster_type != 'All':
        filtered_df = filtered_df[filtered_df['Disaster Type'] == disaster_type]
    
    title = f"{metric} by Disaster Type for State: {state}"
    fig = px.bar(filtered_df, x="Disaster Type", y=metric, title=title, hover_data=df.columns)
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
