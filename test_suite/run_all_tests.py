#!/usr/bin/env python3
"""
Comprehensive test runner for the enhanced RAG pipeline.
Orchestrates all testing components: quality, regression, comparison, multi-turn, and monitoring.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_suite.comprehensive_test_suite import ComprehensiveTestSuite
from test_suite.multi_turn_testing import MultiTurnTester
from test_suite.regression.regression_tests import RegressionTester
from test_suite.comparison.before_after_comparison import BeforeAfterComparer
from test_suite.monitoring.quality_monitor import QualityMonitor

class TestOrchestrator:
    """Orchestrates all testing components"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.results = {
            "test_run_id": f"full_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "test_results": {},
            "summary": {},
            "recommendations": []
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default test configuration"""
        return {
            "vector_store_path": "./chroma_db",
            "model_name": "gpt-3.5-turbo",
            "test_categories": ["framework", "tactical", "mindset", "contrarian", "first_sale", "pricing"],
            "run_comprehensive": True,
            "run_multi_turn": True,
            "run_regression": True,
            "run_comparison": True,
            "run_monitoring_demo": False,
            "save_results": True,
            "parallel_execution": False
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        print("="*80)
        print("COMPREHENSIVE RAG PIPELINE VALIDATION")
        print("="*80)
        print(f"Test Run ID: {self.results['test_run_id']}")
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Configuration: {self.config}")
        
        start_time = time.time()
        
        # Initialize test summary
        test_summary = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "critical_issues": 0,
            "warnings": 0,
            "overall_status": "pending"
        }
        
        # Run comprehensive quality tests
        if self.config["run_comprehensive"]:
            print(f"\n{'='*80}")
            print("1. COMPREHENSIVE QUALITY VALIDATION")
            print(f"{'='*80}")
            
            try:
                suite = ComprehensiveTestSuite(
                    self.config["vector_store_path"], 
                    self.config["model_name"]
                )
                comprehensive_results = suite.run_comprehensive_tests(self.config["test_categories"])
                self.results["test_results"]["comprehensive"] = comprehensive_results
                
                # Update summary
                test_summary["tests_run"] += 1
                if comprehensive_results.get("test_summary", {}).get("overall_pass_rate", 0) >= 0.8:
                    test_summary["tests_passed"] += 1
                    print("✅ Comprehensive tests: PASSED")
                else:
                    test_summary["tests_failed"] += 1
                    test_summary["critical_issues"] += 1
                    print("❌ Comprehensive tests: FAILED")
                    
            except Exception as e:
                print(f"❌ Comprehensive tests failed with error: {e}")
                self.results["test_results"]["comprehensive"] = {"error": str(e)}
                test_summary["tests_failed"] += 1
                test_summary["critical_issues"] += 1
        
        # Run multi-turn conversation tests
        if self.config["run_multi_turn"]:
            print(f"\n{'='*80}")
            print("2. MULTI-TURN CONVERSATION VALIDATION")
            print(f"{'='*80}")
            
            try:
                multi_turn_tester = MultiTurnTester(
                    self.config["vector_store_path"], 
                    self.config["model_name"]
                )
                multi_turn_results = multi_turn_tester.run_multi_turn_tests()
                self.results["test_results"]["multi_turn"] = multi_turn_results
                
                # Update summary
                test_summary["tests_run"] += 1
                success_rate = multi_turn_results.get("overall_metrics", {}).get("success_rate", 0)
                if success_rate >= 0.7:
                    test_summary["tests_passed"] += 1
                    print("✅ Multi-turn tests: PASSED")
                else:
                    test_summary["tests_failed"] += 1
                    test_summary["warnings"] += 1
                    print("⚠️ Multi-turn tests: WARNINGS")
                    
            except Exception as e:
                print(f"❌ Multi-turn tests failed with error: {e}")
                self.results["test_results"]["multi_turn"] = {"error": str(e)}
                test_summary["tests_failed"] += 1
                test_summary["warnings"] += 1
        
        # Run regression tests
        if self.config["run_regression"]:
            print(f"\n{'='*80}")
            print("3. REGRESSION TESTING")
            print(f"{'='*80}")
            
            try:
                regression_tester = RegressionTester(
                    self.config["vector_store_path"], 
                    self.config["model_name"]
                )
                regression_results = regression_tester.run_regression_tests()
                self.results["test_results"]["regression"] = regression_results
                
                # Update summary
                test_summary["tests_run"] += 1
                status = regression_results.get("overall_status", "FAIL")
                if status == "PASS":
                    test_summary["tests_passed"] += 1
                    print("✅ Regression tests: PASSED")
                elif status == "WARN":
                    test_summary["tests_passed"] += 1
                    test_summary["warnings"] += 1
                    print("⚠️ Regression tests: WARNINGS")
                else:
                    test_summary["tests_failed"] += 1
                    test_summary["critical_issues"] += 1
                    print("❌ Regression tests: FAILED")
                    
            except Exception as e:
                print(f"❌ Regression tests failed with error: {e}")
                self.results["test_results"]["regression"] = {"error": str(e)}
                test_summary["tests_failed"] += 1
                test_summary["critical_issues"] += 1
        
        # Run before/after comparison
        if self.config["run_comparison"]:
            print(f"\n{'='*80}")
            print("4. BEFORE/AFTER COMPARISON")
            print(f"{'='*80}")
            
            try:
                comparer = BeforeAfterComparer(
                    self.config["vector_store_path"], 
                    self.config["model_name"]
                )
                comparison_results = comparer.run_before_after_comparison(self.config["test_categories"])
                self.results["test_results"]["comparison"] = comparison_results
                
                # Update summary
                test_summary["tests_run"] += 1
                improvement_rate = comparison_results.get("overall_improvements", {}).get("improvement_rate", 0)
                if improvement_rate >= 0.7:
                    test_summary["tests_passed"] += 1
                    print("✅ Comparison tests: SIGNIFICANT IMPROVEMENTS")
                elif improvement_rate >= 0.5:
                    test_summary["tests_passed"] += 1
                    print("✅ Comparison tests: MODERATE IMPROVEMENTS")
                else:
                    test_summary["tests_failed"] += 1
                    test_summary["warnings"] += 1
                    print("⚠️ Comparison tests: LIMITED IMPROVEMENTS")
                    
            except Exception as e:
                print(f"❌ Comparison tests failed with error: {e}")
                self.results["test_results"]["comparison"] = {"error": str(e)}
                test_summary["tests_failed"] += 1
                test_summary["warnings"] += 1
        
        # Run monitoring demonstration
        if self.config["run_monitoring_demo"]:
            print(f"\n{'='*80}")
            print("5. QUALITY MONITORING DEMONSTRATION")
            print(f"{'='*80}")
            
            try:
                monitor = QualityMonitor()
                
                # Start monitoring session
                monitor.start_monitoring({"demo": True, "test_run": self.results["test_run_id"]})
                
                # Simulate monitoring a few responses
                test_queries = [
                    "What is customer research?",
                    "How do I price my services?",
                    "Tell me about the profit playbook"
                ]
                
                print("Simulating quality monitoring...")
                for query in test_queries:
                    # This would normally be called during actual RAG responses
                    print(f"  Monitoring query: {query}")
                    # In real usage, you'd call monitor.monitor_response() here
                
                # Get dashboard data
                dashboard = monitor.get_quality_dashboard()
                
                # Stop monitoring
                monitor.stop_monitoring()
                
                self.results["test_results"]["monitoring_demo"] = {
                    "dashboard": dashboard,
                    "demo_completed": True
                }
                
                test_summary["tests_run"] += 1
                test_summary["tests_passed"] += 1
                print("✅ Monitoring demo: COMPLETED")
                
            except Exception as e:
                print(f"❌ Monitoring demo failed with error: {e}")
                self.results["test_results"]["monitoring_demo"] = {"error": str(e)}
                test_summary["tests_failed"] += 1
        
        # Calculate final results
        total_time = time.time() - start_time
        test_summary["total_time"] = total_time
        test_summary["overall_status"] = self._determine_overall_status(test_summary)
        
        self.results["summary"] = test_summary
        self.results["recommendations"] = self._generate_recommendations()
        
        # Print final summary
        self._print_final_summary()
        
        # Save results
        if self.config["save_results"]:
            self._save_results()
        
        return self.results
    
    def _determine_overall_status(self, test_summary: Dict[str, Any]) -> str:
        """Determine overall test status"""
        if test_summary["critical_issues"] > 0:
            return "CRITICAL_ISSUES"
        elif test_summary["tests_failed"] > test_summary["tests_passed"]:
            return "FAILED"
        elif test_summary["warnings"] > 0:
            return "PASSED_WITH_WARNINGS"
        else:
            return "PASSED"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check comprehensive test results
        comprehensive = self.results["test_results"].get("comprehensive", {})
        if comprehensive.get("overall_metrics", {}).get("ramit_authenticity", 0) < 3.0:
            recommendations.append("Improve Ramit authenticity: Review context-aware prompting configuration")
        
        if comprehensive.get("overall_metrics", {}).get("framework_coherence", 0) < 3.0:
            recommendations.append("Improve framework coherence: Review semantic chunking and framework detection")
        
        # Check multi-turn results
        multi_turn = self.results["test_results"].get("multi_turn", {})
        if multi_turn.get("overall_metrics", {}).get("average_context_retention", 0) < 0.6:
            recommendations.append("Improve context retention: Review conversation memory and context tracking")
        
        # Check regression results
        regression = self.results["test_results"].get("regression", {})
        if regression.get("overall_status") == "FAIL":
            recommendations.append("Address regression issues: Review system performance and functionality")
        
        # Check comparison results
        comparison = self.results["test_results"].get("comparison", {})
        improvement_rate = comparison.get("overall_improvements", {}).get("improvement_rate", 0)
        if improvement_rate < 0.5:
            recommendations.append("Limited improvements detected: Review enhanced features effectiveness")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("System performing well - consider advanced optimizations")
        
        recommendations.append("Continue monitoring quality metrics for ongoing improvements")
        
        return recommendations
    
    def _print_final_summary(self):
        """Print comprehensive final summary"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TESTING SUMMARY")
        print("="*80)
        
        summary = self.results["summary"]
        status_icons = {
            "PASSED": "✅",
            "PASSED_WITH_WARNINGS": "⚠️",
            "FAILED": "❌",
            "CRITICAL_ISSUES": "💥"
        }
        
        icon = status_icons.get(summary["overall_status"], "❓")
        print(f"\n{icon} OVERALL STATUS: {summary['overall_status']}")
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total Tests Run: {summary['tests_run']}")
        print(f"   Tests Passed: {summary['tests_passed']}")
        print(f"   Tests Failed: {summary['tests_failed']}")
        print(f"   Critical Issues: {summary['critical_issues']}")
        print(f"   Warnings: {summary['warnings']}")
        print(f"   Total Time: {summary['total_time']:.1f}s")
        
        # Individual test results
        print(f"\n📋 INDIVIDUAL TEST RESULTS:")
        
        test_results = self.results["test_results"]
        
        for test_name, results in test_results.items():
            if "error" in results:
                print(f"   ❌ {test_name.title()}: ERROR - {results['error']}")
            else:
                # Extract key metrics for each test type
                if test_name == "comprehensive":
                    overall_score = results.get("overall_metrics", {}).get("overall_score", 0)
                    pass_rate = results.get("test_summary", {}).get("overall_pass_rate", 0)
                    print(f"   📋 {test_name.title()}: Quality {overall_score:.2f}/5.0, Pass Rate {pass_rate:.1%}")
                
                elif test_name == "multi_turn":
                    success_rate = results.get("overall_metrics", {}).get("success_rate", 0)
                    context_retention = results.get("overall_metrics", {}).get("average_context_retention", 0)
                    print(f"   💬 {test_name.title()}: Success {success_rate:.1%}, Context {context_retention:.2f}")
                
                elif test_name == "regression":
                    status = results.get("overall_status", "unknown")
                    print(f"   🔄 {test_name.title()}: {status}")
                
                elif test_name == "comparison":
                    improvement_rate = results.get("overall_improvements", {}).get("improvement_rate", 0)
                    avg_improvement = results.get("overall_improvements", {}).get("avg_overall_improvement", 0)
                    print(f"   🔄 {test_name.title()}: {improvement_rate:.1%} improved, Avg +{avg_improvement:.2f}")
                
                elif test_name == "monitoring_demo":
                    print(f"   📊 {test_name.title()}: Demo completed successfully")
        
        # Key insights from comprehensive testing
        comprehensive = test_results.get("comprehensive", {})
        if comprehensive and "overall_metrics" in comprehensive:
            metrics = comprehensive["overall_metrics"]
            print(f"\n🎯 KEY QUALITY METRICS:")
            print(f"   Ramit Authenticity: {metrics.get('ramit_authenticity', 0):.2f}/5.0")
            print(f"   Framework Coherence: {metrics.get('framework_coherence', 0):.2f}/5.0")
            print(f"   Actionability: {metrics.get('actionability', 0):.2f}/5.0")
            print(f"   Coaching Effectiveness: {metrics.get('coaching_effectiveness', 0):.2f}/5.0")
        
        # Comparison insights
        comparison = test_results.get("comparison", {})
        if comparison and "overall_improvements" in comparison:
            improvements = comparison["overall_improvements"]
            print(f"\n📈 ENHANCEMENT IMPACT:")
            print(f"   Queries Improved: {improvements.get('improved_queries', 0)}/{improvements.get('total_queries', 0)}")
            print(f"   Average Quality Gain: {improvements.get('avg_overall_improvement', 0):+.2f}/5.0")
            print(f"   Authenticity Gain: {improvements.get('avg_authenticity_improvement', 0):+.2f}/5.0")
        
        # Recommendations
        if self.results["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📁 Test Run ID: {self.results['test_run_id']}")
        if self.config["save_results"]:
            print(f"   Results saved to: test_results_{self.results['test_run_id']}.json")
    
    def _save_results(self):
        """Save comprehensive test results"""
        filename = f"test_results_{self.results['test_run_id']}.json"
        
        try:
            # Make results JSON serializable
            serializable_results = self._make_serializable(self.results)
            
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            print(f"✅ Comprehensive results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def _make_serializable(self, obj):
        """Make object JSON serializable"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return obj

def main():
    """Main entry point for comprehensive testing"""
    parser = argparse.ArgumentParser(description="Run comprehensive RAG pipeline tests")
    
    # Test selection
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive quality tests")
    parser.add_argument("--multi-turn", action="store_true", help="Run multi-turn conversation tests")
    parser.add_argument("--regression", action="store_true", help="Run regression tests")
    parser.add_argument("--comparison", action="store_true", help="Run before/after comparison")
    parser.add_argument("--monitoring", action="store_true", help="Run monitoring demonstration")
    parser.add_argument("--all", action="store_true", help="Run all test suites")
    
    # Configuration
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to use for testing")
    parser.add_argument("--vector-store", default="./chroma_db", help="Vector store path")
    parser.add_argument("--categories", nargs="+", help="Test categories to run")
    parser.add_argument("--quick", action="store_true", help="Run quick subset of tests")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to file")
    
    args = parser.parse_args()
    
    # Build configuration
    config = {
        "vector_store_path": args.vector_store,
        "model_name": args.model,
        "save_results": not args.no_save
    }
    
    # Determine which tests to run
    if args.all:
        config.update({
            "run_comprehensive": True,
            "run_multi_turn": True,
            "run_regression": True,
            "run_comparison": True,
            "run_monitoring_demo": True
        })
    else:
        config.update({
            "run_comprehensive": args.comprehensive,
            "run_multi_turn": args.multi_turn,
            "run_regression": args.regression,
            "run_comparison": args.comparison,
            "run_monitoring_demo": args.monitoring
        })
        
        # If no specific tests selected, run comprehensive by default
        if not any([args.comprehensive, args.multi_turn, args.regression, 
                   args.comparison, args.monitoring]):
            config["run_comprehensive"] = True
    
    # Configure test categories
    if args.categories:
        config["test_categories"] = args.categories
    elif args.quick:
        config["test_categories"] = ["framework", "tactical"]
    else:
        config["test_categories"] = ["framework", "tactical", "mindset", "contrarian", "first_sale", "pricing"]
    
    # Run tests
    orchestrator = TestOrchestrator(config)
    results = orchestrator.run_all_tests()
    
    # Return appropriate exit code
    status = results["summary"]["overall_status"]
    if status == "CRITICAL_ISSUES":
        sys.exit(2)
    elif status == "FAILED":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()