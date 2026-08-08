// SQLClient.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <iostream>

using ::std::cout;
using ::std::endl;

#include <mysql.h>
// 初始化 MySQL 连接池
void init_mysql_pool() {
    //mysql_error();
    std::string response;
    for (int i = 0; i < 5; ++i) {
        MYSQL* conn = mysql_init(nullptr);
        if (!mysql_real_connect(conn, "192.168.1.108", "root", "123456", "employees", 0, nullptr, 0)) {//port = 3306
        //if (!mysql_real_connect(conn, "localhost", "root", "123456", "employees", 3307, nullptr, 0)) {
            std::cerr << "MySQL connection failed: " << mysql_error(conn) << std::endl;
            continue;
        }
        std::cout << "step 1\n";
        if (mysql_query(conn, "select * from employees limit 10 ")) {
            response = "MySQL error: " + std::string(mysql_error(conn));
            std::cout << response << endl;
        }
        else {
            MYSQL_RES* result = mysql_store_result(conn);
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
                std::cout << response << endl;
            }
            else {
                response = "Query executed successfully.";
            }
        }
    }
    std::cout << "Initialized " << " MySQL connections."  << response << std::endl;
}


int testMYSQL()
{
    init_mysql_pool();


    return EXIT_SUCCESS;

}



int main()
{
    std::cout << "Hello World!\n";
    init_mysql_pool();
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
