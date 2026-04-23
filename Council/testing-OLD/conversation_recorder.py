import json
import os
from datetime import datetime
from typing import List, Dict, Any


class ConversationRecorder:
    def __init__(self, output_directory: str = "testing/conversations"):
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
    
    def record_debate_conversation(self, debate_summary: Dict[str, Any], debate_id: str):
        conversation = {
            "debate_id": debate_id,
            "timestamp": datetime.now().isoformat(),
            "problem": debate_summary.get("problem", "Unknown"),
            "duration": debate_summary.get("duration_seconds", 0),
            "participants": [],
            "conversation_flow": [],
            "outcome": {}
        }
        
        for agent_stats in debate_summary.get("agent_stats", []):
            conversation["participants"].append({
                "name": agent_stats["name"],
                "agent_id": agent_stats["agent_id"],
                "final_score": agent_stats["current_score"],
                "win_rate": agent_stats["win_rate"]
            })
        
        proposals = debate_summary.get("proposals", [])
        
        for proposal in proposals:
            conversation["conversation_flow"].append({
                "type": "proposal",
                "agent": proposal["agent_name"],
                "content": proposal["content"],
                "timestamp": proposal["timestamp"],
                "score": proposal["score"]
            })
            
            for challenge in proposal.get("challenges", []):
                conversation["conversation_flow"].append({
                    "type": "challenge",
                    "agent": challenge["agent_name"],
                    "target": proposal["agent_name"],
                    "content": challenge["content"],
                    "timestamp": challenge["timestamp"]
                })
            
            for rebuttal in proposal.get("rebuttals", []):
                conversation["conversation_flow"].append({
                    "type": "rebuttal",
                    "agent": rebuttal["agent_name"],
                    "target": rebuttal.get("metadata", {}).get("challenge_agent", "Unknown"),
                    "content": rebuttal["content"],
                    "timestamp": rebuttal["timestamp"]
                })
        
        conversation["conversation_flow"].sort(key=lambda x: x["timestamp"])
        
        if debate_summary.get("final_decision"):
            conversation["outcome"] = {
                "decision": debate_summary["final_decision"]["decision"],
                "winner": debate_summary["final_decision"]["winning_proposal"]["agent_name"],
                "confidence": debate_summary["final_decision"]["confidence"],
                "reasoning": debate_summary["final_decision"]["reasoning"]
            }
        
        filename = f"conversation_{debate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(conversation, f, indent=2)
        
        return filepath
    
    def generate_readable_transcript(self, conversation_file: str, output_file: str = None):
        with open(conversation_file, 'r') as f:
            conversation = json.load(f)
        
        transcript = []
        transcript.append("="*80)
        transcript.append("DEBATE TRANSCRIPT")
        transcript.append("="*80)
        transcript.append(f"\nProblem: {conversation['problem']}")
        transcript.append(f"Date: {conversation['timestamp']}")
        transcript.append(f"Duration: {conversation['duration']:.2f} seconds")
        transcript.append(f"\nParticipants:")
        
        for participant in conversation['participants']:
            transcript.append(f"  - {participant['name']} (Score: {participant['final_score']:.1f}, Win Rate: {participant['win_rate']:.1%})")
        
        transcript.append("\n" + "="*80)
        transcript.append("CONVERSATION FLOW")
        transcript.append("="*80 + "\n")
        
        for idx, exchange in enumerate(conversation['conversation_flow'], 1):
            if exchange['type'] == 'proposal':
                transcript.append(f"\n[PROPOSAL #{idx}] {exchange['agent']}:")
                transcript.append(f"  {exchange['content']}")
                transcript.append(f"  Final Score: {exchange['score']:.1f}")
            
            elif exchange['type'] == 'challenge':
                transcript.append(f"\n[CHALLENGE #{idx}] {exchange['agent']} → {exchange['target']}:")
                transcript.append(f"  {exchange['content']}")
            
            elif exchange['type'] == 'rebuttal':
                transcript.append(f"\n[REBUTTAL #{idx}] {exchange['agent']} → {exchange['target']}:")
                transcript.append(f"  {exchange['content']}")
        
        transcript.append("\n" + "="*80)
        transcript.append("OUTCOME")
        transcript.append("="*80)
        transcript.append(f"\nDecision: {conversation['outcome']['decision']}")
        transcript.append(f"Winner: {conversation['outcome']['winner']}")
        transcript.append(f"Confidence: {conversation['outcome']['confidence']:.1%}")
        transcript.append(f"\nReasoning:")
        transcript.append(f"  {conversation['outcome']['reasoning']}")
        transcript.append("\n" + "="*80)
        
        transcript_text = "\n".join(transcript)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(transcript_text)
        
        return transcript_text
    
    def analyze_conversation_patterns(self, conversation_file: str) -> Dict[str, Any]:
        with open(conversation_file, 'r') as f:
            conversation = json.load(f)
        
        flow = conversation['conversation_flow']
        
        message_types = {"proposal": 0, "challenge": 0, "rebuttal": 0}
        agent_activity = {}
        interaction_matrix = {}
        
        for exchange in flow:
            message_types[exchange['type']] += 1
            
            agent = exchange['agent']
            if agent not in agent_activity:
                agent_activity[agent] = {"proposals": 0, "challenges": 0, "rebuttals": 0}
            
            agent_activity[agent][exchange['type'] + 's'] += 1
            
            if 'target' in exchange:
                target = exchange['target']
                key = f"{agent} → {target}"
                interaction_matrix[key] = interaction_matrix.get(key, 0) + 1
        
        total_exchanges = len(flow)
        avg_exchange_length = sum(len(e['content']) for e in flow) / total_exchanges if total_exchanges > 0 else 0
        
        most_active_agent = max(agent_activity.items(), key=lambda x: sum(x[1].values()))[0] if agent_activity else "None"
        
        return {
            "total_exchanges": total_exchanges,
            "message_type_distribution": message_types,
            "agent_activity": agent_activity,
            "interaction_matrix": interaction_matrix,
            "average_exchange_length": avg_exchange_length,
            "most_active_agent": most_active_agent,
            "debate_intensity": total_exchanges / conversation['duration'] if conversation['duration'] > 0 else 0
        }


