#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/8/23 14:13
@Author  : Rex
@File    : mysql_util.py
"""
from contextlib import contextmanager
from typing import Optional, Generator

import pymysql
from auto_full_stack.common.log import logger

class MySQLUtil:

    @staticmethod
    @contextmanager
    def get_connection(database: Optional[str] = None,
                       user: str = "root",
                       password: str = "root",
                       host: str = "localhost",
                       port: int = 3306) -> Generator[pymysql.Connection, None, None]:
        """
        Database connection context manager
        """
        connection = None
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset='utf8mb4',
                autocommit=False,
                # Compatible with MySQL 8.0+ authentication methods
                auth_plugin_map={
                    'caching_sha2_password': 'mysql_native_password'
                }
            )
            logger.info(f"Connected to MySQL: {host}:{port}/{database or 'N/A'}")
            yield connection
        except pymysql.Error as e:
            if connection:
                connection.rollback()
            logger.error(f"MySQL connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()
                logger.info("MySQL connection closed")

    @staticmethod
    def create_database(database: str,
                        user: str = "root",
                        password: str = "root",
                        host: str = "localhost",
                        port: int = 3306,
                        charset: str = "utf8mb4",
                        collate: str = "utf8mb4_general_ci") -> bool:
        """
        Create a new database
        """
        try:
            with MySQLUtil.get_connection(None, user, password, host, port) as conn:
                with conn.cursor() as cursor:
                    sql = f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET {charset} COLLATE {collate}"
                    cursor.execute(sql)
                    conn.commit()

                logger.info(f"Database '{database}' created successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to create database {database}: {e}")
            return False

    @staticmethod
    def drop_database(database: str,
                        user: str = "root",
                        password: str = "root",
                        host: str = "localhost",
                        port: int = 3306,
                        charset: str = "utf8mb4",
                        collate: str = "utf8mb4_general_ci") -> bool:
        """
        Drop the specified database
        """
        try:
            with MySQLUtil.get_connection(None, user, password, host, port) as conn:
                with conn.cursor() as cursor:
                    sql = f"DROP DATABASE IF EXISTS `{database}`"
                    cursor.execute(sql)
                    conn.commit()

                logger.info(f"Database '{database}' dropped successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to drop database {database}: {e}")
            return False


    @staticmethod
    def drop_all_table(database: str,
                          user: str = "root",
                          password: str = "root",
                          host: str = "localhost",
                          port: int = 3306) -> bool:
        """
        Drop all tables in the specified database
        """
        try:
            with MySQLUtil.get_connection(database, user, password, host, port) as conn:
                with conn.cursor() as cursor:
                    # Disable foreign key checks
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

                    # Get all table names
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()

                    if not tables:
                        logger.info("No tables found to drop")
                        return True

                    # Drop each table
                    for (table_name,) in tables:
                        cursor.execute("DROP TABLE IF EXISTS `%s`" % table_name)
                        logger.info(f"Dropped table: {table_name}")

                    # Re-enable foreign key checks
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    conn.commit()

                logger.info(f"Successfully dropped {len(tables)} tables from database: {database}")
                return True

        except Exception as e:
            logger.error(f"Failed to drop tables in database {database}: {e}")
            return False


    @staticmethod
    def execute_sql_by_file(script_path: str,
                            database: str,
                            user: str = "root",
                            password: str = "root",
                            host: str = "localhost",
                            port: int = 3306):
        """
        Execute SQL script from a file
        """

        try:
            with open(script_path, 'r', encoding="utf-8") as file:
                sql_script = file.read()

            logger.info(f"Reading SQL script from: {script_path}")
            return MySQLUtil.execute_sql_script(
                sql_script=sql_script,
                database=database,
                user=user,
                password=password,
                host=host,
                port=port
            )

        except FileNotFoundError:
            logger.error(f"SQL script file not found: {script_path}")
        except IOError as e:
            logger.error(f"Error reading SQL script file {script_path}: {e}")

    @staticmethod
    def execute_sql_script(sql_script: str,
                            database: str,
                            user: str = "root",
                            password: str = "root",
                            host: str = "localhost",
                            port: int = 3306) -> bool:
        """
        Execute SQL script from a string
        """
        if not sql_script.strip():
            logger.warning("Empty SQL script provided")

        try:
            with MySQLUtil.get_connection(database, user, password, host, port) as conn:
                sql_commands = sql_script.split(";")

                with conn.cursor() as cursor:
                    executed_count = 0
                    for command in sql_commands:
                        if command:
                            try:
                                result = cursor.execute(command)
                                executed_count += 1
                                logger.debug(f"Executed SQL command {executed_count}, affected rows: {result}")
                            except pymysql.Error as e:
                                logger.error(f"Error executing SQL command: {command[:100]}... Error: {e}")
                                raise

                conn.commit()
                logger.info(f"Successfully executed {executed_count} SQL commands")
                return True

        except Exception as e:
            logger.error(f"Failed to execute SQL script: {e}")
            return False

