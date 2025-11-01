# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    
    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    
    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for Pie Chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Pie chart for all sites showing successful launches
        success_counts = spacex_df[spacex_df['class']==1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Successes']
        fig = px.pie(success_counts, 
                     names='Launch Site', 
                     values='Successes', 
                     title='Total Successful Launches by Site', 
                     hole=0.3)  # Donut style
    else:
        # Pie chart for a specific site showing Success vs Failure
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        filtered_df['Outcome'] = filtered_df['class'].map({0:'Failure', 1:'Success'})
        outcome_counts = filtered_df['Outcome'].value_counts().reset_index()
        outcome_counts.columns = ['Outcome', 'Count']
        fig = px.pie(outcome_counts, 
                     names='Outcome', 
                     values='Count', 
                     title=f'Success vs. Failure for site {selected_site}',
                     hole=0.3)
    return fig

# TASK 4: Callback for Scatter Chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask].copy()
    
    # Map class 0/1 to Failure/Success
    filtered_df['Outcome'] = filtered_df['class'].map({0:'Failure', 1:'Success'})
    
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(filtered_df,
                     x='Payload Mass (kg)',
                     y='Outcome',
                     color='Booster Version Category',
                     title='Payload vs. Success Correlation',
                     hover_data=['Launch Site'])
    return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8050)  # Default port
