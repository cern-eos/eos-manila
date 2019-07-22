# EOS Manila: Manila Driver for EOS Storage
The purpose of this driver is to directly connect CERN users with the OpenStack interface in order to request and configure in a self-service approach storage space at CERN. Every CERN user has a dashboard in OpenStack where one can for example request virtual machines and space in storage systems. The driver aims to connect the two systems using their APIs. 

The driver in this repository is a generic baseline to understand how OpenStack Manila handles calls made to drivers in order to communicate with outside interfaces. Through this sample driver we are able to "interface" with the local machine in order to create fake shares in the logged-in user's home directory. The server-side of this system employs a Python GRPC server to process requests. All requests must use the EOS protocol and a valid "fake" authentication key.

### About EOS Storage
EOS is a disk-based, low-latency storage service. Having a highly-scalable hierarchical namespace, and with data access possible by the XROOT protocol, it was initially used for physics data storage. Today, EOS provides storage for both physics and user use cases. The main target area for the EOS is physics data analysis, which is characterised by many concurrent users, a significant fraction of random data access and a large file-open rate \[1\]. 

## Driver Capabilities
This driver currently supports:

 - Creating a Share
 - Deleting a Share
 - Extending a Share
 - Shrinking a Share

## OpenStack Manila Installation With DevStack
To begin using the EOS Manila driver with OpenStack, it is first necessary to install OpenStack with Manila support. To do this, we will be using **DevStack**: scripts meant to seamlessly build an OpenStack environment on your desired machine. 

After building a [compatible](https://docs.openstack.org/sahara/latest/contributor/devstack.html) Linux machine dedicated to OpenStack, using *root*, run the following commands:

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
4. Copy "local.conf" file from /devstack/samples into the root folder.  "local.conf".

```
$ cp samples/local.conf ./
```

5. Add the following lines at the bottom of the local.conf just copied into the root directory of the devstack folder.

```sh
enable_plugin manila https://github.com/openstack/manila
enable_plugin manila-ui https://github.com/openstack/manila-ui
```

5. Start the install.

```sh
$ ./stack.sh
```

*The installation will take 30-40 minutes, depending on the speed of your internet connection. Devstack will supply sample admin and demo accounts to use freely.*

## Configuring the EOS Driver

## Modifying OpenStack UI for End-User 

## References:
\[1\]: [CERN EOS Service Main Page](http://information-technology.web.cern.ch/services/eos-service)
\[2\]: [DevStack Documentation](https://docs.openstack.org/devstack/latest/)