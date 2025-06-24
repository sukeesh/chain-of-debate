# Chain of Debate

An intelligent multi-AI discussion system that facilitates thoughtful exchanges between GPT-4o-mini and Claude 3 Haiku to arrive at more reliable answers through collaborative reasoning.

## Key Features

- **🔄 Multi-Round Discussions**: Extended 6-round format with dynamic phase transitions
- **📊 Dual Consensus Mechanisms**: Both explicit agreement detection and semantic equivalence checking
- **🔄 Early Termination**: Stops immediately when AIs reach agreement

## How The System Works

### **Two-Phase Discussion Structure**

#### **Phase 1: Exploration (Rounds 1-3)**
- Each AI presents their perspective thoroughly
- Focus on sharing different viewpoints and insights
- Constructive examination of each other's reasoning
- Goal: Explore the full scope of the question

#### **Phase 2: Reflection (Rounds 4-6)**
- AIs consider both their original thoughts and the other's perspective
- More collaborative and synthesis-oriented approach
- Focus on finding common ground or refining positions
- Goal: Reach thoughtful conclusions

### **Context-Aware Conversations**

- Each AI sees the other's previous full response
- Builds genuine conversational flow
- Enables natural agreement and disagreement patterns
- Preserves discussion context throughout all rounds

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- Anthropic API key

### Installation

1. Install required packages:
```bash
pip install openai anthropic
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## Usage

### Interactive Mode (Recommended)

```bash
python main.py
```

The system will:
1. ✅ Validate your API keys
2. 📝 Prompt you to enter any question
3. 🤖 Run the multi-AI discussion
4. 📊 Display the final answer

### Programmatic Usage

```python
from main import debate

# Ask any question and let the AIs discuss
question = "Should pineapple go on pizza?"
final_answer = debate(question)
print(f"Final Answer: {final_answer}")
```

### Advanced Configuration

```python
# Customize the number of discussion rounds (default: 6)
final_answer = debate(question, max_rounds=4)
```

## Example Discussions

### **Quick Consensus Example**
```
Enter your question: What is 15 + 27?

=== Round 1 ===
(Exploration phase: Each AI shares their perspective)

--- GPT-4 says ---
I need to add 15 + 27 step by step.
15 + 27 = 42
Answer: 42

--- Claude says ---
This is a straightforward addition problem. GPT-4 is absolutely correct.
15 + 27 = 42
Answer: 42

🤝 Claude explicitly agrees with GPT-4! Discussion concluded.

=== Final Answer ===
42
```

### **Extended Discussion Example**
```
Enter your question: Is artificial intelligence dangerous?

=== Round 1 ===
(Exploration phase: Each AI shares their perspective)

--- GPT-4 says ---
AI presents both opportunities and risks. The key concerns include...
Answer: AI has potential dangers that require careful management

--- Claude says ---
While AI does pose some risks, I think the benefits outweigh the concerns...
Answer: AI is generally beneficial with proper safeguards

=== Round 2 ===
(Exploration phase: Each AI shares their perspective)
...continues for up to 6 rounds...
```
