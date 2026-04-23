# Council Framework - Phase 2 Testing Plan

**Objective**: Transform proof-of-concept into publication-ready research through systematic validation of learning, comparative performance, component contributions, and robustness.

---

## 🎯 Research Questions & Validation Goals

| Research Question | Current Status | Phase 2 Goal | Success Criteria |
|-------------------|----------------|--------------|------------------|
| Does learning actually improve performance? | ❌ Not demonstrated | ✅ Show learning curves over 50+ debates | Statistically significant improvement (p<0.05) |
| Is Council better than existing systems? | ❌ No comparisons | ✅ Beat AutoGen/CrewAI on benchmarks | >20% improvement on quality metrics |
| Which components actually matter? | ❌ Unknown | ✅ Ablation studies isolate contribution | Quantify each component's impact |
| Do humans think the output is good? | ❌ No human evaluation | ✅ Quality ratings from judges | >4.0/5.0 average rating |
| Does evolution beat random search? | ❌ Not tested | ✅ Compare evolved vs random agents | >15% performance delta |
| Does fluid resourcing help? | ⚠️ Shown, not proven | ✅ Statistical comparison fluid vs static | Significant quality/efficiency gain |

---

## 📋 Test Suite Architecture

```
Phase 2 Testing Structure:
├── Phase A: Learning Validation (Tests 9-11)
│   ├── Test 9: Learning Curves (50 debates)
│   ├── Test 10: Transfer Learning
│   └── Test 11: Evolution vs Random
│
├── Phase B: Baseline Comparisons (Tests 12-14)
│   ├── Test 12: Council vs AutoGen
│   ├── Test 13: Council vs Fixed-Team
│   └── Test 14: Council vs Random-Spawn
│
├── Phase C: Ablation Studies (Tests 15-18)
│   ├── Test 15: With/Without Fluid Resourcing
│   ├── Test 16: With/Without Q-Learning
│   ├── Test 17: With/Without Knowledge Graph
│   └── Test 18: With/Without Coalition Detection
│
├── Phase D: Human Evaluation (Tests 19-20)
│   ├── Test 19: Expert Panel Ratings
│   └── Test 20: Mechanical Turk Crowd Eval
│
└── Phase E: Robustness Testing (Tests 21-22)
    ├── Test 21: Adversarial Agents
    └── Test 22: Edge Cases & Failure Modes
```

---

## Phase A: Learning Validation

### Test 9: Learning Curves (50 Debates)

**Objective**: Demonstrate that the system improves performance through experience.

**Hypothesis**: Agent quality scores, debate coherence, and moderator decision accuracy will improve over successive debates.

**Experimental Design**:
- **Problem Set**: 10 diverse problems (5 practical, 5 philosophical)
- **Iterations**: 5 debates per problem (50 total debates)
- **Configuration**: 
  - Start with naive agents (no prior experience)
  - Enable Q-learning for moderator decisions
  - Enable reputation system for agent performance tracking
  - Track all metrics across debates

**Metrics to Track**:
1. **Argument Quality**: Average quality score per debate (0.0-1.0)
2. **Debate Efficiency**: Time to convergence (seconds)
3. **Moderator Accuracy**: Spawning decision appropriateness (manual evaluation)
4. **Knowledge Graph Density**: Concepts/relationships per debate
5. **Agent Reputation**: Reputation score evolution over time

**Success Criteria**:
- Quality score increases >10% from debate 1 to debate 50
- Time to convergence decreases >15%
- Moderator spawning accuracy improves (fewer unnecessary spawns)
- Statistical significance: p < 0.05 (paired t-test)

**Data Collection**:
```python
learning_metrics = {
    "debate_id": int,
    "problem_type": str,
    "iteration": int,  # 1-5
    "avg_quality": float,
    "time_to_convergence": float,
    "spawns_count": int,
    "spawns_appropriate": int,
    "knowledge_concepts": int,
    "agent_reputations": dict
}
```

**Analysis Plan**:
1. Plot learning curves for each metric
2. Fit regression lines to identify trends
3. Compare early debates (1-10) vs late debates (41-50)
4. Statistical testing: paired t-test, ANOVA across problem types

