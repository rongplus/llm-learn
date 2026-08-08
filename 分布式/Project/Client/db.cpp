#include <iostream>

using ::std::cout;
using ::std::endl;

#include <sqlcli1.h>
#include "TestMyDB.h"
//https://www.ibm.com/support/pages/db2-odbc-cli-driver-download-and-installation-information#%5B%3Ch2%3E%5DDownload%5B%3C%2Fh2%3E%5D
//download db2
int testDB() {
    SQLHENV hEnv;
    SQLHDBC hDbc;
    SQLRETURN rc;

    // 初始化环境
    rc = SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, &hEnv);
    rc = SQLSetEnvAttr(hEnv, SQL_ATTR_ODBC_VERSION, (SQLPOINTER)SQL_OV_ODBC3, 0);
    rc = SQLAllocHandle(SQL_HANDLE_DBC, hEnv, &hDbc);

    // 连接数据库
    rc = SQLConnect(hDbc, (SQLCHAR*)"MYDB", SQL_NTS, (SQLCHAR*)"user", SQL_NTS, (SQLCHAR*)"password", SQL_NTS);
    if (rc == SQL_SUCCESS || rc == SQL_SUCCESS_WITH_INFO) {
        std::cout << "Connected to Db2 successfully!" << std::endl;
    }
    else {
        std::cout << "Failed to connect to Db2!" << std::endl;
    }

    // 断开连接
    SQLDisconnect(hDbc);
    SQLFreeHandle(SQL_HANDLE_DBC, hDbc);
    SQLFreeHandle(SQL_HANDLE_ENV, hEnv);

    return 0;
}


