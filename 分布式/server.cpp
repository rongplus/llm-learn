#include <iostream>
#include <string>
#include <thread>
#include <vector>
#include <mutex>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <mysql/mysql.h>
#include <hiredis/hiredis.h>
#include <sys/select.h>
#include "person.pb.h"

#include "KafkaConsumer.h"


//g++ server.cpp  -o server -I /usr/include/mysql -L/usr/lib/mysql -lmysqlclient  -pthread  -lhiredis


const int MYSQL_POOL_SIZE = 5;  // MySQL 连接池大小
const int REDIS_POOL_SIZE = 5;  // Redis 连接池大小
std::vector<MYSQL*> mysql_pool; // MySQL 连接池
std::vector<redisContext*> redis_pool; // Redis 连接池
std::mutex mysql_mutex, redis_mutex; // 保护连接池的互斥锁

// 初始化 MySQL 连接池
void init_mysql_pool() {
    for (int i = 0; i < MYSQL_POOL_SIZE; ++i) {
        MYSQL *conn = mysql_init(nullptr);
        if (!mysql_real_connect(conn, "192.168.1.115", "root", "123456", "employees", 0, nullptr, 0)) {
            std::cerr << "MySQL connection failed: " << mysql_error(conn) << std::endl;
            continue;
        }
        mysql_pool.push_back(conn);
    }
    std::cout << "Initialized " << mysql_pool.size() << " MySQL connections." << std::endl;
}

// 初始化 Redis 连接池
void init_redis_pool() {
    for (int i = 0; i < REDIS_POOL_SIZE; ++i) {
        redisContext *conn = redisConnect("192.168.1.115", 6379);
        if (conn == nullptr || conn->err) {
            std::cerr << "Redis connection failed: " << (conn ? conn->errstr : "Unknown error") << std::endl;
            continue;
        }
        redis_pool.push_back(conn);
    }
    std::cout << "Initialized " << redis_pool.size() << " Redis connections." << std::endl;
}

// 从 MySQL 连接池获取连接
MYSQL* get_mysql_connection() {
    std::lock_guard<std::mutex> lock(mysql_mutex);
    if (mysql_pool.empty()) return nullptr;
    MYSQL* conn = mysql_pool.back();
    mysql_pool.pop_back();
    return conn;
}

// 归还 MySQL 连接到池中
void release_mysql_connection(MYSQL* conn) {
    std::lock_guard<std::mutex> lock(mysql_mutex);
    mysql_pool.push_back(conn);
}

// 从 Redis 连接池获取连接
redisContext* get_redis_connection() {
    std::lock_guard<std::mutex> lock(redis_mutex);
    if (redis_pool.empty()) return nullptr;
    redisContext* conn = redis_pool.back();
    redis_pool.pop_back();
    return conn;
}

// 归还 Redis 连接到池中
void release_redis_connection(redisContext* conn) {
    std::lock_guard<std::mutex> lock(redis_mutex);
    redis_pool.push_back(conn);
}

