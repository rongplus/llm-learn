#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>

#pragma comment(lib, "ws2_32.lib")  // 链接 WinSock 库

#include "TestMyDB.h"

int main() {

    testDB();
    WSADATA wsaData;              // WinSock 初始化数据
    SOCKET sock = INVALID_SOCKET; // 客户端 socket
    struct sockaddr_in server_addr; // 服务器地址结构
    char buffer[1024];            // 接收数据的缓冲区

    // 初始化 WinSock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed" << std::endl;
        return 1;
    }

    // 创建 socket
    sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "Socket creation failed" << std::endl;
        WSACleanup();
        return 1;
    }

    // 设置服务器地址
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);  // 服务器端口号
    inet_pton(AF_INET, "192.168.226.129", &server_addr.sin_addr);  // 服务器 IP 地址

    // 连接到服务器
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "Connection failed" << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    std::cout << "Connected to server. Type 'quit' to exit." << std::endl;

    // 主循环：发送消息并接收响应
    while (true) {
        std::string message;
        std::cout << "Enter message: ";
        std::getline(std::cin, message);  // 获取用户输入

        if (message == "quit") {
            break;  // 输入 "quit" 退出
        }

        // 发送消息到服务器
        send(sock, message.c_str(), message.size(), 0);

        // 接收服务器响应
        int bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received > 0) {
            buffer[bytes_received] = '\0';  // 添加字符串结束符
            std::cout << "Server response: " << buffer << std::endl;
        }
    }

    // 清理并关闭
    closesocket(sock);
    WSACleanup();
    return 0;
}