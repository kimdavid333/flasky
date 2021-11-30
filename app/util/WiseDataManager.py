from datetime import datetime

from backports.datetime_fromisoformat import MonkeyPatch
from flask.scaffold import F

MonkeyPatch.patch_fromisoformat()

class WiseDataManager:
    """Class that handles raw MQTT data to Ploting ready format"""

    def __init__(self):
        """ inits DataPlot with appropriate flags """
        self.initialized = False
        self.df = None
        self.itervalReceived = []
        self.trace_x = None
        self.trace_y = None
        self.ch_names = None
        self.update_flags = None
        self.start_time = None

    def extract_fields(self, mqtt_message):
        assert(mqtt_message)
        data_dict = mqtt_message.get('Accelerometer').get('X-Axis')
        if data_dict:
            output = []
            for field in data_dict.keys():
                field_safe = field
                if ' ' in field:
                    field_safe = field_safe.replace(' ', '_')
                if '-' in field_safe:
                    field_safe = field_safe.replace('-', '_')
                output.append(field_safe)

            return output
        else:
            return None
        
    
    def process_msg(self, mqtt_message, fields=None):
        """parse raw DAQ records to client-side ready data format.

        Parameters
        ----------
        mqtt_message : JSON mqtt data
            JSON data from sensor
        
        Returns
        -------
        output_dict : python_dict
            It has 3 keys - X-Axis, Y-Axis, and Z-Axis. For each, it has a dict for its value containing SenEvent and RMSmg values.

        """
        assert(mqtt_message)
        # axes = ['X-Axis', 'Y-Axis', 'Z-Axis']
        axes = ['X-Axis']
        if fields is None:
            fields = mqtt_message.get('Accelerometer').get('X-Axis')
        
        output_dict = {}

        for axis in axes:
            if axis not in output_dict:
                output_dict[axis] = {}

            for field in fields:
                value = mqtt_message['Accelerometer'][axis][field]
                # print('field = ', field)
                field_safe = field
                if ' ' in field_safe:
                    field_safe = field_safe.replace(' ', '_')
                if '-' in field_safe:
                    field_safe = field_safe.replace('-', '_')
                output_dict[axis][field_safe] = value

        return output_dict

    def process_batch(self, mqtt_list, fields=None):
        """parse raw DAQ records to client-side ready data format.

        Parameters
        ----------
        mqtt_list : list
            list containing rows from DB
        
        Returns
        -------
        output_dict : python_dict
            It has 3 keys - X-Axis, Y-Axis, and Z-Axis. For each, it has a dict for its value containing SenEvent and RMSmg values.
        fields : list
            list containing column names
        """
        assert(mqtt_list)
        axes = ['X_Axis', 'Y_Axis', 'Z_Axis']
        # axes = ['X_Axis']
        if fields is None:
            row = mqtt_list[0]
            fields = list(row.get('X_Axis').keys())
        # fields.append('created_at')
        output_dict = {}
        x_val = []
        for row in mqtt_list:
            x_val.append(row['created_at'])

            for axis in axes:
                if axis not in output_dict:
                    output_dict[axis] = {}
                for field in fields:
                    if field not in output_dict[axis]:
                        output_dict[axis][field] = []

                        value = row[axis][field]
                        output_dict[axis][field].append(value)

        return output_dict, x_val, fields
        