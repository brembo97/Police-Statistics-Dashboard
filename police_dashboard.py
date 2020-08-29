import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import pandas as pd
from plotly import graph_objs as go
import plotly.express as px

police_final = pd.read_csv('./Data/police_final.csv', index_col=False)
info_canton = pd.read_csv('Data/info_canton.csv', index_col=False)

app = dash.Dash()

main_scatter = go.Scatter(
    x=info_canton['Tasa'],
    y=info_canton['Media'],
    text=info_canton['Canton'],
    name='Canton',
    mode='markers',
    opacity=0.7,
    marker=dict(
        symbol='diamond',
        size=12
    ))

cr_tasa = info_canton['Tasa'].mean()
cr_media = info_canton['Media'].mean()
x_max = info_canton['Tasa'].max() * 1.05
x_min = info_canton['Tasa'].min() * 0.95
y_max = info_canton['Media'].max() * 1.05
y_min = 0

main_lineh = {'x': [x_min, 0, x_max],
              'y': [cr_media, cr_media, cr_media],
              'name': 'Promedio CR',
              'mode': 'lines',
              'text': 'Delitos',
              'line': dict(color='rgb(228, 26, 28)')}

main_linev = {'x': [cr_tasa, cr_tasa, cr_tasa],
              'y': [y_min, y_max],
              'mode': 'lines',
              'text': 'Tasa',
              'showlegend': False,
              'line': dict(color='rgb(228, 26, 28)')}

main_layout = go.Layout(title='Tendencia de Crimenes',
                        xaxis=dict(title='Tasa de Crecimiento', range=[x_min, x_max]),
                        yaxis=dict(title='Frecuencia', range=[y_min, y_max]),
                        hovermode='closest')

main_figure = go.Figure(data=[main_scatter, main_lineh, main_linev],
                        layout=main_layout)

app.layout = html.Div([
    html.H1('Estadisticas Policiales 2015-2019'),
    html.Div([
        dcc.Graph(
            id='tasa_canton',
            figure=main_figure
        )
    ], style={'width': '50vw',
              'display': 'inline-block',
              'height': '50vh'}),
    html.Div([
        dcc.Graph(id='delitos')
    ], style={'width': '40vw',
              'display': 'inline-block',
              'marginLeft': '30px',
              'height': '50vh'}),
    html.Div([
        dcc.Graph(id='distritos')
    ], style={'width': '80vw',
              'height': '30vh',
              'display': 'inline-block',
              'margin': '0 auto'})
])


@app.callback(Output('delitos', 'figure'),
              [Input('tasa_canton', 'clickData')])
def update_canton(clickData):
    if (clickData):
        canton = clickData['points'][0]['text']
        grouped_canton = police_final.groupby(['Canton', 'Delito'], as_index=False)['Count'].sum()
        canton_selec = grouped_canton[grouped_canton['Canton'] == canton]

        fig = px.bar(x=canton_selec['Delito'],
                     y=canton_selec['Count'],
                     title='Delitos en {}'.format(canton))
        fig.update_layout(
            xaxis_title="Delito",
            yaxis_title="Frecuencia",
        )

        return fig

    return {}


@app.callback(Output('distritos', 'figure'),
              [Input('tasa_canton', 'clickData')])
def update_distritos(clickData):
    if (clickData):
        canton = clickData['points'][0]['text']
        grouped_canton = police_final.groupby(['Canton', 'Distrito', 'Ano'], as_index=False)['Count'].sum()
        canton_selec = grouped_canton[grouped_canton['Canton'] == canton]

        fig = px.line(x=canton_selec['Ano'],
                      y=canton_selec['Count'],
                      color=canton_selec['Distrito'],
                      title='Distritos de {}'.format(canton)
                      )
        fig.update_layout(
            xaxis=dict(tickmode='array',
                       tickvals=canton_selec['Ano'].values,
                       ticktext=canton_selec['Ano'].values),
            xaxis_title="Ano",
            yaxis_title="Frecuencia")

        for obj in fig.data:
            obj.update(mode='markers+lines')

        return fig

    return {}


if __name__ == "__main__":
    app.run_server(debug=True)
