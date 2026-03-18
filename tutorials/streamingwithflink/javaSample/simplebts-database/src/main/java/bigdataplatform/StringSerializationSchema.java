package bigdataplatform;
import org.apache.flink.streaming.connectors.kafka.KafkaSerializationSchema;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.nio.charset.StandardCharsets;

public class StringSerializationSchema implements KafkaSerializationSchema<String>{

    private String topic;

    public StringSerializationSchema(String topic) {
        super();
        this.topic = topic;
    }

    @Override
    public ProducerRecord<byte[], byte[]> serialize(String element, Long timestamp) {
        return new ProducerRecord<>(this.topic, element.getBytes(StandardCharsets.UTF_8));
    }

}
