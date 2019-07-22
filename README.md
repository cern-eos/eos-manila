# EOS Manila: Manila Driver for EOS Storage
The purpose of this driver is to directly connect CERN users with the OpenStack interface in order to request and configure in a self-service approach storage space at CERN. Every CERN user has a dashboard in OpenStack where one can for example request virtual machines and space in storage systems. The driver aims to connect the two systems using their APIs. 

The driver in this repository is a generic baseline to understand how OpenStack Manila handles calls made to drivers in order to communicate with outside interfaces. Through this sample driver we are able to "interface" with the local machine in order to create fake shares in the logged-in user's home directory. The server-side of this system employs a Python GRPC server to process requests. All requests must use the EOS protocol and a valid "fake" authentication key.

### About OpenStack
OpenStack is a popular open source cloud-computing software platform. The system makes use of commodity hardware as its main source for computing and is tied in with several other services, such as networking and authentication. \[1\] 

### About EOS Storage
EOS is a disk-based, low-latency storage service. Having a highly-scalable hierarchical namespace, and with data access possible by the XROOT protocol, it was initially used for physics data storage. Today, EOS provides storage for both physics and user use cases. The main target area for the EOS is physics data analysis, which is characterised by many concurrent users, a significant fraction of random data access and a large file-open rate \[2\]. 

## Driver Capabilities
This driver currently supports:

 - Creating a Share
 - Deleting a Share
 - Extending a Share
 - Shrinking a Share

## OpenStack Manila Installation With DevStack
To begin using the EOS Manila driver with OpenStack, it is first necessary to install OpenStack with Manila support. To do this, we will be using **DevStack**: scripts meant to seamlessly build an OpenStack environment on your desired machine. 

After building a [compatible](https://docs.openstack.org/sahara/latest/contributor/devstack.html) Linux machine dedicated to OpenStack, using your machine's *root* account, run the following commands:

1. Create a "stack" user with sudo privileges.

```sh
$ sudo useradd -s /bin/bash -d /opt/stack -m stack
$ echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
```

2. Switch to the "stack" user.

```sh
$ sudo su - stack
```

3. Clone the DevStack repository and change directories into the newly downloaded folder.

```sh
$ git clone https://opendev.org/openstack/devstack
$ cd devstack
```
4. Copy "local.conf" file from /devstack/samples into the devstack folder. 

```
$ cp samples/local.conf ./
```

5. Add the following lines at the bottom of the local.conf file just copied into the root directory of the devstack folder.

```sh
enable_plugin manila https://github.com/openstack/manila
enable_plugin manila-ui https://github.com/openstack/manila-ui
```

5. Start the install.

```sh
$ ./stack.sh
```

*The installation will take 30-40 minutes, depending on the speed of your internet connection. After it has finished, Devstack will supply sample admin and demo accounts to use freely.*

## Configuring the EOS Driver

Before beginning these series of steps, [ensure that you are recognized as an admin user](https://docs.oracle.com/cd/E78305_01/E78304/html/openstack-envars.html) on your OpenStack instance. 

*These instructions assume that DevStack was installed in stack's home directory.*

1. Navigate to the OpenStack Manila drivers folder and clone the repository.

```sh
$ cd ~/manila/manila/share/drivers/eos-manila
$ git clone https://github.com/cern-eos/eos-manila.git
```
2. Modify the bottom of Manila configuration file.
```sh
$ vi /etc/manila/manila.conf
```

3. Add a new stanza to manila.conf for the EOS Manila driver configuration:
```sh
[eos]
driver_handles_share_servers = False
share_backend_name = EOS
share_driver = manila.share.drivers.eos-manila.driver.EOSDriver
auth_key = BakTIcB08XwQ7vNvagi8 # arbitrary authentication key defined in server
```

4. Enable the EOS Manila driver in the [DEFAULT] stanza of the manila.conf file and enable the EOS protocol.
```sh
enabled_share_backends = eos
...
enabled_share_protocols = NFS,CIFS,EOS
```

5. Modify Manila UI to enable EOS as a share protocol.
```sh
$ vi ~/manila-ui/manila_ui/local/local_settings.d/_90_manila_shares.py
```

```sh
OPENSTACK_MANILA_FEATURES = {
    'enable_share_groups': True,
    'enable_replication': True,
    'enable_migration': True,
    'enable_public_share_type_creation': True,
    'enable_public_share_group_type_creation': True,
    'enable_public_shares': True,
    'enabled_share_protocols': ['NFS', 'CIFS', 'GlusterFS', 'HDFS', 'CephFS',
                                'MapRFS', 'EOS'],
}
```

6. Register the configuration options for the EOS Manila Driver.
```sh
$ vi ~/manila/manila/opts.py
```

```sh
import manila.share.drivers.eos-manila.driver
...
_global_opt_lists = [
    ...
    manila.share.drivers.eos-manila.driver.eos_opts
    ...
]
```

7. Define EOSException.
```sh
$ vi ~/manila/manila/exception.py
```

```sh
class EOSException(ManilaException):
    message = _("EOS exception occurred: %(msg)s")
```

8. Add "EOS" as a share protocol constant.
```sh
vi ~/manila/manila/common/constants.py
```

```sh
SUPPORTED_SHARE_PROTOCOLS = (
    'NFS', 'CIFS', 'GLUSTERFS', 'HDFS', 'CEPHFS', 'MAPRFS', 'EOS')
```

9. Create a new share type for EOS.
```sh
$ manila type-create eos False --extra-specs share_backend_name=EOS
```

10. Restart all Manila services.
```sh
$ sudo systemctl restart devstack@m*
```

## Running the Sample GRPC Server with EOS Manila Driver


## Modifying OpenStack UI for End-User 


## References:
* \[1\]: [Manila – OpenStack File Sharing Service](https://zenodo.org/record/33192#.XTXBwHUzYeM)
* \[2\]: [CERN EOS Service Main Page](http://information-technology.web.cern.ch/services/eos-service)
* \[3\]: [DevStack Documentation](https://docs.openstack.org/devstack/latest/)
* \[4\]: [Setting Environment Variables for OpenStack CLI Clients](https://docs.oracle.com/cd/E78305_01/E78304/html/openstack-envars.html)