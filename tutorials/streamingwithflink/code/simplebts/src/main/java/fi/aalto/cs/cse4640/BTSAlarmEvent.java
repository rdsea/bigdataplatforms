/*
* CS-E4640
 * Linh Truong
 */
package fi.aalto.cs.cse4640;

import java.util.Date;

/**
 *
 * @author truong
 */
public class BTSAlarmEvent {
    public String station_id;
    public String datapoint_id;
    public String alarm_id;
    public Date event_time;
    public float value;
    public float valueThreshold;
    BTSAlarmEvent() {

    }
    BTSAlarmEvent(String station_id, String datapoint_id, String alarm_id, Date event_time, Float value, Float valueThreshold) {
        this.station_id = station_id;
        this.datapoint_id = datapoint_id;
        this.alarm_id = alarm_id;
        this.event_time = event_time;
        this.value = value;
        this.valueThreshold = valueThreshold;
    }
    public String toString() {
        return "station_id="+station_id + " for datapoint_id=" + datapoint_id + " at " + event_time.toString() + " alarm_id="+alarm_id+" with value =" +value;
    }
}