// 处理客户端请求
void handle_client(int client_sock) {
    MYSQL* mysql_conn = get_mysql_connection();
    redisContext* redis_conn = get_redis_connection();
    if (!mysql_conn || !redis_conn) {
        std::cerr << "Failed to get connections from pool" << std::endl;
        close(client_sock);
        return;
    }

    char buffer[1024];
    while (true) 
    {
        int bytes_received = recv(client_sock, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received <= 0)
        {
            
            break; // 客户端断开连接
        } 
        MyProto proto;
        if (!proto.ParseFromArray(buffer, bytes_received)) {
            std::cerr << "Failed to parse protobuf message" << std::endl;
            break;
        }
       
        std::string response;

        // 处理 MySQL 请求
        std::string query = proto.cmd();
        if (proto.end().find("MYSQL") == 0) {
            
            if (mysql_query(mysql_conn, query.c_str())) {
                response = "MySQL error: " + std::string(mysql_error(mysql_conn));
            } else {
                MYSQL_RES *result = mysql_store_result(mysql_conn);
                if (result) {
                    int num_fields = mysql_num_fields(result);
                    MYSQL_ROW row;
                    while ((row = mysql_fetch_row(result))) {
                        for (int i = 0; i < num_fields; i++) {
                            response += (row[i] ? row[i] : "NULL");
                            if (i < num_fields - 1) response += ",";
                        }
                        response += "\n";
                    }
                    mysql_free_result(result);
                } else {
                    response = "Query executed successfully.";
                }
            }
        }
        // 处理 Redis 请求
        else if (proto.end().find("REDIS") == 0) {
  
            redisReply *reply = (redisReply*)redisCommand(redis_conn, query.c_str());
            if (reply == nullptr) {
                response = "Redis error: " + std::string(redis_conn->errstr);
            } else {
                if (reply->type == REDIS_REPLY_STRING || reply->type == REDIS_REPLY_STATUS) {
                    response = reply->str ? reply->str : "";
                } else if (reply->type == REDIS_REPLY_INTEGER) {
                    response = std::to_string(reply->integer);
                } else {
                    response = "Unsupported Redis reply type";
                }
                freeReplyObject(reply);
            }
        } else {
            response = "Invalid request format";
        }

        response += "END_OF_RESPONSE\n";
        send(client_sock, response.c_str(), response.size(), 0);
    }

    release_mysql_connection(mysql_conn);
    release_redis_connection(redis_conn);
    //TEST not close
    close(client_sock);
    std::cout << "connections closed" << std::endl;
}

int main() {
    // 初始化连接池
    init_mysql_pool();
    init_redis_pool();

    std::string brokers = "192.168.226.129:9092";
std::vector<std::string> topics;
topics.push_back("test123");
// topics.push_back("test2");
std::string group = "testG";
  
std::cout << "group " << group << std::endl;

KafkaConsumer consumer(brokers, group, topics, RdKafka::Topic::OFFSET_BEGINNING);
consumer.pullMessage();

    // 创建服务器 socket
    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock == -1) {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_sock, (sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        std::cerr << "Bind failed" << std::endl;
        close(server_sock);
        return 1;
    }

    if (listen(server_sock, 5) == -1) {
        std::cerr << "Listen failed" << std::endl;
        close(server_sock);
        return 1;
    }

    std::cout << "Server listening on port 8080..." << std::endl;

    // 使用 select 进行事件驱动 I/O
    fd_set master_set, read_set;
    FD_ZERO(&master_set);
    FD_SET(server_sock, &master_set);
    int max_fd = server_sock;

    while (true) {
        read_set = master_set;
        if (select(max_fd + 1, &read_set, nullptr, nullptr, nullptr) == -1) {
            std::cerr << "Select failed" << std::endl;
            continue;
        }

        for (int fd = 0; fd <= max_fd; ++fd) {
            if (FD_ISSET(fd, &read_set)) {
                //add a new line to 
                //因此，当 fd == server_sock 且 FD_ISSET(server_sock, &read_set) 为 true 时，说明有新的客户端连接请求到达。
                //如果 fd != server_sock 且 FD_ISSET(fd, &read_set) 为 true，则表示某个已连接的客户端套接字有数据可读。这时，服务器需要从该客户端套接字读取数据并进行处理，而不是接受新连接。
                std::cout << "fd=" << fd << std::endl;
                if (fd == server_sock) {
                    // 接受新连接
                    int client_sock = accept(server_sock, nullptr, nullptr);
                    if (client_sock == -1) {
                        std::cerr << "Accept failed" << std::endl;
                        continue;
                    }
                    FD_SET(client_sock, &master_set);
                    std::cout << "client_sock=" << client_sock << std::endl;
                    if (client_sock > max_fd) max_fd = client_sock;
                    std::cout << "New client connected: " << client_sock << std::endl;
                } else {
                    // 处理客户端请求，创建线程
                    std::cout << "Exit client connected: " << fd << std::endl;
                    std::thread(handle_client, fd).detach();
                    FD_CLR(fd, &master_set); // 处理完后移除，避免重复处理
                }
            }
        }
    }

    close(server_sock);
    return 0;
}