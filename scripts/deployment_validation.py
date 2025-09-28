#!/usr/bin/env python3
"""
Medical Knowledge Platform - Deployment Validation Script
===========================================================

Comprehensive pre-deployment validation to ensure all systems are ready for production.
Validates API keys, database connections, service health, and configuration integrity.
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import aiohttp
import asyncpg
import redis
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.api_key_manager import api_key_manager
from services.monitoring_service import monitoring_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class ValidationResult:
    def __init__(self, name: str, passed: bool, message: str, details: Optional[Dict] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}

class DeploymentValidator:
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.critical_failures = 0
        self.warnings = 0

    def add_result(self, result: ValidationResult):
        self.results.append(result)
        if not result.passed:
            if "critical" in result.name.lower():
                self.critical_failures += 1
            else:
                self.warnings += 1

    async def validate_environment_variables(self) -> ValidationResult:
        """Validate all required environment variables are set"""
        required_vars = {
            "SECRET_KEY": "JWT secret key",
            "DATABASE_URL": "PostgreSQL connection string",
            "REDIS_URL": "Redis connection string",
            "OPENAI_API_KEY": "OpenAI API key",
            "GEMINI_API_KEY": "Google Gemini API key",
            "CLAUDE_API_KEY": "Anthropic Claude API key",
            "PERPLEXITY_API_KEY": "Perplexity API key",
            "PUBMED_EMAIL": "PubMed API email"
        }

        missing_vars = []
        empty_vars = []
        valid_vars = []

        for var, description in required_vars.items():
            value = os.getenv(var)
            if value is None:
                missing_vars.append(f"{var} ({description})")
            elif not value.strip():
                empty_vars.append(f"{var} ({description})")
            else:
                valid_vars.append(var)

        if missing_vars or empty_vars:
            message = ""
            if missing_vars:
                message += f"Missing variables: {', '.join(missing_vars)}. "
            if empty_vars:
                message += f"Empty variables: {', '.join(empty_vars)}."

            return ValidationResult(
                "Critical: Environment Variables",
                False,
                message,
                {"missing": missing_vars, "empty": empty_vars, "valid": valid_vars}
            )

        return ValidationResult(
            "Environment Variables",
            True,
            f"All {len(required_vars)} required environment variables are set",
            {"valid_count": len(valid_vars)}
        )

    async def validate_database_connection(self) -> ValidationResult:
        """Test PostgreSQL database connection and required extensions"""
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                return ValidationResult(
                    "Critical: Database Connection",
                    False,
                    "DATABASE_URL not configured"
                )

            conn = await asyncpg.connect(database_url)

            # Test basic connection
            result = await conn.fetch("SELECT 1")

            # Check for required extensions
            extensions = await conn.fetch("""
                SELECT extname FROM pg_extension
                WHERE extname IN ('vector', 'uuid-ossp', 'pg_trgm')
            """)

            installed_extensions = [ext['extname'] for ext in extensions]
            required_extensions = ['vector', 'uuid-ossp', 'pg_trgm']
            missing_extensions = [ext for ext in required_extensions if ext not in installed_extensions]

            await conn.close()

            if missing_extensions:
                return ValidationResult(
                    "Database Extensions",
                    False,
                    f"Missing required extensions: {', '.join(missing_extensions)}",
                    {"missing": missing_extensions, "installed": installed_extensions}
                )

            return ValidationResult(
                "Database Connection",
                True,
                "PostgreSQL connection successful with all required extensions",
                {"extensions": installed_extensions}
            )

        except Exception as e:
            return ValidationResult(
                "Critical: Database Connection",
                False,
                f"Database connection failed: {str(e)}"
            )

    async def validate_redis_connection(self) -> ValidationResult:
        """Test Redis cache connection"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            r = redis.from_url(redis_url)

            # Test connection
            r.ping()

            # Test basic operations
            r.set("deployment_test", "ok", ex=5)
            result = r.get("deployment_test")
            r.delete("deployment_test")

            if result != b"ok":
                return ValidationResult(
                    "Redis Operations",
                    False,
                    "Redis read/write operations failed"
                )

            return ValidationResult(
                "Redis Connection",
                True,
                "Redis connection and operations successful"
            )

        except Exception as e:
            return ValidationResult(
                "Critical: Redis Connection",
                False,
                f"Redis connection failed: {str(e)}"
            )

    async def validate_ai_provider_keys(self) -> ValidationResult:
        """Validate all AI provider API keys"""
        try:
            await api_key_manager.initialize()

            providers = ["openai", "gemini", "claude", "perplexity"]
            health_results = {}

            for provider in providers:
                try:
                    health = await api_key_manager.check_service_health(provider)
                    health_results[provider] = health
                except Exception as e:
                    health_results[provider] = {"health": "unhealthy", "error": str(e)}

            healthy_providers = [p for p, h in health_results.items() if h.get("health") == "healthy"]
            unhealthy_providers = [p for p, h in health_results.items() if h.get("health") != "healthy"]

            if len(healthy_providers) == 0:
                return ValidationResult(
                    "Critical: AI Provider Keys",
                    False,
                    "No AI providers are accessible",
                    health_results
                )
            elif len(unhealthy_providers) > 0:
                return ValidationResult(
                    "AI Provider Keys",
                    len(healthy_providers) >= 2,  # At least 2 providers working
                    f"Some providers inaccessible: {', '.join(unhealthy_providers)}. Working: {', '.join(healthy_providers)}",
                    health_results
                )
            else:
                return ValidationResult(
                    "AI Provider Keys",
                    True,
                    f"All {len(providers)} AI providers accessible",
                    health_results
                )

        except Exception as e:
            return ValidationResult(
                "Critical: AI Provider Keys",
                False,
                f"AI provider validation failed: {str(e)}"
            )

    async def validate_required_directories(self) -> ValidationResult:
        """Ensure all required directories exist with proper permissions"""
        required_dirs = [
            "logs",
            "uploads",
            "reference_library",
            "data/embeddings",
            "backups"
        ]

        missing_dirs = []
        permission_errors = []
        valid_dirs = []

        for dir_path in required_dirs:
            path = Path(dir_path)
            try:
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)

                # Test write permissions
                test_file = path / "test_write_permission.tmp"
                test_file.touch()
                test_file.unlink()

                valid_dirs.append(str(path))

            except PermissionError:
                permission_errors.append(str(path))
            except Exception as e:
                missing_dirs.append(f"{path}: {str(e)}")

        if missing_dirs or permission_errors:
            message = ""
            if missing_dirs:
                message += f"Directory creation failed: {', '.join(missing_dirs)}. "
            if permission_errors:
                message += f"Permission errors: {', '.join(permission_errors)}."

            return ValidationResult(
                "Required Directories",
                False,
                message,
                {"missing": missing_dirs, "permission_errors": permission_errors}
            )

        return ValidationResult(
            "Required Directories",
            True,
            f"All {len(required_dirs)} directories ready",
            {"directories": valid_dirs}
        )

    async def validate_configuration_files(self) -> ValidationResult:
        """Validate configuration files exist and are properly formatted"""
        config_files = {
            ".env": "Environment configuration",
            "requirements.txt": "Python dependencies",
            "simple_main.py": "Main application file",
            "Dockerfile": "Container configuration",
            "docker/docker-compose.prod.yml": "Production docker compose"
        }

        missing_files = []
        invalid_files = []
        valid_files = []

        for file_path, description in config_files.items():
            path = Path(file_path)
            if not path.exists():
                missing_files.append(f"{file_path} ({description})")
                continue

            try:
                # Basic validation for each file type
                if file_path == ".env":
                    content = path.read_text()
                    if "OPENAI_API_KEY" not in content:
                        invalid_files.append(f"{file_path}: Missing API key configurations")
                        continue

                elif file_path.endswith(".yml"):
                    import yaml
                    with open(path) as f:
                        yaml.safe_load(f)

                elif file_path.endswith(".py"):
                    # Basic syntax check
                    with open(path) as f:
                        compile(f.read(), file_path, 'exec')

                valid_files.append(file_path)

            except Exception as e:
                invalid_files.append(f"{file_path}: {str(e)}")

        if missing_files or invalid_files:
            message = ""
            if missing_files:
                message += f"Missing files: {', '.join(missing_files)}. "
            if invalid_files:
                message += f"Invalid files: {', '.join(invalid_files)}."

            return ValidationResult(
                "Configuration Files",
                False,
                message,
                {"missing": missing_files, "invalid": invalid_files}
            )

        return ValidationResult(
            "Configuration Files",
            True,
            f"All {len(config_files)} configuration files valid",
            {"valid_files": valid_files}
        )

    async def validate_system_resources(self) -> ValidationResult:
        """Check system resources and requirements"""
        try:
            import psutil

            # Check available memory (recommend 4GB minimum)
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)

            # Check available disk space (recommend 20GB minimum)
            disk = psutil.disk_usage('.')
            disk_gb = disk.free / (1024**3)

            # Check CPU cores
            cpu_cores = psutil.cpu_count()

            warnings = []
            if memory_gb < 4:
                warnings.append(f"Low memory: {memory_gb:.1f}GB (recommend 4GB+)")
            if disk_gb < 20:
                warnings.append(f"Low disk space: {disk_gb:.1f}GB (recommend 20GB+)")
            if cpu_cores < 2:
                warnings.append(f"Low CPU cores: {cpu_cores} (recommend 2+)")

            return ValidationResult(
                "System Resources",
                len(warnings) == 0,
                f"Memory: {memory_gb:.1f}GB, Disk: {disk_gb:.1f}GB, CPU: {cpu_cores} cores" +
                (f". Warnings: {'; '.join(warnings)}" if warnings else ""),
                {
                    "memory_gb": round(memory_gb, 1),
                    "disk_gb": round(disk_gb, 1),
                    "cpu_cores": cpu_cores,
                    "warnings": warnings
                }
            )

        except Exception as e:
            return ValidationResult(
                "System Resources",
                False,
                f"Resource check failed: {str(e)}"
            )

    async def run_all_validations(self) -> Dict:
        """Run all validation checks"""
        console.print("\n[bold blue]🔍 Medical Knowledge Platform - Deployment Validation[/bold blue]")
        console.print(f"Validation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        validations = [
            ("Environment Variables", self.validate_environment_variables),
            ("Database Connection", self.validate_database_connection),
            ("Redis Connection", self.validate_redis_connection),
            ("AI Provider Keys", self.validate_ai_provider_keys),
            ("Required Directories", self.validate_required_directories),
            ("Configuration Files", self.validate_configuration_files),
            ("System Resources", self.validate_system_resources),
        ]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for name, validation_func in validations:
                task = progress.add_task(f"Validating {name}...", total=1)

                try:
                    result = await validation_func()
                    self.add_result(result)
                    progress.update(task, completed=1)

                    status = "[green]✓[/green]" if result.passed else "[red]✗[/red]"
                    console.print(f"{status} {name}: {result.message}")

                except Exception as e:
                    error_result = ValidationResult(name, False, f"Validation error: {str(e)}")
                    self.add_result(error_result)
                    progress.update(task, completed=1)
                    console.print(f"[red]✗[/red] {name}: Validation error: {str(e)}")

        return self.generate_report()

    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        passed_count = len([r for r in self.results if r.passed])
        total_count = len(self.results)

        # Create summary table
        table = Table(title="Validation Summary", show_header=True, header_style="bold magenta")
        table.add_column("Check", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Message", style="dim")

        for result in self.results:
            status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
            table.add_row(result.name, status, result.message)

        console.print("\n")
        console.print(table)

        # Overall status
        if self.critical_failures > 0:
            status = "CRITICAL FAILURES"
            color = "red"
            deployment_ready = False
        elif self.warnings > 0:
            status = "WARNINGS"
            color = "yellow"
            deployment_ready = True
        else:
            status = "ALL CHECKS PASSED"
            color = "green"
            deployment_ready = True

        console.print(f"\n[bold {color}]Overall Status: {status}[/bold {color}]")
        console.print(f"Passed: {passed_count}/{total_count} checks")

        if deployment_ready:
            console.print("\n[bold green]🚀 PLATFORM READY FOR DEPLOYMENT[/bold green]")
        else:
            console.print("\n[bold red]❌ PLATFORM NOT READY - RESOLVE CRITICAL ISSUES FIRST[/bold red]")

        return {
            "deployment_ready": deployment_ready,
            "overall_status": status,
            "passed_checks": passed_count,
            "total_checks": total_count,
            "critical_failures": self.critical_failures,
            "warnings": self.warnings,
            "checks": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ],
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Run deployment validation"""
    validator = DeploymentValidator()

    try:
        report = await validator.run_all_validations()

        # Save report to file
        report_file = Path("deployment_validation_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        console.print(f"\n📄 Detailed report saved to: {report_file}")

        # Exit with appropriate code
        exit_code = 0 if report["deployment_ready"] else 1
        console.print(f"\nValidation completed with exit code: {exit_code}")
        return exit_code

    except Exception as e:
        console.print(f"\n[bold red]Validation failed with error: {str(e)}[/bold red]")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)