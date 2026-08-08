#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "person.pb.h"
#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    // 创建socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket");
        exit(1);
    }

    // 设置服务器地址
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    // 连接服务器
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("connect");
        close(sock);
        exit(1);
    }

    printf("Connected to server. Type 'quit' to exit.\n");

    while (1) {
        MyProto proto;
        printf("Enter end: ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = '\0'; // 移除换行符
        proto.set_end( buffer);
        printf("Enter cmd: ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = '\0'; // 移除换行符
        proto.set_cmd( buffer);


        std::string buff_str;
        proto.SerializeToString(&buff_str);

        send(sock, buff_str.c_str(), buff_str.size(), 0);
        if (strcmp(buffer, "quit") == 0) break;

        // 接收响应
        int len = recv(sock, buffer, BUFFER_SIZE - 1, 0);
        if (len <= 0) break;
        buffer[len] = '\0';
        printf("Server response: %s %d\n", buffer,len);
    }

    close(sock);
    return 0;
}