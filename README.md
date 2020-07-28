Date: 2018 04/29

## Introduction:
- netconnect is based on netmiko libary, define new api to used by rasta framework.  
- netconnect is used by rasta to connect devices, supported devices depend on netmiko feature, mainly include all cisco devices, linux etc ...

## Version History:
version 1.0: 2018/04/29  -> first build  
version 2.0: 2018/05/02  -> add support for connection to nso(Modify based on netmiko class)


## How To Use:
Please define devices into test.yaml which is used by pyats framework, below is the example parameters  
    Notes: os                           -> specify device type which should follow netmiko keyword, please search netmiko website for details  
         passwords.tacacs             -> given username's passwords  
         passwords.enable             -> enable passwords if needed  
         connections.defaults.class   -> specify connections class used by rasta, so here should be netconnect.Netconnect   
         connections.defaults.cli     -> specify device connection information, the ip and port is needed  
```
Example .yaml:
  ASR9K-v2-0:
    type: router
    os: cisco_xr
    tacacs:
      username: admin
    passwords:
      tacacs: admin
      line: admin
      enable: admin
    connections:
      defaults:
        class: netconnect.Netconnect
      cli:
        protocol: ssh
        ip: 192.168.100.53
        port: 22
  nat0:
    type: router
    os: cisco_ios_telnet
    tacacs:
      username: cisco
    passwords:
      tacacs: cisco
      line: cisco
      enable: cisco
    connections:
      defaults:
        class: netconnect.Netconnect
      cli:
        protocol: telnet
        ip: 192.168.100.49
        port: 23
  nso_Linux:
    os: linux
    type: server
    tacacs:
      username: admin
    passwords:
      linux: admin
    connections:
      defaults:
        class: netconnect.Netconnect
      cli:
        protocol: ssh
        ip: 172.17.0.2
        port: 22
```
