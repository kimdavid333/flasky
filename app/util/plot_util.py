from flask import flash
from application import socketio
import io
import numpy as np
import scipy.fftpack
from scipy.signal import hilbert, chirp
from application.models import Information_Model, Vib1_Table, Vib6_Table, Vib5_Table, Vib4_Table, Vib3_Table, Vib2_Table, to_json
from sqlalchemy import desc


def process_plots(info_table_data):
    print(f'@render_plots info_table_data={info_table_data}')
    '''TODO: render bar which represents # of exps with that info_id'''
    total_table_triggered = False
    info_id = info_table_data['id']
    for i in range(1, 9):
        vib_id = f'vib{i}'
        if info_table_data[vib_id]:
            data = get_vib_content(info_id, vib_id)
            if data:
                record_list = to_json(data)
                total_tables = len(data)
                # display default last one and update the page number
                if not total_table_triggered:
                    socketio.emit(
                        "registry", {'info_id': info_id, 'total_tables': total_tables}, namespace='/historic')
                    total_table_triggered = True
                target = record_list[-1]
                render_plot(vib_id, target)
                # print(f"{vib_id} total = {total_tables}, \ntarget={target}")
                print(
                    f"{vib_id} total = {total_tables} len(record_list) = {len(record_list)}")
    if not total_table_triggered:
        socketio.emit(
            "registry", {'info_id': info_id, 'total_tables': 0}, namespace='/historic')


def update_plots(info_id, table_index):
    info_content = to_json(
        Information_Model.query.filter_by(id=info_id).all())[0]

    for i in range(1, 9):
        vib_id = f'vib{i}'
        if info_content[vib_id]:
            data = get_vib_content(info_id, vib_id)
            if data:
                record_list = to_json(data)
                target = record_list[table_index-1]
                render_plot(vib_id, target)


def data_fft(data, spec, sprate):
    x_fft = []
    y_fft = []

    x_fft, y_fft = scipy.signal.welch(
        data, fs=sprate, window='hann', nperseg=spec, scaling='spectrum')  # window='hann'

    return x_fft, y_fft


def render_plot(target_id, target):
    try:
        print(f'@render_plot')
        vib_id = f'{target_id}_plot'
        fft_id = f'{target_id}_fft'
        info_id = target['id']
        index = target['index']
        ch_name = target['ch_name']
        spec = target['spec']
        sprate = target['sprate']
        update_flag = target['update_flag']
        data = target['value']
        b_data = io.BytesIO(data)
        b_data.seek(0)

        y_value = np.load(b_data, allow_pickle=True)
        time_X = np.linspace(0, 1/sprate * spec, spec)

        x_fft, y_fft = data_fft(y_value, spec, sprate)

        socketio.emit('render_plot', {
            'info_id': info_id, 'vib_id': vib_id, 'index': index, 'ch_name': ch_name, 'time_X': time_X.tolist(), 'y_value': y_value.tolist(), 'fft_id': fft_id, 'x_fft': x_fft.tolist(), 'y_fft': y_fft.tolist()}, namespace='/historic')
    except ValueError as err:
        print(err)
        print(f'detected Value error for {fft_id} {vib_id} {target["index"]}')
        print(f"type of target value = {type(data)}")

    print(f'vib_id={vib_id}, len(y_value) = {len(y_value)}')
    print(f'time_X = {len(time_X)}')
    print(f'len(x_fft) = {x_fft}, len(y_fft) = {(y_fft)}')


def get_vib_content(info_id, vib_id):
    if 'vib1' in vib_id:
        return Vib1_Table.query.filter_by(
            id=info_id).all()

    if 'vib2' in vib_id:
        return Vib2_Table.query.filter_by(
            id=info_id).all()

    if 'vib3' in vib_id:
        return Vib3_Table.query.filter_by(
            id=info_id).all()

    if 'vib4' in vib_id:
        return Vib4_Table.query.filter_by(
            id=info_id).all()

    if 'vib5' in vib_id:
        return Vib5_Table.query.filter_by(
            id=info_id).all()

    if 'vib6' in vib_id:
        return Vib6_Table.query.filter_by(
            id=info_id).all()


    else:
        raise Exception(f'Unrecognizable vib_id, {vib_id} received!')


def fetch_last(info_id, vib_id):
    if 'vib1' in vib_id:
        return Vib1_Table.query.filter_by(id=info_id).order_by(desc(Vib1_Table.index)).first()
    if 'vib2' in vib_id:
        return Vib2_Table.query.filter_by(id=info_id).order_by(desc(Vib2_Table.index)).first()
    if 'vib3' in vib_id:
        return Vib3_Table.query.filter_by(id=info_id).order_by(desc(Vib3_Table.index)).first()

    if 'vib4' in vib_id:
        return Vib4_Table.query.filter_by(id=info_id).order_by(desc(Vib4_Table.index)).first()

    if 'vib5' in vib_id:
        return Vib5_Table.query.filter_by(id=info_id).order_by(desc(Vib5_Table.index)).first()
    if 'vib6' in vib_id:
        return Vib6_Table.query.filter_by(id=info_id).order_by(desc(Vib6_Table.index)).first()
    else:
        raise Exception


def fetch_row(info_id, vib_id, index):
    if 'vib1' in vib_id:
        return Vib1_Table.query.filter_by(id=info_id, index=index).first()
    if 'vib2' in vib_id:
        return Vib2_Table.query.filter_by(id=info_id, index=index).first()
    if 'vib3' in vib_id:
        return Vib3_Table.query.filter_by(id=info_id, index=index).first()
    if 'vib4' in vib_id:
        return Vib4_Table.query.filter_by(id=info_id, index=index).first()
    if 'vib5' in vib_id:
        return Vib5_Table.query.filter_by(id=info_id, index=index).first()
    if 'vib6' in vib_id:
        return Vib6_Table.query.filter_by(id=info_id, index=index).first()


    else:
        raise Exception
