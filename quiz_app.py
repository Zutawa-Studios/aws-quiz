import streamlit as st
import json
import random
import os
from datetime import datetime
import pandas as pd

def reset_session_state():
    """Reset all session state variables"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()

def load_questions():
    """Load questions from the database"""
    if not os.path.exists('data/questions_db.json'):
        return None
    
    with open('data/questions_db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_test_result(name, score, total, wrong_questions, test_date):
    """Save test result to file"""
    os.makedirs('results', exist_ok=True)
    
    result = {
        'name': name,
        'date': test_date,
        'score': score,
        'total': total,
        'percentage': round((score / total) * 100, 2),
        'wrong_questions': wrong_questions
    }
    
    filename = f"results/test_{test_date.replace(':', '-').replace(' ', '_')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return filename

def load_previous_results():
    """Load all previous test results"""
    if not os.path.exists('results'):
        return []
    
    results = []
    for filename in os.listdir('results'):
        if filename.startswith('test_') and filename.endswith('.json'):
            with open(f'results/{filename}', 'r', encoding='utf-8') as f:
                results.append(json.load(f))
    
    return sorted(results, key=lambda x: x['date'], reverse=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'test_completed' not in st.session_state:
        st.session_state.test_completed = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'result_saved' not in st.session_state:
        st.session_state.result_saved = False

def start_new_test(questions, name):
    """Start a new test"""
    selected = random.sample(questions, min(40, len(questions)))
    
    st.session_state.test_started = True
    st.session_state.current_question = 0
    st.session_state.selected_questions = selected
    st.session_state.user_answers = {}
    st.session_state.test_completed = False
    st.session_state.user_name = name
    st.session_state.result_saved = False

def main():
    st.set_page_config(page_title="AWS Certification Quiz", layout="wide")
    
    # Load questions
    questions = load_questions()
    
    if questions is None:
        st.error("❌ No question database found! Please run the Question Aggregator first.")
        st.info("Run `streamlit run aggregator.py` to create the question database.")
        return
    
    initialize_session_state()
    
    # Main navigation
    if not st.session_state.test_started:
        st.title("🚀 AWS Certification Quiz")
        st.markdown("### Ready to test your AWS knowledge?")
        
        # Navigation tabs
        tab1, tab2 = st.tabs(["🆕 New Test", "📊 Previous Results"])
        
        with tab1:
            st.markdown("---")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info(f"📚 **{len(questions)}** questions available in database")
                st.info("🎯 **40** random questions will be selected for your test")
                
                # User name input
                name = st.text_input("👤 Enter your name:", placeholder="Your name here...")
                name = name.strip()[:50]  # Limit length and trim spaces
                
                if st.button("🚀 Start New Test", type="primary", disabled=not name.strip()):
                    start_new_test(questions, name.strip())
                    st.rerun()
            
            with col2:
                st.markdown("### 📋 Test Info")
                st.markdown("- **Questions:** 40")
                st.markdown("- **Time:** Unlimited")
                st.markdown("- **Format:** Multiple Choice")
                st.markdown("- **Passing:** 70%")
        
        with tab2:
            st.markdown("---")
            results = load_previous_results()
            
            if results:
                st.subheader("📈 Previous Test Results")
                
                # Create summary table
                df_data = []
                for result in results:
                    df_data.append({
                        'Name': result['name'],
                        'Date': result['date'],
                        'Score': f"{result['score']}/{result['total']}",
                        'Percentage': f"{result['percentage']}%",
                        'Status': "✅ Pass" if result['percentage'] >= 70 else "❌ Fail"
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                # Detailed view
                if st.checkbox("📋 Show detailed results"):
                    for result in results[:5]:  # Show last 5 results
                        with st.expander(f"{result['name']} - {result['date']} ({result['percentage']}%)"):
                            st.write(f"**Score:** {result['score']}/{result['total']} ({result['percentage']}%)")
                            if result['wrong_questions']:
                                st.write("**Questions answered incorrectly:**")
                                for i, wrong in enumerate(result['wrong_questions'], 1):
                                    st.write(f"{i}. {wrong['question']}")
                                    st.write(f"   Your answer: {wrong['user_answer']}")
                                    st.write(f"   Correct answer: {wrong['correct_answer']}")
            else:
                st.info("📝 No previous test results found.")
    
    elif st.session_state.test_started and not st.session_state.test_completed:
        # Test in progress
        current_q_num = st.session_state.current_question
        total_questions = len(st.session_state.selected_questions)
        current_question = st.session_state.selected_questions[current_q_num]
        
        # Header
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.title("📝 AWS Certification Quiz")
        with col2:
            st.metric("Question", f"{current_q_num + 1}/{total_questions}")
        with col3:
            st.metric("Progress", f"{round(((current_q_num + 1) / total_questions) * 100)}%")
        
        # Progress bar
        progress = (current_q_num + 1) / total_questions
        st.progress(progress)
        
        st.markdown("---")
        
        # Question display
        st.subheader(f"Question {current_q_num + 1}")
        question_text = current_question['question']

        # Check if multiple answers required
        is_multiple = isinstance(current_question['correct_answer'], list) and len(current_question['correct_answer']) > 1

        if is_multiple:
            st.markdown(f"**{question_text}** *(Select multiple answers)*")
            st.info("📝 This question requires multiple correct answers")
        else:
            st.markdown(f"**{question_text}**")

        # Options - handle both single and multiple selection
        option_key = f"question_{current_q_num}"

        if is_multiple:
            selected_options = []
            for opt in current_question['options']:
                if st.checkbox(f"{opt['letter']}. {opt['text']}", key=f"{option_key}_{opt['letter']}"):
                    selected_options.append(opt['letter'])
            selected_option = selected_options if selected_options else None
        else:
            selected_option = st.radio(
                "Select your answer:",
                options=[f"{opt['letter']}. {opt['text']}" for opt in current_question['options']],
                key=option_key,
                index=None
            )
            if selected_option:
                selected_option = selected_option[0]  # Get just the letter
        
        st.markdown("---")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_q_num > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if st.button("🏠 Quit Test", type="secondary"):
                st.session_state.test_started = False
                st.session_state.test_completed = False
                st.rerun()
        
        with col3:
            if selected_option:
                # Save answer (handle both single answer and multiple answers)
                if isinstance(selected_option, list):
                    st.session_state.user_answers[current_q_num] = selected_option
                else:
                    st.session_state.user_answers[current_q_num] = selected_option
                
                if current_q_num < total_questions - 1:
                    if st.button("Next ➡️", type="primary"):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("✅ Submit Test", type="primary"):
                        st.session_state.test_completed = True
                        st.rerun()
    
    elif st.session_state.test_completed:
        # Test completed - show results
        st.title("🎉 Test Completed!")
        
        # Calculate score
        correct_answers = 0
        wrong_questions = []
        total_questions = len(st.session_state.selected_questions)
        
        for i, question in enumerate(st.session_state.selected_questions):
            user_answer = st.session_state.user_answers.get(i, "")
            correct_answer = question['correct_answer']
            
            # Handle both single and multiple correct answers
            if isinstance(correct_answer, list):
                # Multiple correct answers
                user_set = set(user_answer) if isinstance(user_answer, list) else set()
                correct_set = set(correct_answer)
                is_correct = user_set == correct_set
            else:
                # Single correct answer
                is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_answers += 1
            else:
                wrong_questions.append({
                    'question': question['question'],
                    'options': question['options'],
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_multiple': isinstance(correct_answer, list)
                })
        
        percentage = round((correct_answers / total_questions) * 100, 2)
        
        # Save result only once
        test_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not st.session_state.result_saved:
            filename = save_test_result(
                st.session_state.user_name, 
                correct_answers, 
                total_questions, 
                wrong_questions, 
                test_date
            )
            st.session_state.result_saved = True
        
        # Display results
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Score", f"{correct_answers}/{total_questions}")
        with col2:
            st.metric("Percentage", f"{percentage}%")
        with col3:
            status = "✅ PASS" if percentage >= 70 else "❌ FAIL"
            st.metric("Result", status)
        with col4:
            st.metric("Date", test_date.split()[0])
        
        # Result message
        if percentage >= 70:
            st.success(f"🎉 Congratulations {st.session_state.user_name}! You passed the test!")
        else:
            st.error(f"📚 {st.session_state.user_name}, you need more practice. Keep studying!")
        
        if st.session_state.result_saved:
            st.info("💾 Results saved successfully!")
        
        # Wrong answers section
        if wrong_questions:
            st.markdown("---")
            st.subheader("📋 Review Incorrect Answers")
            
            for i, wrong in enumerate(wrong_questions, 1):
                with st.expander(f"Question {i} - You got this wrong"):
                    st.write(f"**Q:** {wrong['question']}")
                    
                    if wrong.get('is_multiple', False):
                        # Multiple choice question
                        correct_answers_set = set(wrong['correct_answer'])
                        user_answers_set = set(wrong['user_answer']) if isinstance(wrong['user_answer'], list) else set()
                        
                        for opt in wrong['options']:
                            if opt['letter'] in correct_answers_set:
                                st.success(f"✅ {opt['letter']}. {opt['text']} (Correct Answer)")
                            elif opt['letter'] in user_answers_set:
                                st.error(f"❌ {opt['letter']}. {opt['text']} (Your Selection)")
                            else:
                                st.write(f"⚪ {opt['letter']}. {opt['text']}")
                                
                        st.write(f"**Your answers:** {', '.join(wrong['user_answer']) if isinstance(wrong['user_answer'], list) else 'None selected'}")
                        st.write(f"**Correct answers:** {', '.join(wrong['correct_answer'])}")
                    else:
                        # Single choice question
                        for opt in wrong['options']:
                            if opt['letter'] == wrong['correct_answer']:
                                st.success(f"✅ {opt['letter']}. {opt['text']} (Correct Answer)")
                            elif opt['letter'] == wrong['user_answer']:
                                st.error(f"❌ {opt['letter']}. {opt['text']} (Your Answer)")
                            else:
                                st.write(f"⚪ {opt['letter']}. {opt['text']}")
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Take Another Test", type="primary"):
                reset_session_state()
                st.rerun()
        
        with col2:
            if st.button("📊 View All Results"):
                reset_session_state()
                st.rerun()

if __name__ == "__main__":
    main()