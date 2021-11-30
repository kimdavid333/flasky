import os
import io
import numpy as np


def create_dir(dir_path, new_dir):
    path = os.path.join(dir_path, new_dir)
    os.mkdir(path)
    print(f"Directory {path} created")
    return path

    """
    content: list
        [vib_id, row.index, row.ch_name, row.spec, row.sprate, row.update_flag, row.time]
    """


def generate_readme(dir_path, content):
    path = os.path.join(dir_path, 'README.txt')
    if not os.path.exists(path):
        print(f'generating readme for {path}')
        with open(path, 'w') as f:
            text = f"""\n
inspector: {content['inspector']}\n
model: {content['model']}\n
serial: {content['serial']}\n
ch_name: {content['ch_name']}\n
total iterations: {content['num_iter']}\n

spec: {content['spec']}\n
sprate: {content['sprate']}\n
start_time: {content['time']}\n
            """
            f.write(text)


def saveBinary(dir_path, binary_data):
    path = os.path.join(dir_path, 'sample_data.bin')
    data = np.load(io.BytesIO(binary_data))
    print(f'about to insert {len(data)} amount of numpy array data')
    if not os.path.exists(path):
        with open(path, 'wb') as f:

            # print(
            #     f'\tabout to write to a file of type = {type(binary_data)} with length = {len(binary_data)}')
            f.write(binary_data)
    else:
        with open(path, 'ab') as f:
            # print(
            #     f'\tabout to write to a file of type = {type(binary_data)} with length = {len(binary_data)}')
            f.write(binary_data)
    # print(f'total file size now = {os.path.getsize(path)}')


def readBinary(file_path):
    data = None
    with open(file_path) as f:
        str_format = f.read()

    data_buffer = io.BytesIO(str_format)
    np_array_list = []
    try:
        # this will move the buffer 288128 forward
        np_array_list.append(np.load(data_buffer))
        # data_buffer.tell()  # sanity check
    except Exception:
        # at this point end of buffer is reached
        pass
    return np_array_list
