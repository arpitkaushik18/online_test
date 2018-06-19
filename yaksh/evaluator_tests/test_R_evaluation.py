from __future__ import absolute_import
import unittest
import os
import shutil
import tempfile
from textwrap import dedent
from psutil import Process

from yaksh.grader import Grader
from yaksh.R_stdio_evaluator import RStdIOEvaluator
from yaksh.evaluator_tests.test_python_evaluation import EvaluatorBaseTest
from yaksh.settings import SERVER_TIMEOUT


class RStdIOEvaluationTestCases(EvaluatorBaseTest):
    def setUp(self):
        self.test_case_data = [{'expected_output': '11',
                                'expected_input': '5\n6',
                                'weight': 0.0,
                                'test_case_type': 'stdiobasedtestcase',
                                }]
        self.in_dir = tempfile.mkdtemp()
        self.timeout_msg = ("Code took more than {0} seconds to run. "
                            "You probably have an infinite loop in"
                            " your code.").format(SERVER_TIMEOUT)
        self.file_paths = None

    def tearDown(self):
        shutil.rmtree(self.in_dir)

    def test_correct_answer(self):
        # Given
        user_answer = dedent("""
        a<-readline()
        b<-readline()
        print(as.interger(a)+as.integer(b))
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'ruby'
                    },
                    'test_case_data': self.test_case_data,
                 }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertTrue(result.get('success'))

    def test_incorrect_answer(self):
        # Given
        user_answer = dedent("""
        a<-readline()
        b<-readline()
        print(as.interger(a)-as.integer(b))
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'R'
                    },
                    'test_case_data': self.test_case_data,
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        lines_of_error = len(result.get('error')[0].get('error_line_numbers'))
        result_error = result.get('error')[0].get('error_msg')
        self.assertFalse(result.get('success'))
        self.assert_correct_output("Incorrect", result_error)
        self.assertTrue(lines_of_error > 0)

    def test_infinite_loop(self):
        # Given
        user_answer = dedent("""
        i<-1
        while(i>0){
        print(i)
        i=i+1
        }
        """)
        timeout_msg = ("Code took more than {0} seconds to run. "
                       "You probably have an infinite loop in"
                       " your code.").format(SERVER_TIMEOUT)

        kwargs = {'metadata': {
                  'user_answer': user_answer,
                  'file_paths': self.file_paths,
                  'partial_grading': False,
                  'language': 'ruby'},
                  'test_case_data': self.test_case_data
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assert_correct_output(timeout_msg,
                                   result.get("error")[0]['message']
                                   )
        self.assertFalse(result.get('success'))
        parent_proc = Process(os.getpid()).children()
        if parent_proc:
            children_procs = Process(parent_proc[0].pid)
            self.assertFalse(any(children_procs.children(recursive=True)))

    def test_error(self):
        user_answer = dedent("""
         print("Hello"
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'R'
                    },
                    'test_case_data': self.test_case_data,
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertFalse(result.get("success"))
        self.assert_correct_output("Compilation Error", result.get("error"))

    def test_only_stdout(self):
        # Given
        self.test_case_data = [{'expected_output': '11',
                                'weight': 0.0,
                                'test_case_type': 'stdiobasedtestcase',
                                }]
        user_answer = dedent("""
        print("11")
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'R'
                    },
                    'test_case_data': self.test_case_data,
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertTrue(result.get('success'))


def test_array_input(self):
        # Given
        self.test_case_data = [{'expected_output': '561',
                                'expected_input': '5\n6\n1',
                                'weight': 0.0,
                                'test_case_type': 'stdiobasedtestcase',
                                }]
        user_answer = dedent("""
        a<-readline()
        b<-strsplit(a,"")[[1]]
        for(i in b)
        print(as.integer(i))
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'ruby'
                    },
                    'test_case_data': self.test_case_data,
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertTrue(result.get('success'))


def test_R_string_input(self):
        # Given
        self.test_case_data = [{'expected_output': 'abc',
                                'expected_input': 'abc',
                                'weight': 0.0,
                                'test_case_type': 'stdiobasedtestcase',
                                }]
        user_answer = dedent("""
        a<-readline()
        b<-strsplit(a,"")[[1]]
        for(c in b)
        {
        print(c)
        }
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'R'
                    },
                    'test_case_data': self.test_case_data,
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertTrue(result.get('success'))
