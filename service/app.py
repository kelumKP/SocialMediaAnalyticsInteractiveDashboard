from enum import auto
from operator import itemgetter
from tkinter import Scrollbar
from bokeh.transform import cumsum
from bokeh.plotting import figure
from bokeh.palettes import Category20c, Category20
from math import pi
from turtle import title, width
from langdetect import detect
import pathlib
import holoviews as hv
import hvplot.pandas  # noqa
import numpy as np
import pandas as pd
import panel as pn
import datetime as dt
import calendar
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections.abc import Iterable
import hvplot.networkx as hvnx
import networkx as nx
import holoviews as hv
import dask.dataframe as dd

##
##files = ['https://raw.githubusercontent.com/kelumKP/csv_files/master/PrimeLands.csv', 
##         'https://raw.githubusercontent.com/kelumKP/csv_files/master/BlueOcean.csv', 
##         'https://raw.githubusercontent.com/kelumKP/csv_files/master/CBHLands.csv',
##         'https://raw.githubusercontent.com/kelumKP/csv_files/master/HomeLands.csv', 
##         'https://raw.githubusercontent.com/kelumKP/csv_files/master/HouseAndLandsLk.csv', 
##         'https://raw.githubusercontent.com/kelumKP/csv_files/master/SkyLine.csv']

#df_all_data = pd.DataFrame()

#for file in files:
#    if file.endswith('.csv'):
#        df_all_data = df_all_data.append(pd.read_csv(file, encoding = "ISO-8859-1", engine='python')) 
#df_all_data = pd.read_csv('https://raw.githubusercontent.com/kelumKP/csv_files/master/all_data.csv', encoding = "ISO-8859-1", engine='python')
df_all_data = dd.read_csv('all_data.csv', encoding = "ISO-8859-1", engine='python', dtype='object')

df_all_data = df_all_data.compute()

df_all_data['post_id'] = df_all_data['post_id'].replace('', np.nan)
df_all_data = df_all_data.dropna(axis=0, subset=['post_id'])

df_all_data['created_time'] = df_all_data['created_time'].replace('', np.nan)
df_all_data = df_all_data.dropna(axis=0, subset=['created_time'])

df_all_data['updated_time'] = df_all_data['updated_time'].replace('', np.nan)
df_all_data = df_all_data.dropna(axis=0, subset=['updated_time'])

df_all_data['created_date'] = pd.to_datetime(
    df_all_data['created_time']).dt.date

# Fill NAs with 0s and create GDP per capita column
df_all_data = df_all_data.fillna(0)


df_all_data['created_year'] = pd.to_datetime(
    df_all_data['created_time']).dt.year
df_all_data['created_month'] = pd.to_datetime(
    df_all_data['created_time']).dt.month

df_all_data['shares'] = df_all_data['shares_count'].replace(np.nan, 0)
df_all_data['comments'] = df_all_data['comments_count'].replace(np.nan, 0)
df_all_data['reactions'] = df_all_data['reactions_count'].replace(np.nan, 0)
df_all_data['like'] = df_all_data['like_count'].replace(np.nan, 0)
df_all_data['love'] = df_all_data['love_count'].replace(np.nan, 0)
df_all_data['haha'] = df_all_data['haha_count'].replace(np.nan, 0)
df_all_data['wow'] = df_all_data['wow_count'].replace(np.nan, 0)
df_all_data['sad'] = df_all_data['sad_count'].replace(np.nan, 0)
df_all_data['angry'] = df_all_data['angry_count'].replace(np.nan, 0)

df_all_data['created_time'] = pd.to_datetime(df_all_data['created_time'])
df_all_data['updated_time'] = pd.to_datetime(df_all_data['updated_time'])

df_all_data.sort_values(by='created_time', inplace=True)

# Make DataFrame Pipeline Interactive
idf_all_data = df_all_data.interactive()

df_all_data.set_index('created_date', inplace=True)

months_slider = pn.widgets.IntSlider(name='Month', start=1, end=12, step=1)

years_slider = pn.widgets.IntSlider(name='Year', start=2021, end=2022, step=1)


yaxis_all_data_dimentions = pn.widgets.RadioButtonGroup(
    name='Dimentions',
    options=['shares', 'comments', 'reactions',
             'like', 'love', 'haha', 'wow', 'sad', 'angry'],
    button_type='success',
    width = 950
)

