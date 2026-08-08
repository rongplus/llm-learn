




---在Ubuntu 写C++ code
- 1 设置环境
      apt install librdkafka-dev
      sudo apt-get install libhiredis-dev
      sudo apt-get install libmysqlclient-dev
      sudo apt  install protobuf-compiler 
      sudo apt install librdkafka-dev
- 2 代码
    @server.cpp  @KafkaConsumer.cpp  @person.proto 
- 3 编译
      protoc --cpp_out=. person.proto 
      g++ server.cpp  person.pb.cc KafkaConsumer -o server -I /usr/include/mysql -L/usr/lib/mysql -lmysqlclient  -pthread  -lhiredis -lprotobuf -lrdkafka++

        protoc --cpp_out=. person.proto

        g++ server.cpp  -o server -I /usr/include/mysql -L/usr/lib/mysql -lmysqlclient  -pthread  -lhiredis

        g++ server-proto.cpp person.pb.cc -o server -std=c++11 -lprotobuf -pthread -o proto-server


        g++ server.cpp  person.pb.cc -o server -I /usr/include/mysql -L/usr/lib/mysql -lmysqlclient  -pthread  -lhiredis -lprotobuf

        g++ client.cpp  person.pb.cc -o client -I /usr/include/mysql -L/usr/lib/mysql -lmysqlclient  -pthread  -lhiredis -lprotobuf

        g++ server.cpp  person.pb.cc kfk-consumer.cpp -o server -I /usr/include/mysql -L/usr/lib/mysql -lmysqlclient  -pthread  -lhiredis -lprotobuf -lrdkafka++
 

--------------C++ kafka--------------

------编译环境 windows---
./vcpkg.exe install lz4
./vcpkg.exe install rdkafkacpp

------编译环境 ubuntu---
 apt install librdkafka-dev

-------------------c++ mysql--------------------
 Connector/C++ 8.0+ 兼容 MySQL 5.7、8.0 和 8.4。

---在Windows 跑server

- 1 编译环境 windows---
./vcpkg.exe install lz4
./vcpkg.exe install rdkafkacpp

- 2 代码: 
    @server.cpp  @KafkaConsumer.cpp  @person.proto 
