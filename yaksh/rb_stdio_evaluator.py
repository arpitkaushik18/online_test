#!/usr/bin/env python
from __future__ import unicode_literals
import subprocess
import os
from os.path import isfile
import sys
from contextlib import contextmanager

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
#Local imports
from .stdio_evaluator import StdIOEvaluator
from .file_utils import copy_files, delete_files
from .error_messages import compare_outputs
@contextmanager
def redirect_stdout():
    new_target = StringIO()
    old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target 

class RbStdIOEvaluator(StdIOEvaluator):
    """Evaluates C StdIO based code"""
    def __init__(self, metadata, test_case_data):
        self.files = []

        # Set metadata values
        self.user_answer = metadata.get('user_answer')
        self.file_paths = metadata.get('file_paths')
        self.partial_grading = metadata.get('partial_grading')

        # Set test case data values
        self.expected_input = test_case_data.get('expected_input')
        self.expected_output = test_case_data.get('expected_output')
        self.weight = test_case_data.get('weight')

    def teardown(self):
        os.remove(self.submit_code_path)
        if self.files:
            delete_files(self.files)

    # def set_file_paths(self):
    #   user_output_path = os.getcwd() + '/output_file'
    #   ref_output_path = os.getcwd() + '/executable'
    #   return user_output_path, ref_output_path

    def compile_code(self):
        self.submit_code_path=self.create_submit_code_file('submit.rb')
        self.write_to_submit_code_file(self.submit_code_path, self.user_answer)
        if self.expected_input:
            self.expected_input = self.expected_input.replace('\r', '')
            input_buffer = StringIO()
            input_buffer.write(self.expected_input)
            input_buffer.seek(0)
            sys.stdin = input_buffer
        with redirect_stdout() as output_buffer:
         self.proc=subprocess.Popen('ruby {0}'.format(self.submit_code_path),
                                        shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        preexec_fn=os.setpgrp
                                        )
        # self.compiled_user_answer = self._run_command('ruby {0}'.format(self.submit_code_path),
        #                                               shell=True,
        #                                               stdin=subprocess.PIPE,
        #                                               stdout=subprocess.PIPE,
        #                                               stderr=subprocess.PIPE
        #                                               )
        #self.compiled_test_code = self._run_command('ruby '
                                                    #shell=True,
                                                    #stdin=subprocess.PIPE,
                                                    #stdout=subprocess.PIPE,
                                                    #stderr=subprocess.PIPE
                                                    #)
        #return self.compiled_user_answer
    def check_code(self):
      success=False
      err = ''
      mark_fraction=0.0
      # proc, stdnt_out, stdnt_stderr = self.compiled_user_answer
      #print(">>>>>>", stdnt_out, proc, stdnt_stderr)
      success, err = self.evaluate_stdio(self.user_answer,self.proc,
                                                   self.expected_input,
                                                   self.expected_output
                                                   )
      # success, err = compare_outputs(self.expected_output,
      #                                  stdnt_out,
      #                                  self.expected_input
      #                                  )
      mark_fraction = 1.0 if self.partial_grading and success else 0.0
      return success, err, mark_fraction