---

### Test 10: Transfer Learning

**Objective**: Validate that learning from one problem domain transfers to related domains.

**Hypothesis**: Agents trained on practical problems will perform better on new practical problems than untrained agents. Same for philosophical problems.

**Experimental Design**:
- **Training Set**: 20 debates on practical city planning problems
- **Test Set**: 5 new practical problems (urban design, infrastructure)
- **Control**: 5 debates with untrained agents on same test problems
- **Comparison**: Trained vs untrained performance

**Metrics**:
1. **Quality Delta**: Trained - Untrained quality scores
2. **Efficiency Delta**: Time reduction with trained agents
3. **Knowledge Reuse**: Concepts from training appearing in test debates

**Success Criteria**:
- Trained agents score >15% higher quality than untrained
- Trained agents converge >20% faster
- >30% concept overlap between training and test knowledge graphs
- p < 0.05 significance

**Implementation**:
```python
# Training phase
for problem in training_set:
    debate = run_debate(problem, enable_learning=True)
    save_agent_states()

# Test phase
trained_results = run_debates(test_set, load_agents=True)
untrained_results = run_debates(test_set, load_agents=False)

# Analysis
compare_performance(trained_results, untrained_results)
```

---

### Test 11: Evolution vs Random Agent Selection

**Objective**: Prove that evolved agent personalities outperform random personality assignments.

**Hypothesis**: Agents with evolved personalities (optimized through Q-learning) will produce higher quality debates than agents with random personalities.

**Experimental Design**:
- **Evolved Condition**: 25 debates with Q-learning optimized agent personalities
- **Random Condition**: 25 debates with randomly assigned personalities
- **Same Problems**: Both conditions use identical problem set
- **Controlled Variables**: Same moderator logic, same problem complexity

**Personality Evolution Mechanism**:
```python
# Q-learning for personality optimization
Q[state, action] = Q[state, action] + α * (reward + γ * max(Q[next_state]) - Q[state, action])

# State: debate context (similarity, complexity, agent count)
# Action: spawn agent with personality vector
# Reward: debate quality improvement after spawn
```

**Metrics**:
1. **Quality Comparison**: Evolved vs Random average quality
2. **Convergence Speed**: Time to reach quality threshold
3. **Spawning Efficiency**: Spawns needed per debate
4. **Personality Diversity**: Variance in personality vectors

**Success Criteria**:
- Evolved agents achieve >15% higher quality
- Evolved agents converge >10% faster
- Statistical significance: p < 0.01 (independent t-test)

---

## Phase B: Baseline Comparisons

### Test 12: Council vs AutoGen

**Objective**: Benchmark Council against Microsoft AutoGen framework.

**Hypothesis**: Council's autonomous orchestration will outperform AutoGen's predefined workflows on complex problems.

**Experimental Design**:
- **Problem Set**: 10 complex decision-making problems
- **Council Configuration**: Full autonomous orchestration (fluid resourcing, Q-learning)
- **AutoGen Configuration**: Equivalent agent count, predefined workflow
- **Evaluation**: Blind human evaluation + automated metrics

**Comparison Metrics**:
1. **Output Quality**: Human ratings (1-5 scale)
2. **Argument Coherence**: Automated coherence scoring
3. **Time Efficiency**: Total execution time
4. **Resource Utilization**: LLM API calls per quality point
5. **Adaptability**: Performance on diverse problem types

**AutoGen Baseline Setup**:
```python
# AutoGen equivalent configuration
autogen_config = {
    "agents": 16,  # Fixed count (Council's Test 7 average)
    "workflow": "sequential",  # Predefined debate structure
    "termination": "fixed_rounds",  # 10 rounds
    "evaluation": "voting"  # Fixed scoring mechanism
}
```

**Success Criteria**:
- Council achieves >20% higher human quality ratings
- Council uses ≤15% fewer LLM calls for equivalent quality
- Council adapts better to problem diversity (lower variance)
- p < 0.05 on quality comparison

**Data Collection**:
```python
comparison_data = {
    "problem_id": str,
    "system": str,  # "Council" or "AutoGen"
    "quality_rating": float,  # 1-5
    "coherence_score": float,  # 0-1
    "execution_time": float,
    "llm_calls": int,
    "output_length": int
}
```