def main():
    recorder = ConversationRecorder()
    
    results_dir = "testing/results"
    if not os.path.exists(results_dir):
        print("No results found. Run test_runner.py first.")
        return
    
    print("\n" + "="*80)
    print("CONVERSATION RECORDER")
    print("="*80)
    
    processed = 0
    
    for filename in os.listdir(results_dir):
        if filename.endswith('.json') and filename.startswith('test'):
            filepath = os.path.join(results_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    debate_data = json.load(f)
                
                debate_id = debate_data.get("system_id", filename.replace('.json', ''))
                
                conv_file = recorder.record_debate_conversation(debate_data, debate_id)
                print(f"\n✓ Recorded conversation: {conv_file}")
                
                transcript_file = conv_file.replace('.json', '_transcript.txt')
                recorder.generate_readable_transcript(conv_file, transcript_file)
                print(f"  Generated transcript: {transcript_file}")
                
                patterns = recorder.analyze_conversation_patterns(conv_file)
                print(f"  Total exchanges: {patterns['total_exchanges']}")
                print(f"  Most active: {patterns['most_active_agent']}")
                print(f"  Debate intensity: {patterns['debate_intensity']:.2f} exchanges/second")
                
                processed += 1
                
            except Exception as e:
                print(f"\n✗ Error processing {filename}: {e}")
    
    print(f"\n" + "="*80)
    print(f"Processed {processed} debate conversations")
    print(f"Conversations saved to: {recorder.output_directory}/")
    print("="*80)


if __name__ == "__main__":
    main()
