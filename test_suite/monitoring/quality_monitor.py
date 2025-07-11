#!/usr/bin/env python3
"""
Quality monitoring and feedback system for ongoing RAG pipeline assessment.
Provides continuous quality tracking, automated scoring, and feedback collection.
"""

import os
import sys
import json
import time
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
from queue import Queue, Empty

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_suite.metrics.quality_metrics import ResponseQualityAnalyzer, QualityScores
from test_suite.data.test_queries import TestQuery

@dataclass
class QualityAlert:
    """Represents a quality alert"""
    timestamp: str
    alert_type: str  # "degradation", "improvement", "anomaly"
    severity: str  # "low", "medium", "high", "critical"
    metric: str
    current_value: float
    threshold_value: float
    description: str
    recommendations: List[str]

@dataclass
class ResponseRecord:
    """Record of a response for monitoring"""
    timestamp: str
    query: str
    response: str
    response_time: float
    quality_scores: QualityScores
    user_feedback: Optional[Dict[str, Any]] = None
    system_metadata: Optional[Dict[str, Any]] = None

class QualityMonitor:
    """Continuous quality monitoring system"""
    
    def __init__(self, db_path: str = "./quality_monitoring.db"):
        self.db_path = db_path
        self.quality_analyzer = ResponseQualityAnalyzer()
        
        # Quality thresholds for alerts
        self.quality_thresholds = {
            "ramit_authenticity": {"warning": 2.5, "critical": 2.0},
            "framework_coherence": {"warning": 2.5, "critical": 2.0},
            "actionability": {"warning": 2.5, "critical": 2.0},
            "overall_score": {"warning": 2.5, "critical": 2.0},
            "response_time": {"warning": 10.0, "critical": 20.0}
        }
        
        # Monitoring configuration
        self.monitoring_config = {
            "enabled": True,
            "alert_window_hours": 24,
            "min_samples_for_alert": 5,
            "trend_analysis_days": 7,
            "auto_feedback_sampling_rate": 0.1  # 10% of responses
        }
        
        # Initialize database
        self._init_database()
        
        # Monitoring state
        self.monitoring_active = False
        self.alert_queue = Queue()
        self.feedback_callbacks = []
    
    def _init_database(self):
        """Initialize SQLite database for monitoring data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    ramit_authenticity REAL NOT NULL,
                    framework_coherence REAL NOT NULL,
                    actionability REAL NOT NULL,
                    source_accuracy REAL NOT NULL,
                    coaching_effectiveness REAL NOT NULL,
                    overall_score REAL NOT NULL,
                    user_feedback_rating INTEGER,
                    user_feedback_comments TEXT,
                    system_metadata TEXT
                )
            """)
            
            # Quality alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    threshold_value REAL NOT NULL,
                    description TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Monitoring sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    responses_monitored INTEGER DEFAULT 0,
                    alerts_generated INTEGER DEFAULT 0,
                    average_quality REAL,
                    session_metadata TEXT
                )
            """)
            
            conn.commit()
    
    def start_monitoring(self, session_metadata: Dict[str, Any] = None):
        """Start a monitoring session"""
        if self.monitoring_active:
            print("⚠️  Monitoring already active")
            return
        
        self.monitoring_active = True
        self.session_start_time = datetime.now().isoformat()
        
        # Record session start
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO monitoring_sessions (start_time, session_metadata)
                VALUES (?, ?)
            """, (self.session_start_time, json.dumps(session_metadata or {})))
            self.session_id = cursor.lastrowid
            conn.commit()
        
        print(f"✅ Quality monitoring started (Session ID: {self.session_id})")
    
    def stop_monitoring(self):
        """Stop the monitoring session"""
        if not self.monitoring_active:
            print("⚠️  Monitoring not active")
            return
        
        self.monitoring_active = False
        end_time = datetime.now().isoformat()
        
        # Calculate session statistics
        stats = self._calculate_session_stats()
        
        # Update session record
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE monitoring_sessions 
                SET end_time = ?, responses_monitored = ?, alerts_generated = ?, average_quality = ?
                WHERE id = ?
            """, (end_time, stats["responses_monitored"], stats["alerts_generated"], 
                  stats["average_quality"], self.session_id))
            conn.commit()
        
        print(f"✅ Quality monitoring stopped")
        print(f"   Session Duration: {stats['duration']}")
        print(f"   Responses Monitored: {stats['responses_monitored']}")
        print(f"   Alerts Generated: {stats['alerts_generated']}")
        print(f"   Average Quality: {stats['average_quality']:.2f}/5.0")
    
    def monitor_response(
        self, 
        query: str, 
        response: str, 
        response_time: float,
        sources: List[Dict[str, Any]] = None,
        user_feedback: Dict[str, Any] = None,
        system_metadata: Dict[str, Any] = None
    ) -> QualityScores:
        """Monitor a single response and return quality scores"""
        
        if not self.monitoring_active:
            print("⚠️  Monitoring not active - call start_monitoring() first")
            return None
        
        # Analyze response quality
        test_query = TestQuery(
            query=query,
            category="monitoring",
            subcategory="live",
            expected_intent="general",
            expected_coaching_style="direct_teaching",
            ramit_keywords=[],
            framework_expectations=[],
            should_be_contrarian=False,
            should_be_tactical=False,
            complexity_level="basic"
        )
        
        quality_scores = self.quality_analyzer.analyze_response_quality(
            response, test_query, sources
        )
        
        # Record response
        self._record_response(
            query, response, response_time, quality_scores, 
            user_feedback, system_metadata
        )
        
        # Check for quality alerts
        self._check_quality_alerts(quality_scores, response_time)
        
        # Trigger automatic feedback collection if configured
        if self.monitoring_config["auto_feedback_sampling_rate"] > 0:
            if hash(query) % 100 < self.monitoring_config["auto_feedback_sampling_rate"] * 100:
                self._trigger_auto_feedback_collection(query, response, quality_scores)
        
        return quality_scores
    
    def _record_response(
        self, 
        query: str, 
        response: str, 
        response_time: float,
        quality_scores: QualityScores,
        user_feedback: Dict[str, Any] = None,
        system_metadata: Dict[str, Any] = None
    ):
        """Record response in database"""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO responses (
                    timestamp, query, response, response_time,
                    ramit_authenticity, framework_coherence, actionability,
                    source_accuracy, coaching_effectiveness, overall_score,
                    user_feedback_rating, user_feedback_comments, system_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, query, response, response_time,
                quality_scores.ramit_authenticity,
                quality_scores.framework_coherence,
                quality_scores.actionability,
                quality_scores.source_accuracy,
                quality_scores.coaching_effectiveness,
                quality_scores.overall_score,
                user_feedback.get("rating") if user_feedback else None,
                user_feedback.get("comments") if user_feedback else None,
                json.dumps(system_metadata or {})
            ))
            conn.commit()
    
    def _check_quality_alerts(self, quality_scores: QualityScores, response_time: float):
        """Check if quality scores trigger any alerts"""
        current_time = datetime.now().isoformat()
        
        # Check each metric against thresholds
        metrics_to_check = {
            "ramit_authenticity": quality_scores.ramit_authenticity,
            "framework_coherence": quality_scores.framework_coherence,
            "actionability": quality_scores.actionability,
            "overall_score": quality_scores.overall_score,
            "response_time": response_time
        }
        
        for metric, current_value in metrics_to_check.items():
            thresholds = self.quality_thresholds.get(metric, {})
            
            # Check critical threshold
            if "critical" in thresholds and current_value <= thresholds["critical"]:
                alert = QualityAlert(
                    timestamp=current_time,
                    alert_type="degradation",
                    severity="critical",
                    metric=metric,
                    current_value=current_value,
                    threshold_value=thresholds["critical"],
                    description=f"Critical quality degradation: {metric} dropped to {current_value:.2f}",
                    recommendations=self._get_recommendations_for_metric(metric, "critical")
                )
                self._record_alert(alert)
                
            # Check warning threshold
            elif "warning" in thresholds and current_value <= thresholds["warning"]:
                # Only alert if this is part of a trend (not just one bad response)
                if self._is_trend_alert_warranted(metric, current_value, thresholds["warning"]):
                    alert = QualityAlert(
                        timestamp=current_time,
                        alert_type="degradation",
                        severity="medium",
                        metric=metric,
                        current_value=current_value,
                        threshold_value=thresholds["warning"],
                        description=f"Quality warning: {metric} trend below {thresholds['warning']:.2f}",
                        recommendations=self._get_recommendations_for_metric(metric, "warning")
                    )
                    self._record_alert(alert)
    
    def _is_trend_alert_warranted(self, metric: str, current_value: float, threshold: float) -> bool:
        """Check if a trend-based alert is warranted"""
        # Get recent responses for this metric
        window_hours = self.monitoring_config["alert_window_hours"]
        min_samples = self.monitoring_config["min_samples_for_alert"]
        
        cutoff_time = (datetime.now() - timedelta(hours=window_hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT {metric} FROM responses 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (cutoff_time, min_samples * 2))
            
            recent_values = [row[0] for row in cursor.fetchall()]
        
        if len(recent_values) < min_samples:
            return False
        
        # Check if majority of recent values are below threshold
        below_threshold = sum(1 for value in recent_values[:min_samples] if value <= threshold)
        return below_threshold >= min_samples * 0.6  # 60% below threshold
    
    def _get_recommendations_for_metric(self, metric: str, severity: str) -> List[str]:
        """Get recommendations for improving a specific metric"""
        recommendations = {
            "ramit_authenticity": [
                "Review context-aware prompting configuration",
                "Check if Ramit voice patterns are being applied correctly",
                "Verify coaching context injection is working",
                "Review recent queries for pattern changes"
            ],
            "framework_coherence": [
                "Check framework detection accuracy in retrieved content",
                "Review semantic chunking for framework preservation",
                "Verify framework relationship mapping",
                "Check for content quality issues in vector store"
            ],
            "actionability": [
                "Review tactical language generation",
                "Check if step-by-step guidance is being provided",
                "Verify implementation guidance quality",
                "Review query intent classification accuracy"
            ],
            "overall_score": [
                "Run comprehensive quality analysis",
                "Check all individual metrics for issues",
                "Review system integration points",
                "Consider reindexing vector store"
            ],
            "response_time": [
                "Check system resource usage",
                "Review vector store performance",
                "Monitor OpenAI API response times",
                "Consider caching strategies"
            ]
        }
        
        base_recs = recommendations.get(metric, ["Review system configuration"])
        
        if severity == "critical":
            base_recs.append("Consider disabling system until issue is resolved")
            base_recs.append("Alert system administrators immediately")
        
        return base_recs
    
    def _record_alert(self, alert: QualityAlert):
        """Record alert in database and add to queue"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quality_alerts (
                    timestamp, alert_type, severity, metric,
                    current_value, threshold_value, description, recommendations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.timestamp, alert.alert_type, alert.severity, alert.metric,
                alert.current_value, alert.threshold_value, alert.description,
                json.dumps(alert.recommendations)
            ))
            conn.commit()
        
        # Add to alert queue for real-time processing
        self.alert_queue.put(alert)
        
        # Print alert
        severity_icon = {"low": "ℹ️", "medium": "⚠️", "high": "🚨", "critical": "💥"}
        icon = severity_icon.get(alert.severity, "⚠️")
        print(f"{icon} QUALITY ALERT: {alert.description}")
    
    def _trigger_auto_feedback_collection(
        self, 
        query: str, 
        response: str, 
        quality_scores: QualityScores
    ):
        """Trigger automatic feedback collection for sampling"""
        # This would integrate with a feedback collection system
        # For now, we'll just record that feedback should be collected
        feedback_request = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_preview": response[:100] + "...",
            "predicted_quality": quality_scores.overall_score,
            "feedback_requested": True
        }
        
        # In a real implementation, this might:
        # - Send to a feedback queue
        # - Trigger an email/notification
        # - Add to a review interface
        print(f"🔍 Feedback requested for query: {query[:50]}...")
    
    def get_quality_dashboard(self) -> Dict[str, Any]:
        """Get current quality dashboard data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Recent quality metrics (last 24 hours)
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as response_count,
                    AVG(overall_score) as avg_quality,
                    AVG(ramit_authenticity) as avg_authenticity,
                    AVG(framework_coherence) as avg_coherence,
                    AVG(actionability) as avg_actionability,
                    AVG(response_time) as avg_response_time
                FROM responses 
                WHERE timestamp > ?
            """, (cutoff_time,))
            
            recent_stats = cursor.fetchone()
            
            # Active alerts
            cursor.execute("""
                SELECT COUNT(*) FROM quality_alerts 
                WHERE acknowledged = FALSE AND timestamp > ?
            """, (cutoff_time,))
            
            active_alerts = cursor.fetchone()[0]
            
            # Quality trends (last 7 days)
            week_cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    AVG(overall_score) as daily_quality,
                    COUNT(*) as daily_responses
                FROM responses 
                WHERE timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (week_cutoff,))
            
            daily_trends = cursor.fetchall()
        
        dashboard = {
            "current_status": {
                "monitoring_active": self.monitoring_active,
                "responses_last_24h": recent_stats[0] if recent_stats[0] else 0,
                "avg_quality_24h": recent_stats[1] if recent_stats[1] else 0,
                "active_alerts": active_alerts
            },
            "quality_metrics_24h": {
                "overall_score": recent_stats[1] if recent_stats[1] else 0,
                "ramit_authenticity": recent_stats[2] if recent_stats[2] else 0,
                "framework_coherence": recent_stats[3] if recent_stats[3] else 0,
                "actionability": recent_stats[4] if recent_stats[4] else 0,
                "avg_response_time": recent_stats[5] if recent_stats[5] else 0
            },
            "trends_7d": [
                {
                    "date": row[0],
                    "quality": row[1],
                    "responses": row[2]
                }
                for row in daily_trends
            ]
        }
        
        return dashboard
    
    def get_alerts(self, unacknowledged_only: bool = True) -> List[QualityAlert]:
        """Get quality alerts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM quality_alerts"
            if unacknowledged_only:
                query += " WHERE acknowledged = FALSE"
            query += " ORDER BY timestamp DESC LIMIT 50"
            
            cursor.execute(query)
            rows = cursor.fetchall()
        
        alerts = []
        for row in rows:
            alert = QualityAlert(
                timestamp=row[1],
                alert_type=row[2],
                severity=row[3],
                metric=row[4],
                current_value=row[5],
                threshold_value=row[6],
                description=row[7],
                recommendations=json.loads(row[8])
            )
            alerts.append(alert)
        
        return alerts
    
    def acknowledge_alert(self, alert_id: int):
        """Acknowledge an alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE quality_alerts SET acknowledged = TRUE WHERE id = ?
            """, (alert_id,))
            conn.commit()
    
    def _calculate_session_stats(self) -> Dict[str, Any]:
        """Calculate statistics for current monitoring session"""
        if not hasattr(self, 'session_start_time'):
            return {}
        
        start_time = datetime.fromisoformat(self.session_start_time)
        duration = datetime.now() - start_time
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count responses in this session
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    AVG(overall_score) as avg_quality
                FROM responses 
                WHERE timestamp > ?
            """, (self.session_start_time,))
            
            response_stats = cursor.fetchone()
            
            # Count alerts in this session
            cursor.execute("""
                SELECT COUNT(*) FROM quality_alerts 
                WHERE timestamp > ?
            """, (self.session_start_time,))
            
            alert_count = cursor.fetchone()[0]
        
        return {
            "duration": str(duration).split('.')[0],  # Remove microseconds
            "responses_monitored": response_stats[0] if response_stats[0] else 0,
            "average_quality": response_stats[1] if response_stats[1] else 0.0,
            "alerts_generated": alert_count
        }
    
    def export_quality_report(self, days: int = 7) -> Dict[str, Any]:
        """Export a comprehensive quality report"""
        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_responses,
                    AVG(overall_score) as avg_quality,
                    MIN(overall_score) as min_quality,
                    MAX(overall_score) as max_quality,
                    AVG(response_time) as avg_response_time,
                    AVG(ramit_authenticity) as avg_authenticity,
                    AVG(framework_coherence) as avg_coherence,
                    AVG(actionability) as avg_actionability
                FROM responses 
                WHERE timestamp > ?
            """, (cutoff_time,))
            
            overall_stats = cursor.fetchone()
            
            # Quality distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN overall_score >= 4.0 THEN 'excellent'
                        WHEN overall_score >= 3.0 THEN 'good'
                        WHEN overall_score >= 2.0 THEN 'fair'
                        ELSE 'poor'
                    END as quality_bucket,
                    COUNT(*) as count
                FROM responses 
                WHERE timestamp > ?
                GROUP BY quality_bucket
            """, (cutoff_time,))
            
            quality_distribution = dict(cursor.fetchall())
            
            # Alert summary
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM quality_alerts 
                WHERE timestamp > ?
                GROUP BY severity
            """, (cutoff_time,))
            
            alert_summary = dict(cursor.fetchall())
        
        report = {
            "report_period_days": days,
            "generated_at": datetime.now().isoformat(),
            "overall_statistics": {
                "total_responses": overall_stats[0],
                "average_quality": overall_stats[1],
                "quality_range": f"{overall_stats[2]:.2f} - {overall_stats[3]:.2f}",
                "average_response_time": overall_stats[4],
                "average_authenticity": overall_stats[5],
                "average_coherence": overall_stats[6],
                "average_actionability": overall_stats[7]
            },
            "quality_distribution": quality_distribution,
            "alert_summary": alert_summary
        }
        
        return report

# Command-line interface for monitoring
def run_quality_monitor():
    """Run quality monitor from command line"""
    monitor = QualityMonitor()
    
    print("Quality Monitor - Interactive Mode")
    print("Commands: start, stop, status, alerts, dashboard, export, help, quit")
    
    while True:
        try:
            command = input("\nmonitor> ").strip().lower()
            
            if command == "start":
                monitor.start_monitoring()
            elif command == "stop":
                monitor.stop_monitoring()
            elif command == "status":
                dashboard = monitor.get_quality_dashboard()
                print(f"Monitoring Active: {dashboard['current_status']['monitoring_active']}")
                print(f"Responses Last 24h: {dashboard['current_status']['responses_last_24h']}")
                print(f"Average Quality: {dashboard['quality_metrics_24h']['overall_score']:.2f}/5.0")
                print(f"Active Alerts: {dashboard['current_status']['active_alerts']}")
            elif command == "alerts":
                alerts = monitor.get_alerts()
                if alerts:
                    print(f"Found {len(alerts)} unacknowledged alerts:")
                    for i, alert in enumerate(alerts[:5]):
                        print(f"  {i+1}. {alert.severity.upper()}: {alert.description}")
                else:
                    print("No active alerts")
            elif command == "dashboard":
                dashboard = monitor.get_quality_dashboard()
                print(json.dumps(dashboard, indent=2))
            elif command == "export":
                report = monitor.export_quality_report()
                filename = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"Report exported to {filename}")
            elif command == "help":
                print("Available commands:")
                print("  start    - Start monitoring session")
                print("  stop     - Stop monitoring session")
                print("  status   - Show current status")
                print("  alerts   - Show active alerts")
                print("  dashboard- Show quality dashboard")
                print("  export   - Export quality report")
                print("  quit     - Exit monitor")
            elif command in ["quit", "exit"]:
                if monitor.monitoring_active:
                    monitor.stop_monitoring()
                break
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            if monitor.monitoring_active:
                monitor.stop_monitoring()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_quality_monitor()