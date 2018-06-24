from ..connection import Connection

class Netconnect(object):
    """
        Generic Factory/Adapter for pyATS topology/device connections
    """

    def __new__(cls, device, alias=None, via=None, *args, **kwargs):
        """ Instantiates generic connection instance

         based on the device type and info provided
         This class reads the PyATS topology device object
         and invokes the generic connection with the details read
        """

        # Get the device platform and type details
        os = device.os if hasattr(device, 'os') else None
        return cls.get_netmiko_connection(device, alias, via, *args,
                                             **kwargs)

    @staticmethod
    def get_netmiko_connection(device, alias, via, *args, **kwargs):

        # Get the device platform and type details
        os = device.os if hasattr(device, 'os') else None
        # Fetch the Authentication details
        username = device.tacacs.username
        enable_passwd = device.passwords.enable
        tacacs_passwd = device.passwords.tacacs if not device.os == 'linux' else device.passwords.linux
        line_passwd = device.passwords.line

        # Construct the device connection details
        protocol = device.connections[via].protocol
        ip = "%s" % (device.connections[via].ip)
        port = device.connections[via].port
        print ("create new connection instance")
        # instantiate netconnect connection
        return Connection(protocol=protocol,
                          ip=ip,
                          port=port,
                          username=username,
                          enable_password=enable_passwd,
                          tacacs_password=tacacs_passwd,
                          line_passwd=line_passwd,
                          os=os,
                          *args,
                          **kwargs)
