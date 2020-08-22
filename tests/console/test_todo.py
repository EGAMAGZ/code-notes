import unittest
from typing import List

from codenotes.console.todo import AddTodo, SearchTodo
from codenotes import parse_args


class TestAddTodo(unittest.TestCase):

    def test_add_one_todo(self):
        args = parse_args(['add', 'todo', 'New todo task #1'])
        add_todo = AddTodo(args)
        self.assertTrue(isinstance(add_todo.todo_task, str))
        self.assertEqual(add_todo.todo_task, 'New todo task #1')

    def test_add_many_todos(self):
        args = parse_args(['add', 'todo', 'New todo task #2;New todo task #3'])
        add_todo = AddTodo(args)
        self.assertTrue(isinstance(add_todo.todo_task, List))
        self.assertListEqual(add_todo.todo_task, ['New todo task #2', 'New todo task #3'])

    def test_add_bad_input_todo(self):
        args = parse_args(['add', 'todo', ';'])
        add_todo = AddTodo(args)
        self.assertTrue(isinstance(add_todo.todo_task, List))
        self.assertListEqual(add_todo.todo_task, [])


class TestSearchTodo(unittest.TestCase):

    def test_search_text_todo(self):
        expected_tasks = [('New todo task #1', 0),('New todo task #2',0),('New todo task #3',0)]
        args = parse_args(['search', 'todo', 'New','todo'])
        query = SearchTodo(args).sql_query()
        self.assertCountEqual(query, expected_tasks)

    def test_search_today_todo(self):
        expected_tasks = [('New todo task #1', 0),('New todo task #2',0),('New todo task #3',0)]
        args = parse_args(['search', 'todo', '--today'])
        query = SearchTodo(args).sql_query()
        self.assertCountEqual(query, expected_tasks)

    def test_search_yesterday_todo(self):
        args = parse_args(['search','todo','--yesterday'])

    def test_search_text_date(self):
        args = parse_args(['search', 'todo', 'New', 'todo', 'task', '--today'])

    def test_search_no_argument(self):
        args = parse_args(['search', 'todo'])

if __name__ == '__main__':
    unittest.main()
