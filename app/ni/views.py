"""Routing phase 1"""
""" include all logged-in routes"""

from flask import render_template, request, redirect, url_for
from app import socketio, db
from app.models import de_active, de_active
from threading import Thread
from . import ni
object_objs = None
records_df = None
dataContainer = []
datasheet_column_name = {}
previous_updateFlags = []
initializePlot = True
thread = Thread()
socket_connected = None
interval = 0
clients = []
client = None
info_id = None
scoreboard = {}
current_info_id = None
current_plot_indexes = {}


@ni.route('/viewer/')
def viewer():
    return render_template('ni/viewer.html', async_mode=socketio.async_mode)


@socketio.on("request_info_display", namespace='/test')
def update_display(message):
    info_id = message['info_id']
    from app.tasks import update_info_display
    update_info_display.delay(info_id)


@socketio.on('request_update_vid', namespace='/test')
def update_received(message):
    info_id = message['info_id']
    vib_id = message['vib_id']
    index = message['index']
    '''TODO: call celery task (using .delay() with param'''
    print(
        f'@update_received fib_id={info_id}, vib_id={vib_id}, index = {index}')
    from app.tasks import update_plot
    update_plot.delay(info_id, vib_id, index)


@socketio.on('connect', namespace='/test')
def socket_connect():
    """Start background task of connecting to MQTT broker(s) once socket from viewer get connected.
    """
    global thread, initializePlot, redis_db
    initializePlot = True
    db.app = db.get_app()
    print('Socket connected')


@socketio.on('disconnect', namespace='/test')
def socket_disconnect():
    """Log to server when the socket for viewer get disconnected"""
    print('Client disconnected')