ipipeline_all_data = (
    idf_all_data[
        (idf_all_data.created_month == months_slider) &
        (idf_all_data.created_year == years_slider)
    ]
    .groupby(['company', 'message', 'created_date'])[yaxis_all_data_dimentions].mean()
    .to_frame()
    .reset_index()
    .sort_values(by='created_date')
    .reset_index(drop=True)
)


def environment():
    try:
        get_ipython()
        return "notebook"
    except:
        return "server"


environment()

PALETTE = ["#ff6f69", "#ffcc5c", "#ee82ee", "#5234b0", "#008000", "#ffa500"]
pn.Row(
    pn.layout.HSpacer(height=50, background=PALETTE[0]),
    pn.layout.HSpacer(height=50, background=PALETTE[1]),
    pn.layout.HSpacer(height=50, background=PALETTE[2]),
    pn.layout.HSpacer(height=50, background=PALETTE[3]),
    pn.layout.HSpacer(height=50, background=PALETTE[4]),
    pn.layout.HSpacer(height=50, background=PALETTE[5]),

)

if environment() == "server":
    theme = "fast"
else:
    theme = "simple"


itable_all_data = ipipeline_all_data.pipe(
    pn.widgets.Tabulator, pagination='remote', page_size=10, theme=theme, height=350, layout='fit_columns', width=950)

ihvplot_all_data = ipipeline_all_data.hvplot(x='created_date', y=yaxis_all_data_dimentions,
                                             by='company', color=PALETTE, line_width=3, height=400, title="Monthly Interaction")

depth_hist = ipipeline_all_data.hvplot(x=['shares', 'comments', 'reactions', 'like',
                                       'love', 'haha', 'wow', 'sad', 'angry'], kind='hist', responsive=True, min_height=200)

df_primelands_comments = dd.read_csv('PrimeLands_Comments.csv', encoding = "ISO-8859-1", engine='python', dtype='object')
df_primelands_comments = df_primelands_comments.compute()

"""
def detect_en(text):
    try:
        return detect(text) == 'en'
    except:
        return False
df_primelands_comments = df_primelands_comments[df_primelands_comments['comment'].apply(
    detect_en)]
"""

analyzer = SentimentIntensityAnalyzer()

sentiment_score = []
for index, row in df_primelands_comments.iterrows():
    # print(analyzer.polarity_scores(row['comment']))
    df_primelands_comments.at[index, 'negative'] = analyzer.polarity_scores(
        row['comment'])['neg']
    df_primelands_comments.at[index, 'neutral'] = analyzer.polarity_scores(row['comment'])[
        'neu']
    df_primelands_comments.at[index, 'positive'] = analyzer.polarity_scores(
        row['comment'])['pos']
    df_primelands_comments.at[index, 'compound'] = analyzer.polarity_scores(
        row['comment'])['compound']

df_primelands_comments['comment_date'] = df_primelands_comments['comment_date'].replace(
    '', np.nan)
df_primelands_comments = df_primelands_comments.dropna(
    axis=0, subset=['comment_date'])

df_primelands_comments['created_date'] = pd.to_datetime(
    df_primelands_comments['comment_date']).dt.date

df_primelands_comments['created_year'] = pd.to_datetime(
    df_primelands_comments['comment_date']).dt.year
df_primelands_comments['created_month'] = pd.to_datetime(
    df_primelands_comments['comment_date']).dt.month

df_primelands_comments['comment_date'] = pd.to_datetime(
    df_primelands_comments['comment_date'])
df_primelands_comments.sort_values(by='comment_date', inplace=True)

# Make DataFrame Pipeline Interactive
idf_primelands_comments = df_primelands_comments.interactive()

df_primelands_comments.set_index('comment_date', inplace=True)

yaxis_primelandscomments_dimentions = pn.widgets.RadioButtonGroup(
    name='Dimentions',
    options=['negative', 'neutral', 'positive', 'compound'],
    button_type='success',
    width = 950
)

ipipeline_primelands_comments = (
    idf_primelands_comments[
        (idf_primelands_comments.created_month == months_slider) &
        (idf_primelands_comments.created_year == years_slider)
    ]
    .groupby(['comment', 'comment_date'])[yaxis_primelandscomments_dimentions].mean()
    .to_frame()
    .reset_index()
    .sort_values(by='comment_date')
    .reset_index(drop=True)
)


itable_primelands_comments = ipipeline_primelands_comments.pipe(
    pn.widgets.Tabulator, pagination='remote', page_size=10, theme=theme, height=400, layout='fit_columns', width=950)

positive = df_primelands_comments['positive'].sum()
neutral = df_primelands_comments['neutral'].sum()
negative = df_primelands_comments['negative'].sum()
display_name = "Prime Lands"

positive = (float(round(positive, 2)))
neutral = (float(round(neutral, 2)))
negative = (float(round(negative, 2)))
total = positive + neutral + negative

positive = (float(round(positive*100/total, 2)))
neutral = (float(round(neutral*100/total, 2)))
negative = (float(round(negative*100/total, 2)))


x = {
    'positive': positive,
    'neutral': neutral,
    'negative': negative
}

chart_colors = ['#4fb443', '#d9b42c', '#de061a',
                '#d8e244', '#eeeeee', '#56e244', '#007bff', 'black']

data = pd.Series(x).reset_index(name='value').rename(
    columns={'index': 'sentiment'})
data['angle'] = data['value']/data['value'].sum() * 2*pi
data['color'] = chart_colors[:len(x)]

p = figure(plot_height=600, title="Prime Land Sentiment Analysis for Facebook Data", toolbar_location=None,
           tools="hover", tooltips="@sentiment: @value%", x_range=(-0.5, 1.0))

r = p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='sentiment', source=data)

p.axis.axis_label = None
p.axis.visible = False
p.grid.grid_line_color = None

pie_chart_primelands_comments_sentiment = pn.pane.Bokeh(
    p, theme="dark_minimal", width=950)


# Create a BA model graph
n = 1000
m = 2
G = nx.generators.barabasi_albert_graph(n, m)
# find node with largest degree
node_and_degree = G.degree()
(largest_hub, degree) = sorted(node_and_degree, key=itemgetter(1))[-1]
# Create ego graph of main hub
hub_ego = nx.ego_graph(G, largest_hub)
# Draw graph
pos = nx.spring_layout(hub_ego)
g = hvnx.draw(hub_ego, pos, node_color='blue', node_size=50, with_labels=False)
# Draw ego as large and red
gnodes = hvnx.draw_networkx_nodes(
    hub_ego, pos, nodelist=[largest_hub], node_size=300, node_color='red')

networkgraph_primelands_comments = g * gnodes

G = nx.Graph()

G.add_edge('Prime_Lands', '1', weight=0.6)
G.add_edge('Prime_Lands', '2', weight=0.2)
G.add_edge('2', '3', weight=0.1)
G.add_edge('2', '4', weight=0.7)
G.add_edge('2', '5', weight=0.9)
G.add_edge('Prime_Lands', '3', weight=0.3)

G.add_node('Prime_Lands', size=20)
G.add_node('1', size=10)
G.add_node('2', size=12)
G.add_node('3', size=5)
G.add_node('4', size=8)
G.add_node('5', size=3)

pos = nx.spring_layout(G)  # positions for all nodes

infromation_diffusion_graph_primelands_comments = hvnx.draw(G, pos, edge_color='weight', edge_cmap='viridis',
                                                            edge_width=hv.dim('weight')*10, node_size=hv.dim('size')*20)

template = pn.template.FastListTemplate(
    title='Real State Giants',
    sidebar=[pn.pane.Markdown("### Assignment CIS7029"),
             'Years Selection', years_slider,
             'Months Selection', months_slider,
             pn.pane.Markdown("### this dashboard is depict facebook posts and its social media reactions such as shares, comments, reactions, like, love,	haha, wow, sad,	angry period of 01st of Januray 2021 to 01st of August 2022"),
             ],
    main=[
          pn.Row(yaxis_all_data_dimentions),
          pn.Row(pn.Column(ihvplot_all_data.panel(width=950), depth_hist.panel(width=950))),
          pn.Row(pn.Column(networkgraph_primelands_comments, width=500), 
                pn.Column(infromation_diffusion_graph_primelands_comments, width=500)),
          pn.Row(itable_all_data.panel()),
          pn.Row(yaxis_primelandscomments_dimentions),
          pn.Row(itable_primelands_comments.panel()),
          pn.Row(pie_chart_primelands_comments_sentiment)

    ]

)
# template.show()
template.servable()
