#include "StreamKafka.h"
#include <iostream>
#include <string>
#include <cstdlib>
#include <csignal>
#include <ctime>
#include <thread>
#include <librdkafka/rdkafkacpp.h>

// 全局标志，用于优雅退出
static volatile sig_atomic_t run = 1;

// 信号处理，用于 Ctrl+C 退出
static void stop(int sig) {
    run = 0;
}

// 投递回调函数
class DeliveryReportCb : public RdKafka::DeliveryReportCb {
public:
    void dr_cb(RdKafka::Message& message) override {
        if (message.err()) {
            std::cerr << "Message delivery failed: " << message.errstr() << std::endl;
        }
        else {
            std::cout << "Message delivered to topic " << message.topic_name()
                << " [" << message.partition() << "] at offset "
                << message.offset() << std::endl;
        }
    }
};

// 生成流式消息（示例：时间戳 + 计数器）
std::string generate_stream_message(int counter) {
    time_t now = time(nullptr);
   // std::string timestamp = ctime(&now);
   // timestamp.pop_back(); // 移除换行符
    return "Stream message #" + std::to_string(counter);// +" at " + timestamp;
}

int Produce3() {
    std::string brokers = "192.168.226.131:9092";  // Kafka Broker 地址
    std::string topic = "cpp-stream-producer";      // 目标主题
    std::string errstr;
    int message_counter = 0;

    // 捕获 Ctrl+C 信号
    signal(SIGINT, stop);

    // 配置生产者
    RdKafka::Conf* conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);
    conf->set("bootstrap.servers", brokers, errstr);
    conf->set("client.id", "cpp-stream-producer", errstr);
    // 可选：优化流式发送
    conf->set("batch.size", "10000", errstr); // 批量大小
    conf->set("linger.ms", "5", errstr);     // 等待时间

    DeliveryReportCb dr_cb;
    conf->set("dr_cb", &dr_cb, errstr);  // 设置投递回调

    // 创建生产者
    RdKafka::Producer* producer = RdKafka::Producer::create(conf, errstr);
    if (!producer) {
        std::cerr << "Failed to create producer: " << errstr << std::endl;
        delete conf;
        return 1;
    }

    // 创建 Topic 对象（兼容旧版本）
    RdKafka::Conf* tconf = RdKafka::Conf::create(RdKafka::Conf::CONF_TOPIC);
    RdKafka::Topic* topicObj = RdKafka::Topic::create(producer, topic, tconf, errstr);
    if (!topicObj) {
        std::cerr << "Failed to create topic: " << errstr << std::endl;
        delete producer;
        delete conf;
        return 1;
    }

    // 发送流式消息
    std::cout << "Starting stream producer. Press Ctrl+C to stop..." << std::endl;
    while (run) {
        std::string message = generate_stream_message(++message_counter);
        RdKafka::ErrorCode err = producer->produce(
            topicObj,
            RdKafka::Topic::PARTITION_UA,
            RdKafka::Producer::RK_MSG_COPY,
            const_cast<char*>(message.c_str()),
            message.size(),
            nullptr,  // 键
            nullptr   // 用户数据
        );

        if (err != RdKafka::ERR_NO_ERROR) {
            std::cerr << "Produce failed: " << RdKafka::err2str(err) << std::endl;
            if (err == RdKafka::ERR__QUEUE_FULL) {
                producer->poll(1000);  // 队列满时等待
                continue;
            }
        }
        else {
            std::cout << "Enqueued: " << message << std::endl;
        }

        producer->poll(0);  // 处理回调
        std::this_thread::sleep_for(std::chrono::seconds(1));           // 每秒发送一条消息
    }

    // 清理未发送的消息
    while (producer->outq_len() > 0) {
        std::cout << "Waiting for " << producer->outq_len() << " messages to be delivered..." << std::endl;
        producer->poll(1000);
    }

    // 清理资源
    delete topicObj;
    delete tconf;
    delete producer;
    delete conf;

    std::cout << "Stream producer stopped." << std::endl;
    return 0;
}