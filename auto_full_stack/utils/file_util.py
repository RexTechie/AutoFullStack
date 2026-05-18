#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/14 17:58
@Author  : Rex
@File    : file_util.py.py
"""
import os
import shutil
from string import Template
from auto_full_stack.common.log import logger


class FileUtil:

    @staticmethod
    def create_dir(dir_path):
        """
        If the path does not exist, create it.
        :param dir_path: Directory path
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    @staticmethod
    def write_file(file_path, content):
        """
        Write content to a file, creating the file if it does not exist
        :param file_path: File path
        :param content: File content
        :return:
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def append_file(file_path, content):
        """
        追加内容到文件,如果文件不存在则创建文件
        :param file_path: 文件路径
        :param content: 文件内容
        :return:
        """
        # 获取文件路径中的目录部分
        directory = os.path.dirname(file_path)
        # 如果目录不存在，则创建它
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'a+', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def remove_dir(dir_path):
        """
        Remove the directory
        """
        shutil.rmtree(dir_path)

    @staticmethod
    def remove_file(file_path):
        """
        Remove the file
        """
        os.remove(file_path)

    @staticmethod
    def clear_file(file_path):
        """
        Clean the file content
        """
        with open(file_path, 'w') as f:
            f.truncate()
            logger.info(f"File {file_path} cleared")

    @staticmethod
    def read_file(file_path):
        """
        Read file content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"File {file_path} not exist")
            return None
        except IOError as e:
            logger.error(f"Read file {file_path} error: {e}")
            return None

    @staticmethod
    def get_template(template_file_path):
        """
        Get template content from file
        """
        template_str = None
        with open(template_file_path, 'r', encoding='utf-8') as template_file:
            template_str = template_file.read()

        return Template(template_str)

    @staticmethod
    def copy_all_files(src_dir, dest_dir):
        """
        Copy all files from source directory to destination directory
        """
        try:
            # Ensure the source directory exists
            if not os.path.exists(src_dir):
                raise FileNotFoundError(f"Source directory '{src_dir}' does not exist.")

            # If the destination directory does not exist, create it
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # Iterator over all items in the source directory
            for item in os.listdir(src_dir):
                src_path = os.path.join(src_dir, item)
                dest_path = os.path.join(dest_dir, item)

                # If it's a file, copy it; if it's a directory, copy the directory recursively
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                elif os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            logger.info(f"Copy all files from {src_dir} to {dest_dir}")
        except Exception as e:
            logger.error(f"Error copying files: {e}")

    @staticmethod
    def generate_env(env_dict: dict, file_path):
        """
        Generate .env file
        :return:
        """
        env_str = ""
        for key, value in env_dict.items():
            env_str += f"{key}={value}\n"
        FileUtil.write_file(file_path, env_str)

    @staticmethod
    def exists(file_path):
        """
        Check if file exists
        """
        return os.path.exists(file_path)