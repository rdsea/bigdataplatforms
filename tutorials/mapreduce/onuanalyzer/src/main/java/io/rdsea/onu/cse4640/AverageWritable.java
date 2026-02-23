package io.rdsea.onu.cse4640;
import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import org.apache.hadoop.io.Writable;

public class AverageWritable implements Writable {

private Float average = new Float(0);
private int count = 1;

public Float getAverage() {
return average;
}

public void setAverage(Float average) {
this.average = average;
}

public int getCount() {
return count;
}

public void setCount(int count) {
this.count = count;
}

public void readFields(DataInput in) throws IOException {

average = in.readFloat();
count = in.readInt();
}

public void write(DataOutput out) throws IOException {

out.writeFloat(average);
out.writeInt(count);
}
public String toString() {
return average + "\t" + count;
}

}
