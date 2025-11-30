import streamlit as st
import pandas as pd
import ast

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
    .stCheckbox > label {
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .stButton > button {
        font-weight: 600;
        font-size: 1rem;
    }
    h3 {
        color: #1f77b4;
        margin-top: 1.5rem;
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

# 0-50 to Alex
last_label = 0
stance_dict_reverse = {v: k for k, v in stance_dict.items()} 
samples_df = pd.read_csv("samples.csv")
contexts = samples_df["Context"].tolist()[last_label:last_label+50]
comments = samples_df["Comment"].tolist()[last_label:last_label+50]
gt = pd.read_csv("ai_gt.csv")
gts = gt["matched_stances"].tolist()[last_label:last_label+50]


sample_stances = []
for i, row in gt.iterrows():
    try:
        matched_stances = ast.literal_eval(row["matched_stances"])
    except:
        print("problem with matched_stances")
        print(row["matched_stances"])
        break
    stances = []
    for stance in matched_stances:
        try:
            stances.append(stance_dict_reverse[stance])
        except:
            print("problem with stance")
            print(stance)
            break
    sample_stances.append(stances)

gts = []
for i in range(len(contexts)):
    gt = 28 * [0]
    if 29 in sample_stances[i]:
        gts.append(gt)
        continue
    for stance in sample_stances[i]:
        gt[stance - 1] = 1
    gts.append(gt)

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
    st.markdown("### ✅ Verify AI Labels")
    st.caption("Check or uncheck boxes to modify the stance labels as needed")
    
    # We use a form so the page doesn't reload on every checkbox click
    with st.form(key='verification_form'):
        
        # Display stances in a grid (2 columns within the right side) to save space
        grid_cols = st.columns(2, gap="medium")
        
        # Dynamic dictionary to hold widget states
        user_selections = {}
        
        # Count pre-selected items for summary
        pre_selected_count = sum(current_labels)
        
        for i, stance in enumerate(STANCE_LIST):
            # Determine if this stance was originally labeled (1) or not (0)
            is_pre_selected = bool(current_labels[i])
            
            # Place in grid
            col_idx = i % 2
            with grid_cols[col_idx]:
                # Add visual indicator for pre-selected items
                if is_pre_selected:
                    label_with_indicator = f"✓ {stance}"
                else:
                    label_with_indicator = stance
                
                user_selections[i] = st.checkbox(
                    label=label_with_indicator,
                    value=is_pre_selected,
                    key=f"stance_{st.session_state.current_index}_{i}"
                )

        st.markdown("---")
        
        # Summary and submit button
        col_summary, col_button = st.columns([2, 1])
        with col_summary:
            st.caption(f"📊 Pre-labeled: **{pre_selected_count}** stance(s) | Review and adjust as needed")
        
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