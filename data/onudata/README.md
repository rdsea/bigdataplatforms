# Data Description

>Just a small sample of data is provided for study. Large data sets can be inquired. Kindly note the data license

* TIME: record time
* PROVINCECODE: code of the network sector
* DEVICEID: id of device
* IFINDEX: interface id
* FRAME: frame id
* SLOT: slot id
* PORT: port number
* ONUINDEX: onu index
* ONUID: network interface
* SPEEDIN:  traffic moved into an ONU(network interface) measured in *bit/s*
* SPEEDOUT: traffic moved out an ONU(network interface) measured in *bit/s*
* BYTEIN: byte in during the period of monitoring
* BYTEOUT: byte out during the period of monitoring

>The value of some data fields has been anonymized.

Interfaces  are ports of GPON of OLT equipment, identified by ONUID (DeviceIP/Frame/Slot/Port:OnuIndex) .

Each customer has one ONU. Data of the customer (Internet, IPTV, VoD, VoIP...) will be passed via this ONU. Each PON port could have maximum 64 ONU. One card line has  16 port PON. One  OLT (2 card line) could have 2048 ONU (16 x 2 x 64). Each   OLT could be used for 700-800 customers.

Throughput:
   * 1 port GPON: 1.2Gbps up, 2.4Gbps down
   * OLT = 16 (max) x 1Gbps

Current Payload:
  * ~10K node ~ 5M sensor

  Cycle:
    * per 5 minutes -> 288 record/sensor/day (24x60/5)

  Total records/day
    * 5M x  288 = 1.440 M (records/day)

   Data sizes:
    * 1 record ~ 50 byte -> disk size/day = 1.440M x 50 = 72GB/day
