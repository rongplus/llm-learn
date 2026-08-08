#pragma once
#include <iostream>
#include <string>
#include <list>
#include <stdint.h>
#include <librdkafka/rdkafka.h>
#include <librdkafka/rdkafkacpp.h>
#include <list>
using namespace std;

class Kafka
{
};

class ExampleDeliveryReportCb : public RdKafka::DeliveryReportCb {
public:
    void dr_cb(RdKafka::Message& message) {
        /* If message.err() is non-zero the message delivery failed permanently
        * for the message. */
        if (message.err())
            std::cerr << "% Message delivery failed: " << message.errstr() << std::endl;
        else
            std::cerr << "% Message delivered to topic " << message.topic_name() <<
            " [" << message.partition() << "] at offset " <<
            message.offset() << std::endl;
    }
};


int Consumer();
int Produce1();
int Produce2();