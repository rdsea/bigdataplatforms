# Sample of BTS monitoring data
## Important note about the license of dataset
This data is shared only for the CS-E4640 course participants. You are not allowed to share or used outside the course exercises and assignments.

Data is provided by BachPhu, a company developing IoT solution in Vietnam. Contact: linh.truong@aalto.fi if you have any question about the data license.

## Introduction
This is a collection of sensors data from base stations.
The data structure is as follow:

* station_id: the id of the stations
* datapoint_id: the id of the sensor (data point)
* alarm_id: the id of the alarm
* event_time: the time at which the event occurs
* value: the value of the measurement of the datapoint
* valueThreshold: the threshold set for the alarm. Note that some threshold values are set to a default value of 999999.
* isActive: the alarm is active (true ) or not (false)
* storedtime: no store

Note that the data is not clean.

The following table describes sensors (datapoint_id):

parametr_id  | sensor
--------------  |--------------------
111 |	Room Temperature
112 |	Temperature of Airconditioner 1
126 |	Frequency of Power Generator
123 |	Frequency of Power Grid
124 |	Voltage of Power Generator
114 |	Outdoor temperature
121 |	Voltage of Power Grid
113 |	Temperature of Airconditioner 2
162 |	Runtime of Airconditioner 1
163 |	Runtime of Airconditioner 2
164 |	Runtime of AC
165 |	Runtime of Power Generator
153 |	Motion sensor
151 |	Smoke sensor
152 |	Door sensor
154 |	Water leak sensor
125 |	Load of power generator
122 |	Load of Power Grid
161 |	Capacity
155 |	Heat increase
141 |	Total Battery Voltage
115 |	Humidity
116 |	Battery temperature
143 |	Voltage of Battery 1
144 |	Voltage of Battery 2
142 |	Load of Battery 1
145 |	Load of Battery 1


The follow table explains some types of alarms:

alarm_id | Type of alarms
----------|--------------
316	| smoke
319	| motion
320	| failed temperature sensor
303	| failed equipment
306	| high moisture
307	| low moisture
308	| high AC voltage
309	| low AC voltage
310	| high AC load current
311	| low AC load current
312	| high DC voltage
313	| low  DC voltage
314	| high DC load current
315	| low DC load current
322	|high room temperature
323	|connection loss
302	| equipment connection loss
304	| high outdoor temperature
321	| lack of gass in air conditioner
317	| door open
318	| flooding
324	| increasing temperature
325	| battery's high temperature
301	| AC power loss
305	| low temperature

## Some usages
This is about aggregated data. You can use the station_id to split data into
different small data sets:

    - all data with the same station id comes from one station
    - you can use alarm_id or datapoint_id to identify sensors or alarms

therefore, based on station id, alarm_id, datapoint_id, you can emulate
various sensors from different stations.  For example:

     - using alarm*.csv: you emulate various stations, in which various alarm sensors (using alarm id) sending alarm information about parameters (param id) whose values are above the threashold.


You can also do some analytics, e.g. analyze frequency of alarms.
