from __future__ import absolute_import
import unittest
import os
import shutil
import tempfile
from textwrap import dedent
from psutil import Process

from yaksh.grader import Grader
from yaksh.ruby_assertion_evaluator import rubyCodeEvaluator
from yaksh.ruby_stdio_evaluator import RubyStdIOEvaluator
from yaksh.evaluator_tests.test_python_evaluation import EvaluatorBaseTest
from yaksh.settings import SERVER_TIMEOUT

class RubyAssertionEvalutionTestCases(EvaluatorBaseTest):
    def setUp(self):
        self.f_path = os.path.join(tempfile.gettempdir(),"test.txt")
        with open(self.f_path, 'wb') as f:
            f.write('2'.encode('ascii'))
        tmp_in_dir_path = tempfile.mkdtemp()
        self.tc_data=dedent(
            """
            print("Hello")
            """)
        '''dedent("""
def check(expect,result)
 if(expect==result)
   print("Correct: Expected ",expect," got ",result)
    puts()
 else
    print("Incorrect: Expected ",expect," got ",result)
    puts()
 end
end
r=add(0,0)
print("Input submitted to the function: 0, 0\n")
check(0,r)
r=add(2,3)
print("Input submitted to the function: 2, 3\n")
check(5,r)
            """)'''
        self.test_case_data = [{"test_case": self.tc_data,
                                "test_case_type": "standardtestcase",
                                "weight": 0.0
                                }]
        self.in_dir = tmp_in_dir_path
        self.timeout_msg = ("Code took more than {0} seconds to run. "
            "You probably have an infinite loop in your"
            " code.").format(SERVER_TIMEOUT)
        self.file_paths = None

    def tearDown(self):
        os.remove(self.f_path)
        shutil.rmtree(self.in_dir)


    def test_correct_answer(self):
        # Given
        user_answer = "print('Hello')"
        #"def add(a,b)\nreturn a+b\nend"
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
        print(result.get('error'),"<<<<<<<<<<>>>>>>>>>>>>>")

        # Then
        self.assertTrue(result.get('success'))

    def test_incorrect_answer(self):
        # Given
        user_answer = "print('Hello')"
        #"def add(a,b)\nreturn a-b\nend"
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


class RubyStdIOEvaluationTestCases(EvaluatorBaseTest):
    def setUp(self):
        self.test_case_data = [{'expected_output': '11',
                                'expected_input': '5\n6',
                                'weight': 0.0,
                                'test_case_type': 'stdiobasedtestcase'
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
        val1 = gets
        val2 = gets
        print (val1.to_i + val2.to_i)
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'ruby'
                    },
                    'test_case_data': self.test_case_data
                 }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertTrue(result.get('success'))

    def test_incorrect_answer(self):
        # Given
        user_answer = dedent("""
            val1 = gets
            val2 = gets
            print (val1.to_i * val2.to_i)
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'ruby'
                    },
                    'test_case_data': self.test_case_data
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        lines_of_error = len(result.get('error')[0].get('error_line_numbers'))
        result_error = result.get('error')[0].get('error_msg')
        print(lines_of_error,result_error)
        self.assertFalse(result.get('success'))
        self.assert_correct_output("Incorrect", result_error)
        self.assertTrue(lines_of_error > 0)

    def test_infinite_loop(self):
        # Given
        user_answer = dedent("""
         m=1
         loop do
          puts "232"
          m+=1
          break if m==0
         end
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
         puts "12":
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'ruby'
                    },
                    'test_case_data': self.test_case_data
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertFalse(result.get("success"))
        #self.assert_correct_output("Compilation Error", result.get("error")[0]['error_msg'])

    def test_only_stdout(self):
        # Given
        self.test_case_data = [{'expected_output': '11',
                                'weight': 0.0,
                                'test_case_type': 'stdiobasedtestcase'
                                }]
        user_answer = dedent("""
        print("11")
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'ruby'
                    },
                    'test_case_data': self.test_case_data
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
        a=Array.new(3)
        for i in 0..2
         b=gets
         a[i]=b.to_i
        end
        for i in 0..2
         print(a[i])
        end
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


    def test_rb_string_input(self):
        # Given
        self.test_case_data = [{'expected_output': 'abc',
                                'expected_input': 'abc',
                                'weight': 0.0,
                                'test_case_type': 'stdiobasedtestcase'
                                }]
        user_answer = dedent("""
        a=gets;
        for i in 0..2;
        print(a[i]);
        end
        """)
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'ruby'
                    },
                    'test_case_data': self.test_case_data
                  }

        # When
        grader = Grader(self.in_dir)
        result = grader.evaluate(kwargs)

        # Then
        self.assertTrue(result.get('success'))
