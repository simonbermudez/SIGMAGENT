#!/bin/bash
# Multi-Agent SBDR System - Run Script

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

# Default values
ENVIRONMENT="development"
DETACHED=false
REBUILD=false
SERVICES=""
LOGS=false
STOP=false
STATUS=false

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show usage
show_usage() {
    echo "Multi-Agent SBDR System - Run Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start                     Start the system (default)"
    echo "  stop                      Stop the system"
    echo "  restart                   Restart the system"
    echo "  status                    Show system status"
    echo "  logs                      Show logs"
    echo "  shell                     Open shell in main container"
    echo "  test                      Run tests"
    echo ""
    echo "Options:"
    echo "  -e, --env ENVIRONMENT     Environment to run (development, staging, production) [default: development]"
    echo "  -d, --detach              Run in detached mode (background)"
    echo "  -r, --rebuild             Rebuild images before starting"
    echo "  -s, --services SERVICES   Run specific services only (comma-separated)"
    echo "  -f, --follow-logs         Follow logs output"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Start system in foreground"
    echo "  $0 -d                     # Start system in background"
    echo "  $0 --rebuild -d           # Rebuild and start in background"
    echo "  $0 logs                   # Show logs"
    echo "  $0 --services sbdr-system # Start only main service"
}

# Parse command line arguments
parse_args() {
    COMMAND="start"  # Default command
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status|logs|shell|test)
                COMMAND="$1"
                shift
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -d|--detach)
                DETACHED=true
                shift
                ;;
            -r|--rebuild)
                REBUILD=true
                shift
                ;;
            -s|--services)
                SERVICES="$2"
                shift 2
                ;;
            -f|--follow-logs)
                LOGS=true
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
}

# Function to load environment configuration
load_env_config() {
    cd "$PROJECT_ROOT"
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            print_message $YELLOW "⚠️  .env file not found. Creating from .env.example..."
            cp .env.example .env
            print_message $YELLOW "📝 Please update .env file with your actual configuration values"
        else
            print_message $RED "❌ Neither .env nor .env.example found. Please create configuration file."
            exit 1
        fi
    fi
    
    # Load environment variables
    export $(cat .env | grep -v '^#' | xargs) 2>/dev/null || true
}

# Function to build images if needed
build_if_needed() {
    if [[ "$REBUILD" == "true" ]]; then
        print_message $BLUE "🏗️  Rebuilding Docker images..."
        docker-compose build
        print_message $GREEN "✅ Images rebuilt"
    fi
}

# Function to start the system
start_system() {
    print_message $GREEN "🚀 Starting Multi-Agent SBDR System..."
    print_message $BLUE "   Environment: $ENVIRONMENT"
    
    cd "$PROJECT_ROOT"
    
    # Build images if needed
    build_if_needed
    
    # Prepare docker-compose command
    local compose_cmd="docker-compose"
    
    # Add environment-specific compose file if it exists
    if [[ -f "docker-compose.$ENVIRONMENT.yml" ]]; then
        compose_cmd+=" -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml"
    fi
    
    # Prepare up command
    local up_args="up"
    if [[ "$DETACHED" == "true" ]]; then
        up_args+=" -d"
    fi
    
    # Add specific services if specified
    if [[ -n "$SERVICES" ]]; then
        up_args+=" $(echo $SERVICES | tr ',' ' ')"
    fi
    
    # Start the system
    eval "$compose_cmd $up_args"
    
    if [[ "$DETACHED" == "true" ]]; then
        print_message $GREEN "✅ System started in background"
        show_access_info
        
        if [[ "$LOGS" == "true" ]]; then
            print_message $BLUE "📋 Following logs..."
            eval "$compose_cmd logs -f"
        fi
    else
        print_message $GREEN "✅ System started in foreground"
    fi
}

# Function to stop the system
stop_system() {
    print_message $BLUE "🛑 Stopping Multi-Agent SBDR System..."
    
    cd "$PROJECT_ROOT"
    docker-compose down
    
    print_message $GREEN "✅ System stopped"
}

# Function to restart the system
restart_system() {
    print_message $BLUE "🔄 Restarting Multi-Agent SBDR System..."
    
    stop_system
    sleep 2
    start_system
}

# Function to show system status
show_status() {
    print_message $BLUE "📊 System Status:"
    
    cd "$PROJECT_ROOT"
    docker-compose ps
    
    echo ""
    print_message $BLUE "📈 Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        $(docker-compose ps -q) 2>/dev/null || echo "No running containers"
}

# Function to show logs
show_logs() {
    print_message $BLUE "📋 System Logs:"
    
    cd "$PROJECT_ROOT"
    
    local logs_cmd="docker-compose logs"
    
    if [[ "$LOGS" == "true" ]]; then
        logs_cmd+=" -f"
    fi
    
    if [[ -n "$SERVICES" ]]; then
        logs_cmd+=" $(echo $SERVICES | tr ',' ' ')"
    fi
    
    eval "$logs_cmd"
}

# Function to open shell
open_shell() {
    print_message $BLUE "🐚 Opening shell in SBDR container..."
    
    cd "$PROJECT_ROOT"
    
    # Check if container is running
    if ! docker-compose ps sbdr-system | grep -q "Up"; then
        print_message $RED "❌ SBDR container is not running. Start the system first."
        exit 1
    fi
    
    docker-compose exec sbdr-system /bin/bash
}

# Function to run tests
run_tests() {
    print_message $BLUE "🧪 Running system tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run tests in container
    docker-compose run --rm sbdr-system python multiagent_test_framework.py
    
    if [[ $? -eq 0 ]]; then
        print_message $GREEN "✅ All tests passed"
    else
        print_message $RED "❌ Tests failed"
        exit 1
    fi
}

# Function to show access information
show_access_info() {
    echo ""
    print_message $GREEN "🌐 System Access Information:"
    print_message $BLUE "   Main System:     http://localhost:8000"
    print_message $BLUE "   Web Interface:   http://localhost:8080"
    print_message $BLUE "   Grafana:         http://localhost:3000 (admin/admin123)"
    print_message $BLUE "   Prometheus:      http://localhost:9090"
    print_message $BLUE "   PostgreSQL:      localhost:5432 (sbdr_user/sbdr_pass)"
    print_message $BLUE "   Redis:           localhost:6379"
    echo ""
    print_message $YELLOW "💡 Tips:"
    print_message $YELLOW "   - View logs: $0 logs"
    print_message $YELLOW "   - Check status: $0 status" 
    print_message $YELLOW "   - Stop system: $0 stop"
    print_message $YELLOW "   - Open shell: $0 shell"
}

# Function to handle cleanup on exit
cleanup_on_exit() {
    if [[ "$DETACHED" == "false" ]]; then
        echo ""
        print_message $YELLOW "🛑 Shutting down system..."
        stop_system
    fi
}

# Main function
main() {
    case $COMMAND in
        start)
            check_prerequisites
            load_env_config
            start_system
            ;;
        stop)
            check_prerequisites
            stop_system
            ;;
        restart)
            check_prerequisites
            load_env_config
            restart_system
            ;;
        status)
            check_prerequisites
            show_status
            ;;
        logs)
            check_prerequisites
            show_logs
            ;;
        shell)
            check_prerequisites
            open_shell
            ;;
        test)
            check_prerequisites
            load_env_config
            run_tests
            ;;
        *)
            echo "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
}

# Set up signal handlers
trap cleanup_on_exit SIGINT SIGTERM

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi