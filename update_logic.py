import os
import re

filepath = r'c:\Users\USER\Desktop\Final Year Project\timetable_project\app_ui.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update hard constraints to use session_state
hard_search = r'    hard_input = st\.text_area\(\s*"Define Hard Constraints:",\s*value="[^"]+",\s*height=100\s*\)'
hard_replace = '''    hard_input = st.text_area(
        "Define Hard Constraints:",
        value=st.session_state.get("hard_constraints", "No overlapping classes for lecturers.\\nLarge classes above 200 students must use large halls."),
        height=100
    )'''
content = re.sub(hard_search, hard_replace, content)

content = content.replace('st.session_state.current_page = "Soft Constraints"', 'st.session_state.hard_constraints = hard_input\n        st.session_state.current_page = "Soft Constraints"')

# 2. Update soft constraints to use session_state
soft_search = r'    soft_input = st\.text_area\(\s*"Define Soft Preferences:",\s*value="[^"]+",\s*height=100\s*\)'
soft_replace = '''    soft_input = st.text_area(
        "Define Soft Preferences:",
        value=st.session_state.get("soft_constraints", "Morning classes are preferred.\\nAvoid scheduling lectures late on Fridays."),
        height=100
    )'''
content = re.sub(soft_search, soft_replace, content)

content = content.replace('st.session_state.current_page = "Generator"', 'st.session_state.soft_constraints = soft_input\n        st.session_state.current_page = "Generator"')

# 3. Update Generator execution block
gen_search = r'        # Determine schedule calculations based on uploaded CSV dataset\s+if st\.session_state\.uploaded_file_data is not None:\s+st\.session_state\.timetable_data = local_full_deterministic_scheduler\(st\.session_state\.uploaded_file_data\)\s+st\.success\(f"Successfully scheduled all \{len\(st\.session_state\.timetable_data\)\} courses from your dataset!"\)\s+else:\s+st\.session_state\.timetable_data = default_mock_timetable\s+st\.session_state\.fitness = evaluate_timetable\(st\.session_state\.timetable_data\)\["fitness"\]'

gen_replace = '''        # Determine schedule calculations based on uploaded CSV dataset
        combined_constraints = st.session_state.get("hard_constraints", "") + "\\n" + st.session_state.get("soft_constraints", "")
        
        backend_success = False
        try:
            # Send constraints to backend
            requests.post(f"{BACKEND_URL}/api/constraints", json={"text": combined_constraints}, timeout=5)
            
            # Execute backend generator
            gen_res = requests.post(f"{BACKEND_URL}/api/generate?generations=50", timeout=120)
            if gen_res.status_code == 200:
                # Fetch resulting timetable
                tt_res = requests.get(f"{BACKEND_URL}/api/timetable", timeout=5)
                if tt_res.status_code == 200:
                    st.session_state.timetable_data = tt_res.json().get("data", [])
                    st.success(f"Hyper-Heuristic Engine successfully generated optimal schedule! ({len(st.session_state.timetable_data)} courses)")
                    backend_success = True
        except Exception as e:
            st.warning(f"Backend offline or timeout ({e}). Falling back to local deterministic solver.")
            
        if not backend_success:
            if st.session_state.uploaded_file_data is not None:
                st.session_state.timetable_data = local_full_deterministic_scheduler(st.session_state.uploaded_file_data)
                st.success(f"Successfully scheduled all {len(st.session_state.timetable_data)} courses locally.")
            else:
                st.session_state.timetable_data = default_mock_timetable
                
        st.session_state.fitness = evaluate_timetable(st.session_state.timetable_data).get("fitness", 0)'''

content = re.sub(gen_search, gen_replace, content)

# 4. Update the Data upload block to POST to backend
upload_search = r'            df_preview = pd\.read_csv\(uploaded_file\)\s+st\.session_state\.uploaded_file_data = df_preview\s+st\.success\("Dataset loaded successfully\."\)'

upload_replace = '''            df_preview = pd.read_csv(uploaded_file)
            st.session_state.uploaded_file_data = df_preview
            st.success("Dataset loaded successfully.")
            
            # Send to backend
            if "file_uploaded_to_backend" not in st.session_state or st.session_state.file_uploaded_to_backend != uploaded_file.name:
                try:
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    res = requests.post(f"{BACKEND_URL}/api/upload", files=files, timeout=5)
                    if res.status_code == 200:
                        st.session_state.file_uploaded_to_backend = uploaded_file.name
                        # st.toast("Dataset synchronized with AI Engine.")
                except Exception as e:
                    pass'''

content = re.sub(upload_search, upload_replace, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated app_ui.py to use backend endpoints and session_state constraints!')
