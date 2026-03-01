When creating unit tests for the CICADAS framework, try to follow these guidelines:

1. Bias towards testing with real file system operations in a temp directory versus mocks to ensure proper file and git operations.
2. Ensure 75% coverage of code classes, with a focus on non-trivial functions and operations.
3. Always take full responsibility for the overall health of the test suite, not just the tests for the changes in this work unit.