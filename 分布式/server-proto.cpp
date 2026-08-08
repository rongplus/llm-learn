#include <iostream>
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include "person.pb.h"

int main() {
    // 创建 socket
    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock == -1) {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }

    // 设置服务器地址
    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8090); // 端口号 8080
    server_addr.sin_addr.s_addr = INADDR_ANY;

    // 绑定 socket
    if (bind(server_sock, (sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        std::cerr << "Bind failed" << std::endl;
        close(server_sock);
        return 1;
    }

    // 监听连接
    if (listen(server_sock, 5) == -1) {
        std::cerr << "Listen failed" << std::endl;
        close(server_sock);
        return 1;
    }

    std::cout << "Server listening on port 8080..." << std::endl;

    // 接受客户端连接
    int client_sock = accept(server_sock, nullptr, nullptr);
    if (client_sock == -1) {
        std::cerr << "Accept failed" << std::endl;
        close(server_sock);
        return 1;
    }

    // 接收客户端消息
    char buffer[1024];
    int bytes_received = recv(client_sock, buffer, sizeof(buffer), 0);
    if (bytes_received <= 0) {
        std::cerr << "Receive failed" << std::endl;
        close(client_sock);
        close(server_sock);
        return 1;
    }

    // 解析 Protobuf 消息
    Person person;
    if (!person.ParseFromArray(buffer, bytes_received)) {
        std::cerr << "Failed to parse protobuf message" << std::endl;
        close(client_sock);
        close(server_sock);
        return 1;
    }

    std::cout << "Received: name=" << person.name() << ", age=" << person.age() << std::endl;

    // 发送响应消息
    Person response;
    response.set_name("Servsdfgsdfgdfger");
    response.set_age(100);
    std::string response_str;
    response.SerializeToString(&response_str);
    send(client_sock, response_str.c_str(), response_str.size(), 0);

    // 关闭连接
    close(client_sock);
    close(server_sock);
    return 0;
}