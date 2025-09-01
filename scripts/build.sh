#!/bin/bash
# Multi-Agent SBDR System - Build Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Default values
BUILD_ENV="development"
PUSH_IMAGES=false
NO_CACHE=false
VERBOSE=false

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show usage
show_usage() {
    echo "Multi-Agent SBDR System - Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --env ENVIRONMENT     Build environment (development, staging, production) [default: development]"
    echo "  -p, --push                Push images to registry after build"
    echo "  -n, --no-cache            Build without using cache"
    echo "  -v, --verbose             Enable verbose output"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Build for development"
    echo "  $0 --env production       # Build for production"
    echo "  $0 --push --no-cache      # Build without cache and push to registry"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                BUILD_ENV="$2"
                shift 2
                ;;
            -p|--push)
                PUSH_IMAGES=true
                shift
                ;;
            -n|--no-cache)
                NO_CACHE=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Function to check prerequisites
check_prerequisites() {
    print_message $BLUE "🔍 Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_message $RED "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_message $RED "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_message $RED "❌ docker-compose is not installed. Please install docker-compose first."
        exit 1
    fi
    
    print_message $GREEN "✅ Prerequisites check passed"
}

# Function to validate environment files
validate_env_files() {
    print_message $BLUE "🔍 Validating environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Check if .env.example exists
    if [[ ! -f ".env.example" ]]; then
        print_message $RED "❌ .env.example file not found"
        exit 1
    fi
    
    # Check if .env exists
    if [[ ! -f ".env" ]]; then
        print_message $YELLOW "⚠️  .env file not found. Creating from .env.example..."
        cp .env.example .env
        print_message $YELLOW "📝 Please update .env file with your actual configuration values"
    fi
    
    print_message $GREEN "✅ Environment files validated"
}

# Function to build Docker images
build_images() {
    print_message $BLUE "🏗️  Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build arguments
    local build_args=(
        --build-arg BUILD_DATE="$BUILD_DATE"
        --build-arg GIT_COMMIT="$GIT_COMMIT"
        --build-arg BUILD_ENV="$BUILD_ENV"
    )
    
    # Add no-cache flag if specified
    if [[ "$NO_CACHE" == "true" ]]; then
        build_args+=(--no-cache)
    fi
    
    # Add verbose flag if specified
    if [[ "$VERBOSE" == "true" ]]; then
        build_args+=(--progress=plain)
    fi
    
    # Build main application image
    print_message $BLUE "  📦 Building main SBDR system image..."
    docker build "${build_args[@]}" -t "sbdr-multiagent:latest" -f Dockerfile .
    docker tag "sbdr-multiagent:latest" "sbdr-multiagent:$GIT_COMMIT"
    
    # Build web interface image
    print_message $BLUE "  📦 Building web interface image..."
    docker build "${build_args[@]}" -t "sbdr-web:latest" -f Dockerfile.web .
    docker tag "sbdr-web:latest" "sbdr-web:$GIT_COMMIT"
    
    print_message $GREEN "✅ Docker images built successfully"
}

# Function to run tests in container
run_tests() {
    print_message $BLUE "🧪 Running tests in container..."
    
    cd "$PROJECT_ROOT"
    
    # Run tests using docker-compose
    docker-compose -f docker-compose.yml run --rm sbdr-system python multiagent_test_framework.py
    
    if [[ $? -eq 0 ]]; then
        print_message $GREEN "✅ All tests passed"
    else
        print_message $RED "❌ Tests failed"
        exit 1
    fi
}

# Function to push images to registry
push_images() {
    if [[ "$PUSH_IMAGES" == "false" ]]; then
        return
    fi
    
    print_message $BLUE "📤 Pushing images to registry..."
    
    # Check if registry is configured
    REGISTRY_URL=${DOCKER_REGISTRY:-""}
    if [[ -z "$REGISTRY_URL" ]]; then
        print_message $YELLOW "⚠️  DOCKER_REGISTRY not set. Skipping push."
        return
    fi
    
    # Tag and push images
    docker tag "sbdr-multiagent:latest" "$REGISTRY_URL/sbdr-multiagent:latest"
    docker tag "sbdr-multiagent:$GIT_COMMIT" "$REGISTRY_URL/sbdr-multiagent:$GIT_COMMIT"
    docker tag "sbdr-web:latest" "$REGISTRY_URL/sbdr-web:latest"
    docker tag "sbdr-web:$GIT_COMMIT" "$REGISTRY_URL/sbdr-web:$GIT_COMMIT"
    
    docker push "$REGISTRY_URL/sbdr-multiagent:latest"
    docker push "$REGISTRY_URL/sbdr-multiagent:$GIT_COMMIT"
    docker push "$REGISTRY_URL/sbdr-web:latest"
    docker push "$REGISTRY_URL/sbdr-web:$GIT_COMMIT"
    
    print_message $GREEN "✅ Images pushed to registry"
}

# Function to clean up old images
cleanup_images() {
    print_message $BLUE "🧹 Cleaning up old images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old tagged versions (keep last 5)
    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" \
        | grep "sbdr-multiagent\|sbdr-web" \
        | sort -k2 -r \
        | tail -n +6 \
        | awk '{print $1}' \
        | xargs -r docker rmi 2>/dev/null || true
    
    print_message $GREEN "✅ Cleanup completed"
}

# Function to generate build report
generate_report() {
    print_message $BLUE "📊 Generating build report..."
    
    cat > "$PROJECT_ROOT/build_report.txt" << EOF
Multi-Agent SBDR System - Build Report
=====================================

Build Information:
- Build Date: $BUILD_DATE
- Git Commit: $GIT_COMMIT
- Environment: $BUILD_ENV
- Build Host: $(hostname)

Docker Images Built:
$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep -E "sbdr-multiagent|sbdr-web")

Build Configuration:
- No Cache: $NO_CACHE
- Push Images: $PUSH_IMAGES
- Verbose: $VERBOSE

System Information:
- Docker Version: $(docker --version)
- Docker Compose Version: $(docker-compose --version)
- Available Space: $(df -h . | tail -1 | awk '{print $4}')
- System Load: $(uptime | awk -F'load average:' '{print $2}')
EOF
    
    print_message $GREEN "✅ Build report generated: build_report.txt"
}

# Main build function
main() {
    print_message $GREEN "🚀 Starting Multi-Agent SBDR System Build"
    print_message $BLUE "   Environment: $BUILD_ENV"
    print_message $BLUE "   Git Commit: $GIT_COMMIT"
    print_message $BLUE "   Build Date: $BUILD_DATE"
    echo ""
    
    # Execute build steps
    check_prerequisites
    validate_env_files
    build_images
    run_tests
    push_images
    cleanup_images
    generate_report
    
    echo ""
    print_message $GREEN "🎉 Build completed successfully!"
    print_message $BLUE "📋 Next steps:"
    print_message $BLUE "   1. Review the build report: build_report.txt"
    print_message $BLUE "   2. Update your .env file with actual configuration"
    print_message $BLUE "   3. Run: docker-compose up -d"
    print_message $BLUE "   4. Access the system at: http://localhost:8000"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi