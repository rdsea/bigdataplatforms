/*
 * CS-E4640
 * Tri Nguyen
 */
package fi.aalto.cs.cse4640;
public class BTSTrendAlert {
    public String trend = "";
    public String station_id;
    public BTSTrendAlert() {

    }
    public BTSTrendAlert(String station_id, String trend) {
      this.station_id = station_id;
      this.trend =trend;
    }

    public String toString() {
      return "Station "+station_id+" has "+trend+" trend";
  }
    public String toJSON() {
    return "{\"btsalarmalert\":{\"station_id\":"+station_id+", \"trend\":"+trend+"}}";
  }

}
