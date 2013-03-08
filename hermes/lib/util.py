from ConfigParser import SafeConfigParser
import ast, logging
import logging
import logging.handlers
import os
"""Env variable HERMES_CONF_DIR should be set to /etc/hermes/ or where ever the config files are with a trailing /"""
if 'HERMES_CONF_DIR' not in os.environ:
    os.environ['HERMES_CONF_DIR'] = '/etc/hermes/'

def init_logging():
    '''
    Loads logging with a file destination from the config file
    Sets up a universal logging instance that has autorotation and can be tagged by module such as hermes.api.post all tag must start with hermes
    '''
    conf = load_conf()
    logger = logging.getLogger('hermes')
    logger.setLevel(eval(conf['loglevel']))
    fh = logging.handlers.RotatingFileHandler(conf['logdir'] + conf['logfile'], maxBytes=conf['maxlogsize'], backupCount=5)
    fh.setLevel(eval(conf['loglevel']))
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    
def load_conf(config_file = os.environ['HERMES_CONF_DIR'] + 'hermes.conf'):
    '''
    This function loads the conf file into the program's memory
    '''
    parser = SafeConfigParser()
    parser.read(config_file)
    conf={}
    #take in all keys and values from the conf file into the variable "conf"
    for section_name in parser.sections():
        for name, value in parser.items(section_name):
            conf[name] = value
    # making sure a mysql password is set
    if 'mysql_passwd' not in conf:
        conf['mysql_passwd'] = ''
    
    # converting these from strings to dict
    def convert_to_dict(var):
        '''
        Converts a string (input) to a dictionary (output)
        '''
        try:
            var = ast.literal_eval(var)
            return var
        except:
            # check if value is a single word, in which case, assume as default
            if len(var.split()) == 1:
                var={'default':var}
                return var
            else:
                logging.critical("Bad configuration variable: %s" % (var))
                raise "Bad configuration variable: %s" % (var)

    return conf

def load_client_conf(config_file = os.environ['HERMES_CONF_DIR'] + 'hermes_clients.conf', client = None):
    '''
    This function loads the config file for all clients and (optionally) returns a specific client's conf
    '''
    parser = SafeConfigParser()
    parser.read(config_file)
    print parser.sections()
    conf = {}
    if client == None:
        for section_name in parser.sections():
            subconf = {}
            for name, value in parser.items(section_name):
                subconf[name] = value
            conf[section_name] = subconf
            
    else:
        subconf = {}
        for name, value in parser.items(client):
            subconf[name] = value
        conf[client] = subconf
                
    return conf
#load conf file
#conf = load_conf()

# initiate logging
# init_logging()
