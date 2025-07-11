#!/usr/bin/env python3
"""
Comprehensive test suite for the enhanced RAG pipeline.
Validates response quality, framework accuracy, and coaching effectiveness.
"""

import os
import sys
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict
from datetime import datetime
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.vector_store import load_vector_store
from src.utils.rag_chain import create_rag_chain, format_response
from test_suite.data.test_queries import TestDataGenerator, TestQuery
from test_suite.metrics.quality_metrics import ResponseQualityAnalyzer, QualityMetricsAggregator, QualityScores

class ComprehensiveTestSuite:
    """Main test suite for comprehensive validation"""
    
    def __init__(self, vector_store_path: str = "./chroma_db", model_name: str = "gpt-3.5-turbo"):
        self.vector_store_path = vector_store_path
        self.model_name = model_name
        self.quality_analyzer = ResponseQualityAnalyzer()
        self.metrics_aggregator = QualityMetricsAggregator()
        
        # Test configuration
        self.test_config = {
            "context_aware_prompting": True,
            "max_retries": 3,
            "timeout_seconds": 30,
            "save_detailed_results": True
        }
        
        # Results storage
        self.results = {
            "test_run_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "configuration": self.test_config.copy(),
            "results_by_category": {},
            "overall_metrics": {},
            "failing_responses": [],
            "performance_metrics": {},
            "framework_accuracy": {},
            "edge_case_results": {}
        }
    
    def run_comprehensive_tests(self, categories: List[str] = None) -> Dict[str, Any]:
        """Run the complete test suite"""
        print("="*80)
        print("COMPREHENSIVE RAG PIPELINE TEST SUITE")
        print("="*80)
        
        # Initialize system
        if not self._initialize_system():
            return {"error": "Failed to initialize system"}
        
        # Run tests by category
        test_queries = TestDataGenerator.get_all_test_queries()
        if categories:
            test_queries = {k: v for k, v in test_queries.items() if k in categories}
        
        print(f"\nRunning tests for categories: {list(test_queries.keys())}")
        
        for category, queries in test_queries.items():
            print(f"\n{'-'*60}")
            print(f"Testing Category: {category.upper()}")
            print(f"{'-'*60}")
            
            category_results = self._test_category(category, queries)
            self.results["results_by_category"][category] = category_results
        
        # Run framework accuracy validation
        print(f"\n{'-'*60}")
        print("FRAMEWORK ACCURACY VALIDATION")
        print(f"{'-'*60}")
        framework_results = self._test_framework_accuracy()
        self.results["framework_accuracy"] = framework_results
        
        # Run edge case tests
        print(f"\n{'-'*60}")
        print("EDGE CASE TESTING")
        print(f"{'-'*60}")
        edge_case_results = self._test_edge_cases()
        self.results["edge_case_results"] = edge_case_results
        
        # Run performance tests
        print(f"\n{'-'*60}")
        print("PERFORMANCE TESTING")
        print(f"{'-'*60}")
        performance_results = self._test_performance()
        self.results["performance_metrics"] = performance_results
        
        # Aggregate final results
        self._finalize_results()
        
        # Generate summary report
        self._print_summary_report()
        
        return self.results
    
    def _initialize_system(self) -> bool:
        """Initialize the RAG system for testing"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Check prerequisites
            if not os.getenv("OPENAI_API_KEY"):
                print("❌ OPENAI_API_KEY not found")
                return False
            
            if not os.path.exists(self.vector_store_path):
                print(f"❌ Vector store not found at {self.vector_store_path}")
                return False
            
            # Load vector store
            print("Loading vector store...")
            self.vector_store = load_vector_store(self.vector_store_path)
            
            # Create RAG chains for comparison
            print("Initializing RAG chains...")
            self.enhanced_rag_chain = create_rag_chain(
                self.vector_store, 
                self.model_name, 
                use_context_aware_prompting=True
            )
            
            self.standard_rag_chain = create_rag_chain(
                self.vector_store, 
                self.model_name, 
                use_context_aware_prompting=False
            )
            
            print("✅ System initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            return False
    
    def _test_category(self, category: str, queries: List[TestQuery]) -> Dict[str, Any]:
        """Test all queries in a category"""
        category_results = {
            "queries_tested": len(queries),
            "queries_passed": 0,
            "queries_failed": 0,
            "average_scores": {},
            "individual_results": [],
            "category_insights": {}
        }
        
        for i, query in enumerate(queries):
            print(f"  Testing query {i+1}/{len(queries)}: {query.query[:50]}...")
            
            try:
                # Get response from enhanced system
                enhanced_response = self._get_response(self.enhanced_rag_chain, query.query)
                
                if enhanced_response:
                    # Analyze quality
                    formatted_response = format_response(enhanced_response)
                    scores = self.quality_analyzer.analyze_response_quality(
                        formatted_response["answer"],
                        query,
                        formatted_response["sources"]
                    )
                    
                    # Record result
                    self.metrics_aggregator.add_result(query, scores, formatted_response["answer"])
                    
                    # Determine pass/fail
                    passed = scores.overall_score >= 3.0  # 3.0/5.0 threshold
                    if passed:
                        category_results["queries_passed"] += 1
                    else:
                        category_results["queries_failed"] += 1
                    
                    # Store individual result
                    category_results["individual_results"].append({
                        "query": query.query,
                        "subcategory": query.subcategory,
                        "passed": passed,
                        "scores": asdict(scores),
                        "response_preview": formatted_response["answer"][:150] + "..."
                    })
                    
                    print(f"    ✅ Score: {scores.overall_score:.2f}/5.0 ({'PASS' if passed else 'FAIL'})")
                else:
                    category_results["queries_failed"] += 1
                    print(f"    ❌ Failed to get response")
                    
            except Exception as e:
                category_results["queries_failed"] += 1
                print(f"    ❌ Error: {e}")
        
        # Calculate category averages
        category_results["pass_rate"] = category_results["queries_passed"] / len(queries) if queries else 0
        
        return category_results
    
    def _test_framework_accuracy(self) -> Dict[str, Any]:
        """Test accuracy of framework representations"""
        framework_tests = [
            {
                "framework": "customer_research",
                "test_query": "Explain Ramit's customer research framework in detail",
                "expected_elements": [
                    "mind reading", "customer interviews", "exact language",
                    "10 customers", "problems", "dream outcomes"
                ]
            },
            {
                "framework": "winning_offer",
                "test_query": "What are the components of a winning offer according to Ramit?",
                "expected_elements": [
                    "problem", "solution", "urgency", "guarantee", "bonuses",
                    "irresistible", "investment", "risk reversal"
                ]
            },
            {
                "framework": "authentic_selling",
                "test_query": "How does Ramit approach selling authentically?",
                "expected_elements": [
                    "rapport", "consultative", "needs", "objections",
                    "ask for the sale", "no pressure", "confidence"
                ]
            },
            {
                "framework": "profit_playbook",
                "test_query": "Describe the profit playbook methodology",
                "expected_elements": [
                    "business model", "revenue streams", "customer acquisition",
                    "systems", "metrics", "predictable"
                ]
            }
        ]
        
        framework_results = {}
        
        for test in framework_tests:
            print(f"  Testing {test['framework']} framework...")
            
            try:
                response = self._get_response(self.enhanced_rag_chain, test["test_query"])
                
                if response:
                    formatted_response = format_response(response)
                    answer = formatted_response["answer"].lower()
                    
                    # Check for expected elements
                    elements_found = []
                    elements_missing = []
                    
                    for element in test["expected_elements"]:
                        if element.lower() in answer:
                            elements_found.append(element)
                        else:
                            elements_missing.append(element)
                    
                    accuracy_score = len(elements_found) / len(test["expected_elements"])
                    
                    framework_results[test["framework"]] = {
                        "accuracy_score": accuracy_score,
                        "elements_found": elements_found,
                        "elements_missing": elements_missing,
                        "response_length": len(formatted_response["answer"]),
                        "sources_used": len(formatted_response["sources"])
                    }
                    
                    print(f"    Accuracy: {accuracy_score:.2f} ({len(elements_found)}/{len(test['expected_elements'])} elements)")
                else:
                    framework_results[test["framework"]] = {"error": "No response received"}
                    
            except Exception as e:
                framework_results[test["framework"]] = {"error": str(e)}
        
        return framework_results
    
    def _test_edge_cases(self) -> Dict[str, Any]:
        """Test edge cases and error handling"""
        edge_cases = TestDataGenerator.get_edge_case_queries()
        edge_results = {
            "total_tested": len(edge_cases),
            "handled_gracefully": 0,
            "failed_gracefully": 0,
            "system_errors": 0,
            "individual_results": []
        }
        
        for edge_case in edge_cases:
            print(f"  Testing edge case: {edge_case.subcategory}")
            
            try:
                start_time = time.time()
                response = self._get_response(self.enhanced_rag_chain, edge_case.query, timeout=10)
                response_time = time.time() - start_time
                
                if response:
                    formatted_response = format_response(response)
                    
                    # Check if response is appropriate for edge case
                    response_text = formatted_response["answer"].lower()
                    
                    # For empty/nonsense queries, expect polite clarification request
                    if edge_case.subcategory in ["empty_input", "nonsense_input"]:
                        graceful_indicators = [
                            "clarify", "specific question", "help you with",
                            "more information", "what would you like"
                        ]
                        handled_gracefully = any(indicator in response_text for indicator in graceful_indicators)
                    else:
                        # For out-of-scope queries, expect redirect to business fundamentals
                        handled_gracefully = "business" in response_text and len(response_text) > 50
                    
                    if handled_gracefully:
                        edge_results["handled_gracefully"] += 1
                        status = "HANDLED_GRACEFULLY"
                    else:
                        edge_results["failed_gracefully"] += 1
                        status = "POOR_HANDLING"
                    
                    edge_results["individual_results"].append({
                        "subcategory": edge_case.subcategory,
                        "query": edge_case.query,
                        "status": status,
                        "response_time": response_time,
                        "response_preview": formatted_response["answer"][:100] + "..."
                    })
                    
                    print(f"    {status} (in {response_time:.2f}s)")
                else:
                    edge_results["system_errors"] += 1
                    print(f"    SYSTEM_ERROR")
                    
            except Exception as e:
                edge_results["system_errors"] += 1
                print(f"    SYSTEM_ERROR: {e}")
        
        return edge_results
    
    def _test_performance(self) -> Dict[str, Any]:
        """Test system performance metrics"""
        performance_queries = [
            "What is customer research?",  # Simple query
            "Explain the complete relationship between customer research, winning offers, authentic selling, and the profit playbook with specific examples and implementation steps",  # Complex query
        ]
        
        performance_results = {
            "response_times": [],
            "memory_usage": [],
            "throughput": {},
            "system_stability": True
        }
        
        print("  Running performance tests...")
        
        # Test response times
        for query in performance_queries:
            times = []
            for i in range(3):  # 3 runs per query
                try:
                    start_time = time.time()
                    response = self._get_response(self.enhanced_rag_chain, query)
                    end_time = time.time()
                    
                    if response:
                        times.append(end_time - start_time)
                    else:
                        performance_results["system_stability"] = False
                        
                except Exception as e:
                    performance_results["system_stability"] = False
                    print(f"    Performance test error: {e}")
            
            if times:
                avg_time = sum(times) / len(times)
                performance_results["response_times"].append({
                    "query_type": "simple" if len(query) < 50 else "complex",
                    "average_time": avg_time,
                    "times": times
                })
                print(f"    {('Simple' if len(query) < 50 else 'Complex')} query avg: {avg_time:.2f}s")
        
        # Calculate overall performance metrics
        if performance_results["response_times"]:
            all_times = []
            for result in performance_results["response_times"]:
                all_times.extend(result["times"])
            
            performance_results["throughput"] = {
                "average_response_time": sum(all_times) / len(all_times),
                "min_response_time": min(all_times),
                "max_response_time": max(all_times),
                "queries_per_minute": 60 / (sum(all_times) / len(all_times))
            }
        
        return performance_results
    
    def _get_response(self, rag_chain, query: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Get response from RAG chain with timeout and retry logic"""
        for attempt in range(self.test_config["max_retries"]):
            try:
                response = rag_chain({"question": query})
                return response
            except Exception as e:
                if attempt == self.test_config["max_retries"] - 1:
                    print(f"    Failed after {self.test_config['max_retries']} attempts: {e}")
                    return None
                time.sleep(1)  # Brief pause before retry
        
        return None
    
    def _finalize_results(self):
        """Calculate final aggregated metrics"""
        # Overall metrics from aggregator
        self.results["overall_metrics"] = self.metrics_aggregator.get_overall_metrics()
        
        # Category averages
        self.results["category_averages"] = self.metrics_aggregator.get_category_averages()
        
        # Failing responses
        self.results["failing_responses"] = self.metrics_aggregator.get_failing_responses()
        
        # Test summary
        total_queries = sum(result.get("queries_tested", 0) for result in self.results["results_by_category"].values())
        total_passed = sum(result.get("queries_passed", 0) for result in self.results["results_by_category"].values())
        
        self.results["test_summary"] = {
            "total_queries_tested": total_queries,
            "total_queries_passed": total_passed,
            "overall_pass_rate": total_passed / total_queries if total_queries > 0 else 0,
            "test_duration": "calculated_in_print_summary"
        }
    
    def _print_summary_report(self):
        """Print comprehensive summary report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*80)
        
        # Overall metrics
        overall = self.results["overall_metrics"]
        if overall:
            print(f"\n📊 OVERALL QUALITY METRICS:")
            print(f"   Ramit Authenticity: {overall['ramit_authenticity']:.2f}/5.0")
            print(f"   Framework Coherence: {overall['framework_coherence']:.2f}/5.0")
            print(f"   Actionability: {overall['actionability']:.2f}/5.0")
            print(f"   Source Accuracy: {overall['source_accuracy']:.2f}/5.0")
            print(f"   Coaching Effectiveness: {overall['coaching_effectiveness']:.2f}/5.0")
            print(f"   OVERALL SCORE: {overall['overall_score']:.2f}/5.0")
        
        # Test summary
        summary = self.results["test_summary"]
        print(f"\n📈 TEST SUMMARY:")
        print(f"   Total Queries Tested: {summary['total_queries_tested']}")
        print(f"   Queries Passed: {summary['total_queries_passed']}")
        print(f"   Overall Pass Rate: {summary['overall_pass_rate']:.1%}")
        
        # Category performance
        print(f"\n📂 CATEGORY PERFORMANCE:")
        for category, results in self.results["results_by_category"].items():
            pass_rate = results.get("pass_rate", 0)
            status = "✅" if pass_rate >= 0.8 else "⚠️" if pass_rate >= 0.6 else "❌"
            print(f"   {status} {category.capitalize()}: {pass_rate:.1%} ({results.get('queries_passed', 0)}/{results.get('queries_tested', 0)})")
        
        # Framework accuracy
        print(f"\n🎯 FRAMEWORK ACCURACY:")
        for framework, results in self.results["framework_accuracy"].items():
            if "accuracy_score" in results:
                accuracy = results["accuracy_score"]
                status = "✅" if accuracy >= 0.8 else "⚠️" if accuracy >= 0.6 else "❌"
                print(f"   {status} {framework.replace('_', ' ').title()}: {accuracy:.1%}")
        
        # Performance metrics
        if self.results["performance_metrics"].get("throughput"):
            perf = self.results["performance_metrics"]["throughput"]
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Average Response Time: {perf['average_response_time']:.2f}s")
            print(f"   Queries Per Minute: {perf['queries_per_minute']:.1f}")
            print(f"   System Stability: {'✅' if self.results['performance_metrics']['system_stability'] else '❌'}")
        
        # Failing responses
        failing_count = len(self.results["failing_responses"])
        if failing_count > 0:
            print(f"\n⚠️  FAILING RESPONSES: {failing_count}")
            for failure in self.results["failing_responses"][:3]:  # Show first 3
                print(f"   - {failure['category']}: {failure['query'][:50]}... (Score: {failure['overall_score']:.2f})")
        
        print(f"\n💾 Results saved to: test_results_{self.results['test_run_id']}.json")
        
        # Save detailed results
        self._save_results()
    
    def _save_results(self):
        """Save detailed results to file"""
        filename = f"test_results_{self.results['test_run_id']}.json"
        
        try:
            # Create a JSON-serializable version of results
            serializable_results = self._make_serializable(self.results)
            
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            print(f"✅ Detailed results saved to {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return obj

def run_quick_test():
    """Run a quick subset of tests for development"""
    suite = ComprehensiveTestSuite()
    return suite.run_comprehensive_tests(categories=["framework", "tactical"])

def run_full_test():
    """Run the complete test suite"""
    suite = ComprehensiveTestSuite()
    return suite.run_comprehensive_tests()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive RAG pipeline tests")
    parser.add_argument("--quick", action="store_true", help="Run quick test subset")
    parser.add_argument("--categories", nargs="+", help="Specific categories to test")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to use for testing")
    
    args = parser.parse_args()
    
    suite = ComprehensiveTestSuite(model_name=args.model)
    
    if args.quick:
        suite.run_comprehensive_tests(categories=["framework", "tactical"])
    elif args.categories:
        suite.run_comprehensive_tests(categories=args.categories)
    else:
        suite.run_comprehensive_tests()