---

### Test 13: Council vs Fixed-Team Baseline

**Objective**: Isolate the value of fluid resourcing by comparing against fixed team sizes.

**Hypothesis**: Council's dynamic team sizing will outperform fixed teams on problems with varying complexity.

**Experimental Design**:
- **Council (Fluid)**: Autonomous team sizing (Tests 7-8 configuration)
- **Fixed-Small**: Always 8 agents
- **Fixed-Medium**: Always 16 agents
- **Fixed-Large**: Always 32 agents
- **Problem Set**: 15 problems with varying complexity (5 simple, 5 medium, 5 complex)

**Metrics**:
1. **Quality vs Complexity**: Performance across problem complexity levels
2. **Efficiency**: Quality per agent (quality/agent_count)
3. **Adaptability**: Variance in performance across problem types
4. **Resource Waste**: Unnecessary agents spawned

**Success Criteria**:
- Council matches or exceeds best fixed team on all complexity levels
- Council shows lower variance across problem types
- Council achieves higher quality-per-agent ratio
- Statistical significance: p < 0.05 (ANOVA)

**Analysis**:
```python
# Compare performance across complexity levels
for complexity in ["simple", "medium", "complex"]:
    council_quality = get_quality(council_results, complexity)
    fixed_small = get_quality(fixed_8_results, complexity)
    fixed_medium = get_quality(fixed_16_results, complexity)
    fixed_large = get_quality(fixed_32_results, complexity)
    
    # Council should excel on complex, match on simple
    assert council_quality >= max(fixed_small, fixed_medium, fixed_large)
```

---

### Test 14: Council vs Random-Spawn Baseline

**Objective**: Validate that intelligent spawning decisions outperform random spawning.

**Hypothesis**: Council's Q-learning based spawning will produce better debates than random agent spawning.

**Experimental Design**:
- **Council (Intelligent)**: Q-learning based spawning decisions
- **Random-Spawn**: Same architecture, random spawning triggers
- **Problem Set**: 20 diverse problems
- **Controlled Variables**: Same agent pool, same termination logic

**Random-Spawn Configuration**:
```python
# Random spawning baseline
def random_spawn_decision():
    if random.random() < 0.3:  # 30% chance per round
        archetype = random.choice(["Analyst", "Innovator", "Skeptic", "Mediator"])
        spawn_agent(archetype)
```

**Metrics**:
1. **Spawning Efficiency**: Appropriate spawns / total spawns
2. **Quality Impact**: Quality improvement per spawn
3. **Team Composition**: Diversity of spawned archetypes
4. **Debate Coherence**: Logical flow with spawned agents

**Success Criteria**:
- Council achieves >40% higher spawning efficiency
- Council's spawns correlate with quality improvement (r > 0.6)
- Council produces more diverse teams
- p < 0.01 significance

---

## Phase C: Ablation Studies

### Test 15: With/Without Fluid Resourcing

**Objective**: Quantify the contribution of fluid resourcing to system performance.

**Experimental Design**:
- **Full System**: All components enabled
- **No Fluid Resourcing**: Fixed team size, no spawning
- **Problem Set**: 20 problems (10 simple, 10 complex)
- **Comparison**: Quality, efficiency, adaptability

**Metrics**:
1. **Quality Delta**: Full - NoFluid quality scores
2. **Adaptability**: Performance variance across problem types
3. **Efficiency**: Quality per agent

**Success Criteria**:
- Fluid resourcing improves quality by >12% on complex problems
- Reduces performance variance by >20%
- p < 0.05 significance

---

### Test 16: With/Without Q-Learning

**Objective**: Isolate the contribution of Q-learning to moderator decision quality.

**Experimental Design**:
- **With Q-Learning**: Moderator learns from experience
- **Without Q-Learning**: Moderator uses heuristics only
- **Problem Set**: 30 debates (to observe learning effects)

**Metrics**:
1. **Decision Quality**: Spawning appropriateness over time
2. **Learning Rate**: Improvement slope
3. **Final Performance**: Quality at debate 30

