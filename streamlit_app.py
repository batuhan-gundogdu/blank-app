import streamlit as st
import pandas as pd

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .comment-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .context-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stance-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    .stance-item:hover {
        background-color: #f0f0f0;
    }
    .progress-container {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    .stance-group-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06);
        border: 1px solid #e0e0e0;
    }
    .stance-group-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    /* Style for content inside group boxes */
    div.stance-group-box ~ div {
        margin-left: 0;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. SETUP: DEFINING INPUTS
# -----------------------------------------------------------------------------

# A. The 28 Stances (Transcribed from your image headers)
stance_dict = {1:"Criticism of police and federal detainment practices as abuse of power",
2:"Support for police and federal detainment practices as necessary for law and order",
3:"Support for higher taxes for government involvement",
4:"Criticism of high taxes for government involvement",
5:"Criticism of illegal immigration",
6:"Support for pathway to citizenship for undocumented immigrants",
7:"Support for universal healthcare",
8:"Opposition to government-funded healthcare",
9:"Support for abortion rights",
10:"Support for abortion ban",
11:"Support for LGBTQ+ rights and same-sex marriage",
12:"Opposition to LGBTQ+ rights and same-sex marriage",
13:"Support for gun ownership rights",  
14:"Support for stricter gun control laws",
15:"Support for strong national defense spending",
16:"Criticism of military intervention and spending",
17:"Support for renewable energy and climate action",
18:"Criticism of climate change policies as economically harmful",
19:"Support for legalization of marijuana",
20:"Opposition to legalization of marijuana",
21:"Criticism of Democrats or Liberals",
22:"Criticism of Republicans or Conservatives",
23:"Criticism of Donald Trump or Republican Party Leadership",
24:"Criticism of Joe Biden, Kamala Harris or Democratic Party Leadership",  
25:"Support for Donald Trump or Republican Party Leadership",
26:"Support for Joe Biden, Kamala Harris or Democratic Party Leadership",
27:"Criticism of Local Government or Mayor",
28:"Praise for Local Government or Mayor",
29:"Does not express any politically relevant opinion"}

# B. Group stances by topic
stance_groups = [
    {"title": "Police", "indices": [0, 1]},  # 1-2
    {"title": "Taxes", "indices": [2, 3]},  # 3-4
    {"title": "Immigration", "indices": [4, 5]},  # 5-6
    {"title": "Healthcare", "indices": [6, 7]},  # 7-8
    {"title": "Abortion", "indices": [8, 9]},  # 9-10
    {"title": "LGBTQ+", "indices": [10, 11]},  # 11-12
    {"title": "Gun Control", "indices": [12, 13]},  # 13-14
    {"title": "Military/Defense", "indices": [14, 15]},  # 15-16
    {"title": "Climate/Energy", "indices": [16, 17]},  # 17-18
    {"title": "Marijuana", "indices": [18, 19]},  # 19-20
    {"title": "Political Parties (General)", "indices": [20, 21]},  # 21-22
    {"title": "Political Leadership (Criticism)", "indices": [22, 23]},  # 23-24
    {"title": "Political Leadership (Support)", "indices": [24, 25]},  # 25-26
    {"title": "Local Government", "indices": [26, 27]},  # 27-28
]

# 0-50 to Alex
last_label = 0
samples_df = pd.read_csv("samples.csv")
contexts = samples_df["Context"].tolist()[last_label:last_label+50]
comments = samples_df["Comment"].tolist()[last_label:last_label+50]

# Initialize all labels as zeros (no pre-labeling)
gts = []
for i in range(len(contexts)):
    gts.append(28 * [0])

def load_data():
    data = []
    for i in range(len(contexts)):
        data.append({
            "context": contexts[i],
            "comment": comments[i],
            "labels": gts[i]
        })
    return data

STANCE_LIST = list(stance_dict.values())[:-1]
# -----------------------------------------------------------------------------
# 2. STREAMLIT APP LOGIC
# -----------------------------------------------------------------------------

st.set_page_config(
    layout="wide", 
    page_title="Stance Verifier",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'verified_results' not in st.session_state:
    st.session_state.verified_results = []

# Helper to verify if we are done
if st.session_state.current_index >= len(st.session_state.data):
    st.markdown("<h1 class='main-header'>✅ Verification Complete!</h1>", unsafe_allow_html=True)
    st.success("🎉 You have successfully reviewed all comments!")
    
    # Convert results to DataFrame
    df_results = pd.DataFrame(st.session_state.verified_results)
    
    # Download button with better styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Download Verified Data (CSV)",
            data=df_results.to_csv(index=False).encode('utf-8'),
            file_name='verified_stances.csv',
            mime='text/csv',
            use_container_width=True,
            type="primary"
        )
    st.stop()

# Get current item
current_item = st.session_state.data[st.session_state.current_index]
current_labels = current_item['labels']

# -----------------------------------------------------------------------------
# 3. UI LAYOUT
# -----------------------------------------------------------------------------

# Header with title and progress
st.markdown("<h1 class='main-header'>📊 Stance Verification Tool</h1>", unsafe_allow_html=True)

# Progress section with better styling
progress_pct = st.session_state.current_index / len(st.session_state.data)
col_prog1, col_prog2, col_prog3 = st.columns([1, 3, 1])
with col_prog2:
    st.markdown(f"### 📝 Comment {st.session_state.current_index + 1} of {len(st.session_state.data)}")
    st.progress(progress_pct)
    st.caption(f"Progress: {int(progress_pct * 100)}% ({st.session_state.current_index}/{len(st.session_state.data)})")

st.markdown("---")

# Create two main columns: Left (Comment), Right (Stances)
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.markdown("### 📄 Content")
    
    # Context section with better styling
    with st.container():
        st.markdown("**🌐 Context:**")
        st.markdown(
            f'<div class="context-box">{current_item["context"]}</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("")
    
    # Comment section with better styling
    with st.container():
        st.markdown("**💬 Comment:**")
        st.markdown(
            f'<div class="comment-box">{current_item["comment"]}</div>',
            unsafe_allow_html=True
        )

with col_right:
    st.markdown("### ✅ Select Stances")
    st.caption("Check the boxes for all stances that apply to this comment")
    
    # We use a form so the page doesn't reload on every checkbox click
    with st.form(key='verification_form'):
        
        # Dynamic dictionary to hold widget states
        user_selections = {}
        
        # Display stances grouped by topic in boxes
        for group in stance_groups:
            # Create the group box with title
            st.markdown(
                f'<div class="stance-group-box">'
                f'<div class="stance-group-title">{group["title"]}</div>',
                unsafe_allow_html=True
            )
            
            # Display checkboxes for stances in this group
            for idx in group["indices"]:
                stance_text = STANCE_LIST[idx]
                user_selections[idx] = st.checkbox(
                    label=stance_text,
                    value=False,
                    key=f"stance_{st.session_state.current_index}_{idx}"
                )
            
            # Close the box div
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Summary and submit button
        col_summary, col_button = st.columns([2, 1])
        with col_summary:
            st.caption("📊 Select the appropriate stance(s) for this comment")
        
        with col_button:
            # Submit button with better styling
            submit_button = st.form_submit_button(
                label="✅ Verify & Next ➡️",
                use_container_width=True,
                type="primary"
            )

# -----------------------------------------------------------------------------
# 4. HANDLE SUBMISSION
# -----------------------------------------------------------------------------

if submit_button:
    # Construct the final validated 28-D vector
    final_vector = [1 if user_selections[i] else 0 for i in range(28)]
    
    # Save result
    result_entry = {
        "original_index": st.session_state.current_index,
        "context": current_item['context'],
        "comment": current_item['comment'],
    }
    
    # Add named columns for the CSV
    for i, stance_name in enumerate(STANCE_LIST):
        result_entry[stance_name] = final_vector[i]
        
    st.session_state.verified_results.append(result_entry)
    
    # Move to next
    st.session_state.current_index += 1
    st.rerun()