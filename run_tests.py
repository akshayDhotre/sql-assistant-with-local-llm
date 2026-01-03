#!/usr/bin/env python3
"""
Test runner script for SQL Assistant application

Provides convenient commands to run tests with various options.
"""

import sys
import unittest
import argparse
from pathlib import Path


def run_all_tests(verbosity=2):
    """Run all tests in the tests directory."""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def run_test_file(file_name, verbosity=2):
    """Run tests from a specific file."""
    try:
        module_name = f'tests.{Path(file_name).stem}'
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_name)
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
    except Exception as e:
        print(f"Error loading test file: {e}")
        return 1


def run_test_class(class_path, verbosity=2):
    """Run tests from a specific class."""
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(class_path)
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
    except Exception as e:
        print(f"Error loading test class: {e}")
        return 1


def list_tests():
    """List all available tests."""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    print("\n📋 Available Tests:\n")
    
    def print_suite(suite, indent=0):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                print_suite(test, indent)
            else:
                print(f"{'  ' * indent}• {test}")
    
    print_suite(suite)


def main():
    parser = argparse.ArgumentParser(
        description='SQL Assistant Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -f test_sql_generation.py  # Run specific file
  python run_tests.py -c tests.test_sql_generation.TestSQLValidator
  python run_tests.py -l                 # List all tests
  python run_tests.py -q                 # Quiet mode
        """
    )
    
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Run all tests (default)'
    )
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Run tests from specific file (e.g., test_sql_generation.py)'
    )
    parser.add_argument(
        '-c', '--class',
        type=str,
        dest='test_class',
        help='Run specific test class (e.g., tests.test_sql_generation.TestSQLValidator)'
    )
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List all available tests'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 2
    
    # Handle list command
    if args.list:
        list_tests()
        return 0
    
    # Run appropriate tests
    if args.test_class:
        return run_test_class(args.test_class, verbosity)
    elif args.file:
        return run_test_file(args.file, verbosity)
    else:
        # Default: run all tests
        return run_all_tests(verbosity)


if __name__ == '__main__':
    sys.exit(main())
