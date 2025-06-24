import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from anthropic import Anthropic

# ——— Setup clients ———
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ——— Helpers to talk to each model ———
def gpt_propose(question, context=None, round_num=1, max_rounds=6):
    if round_num <= 3:
        # Early rounds: Present your perspective thoroughly
        system = """You are having a thoughtful discussion to explore different viewpoints on a question. 
        Present your perspective clearly and thoroughly. If you see aspects the other viewpoint might be missing or 
        considerations that weren't fully addressed, share those insights constructively.
        Think step by step, then state your proposed answer prefixed with 'Answer:'."""
    else:
        # Later rounds: Consider and potentially synthesize
        system = """You are in a reflective phase of the discussion. Consider both your original thoughts and the other perspective shared. 
        Your goal is to provide the most thoughtful response - this might mean refining your view, finding common ground, or respectfully maintaining your position if you believe it's well-reasoned.
        Think step by step, then state your proposed answer prefixed with 'Answer:'."""
    
    messages = [{"role": "system", "content": system}]
    if context:
        messages.append({"role": "user", "content": f"Opponent said:\n{context}"})
    messages.append({"role": "user", "content": question})
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"GPT-4 API call failed: {e}")

def claude_propose(question, context=None, round_num=1, max_rounds=6):
    if round_num <= 3:
        # Early rounds: Present your perspective thoroughly
        system_prompt = """You are engaged in a thoughtful discussion to explore different viewpoints on a question. 
        Please share your perspective clearly and comprehensively. If you notice aspects or considerations that the other viewpoint might not have fully explored, 
        feel free to bring those up in a constructive way.
        Think step by step, then state your proposed answer prefixed with 'Answer:'."""
    else:
        # Later rounds: Consider and potentially synthesize
        system_prompt = """You are in a reflective phase of the discussion. Please thoughtfully consider both your initial perspective and what the other participant has shared. 
        Aim to provide the most thoughtful response - whether that means adjusting your view, finding areas of agreement, or respectfully maintaining your position if you feel it's well-reasoned.
        Think step by step, then state your proposed answer prefixed with 'Answer:'."""
    
    messages = []
    if context:
        messages.append({"role": "assistant", "content": context})
    messages.append({"role": "user", "content": question})
    
    try:
        resp = claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=600,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )
        return resp.content[0].text.strip()
    except Exception as e:
        raise Exception(f"Claude API call failed: {e}")

# ——— Check for explicit agreement using LLM ———
def check_explicit_agreement_with_gpt(response: str, previous_response: str) -> bool:
    """
    Use GPT-4 to determine if the response shows explicit agreement with the previous response.
    """
    prompt = f"""
    I will show you two responses in a discussion. Please respond ONLY with "Yes" if the second response 
    explicitly agrees with or defers to the first response, or "No" if it maintains a different position.
    
    Look for explicit agreement, concession, or acknowledgment that the other view is correct.
    
    First response:
    {previous_response}
    --------------------------------
    Second response:
    {response}
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You determine if someone is explicitly agreeing with another person's viewpoint."},
                      {"role": "user", "content": prompt}],
            temperature=0.0
        )
        verdict = resp.choices[0].message.content.strip().lower()
        return verdict.startswith("yes")
    except Exception as e:
        print(f"Warning: Could not check agreement: {e}")
        return False  # Default to no agreement if check fails

# ——— New: Ask GPT to judge equivalence ———
def check_equivalence_with_gpt(ans1: str, ans2: str) -> bool:
    """
    Returns True if GPT-4 judges ans1 and ans2 to be semantically equivalent.
    """
    prompt = f"""
        I will give you two proposed answers to the same question. 
        Please respond ONLY with "Yes" if they are semantically equivalent (i.e., they mean the same thing), 
        or "No" otherwise.

        Answer A:
        {ans1}
        --------------------------------
        Answer B:
        {ans2}
        """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You compare two answers for semantic equivalence."},
                      {"role": "user", "content": prompt}],
            temperature=0.0
        )
        verdict = resp.choices[0].message.content.strip().lower()
        return verdict.startswith("yes")
    except Exception as e:
        print(f"Warning: Could not check answer equivalence: {e}")
        return False  # Default to not equivalent if check fails

# ——— Debate loop orchestrator ———
def debate(question, max_rounds=6):
    gpt_ctx = None
    claude_ctx = None

    for round_idx in range(1, max_rounds + 1):
        print(f"\n=== Round {round_idx} ===")
        if round_idx <= 3:
            print("(Exploration phase: Each AI shares their perspective)")
        else:
            print("(Reflection phase: AIs consider both viewpoints)")

        # Each model proposes
        gpt_out = gpt_propose(question, context=claude_ctx, round_num=round_idx, max_rounds=max_rounds)
        claude_out = claude_propose(question, context=gpt_ctx, round_num=round_idx, max_rounds=max_rounds)

        print("\n--- GPT-4 says ---\n", gpt_out)
        print("\n--- Claude says ---\n", claude_out)

        # Extract the final 'Answer:' lines
        def extract_answer(text):
            for line in text.splitlines():
                if line.strip().lower().startswith("answer:"):
                    return line.split("Answer:", 1)[1].strip()
            return None

        # Check for explicit agreement in both directions
        gpt_agrees_with_claude = check_explicit_agreement_with_gpt(gpt_out, claude_out)
        claude_agrees_with_gpt = check_explicit_agreement_with_gpt(claude_out, gpt_out)
        
        if gpt_agrees_with_claude:
            print(f"\n🤝 GPT-4 explicitly agrees with Claude! Discussion concluded.")
            return extract_answer(claude_out) or claude_out
        
        if claude_agrees_with_gpt:
            print(f"\n🤝 Claude explicitly agrees with GPT-4! Discussion concluded.")
            return extract_answer(gpt_out) or gpt_out

        gpt_ans = extract_answer(gpt_out)
        claude_ans = extract_answer(claude_out)

        if gpt_ans and claude_ans:
            # Use GPT itself to decide if they're equivalent
            if check_equivalence_with_gpt(gpt_ans, claude_ans):
                print(f"\n🤝 Both agree (per GPT) on: {gpt_ans}")
                return gpt_ans

        # Otherwise, feed each model the other's full output for next rebuttal
        gpt_ctx = gpt_out
        claude_ctx = claude_out

    # Fallback if no consensus
    print("\n⚠️ No consensus reached after max rounds. Defaulting to GPT-4’s last answer:")
    return gpt_ans

# ——— Example usage ———
if __name__ == "__main__":
    # Check if API keys are set
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key:
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    if not anthropic_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it with: export ANTHROPIC_API_KEY='your-api-key-here'")
        exit(1)
    
    print("✅ API keys found")
    question = input("Enter your question: ")
    
    try:
        final_answer = debate(question)
        print("\n=== Final Answer ===\n", final_answer)
    except Exception as e:
        print(f"\n❌ Error during debate: {e}")
        print("\nPossible solutions:")
        print("1. Check your internet connection")
        print("2. Verify your OpenAI API key is valid and has credits")
        print("3. Verify your Anthropic API key is valid")
        print("4. Try again in a few minutes (APIs might be temporarily down)")