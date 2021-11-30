import configparser

def get_num_channels(mcc, file_path='application/util/config.ini'):
    """Fetch channel info on the DAQ Device, given by the mcc arg

    Parameters
    ----------
    mcc : str
        represents DAQ Device in use
    file_path : str, optional
        path to the config text file, by default 'util/config.ini'

    Returns
    -------
    tuple (num, total)
        num : int
            channel number of mcc
        total : int
            max_val of the channel number  

    Raises
    ------
    Exception
        Config doesn't recognize mcc given
    """
    parser = configparser.ConfigParser()
    parser.read(file_path)
    section = 'numChannels'
    if parser.has_section(section):
        num = int(parser[section][mcc])
        total = int(parser[section]['TOTAL'])
        # print('\tnum=', num)
        # print('\ttotal=', total)
        return (num, total)
    else:
        raise Exception("Config doesn't recognize section {}".format(section))