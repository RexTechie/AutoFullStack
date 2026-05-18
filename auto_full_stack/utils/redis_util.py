#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/11 14:48
@Author  : Rex
@File    : redis_util.py.py
"""
# auto_full_stack/utils/redis_util.py
import redis
from contextlib import contextmanager
from typing import Optional, Generator
from auto_full_stack.common.log import logger

class RedisUtil:

    @staticmethod
    @contextmanager
    def get_connection(host: str = "localhost",
                      port: int = 6379,
                      db: int = 0,
                      password: Optional[str] = None) -> Generator[redis.Redis, None, None]:
        """
        Redis connection context manager
        """
        connection = None
        try:
            connection = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
            logger.debug(f"Connected to Redis: {host}:{port}/{db}")
            yield connection
        except redis.RedisError as e:
            logger.error(f"Redis connection error: {e}")
            raise
        finally:
            if connection:
                logger.debug("Redis connection closed")

    @staticmethod
    def set(key: str, value: str,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None,
            ex: Optional[int] = None) -> bool:
        """
        Set key-value pair
        """
        try:
            with RedisUtil.get_connection(host, port, db, password) as conn:
                conn.set(key, value, ex=ex)
                return True
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

    @staticmethod
    def get(key: str,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None) -> Optional[str]:
        """
        Get value by key
        """
        try:
            with RedisUtil.get_connection(host, port, db, password) as conn:
                return conn.get(key)
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    @staticmethod
    def hset(name: str, key: str, value: str,
             host: str = "localhost",
             port: int = 6379,
             db: int = 0,
             password: Optional[str] = None) -> bool:
        """
        Set hash field
        """
        try:
            with RedisUtil.get_connection(host, port, db, password) as conn:
                conn.hset(name, key, value)
                return True
        except Exception as e:
            logger.error(f"Failed to hset {name} {key}: {e}")
            return False

    @staticmethod
    def hget(
            name: str, key: str,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None) -> Optional[str]:
        """
        Get hash field
        """
        try:
            with RedisUtil.get_connection(host, port, db, password) as conn:
                return conn.hget(name, key)
        except Exception as e:
            logger.error(f"Failed to hget {name} {key}: {e}")
            return None

    @staticmethod
    def hdel(name: str, key: str,
             host: str = "localhost",
             port: int = 6379,
             db: int = 0,
             password: Optional[str] = None) -> bool:
        """
        Delete hash field
        """
        try:
            with RedisUtil.get_connection(host, port, db, password) as conn:
                result = conn.hdel(name, key)
                return result > 0
        except Exception as e:
            logger.error(f"Failed to hdel {name} {key}: {e}")
            return False

    @staticmethod
    def delete(key: str,
               host: str = "localhost",
               port: int = 6379,
               db: int = 0,
               password: Optional[str] = None) -> bool:
        """
        Delete key
        """
        try:
            with RedisUtil.get_connection(host, port, db, password) as conn:
                result = conn.delete(key)
                return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False
