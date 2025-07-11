#!/usr/bin/env python3
"""
Regression testing framework for the enhanced RAG pipeline.
Ensures new features don't break existing functionality and performance remains acceptable.
"""

import os
import sys
import time
import json
import psutil
import tracemalloc
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.vector_store import load_vector_store
from src.utils.rag_chain import create_rag_chain, format_response
from test_suite.data.test_queries import TestDataGenerator

@dataclass
class PerformanceMetrics:
    """Performance metrics for a test run"""
    response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    memory_peak_mb: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class RegressionResult:
    """Results from a regression test"""
    test_name: str
    baseline_metrics: Optional[PerformanceMetrics]
    current_metrics: PerformanceMetrics
    performance_regression: bool
    functionality_regression: bool
    details: Dict[str, Any]

class RegressionTester:
    """Comprehensive regression testing framework"""
    
    def __init__(self, vector_store_path: str = "./chroma_db", model_name: str = "gpt-3.5-turbo"):
        self.vector_store_path = vector_store_path
        self.model_name = model_name
        
        # Performance thresholds
        self.performance_thresholds = {
            "max_response_time": 15.0,  # seconds
            "max_memory_usage": 1000.0,  # MB
            "max_cpu_usage": 80.0,  # percent
            "response_time_regression": 0.5,  # 50% increase threshold
            "memory_regression": 0.3  # 30% increase threshold
        }
        
        # Baseline test queries for regression
        self.baseline_queries = [
            "What is customer research?",
            "How do I create a winning offer?",
            "What should I charge for consulting?",
            "Tell me about authentic selling",
            "How do I get my first client?"
        ]
        
        # Test results storage
        self.results = {
            "test_run_id": f"regression_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "performance_tests": [],
            "functionality_tests": [],
            "memory_tests": [],
            "concurrency_tests": [],
            "integration_tests": [],
            "overall_status": "pending"
        }
    
    def run_regression_tests(self, baseline_file: Optional[str] = None) -> Dict[str, Any]:
        """Run comprehensive regression tests"""
        print("="*80)
        print("REGRESSION TESTING FRAMEWORK")
        print("="*80)
        
        if not self._initialize_system():
            return {"error": "Failed to initialize system"}
        
        # Load baseline metrics if provided
        baseline_metrics = self._load_baseline_metrics(baseline_file) if baseline_file else None
        
        print(f"\nRunning regression tests...")
        if baseline_metrics:
            print(f"Comparing against baseline: {baseline_file}")
        else:
            print("Creating new baseline (no comparison data)")
        
        # Run different types of regression tests
        self._test_basic_functionality()
        self._test_performance_regression(baseline_metrics)
        self._test_memory_usage()
        self._test_concurrency()
        self._test_integration_points()
        
        # Analyze results and determine overall status
        self._analyze_regression_results()
        
        # Save results
        self._save_regression_results()
        
        # Print summary
        self._print_regression_summary()
        
        return self.results
    
    def _initialize_system(self) -> bool:
        """Initialize systems for testing"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            if not os.getenv("OPENAI_API_KEY"):
                print("❌ OPENAI_API_KEY not found")
                return False
            
            if not os.path.exists(self.vector_store_path):
                print(f"❌ Vector store not found at {self.vector_store_path}")
                return False
            
            # Load vector store
            print("Loading vector store...")
            self.vector_store = load_vector_store(self.vector_store_path)
            
            # Initialize both enhanced and standard RAG chains
            print("Initializing RAG chains...")
            self.enhanced_rag = create_rag_chain(
                self.vector_store, 
                self.model_name, 
                use_context_aware_prompting=True
            )
            
            self.standard_rag = create_rag_chain(
                self.vector_store, 
                self.model_name, 
                use_context_aware_prompting=False
            )
            
            print("✅ Regression testing system initialized")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def _test_basic_functionality(self):
        """Test that basic functionality still works"""
        print(f"\n{'-'*60}")
        print("BASIC FUNCTIONALITY TESTS")
        print(f"{'-'*60}")
        
        functionality_results = []
        
        for i, query in enumerate(self.baseline_queries):
            print(f"  Testing query {i+1}/{len(self.baseline_queries)}: {query[:30]}...")
            
            # Test enhanced RAG
            enhanced_result = self._test_single_query(self.enhanced_rag, query, "enhanced")
            
            # Test standard RAG  
            standard_result = self._test_single_query(self.standard_rag, query, "standard")
            
            functionality_results.append({
                "query": query,
                "enhanced_result": enhanced_result,
                "standard_result": standard_result,
                "both_working": enhanced_result.success and standard_result.success
            })
            
            status = "✅" if enhanced_result.success and standard_result.success else "❌"
            print(f"    {status} Enhanced: {enhanced_result.success}, Standard: {standard_result.success}")
        
        self.results["functionality_tests"] = functionality_results
        
        # Calculate functionality score
        working_count = sum(1 for r in functionality_results if r["both_working"])
        functionality_score = working_count / len(functionality_results)
        print(f"\n  Functionality Score: {functionality_score:.1%} ({working_count}/{len(functionality_results)})")
    
    def _test_performance_regression(self, baseline_metrics: Optional[Dict[str, Any]]):
        """Test for performance regressions"""
        print(f"\n{'-'*60}")
        print("PERFORMANCE REGRESSION TESTS")
        print(f"{'-'*60}")
        
        performance_results = []
        
        for query in self.baseline_queries:
            print(f"  Performance testing: {query[:30]}...")
            
            # Measure enhanced RAG performance
            enhanced_perf = self._measure_performance(self.enhanced_rag, query, "enhanced")
            
            # Measure standard RAG performance
            standard_perf = self._measure_performance(self.standard_rag, query, "standard")
            
            # Compare with baseline if available
            regression_detected = False
            if baseline_metrics:
                baseline_query_data = baseline_metrics.get("queries", {}).get(query)
                if baseline_query_data:
                    regression_detected = self._detect_performance_regression(
                        enhanced_perf, baseline_query_data.get("enhanced")
                    )
            
            performance_results.append({
                "query": query,
                "enhanced_performance": asdict(enhanced_perf),
                "standard_performance": asdict(standard_perf),
                "regression_detected": regression_detected
            })
            
            print(f"    Enhanced: {enhanced_perf.response_time:.2f}s, {enhanced_perf.memory_usage_mb:.1f}MB")
            print(f"    Standard: {standard_perf.response_time:.2f}s, {standard_perf.memory_usage_mb:.1f}MB")
            if regression_detected:
                print(f"    ⚠️  Performance regression detected!")
        
        self.results["performance_tests"] = performance_results
    
    def _test_memory_usage(self):
        """Test memory usage patterns"""
        print(f"\n{'-'*60}")
        print("MEMORY USAGE TESTS")
        print(f"{'-'*60}")
        
        memory_results = []
        
        # Test memory usage over multiple queries
        print("  Testing memory accumulation over multiple queries...")
        
        tracemalloc.start()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        for i in range(10):  # Run 10 queries to test memory accumulation
            query = self.baseline_queries[i % len(self.baseline_queries)]
            
            try:
                response = self.enhanced_rag({"question": query})
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                memory_results.append({
                    "iteration": i + 1,
                    "query": query,
                    "memory_mb": current_memory,
                    "memory_increase_mb": memory_increase,
                    "success": bool(response)
                })
                
                if i % 3 == 0:  # Print every 3rd iteration
                    print(f"    Iteration {i+1}: {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
                    
            except Exception as e:
                memory_results.append({
                    "iteration": i + 1,
                    "query": query,
                    "error": str(e),
                    "success": False
                })
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Analyze memory patterns
        final_memory = memory_results[-1]["memory_mb"] if memory_results else initial_memory
        total_increase = final_memory - initial_memory
        memory_leak_detected = total_increase > 100  # > 100MB increase is concerning
        
        self.results["memory_tests"] = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "total_increase_mb": total_increase,
            "peak_traced_mb": peak / 1024 / 1024,
            "memory_leak_detected": memory_leak_detected,
            "iterations": memory_results
        }
        
        print(f"  Memory Analysis:")
        print(f"    Initial: {initial_memory:.1f}MB")
        print(f"    Final: {final_memory:.1f}MB")
        print(f"    Increase: {total_increase:.1f}MB")
        print(f"    Peak Traced: {peak / 1024 / 1024:.1f}MB")
        if memory_leak_detected:
            print(f"    ⚠️  Potential memory leak detected!")
    
    def _test_concurrency(self):
        """Test concurrent request handling"""
        print(f"\n{'-'*60}")
        print("CONCURRENCY TESTS")
        print(f"{'-'*60}")
        
        # Test with 3 concurrent requests
        concurrent_queries = self.baseline_queries[:3]
        
        print(f"  Testing {len(concurrent_queries)} concurrent requests...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i, query in enumerate(concurrent_queries):
                future = executor.submit(self._test_single_query, self.enhanced_rag, query, f"concurrent_{i}")
                futures.append((query, future))
            
            concurrent_results = []
            for query, future in futures:
                try:
                    result = future.result(timeout=30)
                    concurrent_results.append({
                        "query": query,
                        "success": result.success,
                        "response_time": result.response_time,
                        "error": result.error_message
                    })
                except Exception as e:
                    concurrent_results.append({
                        "query": query,
                        "success": False,
                        "error": str(e)
                    })
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in concurrent_results if r["success"])
        
        self.results["concurrency_tests"] = {
            "queries_tested": len(concurrent_queries),
            "successful": success_count,
            "total_time": total_time,
            "average_time": total_time / len(concurrent_queries),
            "all_successful": success_count == len(concurrent_queries),
            "results": concurrent_results
        }
        
        print(f"  Concurrency Results:")
        print(f"    Successful: {success_count}/{len(concurrent_queries)}")
        print(f"    Total Time: {total_time:.2f}s")
        print(f"    Average Time: {total_time / len(concurrent_queries):.2f}s")
    
    def _test_integration_points(self):
        """Test integration points and dependencies"""
        print(f"\n{'-'*60}")
        print("INTEGRATION TESTS")
        print(f"{'-'*60}")
        
        integration_results = {}
        
        # Test vector store integration
        print("  Testing vector store integration...")
        try:
            # Test retrieval directly
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents("customer research")
            
            integration_results["vector_store"] = {
                "success": len(docs) > 0,
                "documents_retrieved": len(docs),
                "error": None
            }
            print(f"    ✅ Retrieved {len(docs)} documents")
            
        except Exception as e:
            integration_results["vector_store"] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ Vector store error: {e}")
        
        # Test context-aware prompting integration
        print("  Testing context-aware prompting...")
        try:
            from src.utils.context_aware_prompting import create_ramit_prompt_generator
            from src.utils.coaching_context_injector import create_coaching_context_injector
            
            prompt_generator = create_ramit_prompt_generator()
            context_injector = create_coaching_context_injector()
            
            # Test prompt generation
            test_sources = [{"content": "test", "ramit_type": "framework", "ramit_frameworks": [], "ramit_scores": {}}]
            prompt = prompt_generator.generate_context_aware_prompt("test query", test_sources)
            
            integration_results["context_aware_prompting"] = {
                "success": len(prompt) > 0,
                "prompt_length": len(prompt),
                "error": None
            }
            print(f"    ✅ Generated prompt ({len(prompt)} chars)")
            
        except Exception as e:
            integration_results["context_aware_prompting"] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ Context-aware prompting error: {e}")
        
        # Test user profile integration
        print("  Testing user profile integration...")
        try:
            from src.utils.user_profile import UserProfile
            
            profile = UserProfile("./test_user_profile.json")
            profile_text = profile.get_formatted_profile()
            
            integration_results["user_profile"] = {
                "success": True,
                "profile_length": len(profile_text),
                "error": None
            }
            print(f"    ✅ User profile working")
            
        except Exception as e:
            integration_results["user_profile"] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ User profile error: {e}")
        
        self.results["integration_tests"] = integration_results
    
    def _test_single_query(self, rag_chain, query: str, test_type: str) -> PerformanceMetrics:
        """Test a single query and measure performance"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        tracemalloc.start()
        
        try:
            response = rag_chain({"question": query})
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            current, peak = tracemalloc.get_traced_memory()
            
            success = bool(response and response.get("answer"))
            
            return PerformanceMetrics(
                response_time=end_time - start_time,
                memory_usage_mb=end_memory - start_memory,
                cpu_usage_percent=psutil.cpu_percent(),
                memory_peak_mb=peak / 1024 / 1024,
                success=success
            )
            
        except Exception as e:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            return PerformanceMetrics(
                response_time=end_time - start_time,
                memory_usage_mb=end_memory - start_memory,
                cpu_usage_percent=psutil.cpu_percent(),
                memory_peak_mb=0,
                success=False,
                error_message=str(e)
            )
        finally:
            tracemalloc.stop()
    
    def _measure_performance(self, rag_chain, query: str, test_type: str) -> PerformanceMetrics:
        """Measure performance metrics for a query"""
        # Run multiple times and take average
        metrics = []
        for _ in range(3):
            metric = self._test_single_query(rag_chain, query, test_type)
            metrics.append(metric)
            time.sleep(0.5)  # Brief pause between runs
        
        # Calculate averages
        avg_response_time = sum(m.response_time for m in metrics) / len(metrics)
        avg_memory = sum(m.memory_usage_mb for m in metrics) / len(metrics)
        avg_cpu = sum(m.cpu_usage_percent for m in metrics) / len(metrics)
        max_peak_memory = max(m.memory_peak_mb for m in metrics)
        all_successful = all(m.success for m in metrics)
        
        return PerformanceMetrics(
            response_time=avg_response_time,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            memory_peak_mb=max_peak_memory,
            success=all_successful
        )
    
    def _detect_performance_regression(self, current: PerformanceMetrics, baseline: Dict[str, Any]) -> bool:
        """Detect if there's a performance regression"""
        if not baseline:
            return False
        
        baseline_time = baseline.get("response_time", 0)
        baseline_memory = baseline.get("memory_usage_mb", 0)
        
        # Check for significant increases
        time_regression = (
            baseline_time > 0 and 
            current.response_time > baseline_time * (1 + self.performance_thresholds["response_time_regression"])
        )
        
        memory_regression = (
            baseline_memory > 0 and 
            current.memory_usage_mb > baseline_memory * (1 + self.performance_thresholds["memory_regression"])
        )
        
        return time_regression or memory_regression
    
    def _load_baseline_metrics(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load baseline metrics from file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load baseline metrics: {e}")
            return None
    
    def _analyze_regression_results(self):
        """Analyze all regression test results"""
        issues = []
        
        # Check functionality
        functionality_tests = self.results.get("functionality_tests", [])
        if functionality_tests:
            working_count = sum(1 for r in functionality_tests if r["both_working"])
            if working_count < len(functionality_tests):
                issues.append(f"Functionality regression: {len(functionality_tests) - working_count} queries failing")
        
        # Check performance
        performance_tests = self.results.get("performance_tests", [])
        regression_count = sum(1 for r in performance_tests if r["regression_detected"])
        if regression_count > 0:
            issues.append(f"Performance regression: {regression_count} queries showing degradation")
        
        # Check memory
        memory_tests = self.results.get("memory_tests", {})
        if memory_tests.get("memory_leak_detected"):
            issues.append("Memory leak detected")
        
        # Check concurrency
        concurrency_tests = self.results.get("concurrency_tests", {})
        if not concurrency_tests.get("all_successful"):
            issues.append("Concurrency issues detected")
        
        # Check integrations
        integration_tests = self.results.get("integration_tests", {})
        failed_integrations = [name for name, result in integration_tests.items() if not result.get("success")]
        if failed_integrations:
            issues.append(f"Integration failures: {', '.join(failed_integrations)}")
        
        # Determine overall status
        if not issues:
            self.results["overall_status"] = "PASS"
        elif len(issues) <= 2:
            self.results["overall_status"] = "WARN"
        else:
            self.results["overall_status"] = "FAIL"
        
        self.results["issues"] = issues
    
    def _save_regression_results(self):
        """Save regression test results"""
        filename = f"regression_results_{self.results['test_run_id']}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n💾 Regression results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save regression results: {e}")
    
    def _print_regression_summary(self):
        """Print regression testing summary"""
        print("\n" + "="*80)
        print("REGRESSION TEST SUMMARY")
        print("="*80)
        
        status = self.results["overall_status"]
        status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(status, "❓")
        
        print(f"\n{status_icon} OVERALL STATUS: {status}")
        
        if self.results.get("issues"):
            print(f"\n⚠️  ISSUES DETECTED:")
            for issue in self.results["issues"]:
                print(f"   • {issue}")
        
        # Functionality summary
        functionality_tests = self.results.get("functionality_tests", [])
        if functionality_tests:
            working = sum(1 for r in functionality_tests if r["both_working"])
            print(f"\n🔧 FUNCTIONALITY: {working}/{len(functionality_tests)} working")
        
        # Performance summary
        performance_tests = self.results.get("performance_tests", [])
        if performance_tests:
            avg_enhanced_time = sum(r["enhanced_performance"]["response_time"] for r in performance_tests) / len(performance_tests)
            avg_standard_time = sum(r["standard_performance"]["response_time"] for r in performance_tests) / len(performance_tests)
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Enhanced RAG: {avg_enhanced_time:.2f}s average")
            print(f"   Standard RAG: {avg_standard_time:.2f}s average")
        
        # Memory summary
        memory_tests = self.results.get("memory_tests", {})
        if memory_tests:
            print(f"\n💾 MEMORY:")
            print(f"   Total increase: {memory_tests.get('total_increase_mb', 0):.1f}MB")
            print(f"   Peak usage: {memory_tests.get('peak_traced_mb', 0):.1f}MB")
        
        # Concurrency summary
        concurrency_tests = self.results.get("concurrency_tests", {})
        if concurrency_tests:
            print(f"\n🔀 CONCURRENCY:")
            print(f"   Success rate: {concurrency_tests.get('successful', 0)}/{concurrency_tests.get('queries_tested', 0)}")
        
        print(f"\n📊 Test completed: {self.results['timestamp']}")

def run_regression_tests(baseline_file: Optional[str] = None):
    """Run regression tests"""
    tester = RegressionTester()
    return tester.run_regression_tests(baseline_file)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run regression tests")
    parser.add_argument("--baseline", help="Baseline metrics file for comparison")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to use")
    
    args = parser.parse_args()
    
    run_regression_tests(args.baseline)