"""Use flask to display temperature data from a temperature sensor and weather
forecasts on a web page"""

import datetime
from bokeh.plotting import figure
from bokeh.embed import json_item, components
from bokeh.resources import CDN
from bokeh.models import HoverTool, Legend, ColumnDataSource, Range1d, LinearAxis
import json
from flask import Flask, render_template, g, Blueprint, current_app, request

from web_monitor.db import get_db

from . import TimeForm

bp = Blueprint('plots', __name__)


def get_data_range(dt1, dt2):
    """Return all records from the database after the interval"""

    conn = get_db()
    curs = conn.cursor()
    curs.execute("SELECT * FROM temp_and_speed WHERE measurement_time BETWEEN '%s' AND '%s'" % (dt1, dt2))

    rows = curs.fetchall()

    curs.close()

    return rows


def make_range_plot(dt1, dt2):
    """Plot the data in Bokeh"""

    records = get_data_range(dt1, dt2)
    dates = [datetime.datetime.strptime(r[0], '%Y-%m-%d %H:%M:%S.%f') for r in records]

    data = {'dates': dates,
            'cpu_temps': [r[1] for r in records],
            'cpu_temps_1_min': [r[2] for r in records],
            'cpu_temps_5_min': [r[3] for r in records],
            'cpu_temps_10_min': [r[4] for r in records],
            'sensor_temps': [r[5] for r in records],
            'sensor_temps_1_min': [r[6] for r in records],
            'sensor_temps_5_min': [r[7] for r in records],
            'sensor_temps_10_min': [r[8] for r in records],
            'current_duty_cycle': [r[9] for r in records],
            'next_duty_cycle': [r[10] for r in records]
            }

    source = ColumnDataSource(data=data)

    p = figure(plot_width=800, plot_height=500, x_axis_type="datetime",
               toolbar_location="above")
    p.yaxis.axis_label = 'Temperature (C)'
    p.yaxis.axis_label_text_font_style = 'normal'

    p.extra_y_ranges = {'duty_cycles': Range1d(start=0, end=100)}

    p.add_tools(HoverTool(
        tooltips=[
            ('date', '@dates{%Y-%m-%d %H:%M:%S}'),
            ('data', '$y'),
        ],
        formatters={
            '@dates': 'datetime',
        },
    ))

    y_data = [
        'cpu_temps',
        'cpu_temps_1_min',
        'cpu_temps_5_min',
        'cpu_temps_10_min',
        'sensor_temps',
        'sensor_temps_1_min',
        'sensor_temps_5_min',
        'sensor_temps_10_min',
        'current_duty_cycle',
        'next_duty_cycle',
    ]

    colours = ['#006BA4', '#FF800E', '#ABABAB', '#595959', '#5F9ED1',
               '#C85200', '#898989', '#A2C8EC', '#FFBC79', '#CFCFCF']

    line_dashes = ['solid', 'solid', 'solid', 'solid',
                   'solid', 'solid', 'solid', 'solid',
                   'solid', 'dashed'
                   ]

    lines = []
    for y_data, colour, line_dash in zip(y_data, colours, line_dashes):
        if 'duty_cycle' in y_data:
            lines.append(p.line(x='dates',
                                y=y_data,
                                color=colour,
                                line_width=2,
                                line_dash=line_dash,
                                source=source,
                                y_range_name='duty_cycles')
                         )
        else:
            lines.append(p.line(x='dates',
                                y=y_data,
                                color=colour,
                                line_width=2,
                                line_dash=line_dash,
                                source=source)
                         )

    # The legend will be outside the plot, and so must be defined directly
    leg = Legend(
        items=[
            ("CPU Temperature", [lines[0]]),
            ("CPU Temperature (1 min avg)", [lines[1]]),
            ("CPU Temperature (5 min avg)", [lines[2]]),
            ("CPU Temperature (10 min avg)", [lines[3]]),
            ("Sensor Temperature", [lines[4]]),
            ("Sensor Temperature (1 min avg)", [lines[5]]),
            ("Sensor Temperature (5 min avg)", [lines[6]]),
            ("Sensor Temperature (10 min avg)", [lines[7]]),
            ("Current Duty Cycle", [lines[8]]),
            ("Next Duty Cycle", [lines[9]]),
        ],
        location=(5, 200),
        click_policy='hide')

    p.add_layout(LinearAxis(y_range_name='duty_cycles',
                            axis_label='Duty Cycle (%)',
                            axis_label_text_font_style='normal'), 'right')
    p.add_layout(leg, 'right')

    # Jsonify the plot to put in html
    plot_script, plot_div = components(p)
    print(plot_div)
    return plot_script, plot_div


@bp.route('/', methods=['GET', 'POST'])
def show_plot():

    time_chooser = TimeForm.TimeFormRange(request.form)
    # %Y-%m-%d %H:%M:%S
    now = datetime.datetime.now()
    datetime_1 = (now - datetime.timedelta(hours=72)).strftime('%Y-%m-%d %H:%M:%S')
    datetime_2 = now.strftime('%Y-%m-%d %H:%M:%S')

    if time_chooser.validate_on_submit():
        # if time_chooser.the_time.data != 'all':
        datetime_1 = time_chooser.datetime_1.data
        datetime_2 = time_chooser.datetime_2.data
        current_app.logger.info('datetime_1 is %s', datetime_1)
        current_app.logger.info('datetime_2 is %s', datetime_2)

    plot_script, plot_div = make_range_plot(datetime_1, datetime_2)
    # CDN.render() has all of the information to get the javascript libraries
    # for Bokeh to work, loaded from a cdn somewhere.
    return render_template('temp_range_graph.html', plot_div=plot_div,
                           plot_script=plot_script, resources=CDN.render(),
                           form=time_chooser)
