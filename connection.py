from netmiko import ConnectHandler
from netconnect import utils
import logging

log_level = logging.INFO
log = logging.getLogger(__name__)
fh = logging.FileHandler("/tmp/netconnect.log")
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
#log.setLevel(log_level)
log.propagate = False

class Connection(object):
    '''Netmiko Based Connection

    Sample implementation of NetmikoConnection connection to devices
    allowing devices to ssh or telnet to end routers
    '''

    def __init__(self, protocol, ip, port, username, enable_password, tacacs_password, line_passwd, os, *args, **kwargs):
        # instantiate device information
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.username = username
        self.enable_password = enable_password
        self.tacacs_password = tacacs_password
        self.line_passwd = line_passwd
        self.os = os
        self._is_connected = False

    def connect(self):
        #self.net_connect = ConnectHandler(device_type='a10', ip='192.168.100.96', username='admin', password='admin',secret='admin')
        connect_params = self._connect_params_dict()
        try:
            self.net_connect = ConnectHandler(**connect_params)
        except ValueError:
            extends = 'netconnect.extends.' + str(self.os) + '.' + 'ConnectHandler'
            self.net_connect = utils.import_object(extends,**connect_params)
            self._is_connected = True
        except Exception as ex:
            log.info(ex)
            self._is_connected = False
        else:
            self._is_connected = True

    @property
    def connected(self):
        return self._is_connected

    def execute(self, command, timeout=500):
        if not self._is_connected:
            log.error("Error: device not connected")
            return False

        if isinstance(command, str):  ## if string is given, transfer to list
            command = command.splitlines()

        if self.os not in ['linux', 'nso']: ## some devices like linux don't need enable operation
            self.net_connect.enable()

        expect_string = None
        if self.os in ['linux']:  ## add Linux prompt pattern
            expect_string = r'(.*?([>\$~%]|[^#\s]#))\s?$'

        output = ""
        for cmd in command:
            log.debug('To be executed command: %s', cmd)
            result = self.net_connect.send_command_expect(cmd, expect_string=expect_string, max_loops=int(timeout))
            output = output + result

        return output

    def send(self, command):
        result = self.net_connect.send_command_timing(command)

        return result

    def configure(self, cmd):
        if not self._is_connected:
            log.error("Error: device not connected")
            return False

        log.debug('To be configured command: %s', cmd)
        result = self.net_connect.send_config_set(cmd)
        if self.os in ['cisco_xr', 'nso']:  ## some devices like cisco_xr need commit operation
            self.net_connect.commit()
            self.net_connect.exit_config_mode()

        return result

    def disconnect(self):
        self.net_connect.disconnect()
        self._is_connected = False

    def cli_style(self, style):
        if self.os != 'nso':
            log.error("Error: Only nso supported cli")
            return False

        if style == 'cisco' and self.current_cli_style != 'cisco':
            self.net_connect.send_command_timing("switch cli")
        elif style == 'juniper' and self.current_cli_style != 'juniper':
            self.net_connect.send_command_timing("switch cli")
        else: log.error("Please input right cli style!")

        return self.current_cli_style

    @property
    def current_cli_style(self):
        if self.os != 'nso':
            log.error("Error: Only nso supported cli")
            return False

        prompt = self.net_connect.find_prompt()
        if prompt.endswith('#'): self._current_cli_style = 'cisco'
        elif prompt.endswith('>'): self._current_cli_style = 'juniper'
        else: self._current_cli_style = 'unknow'

        log.debug('Current cli style: %s', self._current_cli_style)
        return self._current_cli_style

    def _connect_params_dict(self):
        """Generate dictionary of Paramiko connection parameters."""
        conn_dict = {
            'device_type': self.os,
            'ip': self.ip,
            'port': self.port,
            'username': self.username,
            'password': self.tacacs_password,
            'secret': self.enable_password
        }

        log.debug('The connection info dict: %s', conn_dict)
        return conn_dict