
#include <librdkafka/rdkafka.h>
#include <librdkafka/rdkafkacpp.h>
#include <iostream>
#include <string>

#include "Kafka.h"
#include "StreamKafka.h"

int main() 
{
   // Consumer();
    Produce1();
    std::cout << "Produce1 - ok" << endl;
    //Produce2();
    std::cout << "Produce2 -- ok" << endl;
    //test OK;
    //Produce3();
    std::cout << "Produce3 -- ok" << endl;
    return 0;
}