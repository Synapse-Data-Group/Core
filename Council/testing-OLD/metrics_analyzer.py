import json
import os
from typing import List, Dict, Any
from datetime import datetime
import statistics


class DebateMetricsAnalyzer:
    def __init__(self, results_directory: str = "testing/results"):
        self.results_directory = results_directory
        self.debates: List[Dict[str, Any]] = []
        self.load_all_debates()
    
    def load_all_debates(self):
        if not os.path.exists(self.results_directory):
            print(f"Results directory not found: {self.results_directory}")
            return
        
        for filename in os.listdir(self.results_directory):
            if filename.endswith('.json') and filename != 'test_suite_summary.json':
                filepath = os.path.join(self.results_directory, filename)
                try:
                    with open(filepath, 'r') as f:
                        debate_data = json.load(f)
                        self.debates.append({
                            "filename": filename,
                            "data": debate_data
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def analyze_agent_performance(self) -> Dict[str, Any]:
        all_agents = []
        
        for debate in self.debates:
            for agent_stats in debate["data"].get("agent_stats", []):
                all_agents.append(agent_stats)
        
        if not all_agents:
            return {"error": "No agent data found"}
        
        total_agents = len(all_agents)
        avg_score = statistics.mean([a["current_score"] for a in all_agents])
        avg_win_rate = statistics.mean([a["win_rate"] for a in all_agents])
        avg_memory_size = statistics.mean([a["memory_size"] for a in all_agents])
        avg_exploration = statistics.mean([a["exploration_rate"] for a in all_agents])
        
        total_proposals = sum(a["proposals_made"] for a in all_agents)
        total_challenges = sum(a["challenges_made"] for a in all_agents)
        total_rebuttals = sum(a["rebuttals_made"] for a in all_agents)
        
        return {
            "total_agents": total_agents,
            "average_score": avg_score,
            "average_win_rate": avg_win_rate,
            "average_memory_size": avg_memory_size,
            "average_exploration_rate": avg_exploration,
            "total_proposals": total_proposals,
            "total_challenges": total_challenges,
            "total_rebuttals": total_rebuttals,
            "engagement_ratio": total_challenges / max(total_proposals, 1),
            "rebuttal_ratio": total_rebuttals / max(total_challenges, 1)
        }
    
    def analyze_debate_dynamics(self) -> Dict[str, Any]:
        if not self.debates:
            return {"error": "No debate data found"}
        
        durations = []
        message_counts = []
        proposal_counts = []
        confidences = []
        
        for debate in self.debates:
            data = debate["data"]
            durations.append(data.get("duration_seconds", 0))
            message_counts.append(data.get("total_messages", 0))
            proposal_counts.append(data.get("total_proposals", 0))
            
            if data.get("final_decision") and "confidence" in data["final_decision"]:
                confidences.append(data["final_decision"]["confidence"])
        
        return {
            "total_debates": len(self.debates),
            "average_duration": statistics.mean(durations) if durations else 0,
            "average_messages": statistics.mean(message_counts) if message_counts else 0,
            "average_proposals": statistics.mean(proposal_counts) if proposal_counts else 0,
            "average_confidence": statistics.mean(confidences) if confidences else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "total_messages": sum(message_counts),
            "total_proposals": sum(proposal_counts)
        }
    
    def analyze_learning_progression(self) -> Dict[str, Any]:
        learning_debates = [d for d in self.debates if "learning" in d["filename"].lower()]
        
        if not learning_debates:
            return {"message": "No learning progression data found"}
        
        learning_debates.sort(key=lambda x: x["filename"])
        
        progression = []
        
        for debate in learning_debates:
            data = debate["data"]
            agent_stats = data.get("agent_stats", [])
            
            debate_metrics = {
                "filename": debate["filename"],
                "average_score": statistics.mean([a["current_score"] for a in agent_stats]) if agent_stats else 0,
                "average_memory": statistics.mean([a["memory_size"] for a in agent_stats]) if agent_stats else 0,
                "average_exploration": statistics.mean([a["exploration_rate"] for a in agent_stats]) if agent_stats else 0
            }
            
            progression.append(debate_metrics)
        
        if len(progression) > 1:
            score_improvement = progression[-1]["average_score"] - progression[0]["average_score"]
            memory_growth = progression[-1]["average_memory"] - progression[0]["average_memory"]
            exploration_decay = progression[0]["average_exploration"] - progression[-1]["average_exploration"]
        else:
            score_improvement = 0
            memory_growth = 0
            exploration_decay = 0
        
        return {
            "debates_analyzed": len(progression),
            "progression": progression,
            "score_improvement": score_improvement,
            "memory_growth": memory_growth,
            "exploration_decay": exploration_decay
        }
    
    def analyze_moderator_performance(self) -> Dict[str, Any]:
        moderator_stats = []
        
        for debate in self.debates:
            if "moderator_stats" in debate["data"]:
                moderator_stats.append(debate["data"]["moderator_stats"])
        
        if not moderator_stats:
            return {"error": "No moderator data found"}
        
        avg_debates_moderated = statistics.mean([m.get("debates_moderated", 0) for m in moderator_stats])
        avg_accuracy = statistics.mean([m.get("avg_decision_accuracy", 0.5) for m in moderator_stats])
        avg_exploration = statistics.mean([m.get("exploration_rate", 0.5) for m in moderator_stats])
        avg_memory = statistics.mean([m.get("memory_size", 0) for m in moderator_stats])
        
        return {
            "total_moderator_instances": len(moderator_stats),
            "average_debates_moderated": avg_debates_moderated,
            "average_decision_accuracy": avg_accuracy,
            "average_exploration_rate": avg_exploration,
            "average_memory_size": avg_memory
        }
    
    def generate_report(self, output_file: str = "testing/results/analysis_report.json"):
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "debates_analyzed": len(self.debates),
            "agent_performance": self.analyze_agent_performance(),
            "debate_dynamics": self.analyze_debate_dynamics(),
            "learning_progression": self.analyze_learning_progression(),
            "moderator_performance": self.analyze_moderator_performance()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_report(self):
        print("\n" + "="*80)
        print("DEBATE METRICS ANALYSIS REPORT")
        print("="*80)
        
        agent_perf = self.analyze_agent_performance()
        print("\n--- AGENT PERFORMANCE ---")
        print(f"Total Agents Analyzed: {agent_perf.get('total_agents', 0)}")
        print(f"Average Score: {agent_perf.get('average_score', 0):.2f}")
        print(f"Average Win Rate: {agent_perf.get('average_win_rate', 0):.1%}")
        print(f"Average Memory Size: {agent_perf.get('average_memory_size', 0):.0f} experiences")
        print(f"Average Exploration Rate: {agent_perf.get('average_exploration_rate', 0):.3f}")
        print(f"Total Proposals: {agent_perf.get('total_proposals', 0)}")
        print(f"Total Challenges: {agent_perf.get('total_challenges', 0)}")
        print(f"Total Rebuttals: {agent_perf.get('total_rebuttals', 0)}")
        print(f"Engagement Ratio: {agent_perf.get('engagement_ratio', 0):.2f} challenges per proposal")
        print(f"Rebuttal Ratio: {agent_perf.get('rebuttal_ratio', 0):.2f} rebuttals per challenge")
        
        debate_dyn = self.analyze_debate_dynamics()
        print("\n--- DEBATE DYNAMICS ---")
        print(f"Total Debates: {debate_dyn.get('total_debates', 0)}")
        print(f"Average Duration: {debate_dyn.get('average_duration', 0):.2f}s")
        print(f"Average Messages: {debate_dyn.get('average_messages', 0):.1f}")
        print(f"Average Proposals: {debate_dyn.get('average_proposals', 0):.1f}")
        print(f"Average Confidence: {debate_dyn.get('average_confidence', 0):.1%}")
        print(f"Duration Range: {debate_dyn.get('min_duration', 0):.2f}s - {debate_dyn.get('max_duration', 0):.2f}s")
        
        learning = self.analyze_learning_progression()
        if "message" not in learning:
            print("\n--- LEARNING PROGRESSION ---")
            print(f"Debates Analyzed: {learning.get('debates_analyzed', 0)}")
            print(f"Score Improvement: {learning.get('score_improvement', 0):+.2f}")
            print(f"Memory Growth: {learning.get('memory_growth', 0):+.0f} experiences")
            print(f"Exploration Decay: {learning.get('exploration_decay', 0):+.3f}")
        
        mod_perf = self.analyze_moderator_performance()
        if "error" not in mod_perf:
            print("\n--- MODERATOR PERFORMANCE ---")
            print(f"Moderator Instances: {mod_perf.get('total_moderator_instances', 0)}")
            print(f"Average Debates Moderated: {mod_perf.get('average_debates_moderated', 0):.1f}")
            print(f"Average Decision Accuracy: {mod_perf.get('average_decision_accuracy', 0):.1%}")
            print(f"Average Exploration Rate: {mod_perf.get('average_exploration_rate', 0):.3f}")
            print(f"Average Memory Size: {mod_perf.get('average_memory_size', 0):.0f}")
        
        print("\n" + "="*80)


def main():
    analyzer = DebateMetricsAnalyzer()
    
    if not analyzer.debates:
        print("No debate results found. Please run test_runner.py first.")
        return
    
    analyzer.print_report()
    
    report = analyzer.generate_report()
    print(f"\nDetailed report saved to: testing/results/analysis_report.json")


if __name__ == "__main__":
    main()
