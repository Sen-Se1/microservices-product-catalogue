#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a file exists and is not empty
check_file() {
    local file_path=$1
    local description=$2
    local is_optional=${3:-false}
    
    if [ -f "$file_path" ]; then
        if [ -s "$file_path" ]; then
            print_status "$GREEN" "✓ $description: File exists and is NOT empty"
            return 0
        else
            print_status "$YELLOW" "⚠  $description: File exists but IS EMPTY"
            return 1
        fi
    else
        if [ "$is_optional" = true ]; then
            print_status "$BLUE" "○ $description: Optional file not found"
            return 2
        else
            print_status "$RED" "✗ $description: File NOT FOUND"
            return 3
        fi
    fi
}

# Function to check if a directory exists
check_dir() {
    local dir_path=$1
    local description=$2
    
    if [ -d "$dir_path" ]; then
        print_status "$GREEN" "✓ $description: Directory exists"
        return 0
    else
        print_status "$RED" "✗ $description: Directory NOT FOUND"
        return 1
    fi
}

# Main function
main() {
    echo -e "\n${BLUE}==============================${NC}"
    echo -e "${BLUE}  PROJECT STRUCTURE CHECKER  ${NC}"
    echo -e "${BLUE}==============================${NC}\n"
    
    local total_checks=0
    local passed_checks=0
    local warning_checks=0
    local failed_checks=0
    
    # Check root directory structure
    echo -e "\n${YELLOW}[ROOT DIRECTORY]${NC}"
    check_dir "." "Project root directory"
    ((total_checks++))
    
    # Check main directories
    echo -e "\n${YELLOW}[MAIN DIRECTORIES]${NC}"
    
    local main_dirs=("app" "scripts" "alembic")
    for dir in "${main_dirs[@]}"; do
        check_dir "$dir" "$dir/"
        if [ $? -eq 0 ]; then
            ((passed_checks++))
        else
            ((failed_checks++))
        fi
        ((total_checks++))
    done
    
    # Check app subdirectories
    echo -e "\n${YELLOW}[APP SUBDIRECTORIES]${NC}"
    
    local app_subdirs=("app/core" "app/db" "app/models" "app/schemas" "app/api" "app/api/v1" "app/services")
    for dir in "${app_subdirs[@]}"; do
        check_dir "$dir" "$dir/"
        if [ $? -eq 0 ]; then
            ((passed_checks++))
        else
            ((failed_checks++))
        fi
        ((total_checks++))
    done
    
    # Check __init__.py files
    echo -e "\n${YELLOW}[__INIT__.PY FILES]${NC}"
    
    local init_files=(
        "app/__init__.py"
        "app/core/__init__.py"
        "app/db/__init__.py"
        "app/models/__init__.py"
        "app/schemas/__init__.py"
        "app/api/__init__.py"
        "app/api/v1/__init__.py"
        "app/services/__init__.py"
    )
    
    for file in "${init_files[@]}"; do
        check_file "$file" "$file"
        case $? in
            0) ((passed_checks++)) ;;
            1) ((warning_checks++)) ;;
            3) ((failed_checks++)) ;;
        esac
        ((total_checks++))
    done
    
    # Check main Python files
    echo -e "\n${YELLOW}[MAIN PYTHON FILES]${NC}"
    
    local main_py_files=(
        "app/main.py"
        "app/core/config.py"
        "app/core/security.py"
        "app/db/session.py"
        "app/db/redis_client.py"
        "app/models/postgres_models.py"
        "app/models/redis_models.py"
        "app/schemas/tracking.py"
        "app/schemas/reports.py"
        "app/api/v1/tracking.py"
        "app/api/v1/reports.py"
        "app/services/analytics_service.py"
        "app/services/redis_service.py"
    )
    
    for file in "${main_py_files[@]}"; do
        check_file "$file" "$file"
        case $? in
            0) ((passed_checks++)) ;;
            1) ((warning_checks++)) ;;
            3) ((failed_checks++)) ;;
        esac
        ((total_checks++))
    done
    
    # Check script files
    echo -e "\n${YELLOW}[SCRIPT FILES]${NC}"
    
    local script_files=(
        "scripts/init_db.py"
        "scripts/test_redis.py"
    )
    
    for file in "${script_files[@]}"; do
        check_file "$file" "$file"
        case $? in
            0) ((passed_checks++)) ;;
            1) ((warning_checks++)) ;;
            3) ((failed_checks++)) ;;
        esac
        ((total_checks++))
    done
    
    # Check configuration files
    echo -e "\n${YELLOW}[CONFIGURATION FILES]${NC}"
    
    local config_files=(
        "requirements.txt"
        ".env"
        "docker-compose.yml"
        "Dockerfile"
    )
    
    for file in "${config_files[@]}"; do
        check_file "$file" "$file"
        case $? in
            0) ((passed_checks++)) ;;
            1) ((warning_checks++)) ;;
            3) ((failed_checks++)) ;;
        esac
        ((total_checks++))
    done
    
    # Optional files (not required but nice to have)
    echo -e "\n${YELLOW}[OPTIONAL FILES]${NC}"
    
    local optional_files=(
        "README.md"
        ".gitignore"
        "alembic.ini"
        "alembic/env.py"
        "alembic/script.py.mako"
        ".dockerignore"
    )
    
    for file in "${optional_files[@]}"; do
        check_file "$file" "$file" true
        ((total_checks++))
    done
    
    # Summary
    echo -e "\n${BLUE}==============================${NC}"
    echo -e "${BLUE}           SUMMARY            ${NC}"
    echo -e "${BLUE}==============================${NC}"
    
    echo -e "\nTotal checks: $total_checks"
    echo -e "${GREEN}Passed: $passed_checks${NC}"
    echo -e "${YELLOW}Warnings: $warning_checks${NC}"
    echo -e "${RED}Failed: $failed_checks${NC}"
    
    # Calculate percentage
    if [ $total_checks -gt 0 ]; then
        local success_rate=$(( (passed_checks * 100) / total_checks ))
        echo -e "\nSuccess rate: $success_rate%"
    fi
    
    # Final verdict
    echo -e "\n${BLUE}==============================${NC}"
    if [ $failed_checks -eq 0 ] && [ $warning_checks -eq 0 ]; then
        echo -e "${GREEN}✅ PERFECT STRUCTURE!${NC}"
        echo -e "All required files exist and are non-empty."
    elif [ $failed_checks -eq 0 ]; then
        echo -e "${YELLOW}⚠  GOOD STRUCTURE WITH WARNINGS${NC}"
        echo -e "All required files exist, but some are empty."
        echo -e "Check the warnings above for empty files."
    else
        echo -e "${RED}❌ STRUCTURE ISSUES FOUND${NC}"
        echo -e "Some required files are missing."
        echo -e "Check the failures above for missing files."
    fi
    echo -e "${BLUE}==============================${NC}"
    
    return $failed_checks
}

# Run the main function
main
exit_code=$?
exit $exit_code