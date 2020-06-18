#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 13:53:02 2020

@author: Simon
"""

import pandas as pd
import plotly.graph_objs as go
from itertools import chain
#from datasets import *


def plot_goal_ratio(shot_boxes, title):
    # Data
    goal_ratio_data = go.Scatter(
        x=shot_boxes['centroid_x'],
        y=shot_boxes['centroid_y'],
        mode='markers',
        marker=dict(size=10, color='rgba(255, 0, 0, 0)', symbol='square'),
        text=shot_boxes['goal_ratio_text'],
        hoverinfo='text',
    )
    data = [goal_ratio_data]

    # Layout
    layout = go.Layout(
        title=title,
        hovermode='closest',
        shapes=create_shotbox_shape(shot_boxes) + rink_shapes(),
        yaxis=dict(
            range=[-100, 581],
            scaleanchor="x",
            scaleratio=1,
            ticks='',
            showticklabels=False),
        xaxis=dict(range=[-340.5, 340.5], ticks='', showticklabels=False),
        height=100,
        width=100,
    )

    # Fig and Plot
    fig = go.Figure(data=data, layout=layout)
    return fig


def create_rebound_rate_df(shooting_df, min_goals=5, min_shots=10):
    # Convert dots to boxes that are 25 x 25.825
    x0 = [num for num in range(-250, 250, 25)] * 20
    x1 = [num for num in range(-225, 275, 25)] * 20
    y0 = list(
        chain.from_iterable([[num] * 20 for num in range(0, 516500, 25825)]))
    y1 = list(
        chain.from_iterable(
            [[num] * 20 for num in range(25825, 542325, 25825)]))

    shot_boxes = pd.DataFrame({'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1})
    # Set box size to proper dimension
    shot_boxes['y0'] = shot_boxes['y0'].values / 1000
    shot_boxes['y1'] = shot_boxes['y1'].values / 1000

    # Get num shots and num goals by box
    num_shots = []
    num_goals = []
    num_rebounds = []
    for ix, box in shot_boxes.iterrows():
        box_df = shooting_df[(shooting_df.X >= box['x0'])
                             & (shooting_df.X < box['x1']) &
                             (shooting_df.Y >= box['y0']) &
                             (shooting_df.Y < box['y1'])]
        num_shots.append(box_df.agg({'event': 'count'}).values[0])
        num_goals.append(box_df[box_df.event == 'Goal'].agg({
            'event': 'count'
        }).values[0])
        num_rebounds.append(box_df[box_df.lead_to_reb == True].shape[0])

    shot_boxes['num_shots'] = num_shots
    shot_boxes['num_goals'] = num_goals
    shot_boxes['num_rebounds'] = num_rebounds
    shot_boxes[
        'goal_ratio'] = shot_boxes['num_goals'] / shot_boxes['num_shots']
    shot_boxes[
        'rebound_ratio'] = shot_boxes['num_rebounds'] / shot_boxes['num_shots']

    shot_boxes = shot_boxes[shot_boxes.num_goals > min_goals]
    shot_boxes = shot_boxes[shot_boxes.num_shots > min_shots]

    # Scale for Plotting (refactor wierd column names)
    shot_boxes['goal_ratio_colour'] = \
        (shot_boxes['rebound_ratio'] - shot_boxes['rebound_ratio'].min()) /\
        (shot_boxes['rebound_ratio'].max() - shot_boxes['rebound_ratio'].min())

    # Format for Plotting Hovering Data
    shot_boxes['centroid_x'] = shot_boxes['x1'] - (
        (shot_boxes['x1'] - shot_boxes['x0']) / 2)
    shot_boxes['centroid_y'] = shot_boxes['y1'] - (
        (shot_boxes['y1'] - shot_boxes['y0']) / 2)

    shot_boxes['goal_ratio_text'] = \
        'Rebound Ratio = ' + shot_boxes['rebound_ratio'].apply(
            lambda x: "{0:.2f}%".format(x * 100))\
        + ' <br>Number of Shots = ' + shot_boxes['num_shots'].apply(
            lambda x: str(x))\
        + ' <br>Number of Rebounds = ' + shot_boxes['num_rebounds'].apply(
            lambda x: str(x))\
        + ' <br>Number of Goals = ' + shot_boxes['num_goals'].apply(
            lambda x: str(x))
    return shot_boxes


def create_shotbox_df(shooting_df,
                      min_goals=15,
                      min_shots=100,
                      to_plot='goal_ratio'):
    # Convert dots to boxes that are 25 x 25.825
    x0 = [num for num in range(-250, 250, 25)] * 20
    x1 = [num for num in range(-225, 275, 25)] * 20
    y0 = list(
        chain.from_iterable([[num] * 20 for num in range(0, 516500, 25825)]))
    y1 = list(
        chain.from_iterable(
            [[num] * 20 for num in range(25825, 542325, 25825)]))

    shot_boxes = pd.DataFrame({'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1})
    # Set box size to proper dimension
    shot_boxes['y0'] = shot_boxes['y0'].values / 1000
    shot_boxes['y1'] = shot_boxes['y1'].values / 1000

    # Get num shots and num goals by box
    num_shots = []
    num_goals = []
    for ix, box in shot_boxes.iterrows():
        box_df = shooting_df[(shooting_df.X >= box['x0'])
                             & (shooting_df.X < box['x1']) &
                             (shooting_df.Y >= box['y0']) &
                             (shooting_df.Y < box['y1'])]
        num_shots.append(box_df.agg({'event': 'count'}).values[0])
        num_goals.append(box_df[box_df.event == 'Goal'].agg({
            'event': 'count'
        }).values[0])

    shot_boxes['num_shots'] = num_shots
    shot_boxes['num_goals'] = num_goals
    shot_boxes[
        'goal_ratio'] = shot_boxes['num_goals'] / shot_boxes['num_shots']

    shot_boxes = shot_boxes[shot_boxes.num_goals > min_goals]
    shot_boxes = shot_boxes[shot_boxes.num_shots > min_shots]

    # Scale for Plotting (refactor wierd column names)
    if to_plot == 'goal_ratio':
        shot_boxes['goal_ratio_colour'] = \
            (shot_boxes['goal_ratio'] - shot_boxes['goal_ratio'].min()) /\
            (shot_boxes['goal_ratio'].max() - shot_boxes['goal_ratio'].min())
    if to_plot == 'num_shots':
        shot_boxes['goal_ratio_colour'] = \
            (shot_boxes['num_shots'] - shot_boxes['num_shots'].min()) /\
            (shot_boxes['num_shots'].max() - shot_boxes['num_shots'].min())
    if to_plot == 'num_goals':
        shot_boxes['goal_ratio_colour'] = \
            (shot_boxes['num_goals'] - shot_boxes['num_goals'].min()) /\
            (shot_boxes['num_goals'].max() - shot_boxes['num_goals'].min())

    # Format for Plotting Hovering Data
    shot_boxes['centroid_x'] = shot_boxes['x1'] - (
        (shot_boxes['x1'] - shot_boxes['x0']) / 2)
    shot_boxes['centroid_y'] = shot_boxes['y1'] - (
        (shot_boxes['y1'] - shot_boxes['y0']) / 2)

    shot_boxes['goal_ratio_text'] = \
        'Scoring Ratio = ' + shot_boxes['goal_ratio'].apply(
            lambda x: "{0:.2f}%".format(x * 100))\
        + ' <br>Number of Shots = ' + shot_boxes['num_shots'].apply(
            lambda x: str(x))\
        + ' <br>Number of Goals = ' + shot_boxes['num_goals'].apply(
            lambda x: str(x))
    return shot_boxes


def create_shotbox_shape(shot_boxes):
    # Convert boxes into plottable shape
    shot_box_shapes = []
    for ix, box in shot_boxes.iterrows():
        shot_box_shapes.append(
            dict(
                type='rect',
                xref='x',
                yref='y',
                x0=box['x0'],
                y0=box['y0'],
                x1=box['x1'],
                y1=box['y1'],
                line=dict(width=0),
                fillcolor='rgba(255, 0, 0,' + str(box['goal_ratio_colour']) +
                ')'))
    return shot_box_shapes


def rink_shapes():
    outer_rect_shape = dict(
        type='rect',
        xref='x',
        yref='y',
        x0='-50',
        y0='0',
        x1='50',
        y1='89',
        line=dict(width=2.5,
                  color='rgba(0, 0, 0, 0.75)'))
    outer_line_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-40',
        y0='100',
        x1='40',
        y1='100',
        line=dict(width=5.0,
                  color='rgba(0,0,0,0.9)'))
    outer_arc1_shape = dict(
        type='path',
        xref='x',
        yref='y',
        path='M -50 89 C -49.5 100,-49.5 100, 0 100',
        line=dict(width=3,
                  color='rgba(0,0,0,0.7)'))
    outer_arc2_shape = dict(
        type='path',
        xref='x',
        yref='y',
        path='M 50 89 C 49.5 100, 49.5 100, 0 100',
        line=dict(width=3,
                  color='rgba(0,0,0,0.7)'))
    center_red_line_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-50',
        y0='0',
        x1='50',
        y1='0',
        line=dict(width=3, color='rgba(255, 0, 0, 1)'))
    end_line_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-49.8',
        y0='89',
        x1='49.8',
        y1='89',
        line=dict(width=2, color='rgba(255, 0, 0, 0.9)'))
    blue_line_shape = dict(
        type='rect',
        xref='x',
        yref='y',
        x0='-49.8',
        y0='25',
        x1='49.8',
        y1='25',
        line=dict(width=2.5, color='rgba(0, 0, 255, 0.35)'))
    center_blue_spot_shape = dict(
        type='circle',
        xref='x',
        yref='y',
        x0='2.94',
        y0='2.8',
        x1='-2.94',
        y1='-2.8',
        line=dict(color='rgba(0, 0, 255, 1)', width=1),
        fillcolor='rgba(0, 0, 255, 1)')
    red_spot1_shape = dict(
        type='circle',
        xref='x',
        yref='y',
        x0='-22.5',
        y0='68.5',
        x1='-21.5',
        y1='69.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1),
        fillcolor='rgba(255, 0, 0, 0.4)')
    red_spot2_shape = dict(
        type='circle',
        xref='x',
        yref='y',
        x0='21.5',
        y0='69.5',
        x1='22.5',
        y1='68.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1),
        fillcolor='rgba(255, 0, 0, 0.4)')
    red_spot1_circle_shape = dict(
        type='circle',
        xref='x',
        yref='y',
        x0='-37',
        y0='54',
        x1='-7',
        y1='84',
        line=dict(width=2, color='rgba(255, 0, 0, 0.4)'))
    red_spot2_circle_shape = dict(
        type='circle',
        xref='x',
        yref='y',
        x0='7',
        y0='54',
        x1='37',
        y1='84',
        line=dict(width=2, color='rgba(255, 0, 0, 0.4)'))
    center_ice_circle_shape = dict(
        type='circle',
        xref='x',
        yref='y',
        x0='-15',
        y0='-15',
        x1='15',
        y1='15',
        line=dict(width=2, color='rgba(0, 0, 255, 0.4)'))

    faceoff_line1_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-23.5',
        y0='68.5',
        x1='-22.5',
        y1='68.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line2_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-22.5',
        y0='67.5',
        x1='-22.5',
        y1='68.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line3_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-23.5',
        y0='69.5',
        x1='-22.5',
        y1='69.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line4_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-22.5',
        y0='69.5',
        x1='-22.5',
        y1='70.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line5_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-21.5',
        y0='69.5',
        x1='-20.5',
        y1='69.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line6_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-21.5',
        y0='69.5',
        x1='-21.5',
        y1='70.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line7_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-21.5',
        y0='68.5',
        x1='-20.5',
        y1='68.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line8_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-21.5',
        y0='68.5',
        x1='-21.5',
        y1='67.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))

    faceoff_line9_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='20.5',
        y0='68.5',
        x1='21.5',
        y1='68.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line10_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='21.5',
        y0='67.5',
        x1='21.5',
        y1='68.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line11_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='20.5',
        y0='69.5',
        x1='21.5',
        y1='69.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line12_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='21.5',
        y0='69.5',
        x1='21.5',
        y1='70.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line13_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='22.5',
        y0='69.5',
        x1='23.5',
        y1='69.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line14_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='22.5',
        y0='69.5',
        x1='22.5',
        y1='70.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line15_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='22.5',
        y0='68.5',
        x1='23.5',
        y1='68.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))
    faceoff_line16_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='22.5',
        y0='68.5',
        x1='22.5',
        y1='67.5',
        line=dict(color='rgba(255, 0, 0, 0.4)', width=1))

    goal_line1_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-4',
        y0='89',
        x1='-4',
        y1='84',  
        line=dict(color='rgba(0, 0, 255, 0.4)', width=2))

    goal_line2_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='4',
        y0='89',
        x1='4',
        y1='84',  
        line=dict(color='rgba(0, 0, 255, 0.4)', width=2))


    goal_line3_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='-10',
        y0='89.2',
        x1='-12',
        y1='99.9',
        line=dict(color='rgba(0, 0, 0, 0.4)', width=2))

    goal_line4_shape = dict(
        type='line',
        xref='x',
        yref='y',
        x0='10',
        y0='89.2',
        x1='12',
        y1='99.9',
        line=dict(color='rgba(0, 0, 0, 0.4)', width=2))


    # mirror images of "goal_line1" and "goal_line2" along with the Y-axis

    goal_arc1_shape = dict(
        type='path',
        xref='x',
        yref='y',
        path='M -4 84 C -2 82 , 2 82, 4 84',
        line=dict(color='rgba(0, 0, 255, 0.4)', width=2))

    goal_arc2_shape = dict(
        type='path',
        xref='x',
        yref='y',
        path='M -3 89.1 C -1 91 , 1 91, 3 89.1',
        line=dict(color='rgba(0, 0, 0, 0.4)', width=2))

    rink_shapes = []
    # Main Rink Shape
    rink_shapes.append(outer_rect_shape)
    #rink_shapes.append(outer_line_shape)
    rink_shapes.append(outer_arc1_shape)
    rink_shapes.append(outer_arc2_shape)

    # Main Lines Shapes
    rink_shapes.append(center_red_line_shape)
    rink_shapes.append(end_line_shape)
    rink_shapes.append(blue_line_shape)

    # Faceoff Dots
    rink_shapes.append(red_spot1_shape)
    rink_shapes.append(red_spot2_shape)

    # Faceoff Circles
    rink_shapes.append(red_spot1_circle_shape)
    rink_shapes.append(red_spot2_circle_shape)
    rink_shapes.append(center_ice_circle_shape)
    
    # Faceoff Lines Left Side
    rink_shapes.append(faceoff_line1_shape)
    rink_shapes.append(faceoff_line2_shape)
    rink_shapes.append(faceoff_line3_shape)
    rink_shapes.append(faceoff_line4_shape)
    rink_shapes.append(faceoff_line5_shape)
    rink_shapes.append(faceoff_line6_shape)
    rink_shapes.append(faceoff_line7_shape)
    rink_shapes.append(faceoff_line8_shape)
    
    # Faceoff Lines Right Side
    rink_shapes.append(faceoff_line9_shape)
    rink_shapes.append(faceoff_line10_shape)
    rink_shapes.append(faceoff_line11_shape)
    rink_shapes.append(faceoff_line12_shape)    
    rink_shapes.append(faceoff_line13_shape)
    rink_shapes.append(faceoff_line14_shape)
    rink_shapes.append(faceoff_line15_shape)
    rink_shapes.append(faceoff_line16_shape)

    # Goalie Shapes
    rink_shapes.append(goal_line1_shape)
    rink_shapes.append(goal_line2_shape)
    rink_shapes.append(goal_line3_shape)
    rink_shapes.append(goal_line4_shape)

    rink_shapes.append(goal_arc1_shape)
    rink_shapes.append(goal_arc2_shape)
    return rink_shapes

