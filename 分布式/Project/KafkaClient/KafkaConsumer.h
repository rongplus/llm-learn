#pragma once
#include <string>
#include <iostream>
#include <vector>
#include <stdio.h>
#include <librdkafka/rdkafka.h>
#include <librdkafka/rdkafkacpp.h>

class KafkaConsumer
{
public:/**
     * @brief KafkaConsumer
     * @param brokers
     * @param groupID
     * @param topics
     * @param partition
     */
    explicit KafkaConsumer(const std::string& brokers, const std::string& groupID,
        const std::vector<std::string>& topics, int partition);
    void pullMessage();
    ~KafkaConsumer();
protected:
    std::string m_brokers;
    std::string m_groupID;
    std::vector<std::string> m_topicVector;
    int m_partition;
    RdKafka::Conf* m_config;
    RdKafka::Conf* m_topicConfig;
    RdKafka::KafkaConsumer* m_consumer;
    RdKafka::EventCb* m_event_cb;
    RdKafka::RebalanceCb* m_rebalance_cb;
};