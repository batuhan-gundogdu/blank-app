import streamlit as st
import pandas as pd
import ast
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

stance_dict_reverse = {v: k for k, v in stance_dict.items()} 
samples_df = pd.read_csv("samples.csv")
contexts = samples_df["Context"].tolist()[:10]
comments = samples_df["Comment"].tolist()[:10]
gt = pd.read_csv("ai_gt.csv")
gts = gt["matched_stances"].tolist()[:10]


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

st.set_page_config(layout="wide", page_title="Stance Verifier")

# Initialize Session State
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'verified_results' not in st.session_state:
    st.session_state.verified_results = []

# Helper to verify if we are done
if st.session_state.current_index >= len(st.session_state.data):
    st.title("✅ Verification Complete!")
    st.write("You have reviewed all comments.")
    
    # Convert results to DataFrame
    df_results = pd.DataFrame(st.session_state.verified_results)
    
    # 5. Button to submit/download
    st.download_button(
        label="Download Verified Data (CSV)",
        data=df_results.to_csv(index=False).encode('utf-8'),
        file_name='verified_stances.csv',
        mime='text/csv',
    )
    st.stop()

# Get current item
current_item = st.session_state.data[st.session_state.current_index]
current_labels = current_item['labels']

# -----------------------------------------------------------------------------
# 3. UI LAYOUT
# -----------------------------------------------------------------------------

st.progress(st.session_state.current_index / len(st.session_state.data))
st.subheader(f"Comment {st.session_state.current_index + 1} of {len(st.session_state.data)}")

# Create two main columns: Left (Comment), Right (Stances)
col_left, col_right = st.columns([1, 2])

with col_left:
    st.info("**Context:**")
    st.markdown(f"> {current_item['context']}")
    
    st.warning("**Comment:**")
    st.write(f"{current_item['comment']}")

with col_right:
    st.write("**Verify Stances (Modify if necessary):**")
    
    # We use a form so the page doesn't reload on every checkbox click
    with st.form(key='verification_form'):
        
        # Display stances in a grid (2 columns within the right side) to save space
        grid_cols = st.columns(2)
        
        # Dynamic dictionary to hold widget states
        user_selections = {}
        
        for i, stance in enumerate(STANCE_LIST):
            # Determine if this stance was originally labeled (1) or not (0)
            is_pre_selected = bool(current_labels[i])
            
            # Highlight logic: Add an emoji or bold text if originally selected
            label_display = f"**{stance}**" if is_pre_selected else stance
            
            # Place in grid
            col_idx = i % 2
            with grid_cols[col_idx]:
                # 2. & 4. Toggle button allows Agree (keep as is) or Change
                user_selections[i] = st.checkbox(
                    label=stance, # Plain text for accessibility
                    value=is_pre_selected,
                    key=f"stance_{st.session_state.current_index}_{i}"
                )


        st.divider()
        
        # 3. Button to Verify/Submit for this specific comment
        submit_button = st.form_submit_button(label="Verify & Next Comment ➡")

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