#!/usr/bin/env python3
"""
Before/After comparison system for the enhanced RAG pipeline.
Compares standard RAG vs. Ramit-enhanced RAG responses to show improvements.
"""

import os
import sys
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.vector_store import load_vector_store
from src.utils.rag_chain import create_rag_chain, format_response
from test_suite.data.test_queries import TestDataGenerator, TestQuery
from test_suite.metrics.quality_metrics import ResponseQualityAnalyzer, QualityScores

@dataclass
class ComparisonResult:
    """Results from comparing before/after responses"""
    query: str
    category: str
    
    # Standard RAG (before)
    standard_response: str
    standard_scores: QualityScores
    standard_response_time: float
    standard_sources_count: int
    
    # Enhanced RAG (after)
    enhanced_response: str
    enhanced_scores: QualityScores
    enhanced_response_time: float
    enhanced_sources_count: int
    
    # Improvements
    quality_improvement: float
    authenticity_improvement: float
    actionability_improvement: float
    overall_improvement: float
    
    # Analysis
    key_differences: List[str]
    ramit_elements_added: List[str]
    improvement_summary: str

class BeforeAfterComparer:
    """Compares standard vs enhanced RAG responses"""
    
    def __init__(self, vector_store_path: str = "./chroma_db", model_name: str = "gpt-3.5-turbo"):
        self.vector_store_path = vector_store_path
        self.model_name = model_name
        self.quality_analyzer = ResponseQualityAnalyzer()
        
        # Comparison criteria
        self.comparison_criteria = {
            "ramit_authenticity": "How well response captures Ramit's voice and style",
            "framework_coherence": "How well response represents Ramit's frameworks",
            "actionability": "How actionable and implementable the guidance is",
            "coaching_effectiveness": "How effectively response guides user forward",
            "source_accuracy": "How well response is supported by sources"
        }
        
        # Results storage
        self.results = {
            "test_run_id": f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "queries_compared": 0,
            "overall_improvements": {},
            "category_improvements": {},
            "detailed_comparisons": [],
            "summary_insights": {}
        }
    
    def run_before_after_comparison(self, test_categories: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive before/after comparison"""
        print("="*80)
        print("BEFORE/AFTER COMPARISON ANALYSIS")
        print("="*80)
        
        if not self._initialize_systems():
            return {"error": "Failed to initialize systems"}
        
        # Get test queries
        all_queries = TestDataGenerator.get_all_test_queries()
        if test_categories:
            all_queries = {k: v for k, v in all_queries.items() if k in test_categories}
        
        print(f"\nComparing responses across categories: {list(all_queries.keys())}")
        
        # Run comparisons
        comparison_results = []
        
        for category, queries in all_queries.items():
            print(f"\n{'-'*60}")
            print(f"Comparing Category: {category.upper()}")
            print(f"{'-'*60}")
            
            category_results = []
            
            for i, query in enumerate(queries[:3]):  # Test first 3 queries per category
                print(f"  Query {i+1}: {query.query[:50]}...")
                
                comparison = self._compare_query_responses(query)
                if comparison:
                    comparison_results.append(comparison)
                    category_results.append(comparison)
                    
                    # Print quick comparison
                    improvement = comparison.overall_improvement
                    status = "✅" if improvement > 0.5 else "⚠️" if improvement > 0 else "❌"
                    print(f"    {status} Overall improvement: {improvement:+.2f} points")
            
            # Calculate category averages
            if category_results:
                self.results["category_improvements"][category] = self._calculate_category_improvements(category_results)
        
        self.results["detailed_comparisons"] = [asdict(r) for r in comparison_results]
        self.results["queries_compared"] = len(comparison_results)
        
        # Calculate overall improvements
        self.results["overall_improvements"] = self._calculate_overall_improvements(comparison_results)
        
        # Generate insights
        self.results["summary_insights"] = self._generate_comparison_insights(comparison_results)
        
        # Print summary
        self._print_comparison_summary()
        
        # Save results
        self._save_comparison_results()
        
        return self.results
    
    def _initialize_systems(self) -> bool:
        """Initialize both standard and enhanced RAG systems"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            if not os.getenv("OPENAI_API_KEY"):
                print("❌ OPENAI_API_KEY not found")
                return False
            
            if not os.path.exists(self.vector_store_path):
                print(f"❌ Vector store not found")
                return False
            
            # Load vector store
            print("Loading vector store...")
            self.vector_store = load_vector_store(self.vector_store_path)
            
            # Create both RAG chains
            print("Initializing standard RAG chain...")
            self.standard_rag = create_rag_chain(
                self.vector_store, 
                self.model_name, 
                use_context_aware_prompting=False
            )
            
            print("Initializing enhanced RAG chain...")
            self.enhanced_rag = create_rag_chain(
                self.vector_store, 
                self.model_name, 
                use_context_aware_prompting=True
            )
            
            print("✅ Both systems initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def _compare_query_responses(self, query: TestQuery) -> Optional[ComparisonResult]:
        """Compare responses from standard vs enhanced RAG for a single query"""
        try:
            # Get standard RAG response
            standard_start = time.time()
            standard_response = self.standard_rag({"question": query.query})
            standard_time = time.time() - standard_start
            
            # Get enhanced RAG response
            enhanced_start = time.time()
            enhanced_response = self.enhanced_rag({"question": query.query})
            enhanced_time = time.time() - enhanced_start
            
            if not standard_response or not enhanced_response:
                print(f"    ❌ Failed to get responses")
                return None
            
            # Format responses
            standard_formatted = format_response(standard_response)
            enhanced_formatted = format_response(enhanced_response)
            
            # Analyze quality
            standard_scores = self.quality_analyzer.analyze_response_quality(
                standard_formatted["answer"], query, standard_formatted["sources"]
            )
            
            enhanced_scores = self.quality_analyzer.analyze_response_quality(
                enhanced_formatted["answer"], query, enhanced_formatted["sources"]
            )
            
            # Calculate improvements
            quality_improvement = enhanced_scores.overall_score - standard_scores.overall_score
            authenticity_improvement = enhanced_scores.ramit_authenticity - standard_scores.ramit_authenticity
            actionability_improvement = enhanced_scores.actionability - standard_scores.actionability
            overall_improvement = quality_improvement
            
            # Analyze key differences
            key_differences = self._analyze_response_differences(
                standard_formatted["answer"], 
                enhanced_formatted["answer"]
            )
            
            # Identify Ramit elements added
            ramit_elements = self._identify_ramit_elements_added(
                standard_formatted["answer"], 
                enhanced_formatted["answer"]
            )
            
            # Generate improvement summary
            improvement_summary = self._generate_improvement_summary(
                quality_improvement, authenticity_improvement, actionability_improvement
            )
            
            return ComparisonResult(
                query=query.query,
                category=query.category,
                standard_response=standard_formatted["answer"],
                standard_scores=standard_scores,
                standard_response_time=standard_time,
                standard_sources_count=len(standard_formatted["sources"]),
                enhanced_response=enhanced_formatted["answer"],
                enhanced_scores=enhanced_scores,
                enhanced_response_time=enhanced_time,
                enhanced_sources_count=len(enhanced_formatted["sources"]),
                quality_improvement=quality_improvement,
                authenticity_improvement=authenticity_improvement,
                actionability_improvement=actionability_improvement,
                overall_improvement=overall_improvement,
                key_differences=key_differences,
                ramit_elements_added=ramit_elements,
                improvement_summary=improvement_summary
            )
            
        except Exception as e:
            print(f"    ❌ Comparison failed: {e}")
            return None
    
    def _analyze_response_differences(self, standard: str, enhanced: str) -> List[str]:
        """Analyze key differences between standard and enhanced responses"""
        differences = []
        
        standard_lower = standard.lower()
        enhanced_lower = enhanced.lower()
        
        # Check for length differences
        length_diff = len(enhanced) - len(standard)
        if abs(length_diff) > 100:
            differences.append(f"Length difference: {length_diff:+d} characters")
        
        # Check for framework mentions
        framework_terms = ["framework", "system", "process", "methodology"]
        standard_frameworks = sum(1 for term in framework_terms if term in standard_lower)
        enhanced_frameworks = sum(1 for term in framework_terms if term in enhanced_lower)
        
        if enhanced_frameworks > standard_frameworks:
            differences.append(f"More framework terminology: +{enhanced_frameworks - standard_frameworks}")
        
        # Check for tactical language
        tactical_terms = ["step", "exactly", "specific", "here's how", "do this"]
        standard_tactical = sum(1 for term in tactical_terms if term in standard_lower)
        enhanced_tactical = sum(1 for term in tactical_terms if term in enhanced_lower)
        
        if enhanced_tactical > standard_tactical:
            differences.append(f"More tactical language: +{enhanced_tactical - standard_tactical}")
        
        # Check for contrarian elements
        contrarian_terms = ["wrong", "backwards", "conventional wisdom", "everyone says"]
        standard_contrarian = sum(1 for term in contrarian_terms if term in standard_lower)
        enhanced_contrarian = sum(1 for term in contrarian_terms if term in enhanced_lower)
        
        if enhanced_contrarian > standard_contrarian:
            differences.append(f"More contrarian elements: +{enhanced_contrarian - standard_contrarian}")
        
        # Check for personal coaching language
        coaching_terms = ["you", "your", "let me", "here's what", "i'll"]
        standard_coaching = sum(1 for term in coaching_terms if term in standard_lower)
        enhanced_coaching = sum(1 for term in coaching_terms if term in enhanced_lower)
        
        if enhanced_coaching > standard_coaching:
            differences.append(f"More personal coaching language: +{enhanced_coaching - standard_coaching}")
        
        return differences
    
    def _identify_ramit_elements_added(self, standard: str, enhanced: str) -> List[str]:
        """Identify Ramit-specific elements added in enhanced response"""
        ramit_elements = []
        
        enhanced_lower = enhanced.lower()
        standard_lower = standard.lower()
        
        # Check for signature phrases
        ramit_signatures = [
            "business isn't magic. it's math",
            "systems beat goals",
            "start before you're ready",
            "test everything",
            "focus on your first paying customer"
        ]
        
        for signature in ramit_signatures:
            if signature in enhanced_lower and signature not in standard_lower:
                ramit_elements.append(f"Signature phrase: '{signature}'")
        
        # Check for framework references
        ramit_frameworks = [
            "customer research", "winning offer", "authentic selling", 
            "profit playbook", "mind reading"
        ]
        
        for framework in ramit_frameworks:
            if framework in enhanced_lower and framework not in standard_lower:
                ramit_elements.append(f"Framework reference: '{framework}'")
        
        # Check for contrarian openers
        contrarian_openers = [
            "here's where most people get this wrong",
            "conventional wisdom says",
            "everyone tells you to"
        ]
        
        for opener in contrarian_openers:
            if opener in enhanced_lower and opener not in standard_lower:
                ramit_elements.append(f"Contrarian opener: '{opener}'")
        
        # Check for tactical language
        tactical_phrases = [
            "here's exactly what to do",
            "use this exact script",
            "copy and paste this"
        ]
        
        for phrase in tactical_phrases:
            if phrase in enhanced_lower and phrase not in standard_lower:
                ramit_elements.append(f"Tactical language: '{phrase}'")
        
        return ramit_elements
    
    def _generate_improvement_summary(self, quality: float, authenticity: float, actionability: float) -> str:
        """Generate a summary of improvements"""
        improvements = []
        
        if quality > 0.5:
            improvements.append("significant quality improvement")
        elif quality > 0:
            improvements.append("quality improvement")
        
        if authenticity > 1.0:
            improvements.append("much more authentic Ramit voice")
        elif authenticity > 0.5:
            improvements.append("more authentic Ramit voice")
        
        if actionability > 0.5:
            improvements.append("significantly more actionable")
        elif actionability > 0:
            improvements.append("more actionable")
        
        if not improvements:
            if quality < -0.5:
                return "Quality regression detected"
            else:
                return "Minimal improvement"
        
        return ", ".join(improvements).capitalize()
    
    def _calculate_category_improvements(self, category_results: List[ComparisonResult]) -> Dict[str, float]:
        """Calculate average improvements for a category"""
        if not category_results:
            return {}
        
        return {
            "avg_quality_improvement": sum(r.quality_improvement for r in category_results) / len(category_results),
            "avg_authenticity_improvement": sum(r.authenticity_improvement for r in category_results) / len(category_results),
            "avg_actionability_improvement": sum(r.actionability_improvement for r in category_results) / len(category_results),
            "avg_overall_improvement": sum(r.overall_improvement for r in category_results) / len(category_results),
            "improvement_rate": sum(1 for r in category_results if r.overall_improvement > 0) / len(category_results),
            "queries_compared": len(category_results)
        }
    
    def _calculate_overall_improvements(self, all_results: List[ComparisonResult]) -> Dict[str, float]:
        """Calculate overall improvements across all queries"""
        if not all_results:
            return {}
        
        # Overall averages
        overall_stats = {
            "total_queries": len(all_results),
            "improved_queries": sum(1 for r in all_results if r.overall_improvement > 0),
            "degraded_queries": sum(1 for r in all_results if r.overall_improvement < -0.2),
            "improvement_rate": sum(1 for r in all_results if r.overall_improvement > 0) / len(all_results),
            
            # Average improvements
            "avg_quality_improvement": sum(r.quality_improvement for r in all_results) / len(all_results),
            "avg_authenticity_improvement": sum(r.authenticity_improvement for r in all_results) / len(all_results),
            "avg_actionability_improvement": sum(r.actionability_improvement for r in all_results) / len(all_results),
            "avg_overall_improvement": sum(r.overall_improvement for r in all_results) / len(all_results),
            
            # Performance comparison
            "avg_standard_response_time": sum(r.standard_response_time for r in all_results) / len(all_results),
            "avg_enhanced_response_time": sum(r.enhanced_response_time for r in all_results) / len(all_results),
        }
        
        # Calculate standard deviations
        mean_improvement = overall_stats["avg_overall_improvement"]
        variance = sum((r.overall_improvement - mean_improvement) ** 2 for r in all_results) / len(all_results)
        overall_stats["improvement_std_dev"] = variance ** 0.5
        overall_stats["improvement_consistency"] = 1 - (overall_stats["improvement_std_dev"] / 5)  # Normalize to 0-1
        
        return overall_stats
    
    def _generate_comparison_insights(self, all_results: List[ComparisonResult]) -> Dict[str, Any]:
        """Generate insights from the comparison"""
        insights = {
            "top_improvements": [],
            "areas_of_concern": [],
            "ramit_authenticity_gains": [],
            "tactical_improvements": [],
            "framework_usage": []
        }
        
        if not all_results:
            return insights
        
        # Find top improvements
        top_improved = sorted(all_results, key=lambda x: x.overall_improvement, reverse=True)[:3]
        insights["top_improvements"] = [
            {
                "query": r.query[:60] + "...",
                "category": r.category,
                "improvement": r.overall_improvement,
                "summary": r.improvement_summary
            }
            for r in top_improved
        ]
        
        # Find concerning regressions
        concerning = [r for r in all_results if r.overall_improvement < -0.2]
        insights["areas_of_concern"] = [
            {
                "query": r.query[:60] + "...",
                "category": r.category,
                "regression": r.overall_improvement,
                "issues": r.key_differences
            }
            for r in concerning
        ]
        
        # Analyze authenticity gains
        high_auth_gains = [r for r in all_results if r.authenticity_improvement > 1.0]
        insights["ramit_authenticity_gains"] = [
            {
                "query": r.query[:60] + "...",
                "authenticity_gain": r.authenticity_improvement,
                "ramit_elements": r.ramit_elements_added
            }
            for r in high_auth_gains
        ]
        
        # Analyze tactical improvements
        tactical_improvements = [r for r in all_results if r.actionability_improvement > 0.5]
        insights["tactical_improvements"] = len(tactical_improvements)
        
        # Framework usage analysis
        framework_mentions = {}
        for result in all_results:
            for element in result.ramit_elements_added:
                if "framework reference" in element.lower():
                    framework = element.split("'")[1]
                    framework_mentions[framework] = framework_mentions.get(framework, 0) + 1
        
        insights["framework_usage"] = sorted(framework_mentions.items(), key=lambda x: x[1], reverse=True)
        
        return insights
    
    def _save_comparison_results(self):
        """Save comparison results to file"""
        filename = f"comparison_results_{self.results['test_run_id']}.json"
        
        try:
            # Make results JSON serializable
            serializable_results = self._make_serializable(self.results)
            
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            print(f"\n💾 Comparison results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save comparison results: {e}")
    
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
    
    def _print_comparison_summary(self):
        """Print comprehensive comparison summary"""
        print("\n" + "="*80)
        print("BEFORE/AFTER COMPARISON SUMMARY")
        print("="*80)
        
        overall = self.results.get("overall_improvements", {})
        
        if overall:
            print(f"\n📊 OVERALL IMPROVEMENTS:")
            print(f"   Queries Compared: {overall['total_queries']}")
            print(f"   Queries Improved: {overall['improved_queries']}")
            print(f"   Improvement Rate: {overall['improvement_rate']:.1%}")
            print(f"   Average Quality Gain: {overall['avg_quality_improvement']:+.2f}/5.0")
            print(f"   Average Authenticity Gain: {overall['avg_authenticity_improvement']:+.2f}/5.0")
            print(f"   Average Actionability Gain: {overall['avg_actionability_improvement']:+.2f}/5.0")
            print(f"   Overall Improvement: {overall['avg_overall_improvement']:+.2f}/5.0")
        
        # Category breakdown
        if self.results.get("category_improvements"):
            print(f"\n📂 CATEGORY BREAKDOWN:")
            for category, improvements in self.results["category_improvements"].items():
                improvement = improvements["avg_overall_improvement"]
                rate = improvements["improvement_rate"]
                status = "✅" if improvement > 0.5 else "⚠️" if improvement > 0 else "❌"
                print(f"   {status} {category.capitalize()}: {improvement:+.2f} ({rate:.1%} improved)")
        
        # Performance comparison
        if overall:
            std_time = overall.get("avg_standard_response_time", 0)
            enh_time = overall.get("avg_enhanced_response_time", 0)
            if std_time > 0 and enh_time > 0:
                time_diff = enh_time - std_time
                print(f"\n⚡ PERFORMANCE IMPACT:")
                print(f"   Standard RAG: {std_time:.2f}s average")
                print(f"   Enhanced RAG: {enh_time:.2f}s average")
                print(f"   Time Difference: {time_diff:+.2f}s ({(time_diff/std_time)*100:+.1f}%)")
        
        # Top insights
        insights = self.results.get("summary_insights", {})
        
        if insights.get("top_improvements"):
            print(f"\n🏆 TOP IMPROVEMENTS:")
            for improvement in insights["top_improvements"][:3]:
                print(f"   • {improvement['category']}: {improvement['improvement']:+.2f} - {improvement['summary']}")
        
        if insights.get("areas_of_concern"):
            print(f"\n⚠️  AREAS OF CONCERN:")
            for concern in insights["areas_of_concern"][:2]:
                print(f"   • {concern['category']}: {concern['regression']:+.2f} regression")
        
        if insights.get("ramit_authenticity_gains"):
            ramit_count = len(insights["ramit_authenticity_gains"])
            print(f"\n🎯 RAMIT AUTHENTICITY:")
            print(f"   {ramit_count} queries showed significant authenticity gains")
        
        if insights.get("framework_usage"):
            print(f"\n🎯 FRAMEWORK USAGE:")
            for framework, count in insights["framework_usage"][:3]:
                print(f"   • {framework}: mentioned {count} times")

def run_before_after_comparison(categories: List[str] = None):
    """Run before/after comparison"""
    comparer = BeforeAfterComparer()
    return comparer.run_before_after_comparison(categories)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run before/after comparison")
    parser.add_argument("--categories", nargs="+", help="Categories to test")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to use")
    
    args = parser.parse_args()
    
    run_before_after_comparison(args.categories)