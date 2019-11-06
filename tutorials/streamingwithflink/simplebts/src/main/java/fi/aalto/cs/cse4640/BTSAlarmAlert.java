/*
 * CS-E4640
 * Linh Truong
 */
package fi.aalto.cs.cse4640;
public class BTSAlarmAlert {
    public boolean warning = false;
    public String station_id;
    public BTSAlarmAlert() {

    }
    public BTSAlarmAlert(String station_id, boolean warning) {
      this.station_id = station_id;
      this.warning =warning;
    }

    public String toString() {
      return "Station with "+station_id+" has too many alarms";
  }
  public String toJSON() {
    return "{\"btsalarmalert\":{\"station_id\":"+station_id+", \"active\":true}}";
  }

}
