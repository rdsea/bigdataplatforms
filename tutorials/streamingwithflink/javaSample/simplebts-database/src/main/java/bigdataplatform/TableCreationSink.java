package bigdataplatform;

import org.apache.flink.api.common.functions.AbstractRichFunction;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.sink.SinkFunction;
import org.apache.flink.streaming.api.functions.sink.SinkFunction.Context;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.api.common.functions.RuntimeContext;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class TableCreationSink extends RichSinkFunction<String> {
    private transient Connection connection;
    private String url;
    private String user;
    private String password;
    private String table_name;

    public TableCreationSink(String url, String user, String password, String table_name) {
        this.url = url;
        this.user = user;
        this.password = password;
        this.table_name = table_name;
    }

    @Override
    public void open(Configuration parameters) throws Exception {
        super.open(parameters);
        connection = DriverManager.getConnection(url, user, password);
        Statement stmt = connection.createStatement();
        String createTableSQL = "CREATE TABLE IF NOT EXISTS " + table_name + "(" +
                                "station_id VARCHAR(255), " +
                                "trend VARCHAR(255))";
        stmt.execute(createTableSQL);
        stmt.close();
    }

    @Override
    public void invoke(String value, SinkFunction.Context context) throws Exception {
        // No-op
    }

    @Override
    public void close() throws Exception {
        super.close();
        if (connection != null) {
            connection.close();
        }
    }
}
