#!/usr/bin/env python3
"""
Multi-turn conversation testing for the enhanced RAG pipeline.
Tests context retention, conversation flow, and coaching progression.
"""

import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.vector_store import load_vector_store
from src.utils.rag_chain import create_rag_chain, format_response
from test_suite.data.test_queries import TestDataGenerator, TestQuery
from test_suite.metrics.quality_metrics import ResponseQualityAnalyzer, QualityScores

@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    turn_number: int
    query: str
    response: str
    response_time: float
    quality_scores: Optional[QualityScores] = None
    context_retention_score: float = 0.0
    coaching_progression_score: float = 0.0

@dataclass
class ConversationResult:
    """Results from a complete multi-turn conversation"""
    scenario_name: str
    turns: List[ConversationTurn]
    overall_context_retention: float
    coaching_progression: float
    conversation_coherence: float
    total_duration: float
    success: bool

class MultiTurnTester:
    """Tests multi-turn conversation capabilities"""
    
    def __init__(self, vector_store_path: str = "./chroma_db", model_name: str = "gpt-3.5-turbo"):
        self.vector_store_path = vector_store_path
        self.model_name = model_name
        self.quality_analyzer = ResponseQualityAnalyzer()
        
        # Context retention keywords by topic
        self.context_keywords = {
            "customer_research": ["interview", "customer", "research", "insights", "pain points"],
            "winning_offer": ["offer", "package", "solution", "value", "guarantee"],
            "first_sale": ["first client", "first sale", "starting", "beginning"],
            "pricing": ["price", "charge", "rate", "value", "investment"],
            "scaling": ["scale", "grow", "system", "process", "automation"]
        }
        
        # Conversation flow indicators
        self.progression_indicators = {
            "builds_on_previous": ["based on what we discussed", "following up", "now that", "since you"],
            "references_context": ["you mentioned", "as you said", "from your situation", "in your case"],
            "guides_forward": ["next step", "now", "moving forward", "let's", "your next"],
            "maintains_thread": ["this connects to", "building on", "continuing", "following"]
        }
    
    def run_multi_turn_tests(self) -> Dict[str, Any]:
        """Run all multi-turn conversation tests"""
        print("="*80)
        print("MULTI-TURN CONVERSATION TESTING")
        print("="*80)
        
        if not self._initialize_system():
            return {"error": "Failed to initialize system"}
        
        # Get multi-turn scenarios
        scenarios = TestDataGenerator.get_multi_turn_scenarios()
        
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "scenarios_tested": len(scenarios),
            "scenarios_passed": 0,
            "scenarios_failed": 0,
            "scenario_results": [],
            "overall_metrics": {},
            "insights": {}
        }
        
        for i, scenario in enumerate(scenarios):
            scenario_name = f"scenario_{i+1}_{scenario[0].subcategory.split('_')[0]}"
            print(f"\n{'-'*60}")
            print(f"Testing Scenario: {scenario_name}")
            print(f"{'-'*60}")
            
            scenario_result = self._test_conversation_scenario(scenario_name, scenario)
            results["scenario_results"].append(scenario_result)
            
            if scenario_result.success:
                results["scenarios_passed"] += 1
                print(f"✅ Scenario PASSED")
            else:
                results["scenarios_failed"] += 1
                print(f"❌ Scenario FAILED")
        
        # Calculate overall metrics
        results["overall_metrics"] = self._calculate_overall_metrics(results["scenario_results"])
        results["insights"] = self._generate_insights(results["scenario_results"])
        
        self._print_multi_turn_summary(results)
        
        return results
    
    def _initialize_system(self) -> bool:
        """Initialize the RAG system"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            if not os.getenv("OPENAI_API_KEY") or not os.path.exists(self.vector_store_path):
                print("❌ Missing API key or vector store")
                return False
            
            self.vector_store = load_vector_store(self.vector_store_path)
            self.rag_chain = create_rag_chain(
                self.vector_store, 
                self.model_name, 
                use_context_aware_prompting=True
            )
            
            print("✅ Multi-turn testing system initialized")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def _test_conversation_scenario(self, scenario_name: str, queries: List[TestQuery]) -> ConversationResult:
        """Test a complete conversation scenario"""
        print(f"  Running {len(queries)}-turn conversation...")
        
        turns = []
        total_start_time = time.time()
        conversation_context = []
        
        for turn_num, query in enumerate(queries, 1):
            print(f"    Turn {turn_num}: {query.query[:50]}...")
            
            turn_start_time = time.time()
            
            try:
                # Get response
                response = self.rag_chain({"question": query.query})
                turn_duration = time.time() - turn_start_time
                
                if response:
                    formatted_response = format_response(response)
                    response_text = formatted_response["answer"]
                    
                    # Analyze response quality
                    quality_scores = self.quality_analyzer.analyze_response_quality(
                        response_text, query, formatted_response["sources"]
                    )
                    
                    # Analyze context retention
                    context_retention = self._analyze_context_retention(
                        response_text, conversation_context, query
                    )
                    
                    # Analyze coaching progression
                    coaching_progression = self._analyze_coaching_progression(
                        response_text, turn_num, len(queries)
                    )
                    
                    # Create turn result
                    turn = ConversationTurn(
                        turn_number=turn_num,
                        query=query.query,
                        response=response_text,
                        response_time=turn_duration,
                        quality_scores=quality_scores,
                        context_retention_score=context_retention,
                        coaching_progression_score=coaching_progression
                    )
                    
                    turns.append(turn)
                    conversation_context.append({
                        "query": query.query,
                        "response": response_text,
                        "turn": turn_num
                    })
                    
                    print(f"      Quality: {quality_scores.overall_score:.2f}, Context: {context_retention:.2f}, Progression: {coaching_progression:.2f}")
                else:
                    print(f"      ❌ No response received")
                    # Create failed turn
                    turn = ConversationTurn(
                        turn_number=turn_num,
                        query=query.query,
                        response="",
                        response_time=turn_duration
                    )
                    turns.append(turn)
                    
            except Exception as e:
                print(f"      ❌ Turn failed: {e}")
                turn = ConversationTurn(
                    turn_number=turn_num,
                    query=query.query,
                    response="",
                    response_time=time.time() - turn_start_time
                )
                turns.append(turn)
        
        total_duration = time.time() - total_start_time
        
        # Analyze overall conversation
        overall_context_retention = self._calculate_overall_context_retention(turns)
        coaching_progression = self._calculate_overall_coaching_progression(turns)
        conversation_coherence = self._calculate_conversation_coherence(turns)
        
        # Determine success
        success = (
            len([t for t in turns if t.response]) >= len(queries) * 0.8 and  # 80% responses received
            overall_context_retention >= 0.6 and  # Good context retention
            coaching_progression >= 0.5  # Decent progression
        )
        
        return ConversationResult(
            scenario_name=scenario_name,
            turns=turns,
            overall_context_retention=overall_context_retention,
            coaching_progression=coaching_progression,
            conversation_coherence=conversation_coherence,
            total_duration=total_duration,
            success=success
        )
    
    def _analyze_context_retention(
        self, 
        response: str, 
        conversation_context: List[Dict[str, Any]], 
        current_query: TestQuery
    ) -> float:
        """Analyze how well the response retains context from previous turns"""
        if not conversation_context:
            return 1.0  # First turn, perfect context retention
        
        response_lower = response.lower()
        context_score = 0.0
        
        # Check for direct references to previous conversation
        reference_indicators = self.progression_indicators["references_context"]
        references_found = sum(1 for indicator in reference_indicators if indicator in response_lower)
        
        # Check for topic continuity
        if current_query.multi_turn_context:
            # Look for keywords from previous topics
            previous_topics = set()
            for prev_context in current_query.multi_turn_context:
                prev_lower = prev_context.lower()
                for topic, keywords in self.context_keywords.items():
                    if any(keyword in prev_lower for keyword in keywords):
                        previous_topics.add(topic)
            
            # Check if current response maintains topic relevance
            topic_continuity = 0
            for topic in previous_topics:
                keywords = self.context_keywords[topic]
                if any(keyword in response_lower for keyword in keywords):
                    topic_continuity += 1
            
            if previous_topics:
                topic_score = topic_continuity / len(previous_topics)
            else:
                topic_score = 0.5
        else:
            topic_score = 0.5
        
        # Check for conversation flow indicators
        flow_indicators = (
            self.progression_indicators["builds_on_previous"] +
            self.progression_indicators["maintains_thread"]
        )
        flow_score = min(1.0, sum(1 for indicator in flow_indicators if indicator in response_lower) * 0.3)
        
        # Combine scores
        context_score = (
            min(1.0, references_found * 0.4) * 0.4 +  # Direct references
            topic_score * 0.4 +  # Topic continuity
            flow_score * 0.2  # Conversation flow
        )
        
        return context_score
    
    def _analyze_coaching_progression(self, response: str, turn_num: int, total_turns: int) -> float:
        """Analyze how well the response moves the coaching forward"""
        response_lower = response.lower()
        progression_score = 0.0
        
        # Check for forward-guiding language
        forward_indicators = self.progression_indicators["guides_forward"]
        forward_count = sum(1 for indicator in forward_indicators if indicator in response_lower)
        
        # Check for questions that push thinking
        question_patterns = ["what if", "have you considered", "how might", "why do you think"]
        thinking_questions = sum(1 for pattern in question_patterns if pattern in response_lower)
        
        # Check for actionable next steps
        action_indicators = ["try this", "start by", "your next step", "do this", "implement"]
        action_count = sum(1 for indicator in action_indicators if indicator in response_lower)
        
        # Check for building complexity appropriately
        complexity_indicators = ["now that", "building on", "next level", "advanced"]
        complexity_appropriate = 0
        if turn_num > 1:  # Later turns should build complexity
            complexity_appropriate = sum(1 for indicator in complexity_indicators if indicator in response_lower)
        
        # Calculate progression score based on turn position
        base_score = (
            min(1.0, forward_count * 0.3) * 0.3 +
            min(1.0, thinking_questions * 0.4) * 0.3 +
            min(1.0, action_count * 0.2) * 0.2 +
            min(1.0, complexity_appropriate * 0.3) * 0.2
        )
        
        # Adjust for turn position
        if turn_num == 1:
            # First turn should establish foundation
            progression_score = base_score
        elif turn_num == total_turns:
            # Last turn should provide clear next steps
            progression_score = base_score * 1.2 if action_count > 0 else base_score * 0.8
        else:
            # Middle turns should build and connect
            progression_score = base_score * 1.1 if forward_count > 0 else base_score * 0.9
        
        return min(1.0, progression_score)
    
    def _calculate_overall_context_retention(self, turns: List[ConversationTurn]) -> float:
        """Calculate overall context retention across all turns"""
        if not turns:
            return 0.0
        
        retention_scores = [turn.context_retention_score for turn in turns if turn.context_retention_score > 0]
        
        if not retention_scores:
            return 0.0
        
        # Weight later turns more heavily (they require more context)
        weighted_scores = []
        for i, score in enumerate(retention_scores):
            weight = 1 + (i * 0.2)  # Increasing weight for later turns
            weighted_scores.append(score * weight)
        
        total_weight = sum(1 + (i * 0.2) for i in range(len(retention_scores)))
        
        return sum(weighted_scores) / total_weight
    
    def _calculate_overall_coaching_progression(self, turns: List[ConversationTurn]) -> float:
        """Calculate overall coaching progression across conversation"""
        if not turns:
            return 0.0
        
        progression_scores = [turn.coaching_progression_score for turn in turns if turn.coaching_progression_score > 0]
        
        if not progression_scores:
            return 0.0
        
        return sum(progression_scores) / len(progression_scores)
    
    def _calculate_conversation_coherence(self, turns: List[ConversationTurn]) -> float:
        """Calculate overall conversation coherence"""
        if len(turns) < 2:
            return 1.0
        
        coherence_factors = []
        
        # Check response quality consistency
        quality_scores = [turn.quality_scores.overall_score for turn in turns if turn.quality_scores]
        if quality_scores:
            quality_variance = max(quality_scores) - min(quality_scores)
            quality_consistency = max(0, 1 - (quality_variance / 5))  # Lower variance = higher consistency
            coherence_factors.append(quality_consistency)
        
        # Check response time consistency
        response_times = [turn.response_time for turn in turns if turn.response_time > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            time_variance = sum(abs(t - avg_time) for t in response_times) / len(response_times)
            time_consistency = max(0, 1 - (time_variance / avg_time))
            coherence_factors.append(time_consistency)
        
        # Check thematic consistency
        all_responses = " ".join(turn.response for turn in turns if turn.response)
        thematic_consistency = self._calculate_thematic_consistency(all_responses)
        coherence_factors.append(thematic_consistency)
        
        return sum(coherence_factors) / len(coherence_factors) if coherence_factors else 0.0
    
    def _calculate_thematic_consistency(self, all_responses: str) -> float:
        """Calculate thematic consistency across responses"""
        response_lower = all_responses.lower()
        
        # Count framework terms
        framework_mentions = {}
        for framework, keywords in self.context_keywords.items():
            count = sum(1 for keyword in keywords if keyword in response_lower)
            if count > 0:
                framework_mentions[framework] = count
        
        # Consistency = focused on related themes vs scattered
        if len(framework_mentions) <= 2:
            return 1.0  # Highly focused
        elif len(framework_mentions) <= 4:
            return 0.7  # Moderately focused
        else:
            return 0.4  # Scattered
    
    def _calculate_overall_metrics(self, scenario_results: List[ConversationResult]) -> Dict[str, float]:
        """Calculate overall multi-turn metrics"""
        if not scenario_results:
            return {}
        
        return {
            "average_context_retention": sum(r.overall_context_retention for r in scenario_results) / len(scenario_results),
            "average_coaching_progression": sum(r.coaching_progression for r in scenario_results) / len(scenario_results),
            "average_conversation_coherence": sum(r.conversation_coherence for r in scenario_results) / len(scenario_results),
            "average_scenario_duration": sum(r.total_duration for r in scenario_results) / len(scenario_results),
            "success_rate": sum(1 for r in scenario_results if r.success) / len(scenario_results)
        }
    
    def _generate_insights(self, scenario_results: List[ConversationResult]) -> Dict[str, Any]:
        """Generate insights from multi-turn testing"""
        insights = {
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        if not scenario_results:
            return insights
        
        # Analyze context retention patterns
        context_scores = [r.overall_context_retention for r in scenario_results]
        avg_context = sum(context_scores) / len(context_scores)
        
        if avg_context >= 0.8:
            insights["strengths"].append("Excellent context retention across conversations")
        elif avg_context >= 0.6:
            insights["strengths"].append("Good context retention")
        else:
            insights["weaknesses"].append("Poor context retention - loses track of conversation history")
            insights["recommendations"].append("Improve conversation memory and context tracking")
        
        # Analyze coaching progression
        progression_scores = [r.coaching_progression for r in scenario_results]
        avg_progression = sum(progression_scores) / len(progression_scores)
        
        if avg_progression >= 0.7:
            insights["strengths"].append("Strong coaching progression - guides users forward effectively")
        elif avg_progression >= 0.5:
            insights["strengths"].append("Adequate coaching progression")
        else:
            insights["weaknesses"].append("Weak coaching progression - doesn't effectively guide users forward")
            insights["recommendations"].append("Improve forward-guiding language and next steps provision")
        
        # Analyze conversation coherence
        coherence_scores = [r.conversation_coherence for r in scenario_results]
        avg_coherence = sum(coherence_scores) / len(coherence_scores)
        
        if avg_coherence >= 0.8:
            insights["strengths"].append("High conversation coherence and consistency")
        elif avg_coherence < 0.6:
            insights["weaknesses"].append("Inconsistent conversation quality")
            insights["recommendations"].append("Improve response consistency and thematic focus")
        
        return insights
    
    def _print_multi_turn_summary(self, results: Dict[str, Any]):
        """Print multi-turn testing summary"""
        print("\n" + "="*80)
        print("MULTI-TURN CONVERSATION TEST SUMMARY")
        print("="*80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Scenarios Tested: {results['scenarios_tested']}")
        print(f"   Scenarios Passed: {results['scenarios_passed']}")
        print(f"   Success Rate: {results['scenarios_passed']/results['scenarios_tested']:.1%}")
        
        if results["overall_metrics"]:
            metrics = results["overall_metrics"]
            print(f"\n📈 MULTI-TURN METRICS:")
            print(f"   Context Retention: {metrics['average_context_retention']:.2f}/1.0")
            print(f"   Coaching Progression: {metrics['average_coaching_progression']:.2f}/1.0")
            print(f"   Conversation Coherence: {metrics['average_conversation_coherence']:.2f}/1.0")
            print(f"   Average Duration: {metrics['average_scenario_duration']:.1f}s")
        
        if results["insights"]:
            insights = results["insights"]
            
            if insights["strengths"]:
                print(f"\n✅ STRENGTHS:")
                for strength in insights["strengths"]:
                    print(f"   • {strength}")
            
            if insights["weaknesses"]:
                print(f"\n⚠️  WEAKNESSES:")
                for weakness in insights["weaknesses"]:
                    print(f"   • {weakness}")
            
            if insights["recommendations"]:
                print(f"\n💡 RECOMMENDATIONS:")
                for rec in insights["recommendations"]:
                    print(f"   • {rec}")

def run_multi_turn_tests():
    """Run multi-turn conversation tests"""
    tester = MultiTurnTester()
    return tester.run_multi_turn_tests()

if __name__ == "__main__":
    run_multi_turn_tests()