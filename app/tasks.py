import io
import numpy as np
from app import celeryapp, socketio
from app.models import Information_Model, to_json
from app.util.plot_util import data_fft, fetch_last, fetch_row
# from app.services import FeedEater


celery = celeryapp.celery


@celery.task()
def broadcast_latest_info(vib_num: int):
    # emit to all clients latest info_id and index per vib#_table
    information_row = Information_Model.query.order_by(
        Information_Model.id.desc()).first()
    info_table_data = to_json([information_row])[0]
    info_id = info_table_data['id']
    vib_id = f'vib{vib_num}'
    if info_table_data[vib_id]:
        last_row = fetch_last(info_id, vib_id)
        if last_row:
            index = last_row.index
            # now broadcast info_id, vib_id, last_row.index
            socketio.emit('notify_latest_data', {
                'info_id': info_id, 'vib_id': vib_id, 'index': index}, namespace='/test')


@celery.task
def update_info_display(info_id):
    information_row = Information_Model.query.order_by(
        Information_Model.id.desc()).first()
    info_table_data = to_json([information_row])[0]
    msg = {
        'info_id': info_table_data['id'],
        'inspector': info_table_data['inspector'],
        'model': info_table_data['model'],
        'serial': info_table_data['serial'],
        'created_at': info_table_data['created_at'].strftime('%m/%d/%Y, %H:%M:%S')

    }
    socketio.emit("register_info", msg, namespace='/test')


@celery.task
def update_plot(info_id, vib_num, index):
    # at this point, server know given info_id, vib_id, index exists
    row = fetch_row(info_id, vib_num, index)
    target = to_json([row])[0]
    vib_id = f'{vib_num}_plot'
    fft_id = f'{vib_num}_fft'
    ch_name = target['ch_name']
    index = target['index']
    spec = target['spec']
    sprate = target['sprate']
    update_flag = target['update_flag']
    data = target['value']
    b_data = io.BytesIO(data)
    b_data.seek(0)

    y_value = np.load(b_data)
    time_X = np.linspace(0, 1/sprate * spec, spec)

    x_fft, y_fft = data_fft(y_value, spec, sprate)

    socketio.emit('render_plot', {'info_id': info_id, 'vib_id': vib_id, 'index': index, 'ch_name': ch_name, 'time_X': time_X.tolist(
    ), 'y_value': y_value.tolist(), 'fft_id': fft_id, 'x_fft': x_fft.tolist(), 'y_fft': y_fft.tolist()}, namespace='/test')