**Success Criteria**:
- Q-learning shows positive learning slope (p < 0.05)
- Final performance >10% higher than heuristic-only
- Fewer unnecessary spawns in later debates

---

### Test 17: With/Without Knowledge Graph

**Objective**: Quantify knowledge graph's contribution to debate quality.

**Experimental Design**:
- **With KG**: Full knowledge extraction and concept tracking
- **Without KG**: No concept extraction
- **Problem Set**: 15 debates

**Metrics**:
1. **Argument Depth**: Concept coverage in proposals
2. **Coherence**: Semantic consistency across rounds
3. **Quality**: Overall debate quality

**Success Criteria**:
- Knowledge graph improves coherence by >8%
- Increases concept coverage by >25%
- p < 0.05 significance

---

### Test 18: With/Without Coalition Detection

**Objective**: Measure coalition detection's impact on debate dynamics.

**Experimental Design**:
- **With Coalitions**: Full coalition detection and tracking
- **Without Coalitions**: No coalition awareness
- **Problem Set**: 15 debates with 10+ agents (to enable coalitions)

**Metrics**:
1. **Debate Balance**: Distribution of challenges across agents
2. **Quality**: Overall debate quality
3. **Diversity**: Perspective variety

**Success Criteria**:
- Coalition detection improves debate balance
- Maintains or improves quality
- Increases perspective diversity

---

## Phase D: Human Evaluation

### Test 19: Expert Panel Ratings

**Objective**: Obtain expert validation of output quality.

**Experimental Design**:
- **Experts**: 5 domain experts (AI ethics, policy, systems design)
- **Outputs**: 20 debate reports (10 Council, 10 baseline)
- **Evaluation**: Blind evaluation on 5-point Likert scale
- **Criteria**: Quality, coherence, depth, usefulness, novelty

**Rating Dimensions**:
1. **Argument Quality** (1-5): Logical soundness and evidence
2. **Coherence** (1-5): Flow and consistency
3. **Depth** (1-5): Thoroughness of analysis
4. **Usefulness** (1-5): Practical applicability
5. **Novelty** (1-5): Original insights

