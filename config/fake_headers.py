# Isolated headers required to bypass primitive definitions in pycparser
FAKE_HEADERS = """
typedef int FILE;
typedef int size_t;
typedef int bool;
"""