#!/bin/bash
# GETIVA Test Runner Script

echo "🧪 Running GETIVA Test Suite..."
echo "================================"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Parse command line arguments
TEST_TYPE=${1:-all}

case $TEST_TYPE in
    all)
        echo "Running all tests..."
        pytest -v
        ;;
    coverage)
        echo "Running tests with coverage report..."
        pytest --cov=. --cov-report=html --cov-report=term-missing
        echo "✅ Coverage report generated in htmlcov/index.html"
        ;;
    auth)
        echo "Running authentication tests..."
        pytest tests/test_auth.py -v
        ;;
    applications)
        echo "Running application tests..."
        pytest tests/test_applications.py -v
        ;;
    payments)
        echo "Running payment tests..."
        pytest tests/test_payments.py -v
        ;;
    analytics)
        echo "Running analytics tests..."
        pytest tests/test_analytics.py -v
        ;;
    main)
        echo "Running main app tests..."
        pytest tests/test_main.py -v
        ;;
    quick)
        echo "Running quick tests (without slow tests)..."
        pytest -v -m "not slow"
        ;;
    debug)
        echo "Running tests with debug output..."
        pytest -vvs
        ;;
    *)
        echo "Usage: ./run_tests.sh [all|coverage|auth|applications|payments|analytics|main|quick|debug]"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh              # Run all tests"
        echo "  ./run_tests.sh coverage     # Run tests with coverage report"
        echo "  ./run_tests.sh auth         # Run only auth tests"
        echo "  ./run_tests.sh quick        # Run tests without slow tests"
        echo "  ./run_tests.sh debug        # Run tests with verbose debug output"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests passed!"
else
    echo ""
    echo "❌ Tests failed!"
    exit 1
fi