**Success Criteria**:
- Average rating >4.0/5.0 across all dimensions
- Council significantly outperforms baseline (p < 0.05)
- Inter-rater reliability >0.7 (Cronbach's alpha)

**Data Collection**:
```python
expert_ratings = {
    "expert_id": str,
    "output_id": str,
    "system": str,  # Blind
    "quality": int,  # 1-5
    "coherence": int,
    "depth": int,
    "usefulness": int,
    "novelty": int,
    "comments": str
}
```

---

### Test 20: Mechanical Turk Crowd Evaluation

**Objective**: Validate quality with broader audience.

**Experimental Design**:
- **Participants**: 100 MTurk workers (quality filters applied)
- **Outputs**: 30 debate summaries (15 Council, 15 baseline)
- **Task**: Rate quality, coherence, usefulness (1-5 scale)
- **Quality Control**: Attention checks, duplicate ratings

**Success Criteria**:
- Average rating >3.5/5.0
- Council outperforms baseline by >0.5 points
- High agreement with expert ratings (r > 0.6)

---

## Phase E: Robustness Testing

### Test 21: Adversarial Agents

**Objective**: Test system robustness against bad-faith agents.

**Experimental Design**:
- **Adversarial Behaviors**:
  - Spam agents (low-quality repetitive arguments)
  - Contradiction agents (always oppose, no reasoning)
  - Derailment agents (off-topic arguments)
- **Configuration**: 20% adversarial agents in each debate
- **Problem Set**: 15 debates

**Metrics**:
1. **Quality Degradation**: Impact on overall debate quality
2. **Detection**: System's ability to identify adversarial agents
3. **Mitigation**: Moderator's response (termination, reputation penalties)
4. **Recovery**: Quality restoration after adversarial removal

**Success Criteria**:
- Quality degradation <20% with adversarial agents
- System detects >80% of adversarial agents
- Quality recovers to >90% of baseline after mitigation

---

### Test 22: Edge Cases & Failure Modes

**Objective**: Identify and document system limitations.

**Test Cases**:
1. **Extreme Scale**: 200+ agents
2. **Zero Diversity**: All agents with identical personalities
3. **Contradictory Goals**: Agents with opposing objectives
4. **Resource Constraints**: Limited LLM budget
5. **Ambiguous Problems**: Poorly defined tasks
6. **Rapid Convergence**: Unanimous agreement in round 1
7. **Infinite Debate**: No convergence after 50 rounds

**Success Criteria**:
- Document graceful degradation for each case
- Identify failure thresholds
- Propose mitigation strategies
- No catastrophic failures (crashes, infinite loops)

---

## 📊 Consolidated Metrics & Analysis

### Primary Metrics (All Tests)

1. **Debate Quality Score** (0.0-1.0)
   - Automated: LLM-based quality evaluation
   - Human: Expert/crowd ratings

2. **Efficiency Metrics**
   - Time to convergence (seconds)
   - LLM calls per quality point
   - Agents per quality point

3. **Learning Metrics**
   - Quality improvement over time
   - Decision accuracy improvement
   - Knowledge transfer effectiveness

4. **Comparison Metrics**
   - Council vs baseline quality delta
   - Statistical significance (p-values)
   - Effect sizes (Cohen's d)

### Statistical Analysis Plan

1. **Learning Validation**: Paired t-tests, regression analysis
2. **Baseline Comparisons**: Independent t-tests, ANOVA
3. **Ablation Studies**: Paired t-tests, effect size calculation
4. **Human Evaluation**: Inter-rater reliability, correlation analysis
5. **Robustness**: Descriptive statistics, failure rate analysis

### Publication-Ready Outputs

1. **Learning Curves**: Plots showing improvement over 50 debates
2. **Comparison Tables**: Council vs baselines with p-values
3. **Ablation Results**: Component contribution quantification
4. **Human Ratings**: Expert and crowd evaluation summaries
5. **Robustness Report**: Edge case analysis and failure modes

---

## 🚀 Implementation Roadmap

### Phase A: Learning Validation (Weeks 1-2)
- Implement Q-learning for moderator
- Run 50-debate learning curve test
- Analyze transfer learning
- Compare evolution vs random

### Phase B: Baseline Comparisons (Weeks 3-4)
- Implement AutoGen baseline
- Implement fixed-team baselines
- Run comparison tests
- Statistical analysis

### Phase C: Ablation Studies (Week 5)
- Create component-disabled configurations
- Run ablation tests
- Quantify contributions

### Phase D: Human Evaluation (Week 6)
- Recruit expert panel
- Set up MTurk study
- Collect ratings
- Analyze results

### Phase E: Robustness Testing (Week 7)
- Implement adversarial agents
- Test edge cases
- Document failure modes
- Propose mitigations

### Analysis & Publication (Week 8)
- Consolidate all results
- Statistical analysis
- Create visualizations
- Update whitepaper with Phase 2 results

---

## 📈 Expected Outcomes

**If Successful**:
- Demonstrated learning capability (>10% improvement over 50 debates)
- Outperformed baselines (>20% quality improvement)
- Quantified component contributions (ablation studies)
- Validated with humans (>4.0/5.0 expert ratings)
- Proven robustness (graceful degradation under adversarial conditions)

**Publication Impact**:
- Transforms PoC into validated research
- Provides empirical evidence for all claims
- Enables comparison with existing systems
- Demonstrates practical applicability
- Establishes Council as foundational architecture with proven capabilities

---

## 🔬 Success Criteria Summary

| Phase | Key Metric | Target | Significance |
|-------|------------|--------|--------------|
| A: Learning | Quality improvement | >10% over 50 debates | p < 0.05 |
| B: Comparisons | vs AutoGen quality | >20% improvement | p < 0.05 |
| C: Ablations | Component contribution | Quantified for each | p < 0.05 |
| D: Human Eval | Expert ratings | >4.0/5.0 average | α > 0.7 |
| E: Robustness | Quality degradation | <20% with adversarial | - |

**Overall Goal**: Publication-ready research demonstrating Council Framework as a validated, robust, and superior approach to autonomous multi-agent orchestration.
