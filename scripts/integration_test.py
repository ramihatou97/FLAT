#!/usr/bin/env python3
"""
Medical Knowledge Platform - Integration Test Suite
===================================================

Comprehensive integration testing for all platform interfaces and components.
Tests API endpoints, dashboard functionality, AI providers, and system integration.
"""

import asyncio
import json
import time
import aiohttp
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich import print as rprint

console = Console()

class IntegrationTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: List[Dict] = []
        self.start_time = datetime.now()

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_text = await response.text()

                try:
                    response_data = await response.json() if response.content_type == 'application/json' else {"text": response_text}
                except:
                    response_data = {"text": response_text}

                return {
                    "status": response.status,
                    "success": response.status < 400,
                    "data": response_data,
                    "headers": dict(response.headers),
                    "url": url
                }
        except Exception as e:
            return {
                "status": 0,
                "success": False,
                "error": str(e),
                "url": url
            }

    def add_test_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Add test result to the collection"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })

    async def test_basic_health_endpoints(self) -> bool:
        """Test basic health and status endpoints"""
        console.print("[cyan]🏥 Testing basic health endpoints...[/cyan]")

        endpoints = [
            ("/api/health", "Basic health check"),
            ("/api/monitoring/health/detailed", "Detailed health check"),
            ("/api/monitoring/status/summary", "Status summary"),
        ]

        all_passed = True

        for endpoint, description in endpoints:
            result = await self.make_request("GET", endpoint)
            success = result["success"] and result["status"] == 200

            if success:
                console.print(f"  ✓ {description}")
            else:
                console.print(f"  ✗ {description} - Status: {result['status']}")
                all_passed = False

            self.add_test_result(
                f"Health: {description}",
                success,
                f"Status: {result['status']}",
                {"endpoint": endpoint, "response": result}
            )

        return all_passed

    async def test_api_documentation(self) -> bool:
        """Test API documentation endpoints"""
        console.print("[cyan]📚 Testing API documentation...[/cyan]")

        endpoints = [
            ("/docs", "OpenAPI documentation"),
            ("/redoc", "ReDoc documentation"),
            ("/api/docs/interactive", "Interactive API docs"),
            ("/openapi.json", "OpenAPI schema"),
        ]

        all_passed = True

        for endpoint, description in endpoints:
            result = await self.make_request("GET", endpoint)
            success = result["success"] and result["status"] == 200

            if success:
                console.print(f"  ✓ {description}")
            else:
                console.print(f"  ✗ {description} - Status: {result['status']}")
                all_passed = False

            self.add_test_result(
                f"Docs: {description}",
                success,
                f"Status: {result['status']}",
                {"endpoint": endpoint}
            )

        return all_passed

    async def test_ai_provider_health(self) -> bool:
        """Test AI provider connectivity and health"""
        console.print("[cyan]🤖 Testing AI provider health...[/cyan]")

        # Test AI services health endpoint
        result = await self.make_request("GET", "/api/keys/services/health")
        success = result["success"] and result["status"] == 200

        if not success:
            self.add_test_result(
                "AI Providers: Health Check",
                False,
                f"Health endpoint failed - Status: {result['status']}",
                {"response": result}
            )
            return False

        # Check individual provider status
        try:
            data = result["data"]
            services = data.get("services", {})

            providers = ["openai", "gemini", "claude", "perplexity"]
            healthy_providers = []

            for provider in providers:
                provider_data = services.get(provider, {})
                if provider_data.get("health") == "healthy":
                    healthy_providers.append(provider)
                    console.print(f"  ✓ {provider.title()} - Healthy")
                else:
                    console.print(f"  ✗ {provider.title()} - {provider_data.get('health', 'Unknown')}")

            # At least 2 providers should be healthy for redundancy
            providers_ok = len(healthy_providers) >= 2

            self.add_test_result(
                "AI Providers: Health Status",
                providers_ok,
                f"{len(healthy_providers)}/{len(providers)} providers healthy",
                {"healthy_providers": healthy_providers, "services": services}
            )

            return providers_ok

        except Exception as e:
            self.add_test_result(
                "AI Providers: Health Check",
                False,
                f"Failed to parse response: {str(e)}",
                {"response": result}
            )
            return False

    async def test_semantic_search(self) -> bool:
        """Test semantic search functionality"""
        console.print("[cyan]🔍 Testing semantic search...[/cyan]")

        # Test search stats endpoint
        stats_result = await self.make_request("GET", "/api/search/stats")
        stats_success = stats_result["success"] and stats_result["status"] == 200

        if stats_success:
            try:
                stats_data = stats_result["data"]
                concept_count = stats_data.get("statistics", {}).get("total_concepts", 0)
                console.print(f"  ✓ Search stats - {concept_count} concepts available")
            except:
                console.print(f"  ✗ Search stats - Invalid response format")
                stats_success = False
        else:
            console.print(f"  ✗ Search stats - Status: {stats_result['status']}")

        # Test semantic search endpoint
        search_payload = {
            "query": "glioblastoma treatment",
            "search_type": "semantic",
            "max_results": 5
        }

        search_result = await self.make_request("POST", "/api/search/", json=search_payload)
        search_success = search_result["success"] and search_result["status"] == 200

        if search_success:
            try:
                search_data = search_result["data"]
                result_count = len(search_data.get("results", []))
                console.print(f"  ✓ Semantic search - {result_count} results returned")
            except:
                console.print(f"  ✗ Semantic search - Invalid response format")
                search_success = False
        else:
            console.print(f"  ✗ Semantic search - Status: {search_result['status']}")

        overall_success = stats_success and search_success

        self.add_test_result(
            "Search: Semantic Search",
            overall_success,
            "Search functionality tested",
            {"stats": stats_result, "search": search_result}
        )

        return overall_success

    async def test_ai_generation(self) -> bool:
        """Test AI content generation"""
        console.print("[cyan]✨ Testing AI generation...[/cyan]")

        # Test AI generation endpoint
        generation_payload = {
            "prompt": "Explain the basic anatomy of the brain in 2 sentences.",
            "provider": "gemini",
            "max_tokens": 100
        }

        result = await self.make_request("POST", "/api/ai/generate", json=generation_payload)
        success = result["success"] and result["status"] == 200

        if success:
            try:
                data = result["data"]
                content = data.get("content", "")
                if len(content) > 10:  # Basic content validation
                    console.print(f"  ✓ AI generation - Content generated ({len(content)} chars)")
                else:
                    console.print(f"  ✗ AI generation - Content too short")
                    success = False
            except:
                console.print(f"  ✗ AI generation - Invalid response format")
                success = False
        else:
            console.print(f"  ✗ AI generation - Status: {result['status']}")

        self.add_test_result(
            "AI: Content Generation",
            success,
            "AI generation tested",
            {"response": result}
        )

        return success

    async def test_monitoring_endpoints(self) -> bool:
        """Test monitoring and metrics endpoints"""
        console.print("[cyan]📊 Testing monitoring endpoints...[/cyan]")

        endpoints = [
            ("/api/monitoring/metrics/system", "System metrics"),
            ("/api/monitoring/metrics/database", "Database metrics"),
            ("/api/monitoring/metrics/ai-services", "AI services metrics"),
            ("/api/monitoring/dashboard", "Monitoring dashboard"),
        ]

        all_passed = True

        for endpoint, description in endpoints:
            result = await self.make_request("GET", endpoint)
            success = result["success"] and result["status"] == 200

            if success:
                console.print(f"  ✓ {description}")
            else:
                console.print(f"  ✗ {description} - Status: {result['status']}")
                all_passed = False

            self.add_test_result(
                f"Monitoring: {description}",
                success,
                f"Status: {result['status']}",
                {"endpoint": endpoint}
            )

        return all_passed

    async def test_analytics_endpoints(self) -> bool:
        """Test analytics and dashboard metrics"""
        console.print("[cyan]📈 Testing analytics endpoints...[/cyan]")

        endpoints = [
            ("/api/analytics/dashboard-metrics", "Dashboard metrics"),
            ("/api/analytics/analytics-capabilities", "Analytics capabilities"),
            ("/api/analytics/trend-categories", "Trend categories"),
        ]

        all_passed = True

        for endpoint, description in endpoints:
            result = await self.make_request("GET", endpoint)
            success = result["success"] and result["status"] == 200

            if success:
                console.print(f"  ✓ {description}")
            else:
                console.print(f"  ✗ {description} - Status: {result['status']}")
                all_passed = False

            self.add_test_result(
                f"Analytics: {description}",
                success,
                f"Status: {result['status']}",
                {"endpoint": endpoint}
            )

        return all_passed

    async def test_literature_endpoints(self) -> bool:
        """Test literature analysis endpoints"""
        console.print("[cyan]📚 Testing literature endpoints...[/cyan]")

        endpoints = [
            ("/api/literature/analytics-capabilities", "Literature capabilities"),
        ]

        all_passed = True

        for endpoint, description in endpoints:
            result = await self.make_request("GET", endpoint)
            success = result["success"] and result["status"] == 200

            if success:
                console.print(f"  ✓ {description}")
            else:
                console.print(f"  ✗ {description} - Status: {result['status']}")
                all_passed = False

            self.add_test_result(
                f"Literature: {description}",
                success,
                f"Status: {result['status']}",
                {"endpoint": endpoint}
            )

        return all_passed

    async def test_workflow_endpoints(self) -> bool:
        """Test workflow automation endpoints"""
        console.print("[cyan]🔬 Testing workflow endpoints...[/cyan]")

        # Test workflow capabilities
        result = await self.make_request("GET", "/api/workflow/capabilities")
        success = result["success"] and result["status"] == 200

        if success:
            console.print(f"  ✓ Workflow capabilities")
        else:
            console.print(f"  ✗ Workflow capabilities - Status: {result['status']}")

        self.add_test_result(
            "Workflow: Capabilities",
            success,
            f"Status: {result['status']}",
            {"response": result}
        )

        return success

    async def test_integration_performance(self) -> Dict:
        """Test overall system performance"""
        console.print("[cyan]⚡ Testing system performance...[/cyan]")

        # Test multiple endpoints for response time
        test_endpoints = [
            "/api/health",
            "/api/monitoring/health/detailed",
            "/api/search/stats",
            "/api/analytics/dashboard-metrics"
        ]

        response_times = []

        for endpoint in test_endpoints:
            start_time = time.time()
            result = await self.make_request("GET", endpoint)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)

            status = "✓" if result["success"] else "✗"
            console.print(f"  {status} {endpoint} - {response_time:.0f}ms")

        avg_response_time = sum(response_times) / len(response_times)
        performance_good = avg_response_time < 5000  # 5 seconds threshold

        self.add_test_result(
            "Performance: Response Times",
            performance_good,
            f"Average response time: {avg_response_time:.0f}ms",
            {"response_times": response_times, "endpoints": test_endpoints}
        )

        return {
            "average_response_time": avg_response_time,
            "all_response_times": response_times,
            "performance_good": performance_good
        }

    async def run_full_test_suite(self) -> Dict:
        """Run the complete integration test suite"""
        console.print(Panel.fit(
            "[bold blue]🧪 Medical Knowledge Platform Integration Tests[/bold blue]\n"
            "[cyan]Comprehensive interface and system validation[/cyan]\n"
            f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        ))

        # Define test sequence
        test_functions = [
            ("Basic Health", self.test_basic_health_endpoints),
            ("API Documentation", self.test_api_documentation),
            ("AI Providers", self.test_ai_provider_health),
            ("Semantic Search", self.test_semantic_search),
            ("AI Generation", self.test_ai_generation),
            ("Monitoring", self.test_monitoring_endpoints),
            ("Analytics", self.test_analytics_endpoints),
            ("Literature", self.test_literature_endpoints),
            ("Workflow", self.test_workflow_endpoints),
        ]

        results = {}

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            main_task = progress.add_task("Overall Testing", total=len(test_functions))

            for test_name, test_func in test_functions:
                task = progress.add_task(f"[cyan]{test_name}[/cyan]", total=1)

                try:
                    result = await test_func()
                    results[test_name] = result
                    progress.update(task, completed=1)
                    progress.update(main_task, advance=1)

                except Exception as e:
                    console.print(f"[red]Error in {test_name}: {str(e)}[/red]")
                    results[test_name] = False
                    progress.update(task, completed=1)
                    progress.update(main_task, advance=1)

        # Test performance
        performance_results = await self.test_integration_performance()
        results["Performance"] = performance_results["performance_good"]

        return self.generate_test_report(results)

    def generate_test_report(self, results: Dict) -> Dict:
        """Generate comprehensive test report"""
        passed_tests = len([r for r in results.values() if r is True])
        total_tests = len(results)

        # Create results table
        table = Table(title="Integration Test Results", show_header=True, header_style="bold magenta")
        table.add_column("Test Category", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")

        for test_name, passed in results.items():
            if isinstance(passed, bool):
                status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
                details = "All checks passed" if passed else "Some checks failed"
            else:
                status = "[yellow]INFO[/yellow]"
                details = "Performance data collected"

            table.add_row(test_name, status, details)

        console.print("\n")
        console.print(table)

        # Overall status
        all_passed = all(r is True for r in results.values() if isinstance(r, bool))

        if all_passed:
            status = "ALL TESTS PASSED"
            color = "green"
            ready = True
        else:
            status = "SOME TESTS FAILED"
            color = "red"
            ready = False

        console.print(f"\n[bold {color}]Overall Status: {status}[/bold {color}]")
        console.print(f"Passed: {passed_tests}/{total_tests} test categories")

        if ready:
            console.print("\n[bold green]✅ ALL INTERFACES WORKING CORRECTLY[/bold green]")
        else:
            console.print("\n[bold red]❌ SOME INTERFACES NEED ATTENTION[/bold red]")

        # Test summary
        end_time = datetime.now()
        duration = end_time - self.start_time

        return {
            "all_tests_passed": all_passed,
            "ready_for_use": ready,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_duration": str(duration),
            "test_results": self.test_results,
            "summary": results,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

async def main():
    """Run integration tests"""
    console.print("[bold cyan]🚀 Starting Medical Knowledge Platform Integration Tests[/bold cyan]\n")

    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/health") as response:
                if response.status != 200:
                    console.print("[red]❌ Server not responding. Please start the platform first.[/red]")
                    return 1
    except:
        console.print("[red]❌ Cannot connect to server. Please start the platform first.[/red]")
        console.print("[yellow]Run: python scripts/production_startup.py[/yellow]")
        return 1

    async with IntegrationTest() as tester:
        try:
            report = await tester.run_full_test_suite()

            # Save report
            report_file = Path("integration_test_report.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            console.print(f"\n📄 Detailed report saved to: {report_file}")

            return 0 if report["all_tests_passed"] else 1

        except Exception as e:
            console.print(f"\n[red]Integration testing failed: {str(e)}[/red]")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)