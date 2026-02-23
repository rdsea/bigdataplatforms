package fi.aalto.cse4640;
public class OnuSpeed {
    public float speedin = 0;
    public String onuid;
    public OnuSpeed() {
      
    }
    public OnuSpeed(String onuid, float speedin) {
      this.onuid = onuid;
      this.speedin =speedin;
    }
    public float getSpeedin() {
        return speedin;
      }

  public void setSpeedin(float speedin) {
    this.speedin = speedin;
  }

  public String getOnuid() {
    return onuid;
  }

  public void setOnuid(String onuid) {
    this.onuid = onuid ;
  }

  public String toString() {
    return onuid + "\t" + speedin;
  }

}
