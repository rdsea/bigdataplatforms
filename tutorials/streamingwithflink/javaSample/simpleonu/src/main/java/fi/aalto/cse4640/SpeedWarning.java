package fi.aalto.cse4640;
public class SpeedWarning {
    public boolean warning = false;
    public String onuid;
    public SpeedWarning() {

    }
    public SpeedWarning(String onuid, boolean warning) {
      this.onuid = onuid;
      this.warning =warning;
    }
    public boolean getWarning() {
        return warning;
    }

  public void setWarning(boolean warning) {
    this.warning = warning;
  }

  public String getOnuid() {
    return onuid;
  }

  public void setOnuid(String onuid) {
    this.onuid = onuid ;
  }

  public String toString() {
    return onuid ;
  }

}
