import unittest

from auto_full_stack.utils.mysql_util import MySQLUtil

class MySQLUtilTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def testCreateDatabase(self):
        MySQLUtil.create_database(database="full_stack_db_template")

    def testExecScript1(self):
        MySQLUtil.execute_sql_by_file(
            script_path="sql/quartz.sql",
            database="full_stack_db_template"
        )

    def testExecScript2(self):
        MySQLUtil.execute_sql_by_file(
            script_path="sql/init_20250823.sql",
            database="full_stack_db_template"
        )

    def testDropAllTables(self):
        MySQLUtil.drop_all_table(database="full_stack_db_template")


if __name__ == '__main__':
    unittest.main()
