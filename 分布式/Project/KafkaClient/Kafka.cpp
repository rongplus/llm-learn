#include "Kafka.h"



int Produce1( ) {

    std::string brokers = "192.168.226.131:9092";
    std::string topic = "cpp-test";

    RdKafka::Conf* conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);

    std::string errstr;
    /* Set bootstrap broker(s) as a comma-separated list of
    * host or host:port (default port 9092).
    * librdkafka will use the bootstrap brokers to acquire the full
    * set of brokers from the cluster. */
    if (conf->set("bootstrap.servers", brokers, errstr) !=
        RdKafka::Conf::CONF_OK) {
        std::cerr << errstr << std::endl;
        exit(1);
    }

    ExampleDeliveryReportCb ex_dr_cb;

    if (conf->set("dr_cb", &ex_dr_cb, errstr) != RdKafka::Conf::CONF_OK) {
        std::cerr << errstr << std::endl;
        exit(1);
    }

    /*
    * Create producer instance.
    */
    RdKafka::Producer* producer = RdKafka::Producer::create(conf, errstr);
    if (!producer) {
        std::cerr << "Failed to create producer: " << errstr << std::endl;
        exit(1);
    }
    delete conf;

    /*
    * Read messages from stdin and produce to broker.
    */
    std::cout << "% Type message value and hit enter " <<
        "to produce message." << std::endl;

    for (std::string line; true && std::getline(std::cin, line);)
    {
        if (line.empty()) {
            producer->poll(0);
            continue;
        }

    retry:
        RdKafka::ErrorCode err =
            producer->produce(topic, RdKafka::Topic::PARTITION_UA,
                RdKafka::Producer::RK_MSG_COPY /* Copy payload */,
                /* Value */
                const_cast<char*>(line.c_str()), line.size(),
                /* Key */
                NULL, 0,
                /* Timestamp (defaults to current time) */
                0,
                /* Message headers, if any */
                NULL);

        if (err != RdKafka::ERR_NO_ERROR) {
            std::cerr << "% Failed to produce to topic " << topic << ": " <<
                RdKafka::err2str(err) << std::endl;

            if (err == RdKafka::ERR__QUEUE_FULL) {
                producer->poll(1000/*block for max 1000ms*/);
                goto retry;
            }

        }
        else {
            std::cerr << "% Enqueued message (" << line.size() << " bytes) " <<
                "for topic " << topic << std::endl;
        }

        producer->poll(0);
    }

    std::cerr << "% Flushing final messages..." << std::endl;
    producer->flush(10 * 1000 /* wait for max 10 seconds */);

    if (producer->outq_len() > 0)
        std::cerr << "% " << producer->outq_len() <<
        " message(s) were not delivered" << std::endl;

    delete producer;

    return 0;
}



int Produce2() {
    std::string brokers = "192.168.226.128:9092,192.168.226.130:9092"; // Kafka集群地址和端口号
    std::string topic = "cpp-test"; // Kafka主题

    // 创建Kafka配置对象
    RdKafka::Conf* conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);

    // 设置Kafka集群地址和端口号
    std::string errstr;
    if (conf->set("bootstrap.servers", brokers, errstr) != RdKafka::Conf::CONF_OK) {
        std::cerr << "Failed to set broker list: " << errstr << std::endl;
        delete conf;
        return 1;
    }

    // 创建Kafka Producer对象
    RdKafka::Producer* producer = RdKafka::Producer::create(conf, errstr);
    if (!producer) {
        std::cerr << "Failed to create producer: " << errstr << std::endl;
        delete conf;
        return 1;
    }

    // 发送消息
    std::string message = "Hello, Kafka!";
    RdKafka::ErrorCode resp = producer->produce(topic, RdKafka::Topic::PARTITION_UA,
        RdKafka::Producer::RK_MSG_COPY,
        const_cast<char*>(message.c_str()),
        message.size(),
        NULL, 0, 0, NULL);


    std::string line;

    RdKafka::ErrorCode err =
        producer->produce(topic, RdKafka::Topic::PARTITION_UA,
            RdKafka::Producer::RK_MSG_COPY /* Copy payload */,
            /* Value */
            const_cast<char*>(line.c_str()), line.size(),
            /* Key */
            NULL, 0,
            /* Timestamp (defaults to current time) */
            0,
            /* Message headers, if any */
            NULL);


    if (resp != RdKafka::ERR_NO_ERROR) {
        std::cerr << "Failed to produce message: " << RdKafka::err2str(resp) << std::endl;
    }

    // 等待消息发送完成
    producer->flush(1000);

    // 释放资源
    delete producer;
    delete conf;

    return 0;


}