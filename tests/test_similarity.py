from deepcsim import compare_source
import sys
import os

# Add src to the path so deepcsim can be imported
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


def test_simple_comparison():
    source1 = """
def add(a,b):
    print("Adding numbers")
    return a + b
"""
    source2 = """
def add_numbers(x,y):
    return x + y
"""

    report = compare_source(source1, source2)
    assert report['count'] > 0
    assert report['results'][0]['similarity'] > 0
    print(
        f"Test passed with similarity: {report['results'][0]['similarity']}%")


if __name__ == "__main__":
    test_simple_comparison()
