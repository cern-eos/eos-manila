# EOS Manila: Manila Driver for EOS Storage
The purpose of this driver is to directly connect CERN users with the OpenStack interface in order to request and configure in a self-service approach storage space at CERN. Every CERN user has a dashboard in OpenStack where one can for example request virtual machines and space in storage systems. The driver aims to connect the two systems using their APIs. 

The driver in this repository is a generic baseline to understand how OpenStack Manila handles calls made to drivers in order to communicate with outside interfaces. Through this sample driver we are able to "interface" with the local machine in order to create fake shares in the logged-in user's home directory. The server-side of this system employs a Python GRPC server to process requests. All requests must use the EOS protocol and a valid "fake" authentication key.

## About EOS Storage
EOS is a disk-based, low-latency storage service. Having a highly-scalable hierarchical namespace, and with data access possible by the XROOT protocol, it was initially used for physics data storage. Today, EOS provides storage for both physics and user use cases. The main target area for the EOS is physics data analysis, which is characterised by many concurrent users, a significant fraction of random data access and a large file-open rate \[1\]. 

# Driver Capabilities
This driver currently supports:

 - Creating a Share
 - Deleting a Share
 - Extending a Share
 - Shrinking a Share

# Manila Installation With DevStack

# Configuring the EOS Driver

# Modifying OpenStack UI for End-User 

# References:
\[1\]: [CERN EOS Service Main Page](http://information-technology.web.cern.ch/services/eos-service)