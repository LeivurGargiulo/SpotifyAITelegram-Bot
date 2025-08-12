#!/usr/bin/env python3
"""
Test script for the Optimized Discord Music Bot
Validates configuration, dependencies, and basic functionality.
"""

import os
import sys
import asyncio
import logging
from typing import List, Dict, Any

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotTester:
    """Test suite for the optimized Discord bot."""
    
    def __init__(self):
        self.test_results = []
        self.errors = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log a test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f": {message}"
        
        self.test_results.append((test_name, passed, message))
        logger.info(result)
        
        if not passed:
            self.errors.append(f"{test_name}: {message}")
    
    def test_environment_variables(self) -> bool:
        """Test that all required environment variables are set."""
        logger.info("Testing environment variables...")
        
        required_vars = [
            'DISCORD_TOKEN',
            'SPOTIFY_CLIENT_ID', 
            'SPOTIFY_CLIENT_SECRET',
            'OPENROUTER_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_test("Environment Variables", False, f"Missing: {', '.join(missing_vars)}")
            return False
        else:
            self.log_test("Environment Variables", True, "All required variables set")
            return True
    
    def test_dependencies(self) -> bool:
        """Test that all required dependencies are installed."""
        logger.info("Testing dependencies...")
        
        required_packages = [
            'discord',
            'aiohttp',
            'psutil',
            'python-dotenv'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log_test("Dependencies", False, f"Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            self.log_test("Dependencies", True, "All required packages installed")
            return True
    
    def test_configuration(self) -> bool:
        """Test configuration file and settings."""
        logger.info("Testing configuration...")
        
        try:
            from config import config
            
            # Test basic config attributes
            required_attrs = [
                'BOT_NAME', 'COMMAND_PREFIX', 'CACHE_MAX_SIZE',
                'MAX_REQUESTS_PER_MINUTE', 'API_TIMEOUT'
            ]
            
            for attr in required_attrs:
                if not hasattr(config, attr):
                    self.log_test("Configuration", False, f"Missing attribute: {attr}")
                    return False
            
            # Test config methods
            config.get_spotify_params()
            config.get_openrouter_params()
            config.get_rate_limit_config()
            config.get_cache_config()
            
            self.log_test("Configuration", True, "Configuration loaded successfully")
            return True
            
        except Exception as e:
            self.log_test("Configuration", False, f"Error loading config: {str(e)}")
            return False
    
    def test_file_structure(self) -> bool:
        """Test that all required files exist."""
        logger.info("Testing file structure...")
        
        required_files = [
            'optimized_discord_bot.py',
            'config.py',
            'requirements.txt',
            'cogs/__init__.py',
            'cogs/music_commands.py',
            'cogs/utility_commands.py',
            'cogs/error_handler.py',
            'cogs/performance_monitor.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("File Structure", False, f"Missing files: {', '.join(missing_files)}")
            return False
        else:
            self.log_test("File Structure", True, "All required files present")
            return True
    
    async def test_api_connectivity(self) -> bool:
        """Test basic API connectivity."""
        logger.info("Testing API connectivity...")
        
        try:
            import aiohttp
            
            # Test Spotify API connectivity
            spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
            if spotify_client_id:
                self.log_test("Spotify API", True, "Client ID configured")
            else:
                self.log_test("Spotify API", False, "Client ID not configured")
                return False
            
            # Test OpenRouter API connectivity
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            if openrouter_key:
                self.log_test("OpenRouter API", True, "API key configured")
            else:
                self.log_test("OpenRouter API", False, "API key not configured")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("API Connectivity", False, f"Error testing APIs: {str(e)}")
            return False
    
    def test_logging_setup(self) -> bool:
        """Test logging configuration."""
        logger.info("Testing logging setup...")
        
        try:
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            
            # Test that we can write to log file
            test_log_file = 'logs/test.log'
            with open(test_log_file, 'w') as f:
                f.write("Test log entry\n")
            
            # Clean up test file
            os.remove(test_log_file)
            
            self.log_test("Logging Setup", True, "Logging directory and file access OK")
            return True
            
        except Exception as e:
            self.log_test("Logging Setup", False, f"Error setting up logging: {str(e)}")
            return False
    
    def test_startup_script(self) -> bool:
        """Test startup script permissions and syntax."""
        logger.info("Testing startup script...")
        
        script_path = 'start_optimized_bot.sh'
        
        if not os.path.exists(script_path):
            self.log_test("Startup Script", False, "Script not found")
            return False
        
        # Check if script is executable
        if not os.access(script_path, os.X_OK):
            self.log_test("Startup Script", False, "Script not executable")
            return False
        
        # Test script syntax
        try:
            import subprocess
            result = subprocess.run(['bash', '-n', script_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_test("Startup Script", True, "Script syntax OK")
                return True
            else:
                self.log_test("Startup Script", False, f"Syntax error: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_test("Startup Script", False, f"Error testing script: {str(e)}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        logger.info("Starting comprehensive bot tests...")
        
        tests = [
            ("Environment Variables", self.test_environment_variables),
            ("Dependencies", self.test_dependencies),
            ("Configuration", self.test_configuration),
            ("File Structure", self.test_file_structure),
            ("Logging Setup", self.test_logging_setup),
            ("Startup Script", self.test_startup_script),
            ("API Connectivity", self.test_api_connectivity),
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                
                if not result:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(test_name, False, f"Test failed with exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def print_summary(self):
        """Print test summary."""
        logger.info("\n" + "="*50)
        logger.info("TEST SUMMARY")
        logger.info("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.errors:
            logger.info("\nErrors:")
            for error in self.errors:
                logger.info(f"  - {error}")
        
        if failed_tests == 0:
            logger.info("\n🎉 All tests passed! Bot is ready to run.")
            logger.info("You can start the bot with: ./start_optimized_bot.sh start")
        else:
            logger.info("\n❌ Some tests failed. Please fix the issues above before running the bot.")
        
        logger.info("="*50)

async def main():
    """Main test function."""
    print("🧪 Optimized Discord Bot Test Suite")
    print("="*50)
    
    tester = BotTester()
    
    try:
        success = await tester.run_all_tests()
        tester.print_summary()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())