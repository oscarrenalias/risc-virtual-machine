#!/usr/bin/env bash
# Test runner script for RISC Virtual Machine

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== RISC Virtual Machine Test Suite ===${NC}\n"

# Function to print section headers
print_header() {
    echo -e "\n${YELLOW}>>> $1${NC}"
}

# Parse command line arguments
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""
FAST_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fast)
            FAST_ONLY=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage    Run with coverage report"
            echo "  -v, --verbose     Run with verbose output"
            echo "  -f, --fast        Run only fast tests (skip slow tests)"
            echo "  -t, --test FILE   Run specific test file (e.g., test_cpu.py)"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                    # Run all tests"
            echo "  ./run_tests.sh -c                 # Run with coverage"
            echo "  ./run_tests.sh -t test_cpu.py    # Run specific test file"
            echo "  ./run_tests.sh -f -v              # Run fast tests with verbose output"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Build test command
if [ -n "$SPECIFIC_TEST" ]; then
    # If specific test provided, use it as-is (may be in tests/unit/, tests/integration/, etc.)
    TEST_CMD="uv run pytest ${SPECIFIC_TEST}"
else
    # Otherwise run all tests
    TEST_CMD="uv run pytest tests/"
fi

# Add verbose flag
if [ "$VERBOSE" = true ]; then
    TEST_CMD="${TEST_CMD} -v"
fi

# Add fast-only marker
if [ "$FAST_ONLY" = true ]; then
    TEST_CMD="${TEST_CMD} -m 'not slow'"
    print_header "Running fast tests only"
fi

# Add coverage flags
if [ "$COVERAGE" = true ]; then
    TEST_CMD="${TEST_CMD} --cov=src --cov-report=term-missing --cov-report=html"
    print_header "Running tests with coverage"
else
    print_header "Running tests"
fi

# Run tests
echo -e "${BLUE}Command: ${TEST_CMD}${NC}\n"
eval $TEST_CMD
TEST_RESULT=$?

# Print results
echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo -e "${GREEN}📊 Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

# Print summary
print_header "Test Summary"
echo "Test files: tests/unit/"
echo "Configuration: pyproject.toml"
echo "Fixtures: tests/conftest.py"

exit 0
