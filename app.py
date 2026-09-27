import streamlit as st
import google.generativeai as genai
import pypdf
from PIL import Image

# 1. Page Title & UI Configuration
st.set_page_config(page_title="Bloom's Taxonomy Question Generator", layout="wide")
st.title("📚 LLM-based Bloom's Taxonomy Question Paper Generator")

# 2. Sidebar for API Key (ਸੁਰੱਖਿਅਤ ਤਰੀਕਾ)
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)

# 3. File Upload (PDF/Image) & Text Input
st.subheader("1. Upload Study Material (PDF / Image) or Paste Text")
uploaded_file = st.file_uploader("Upload PDF or Image (JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"])
text_input = st.text_area("Or Paste Content/Syllabus Here", height=150)

extracted_text = ""
loaded_image = None

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == "pdf":
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() or ""
    elif file_type in ["png", "jpg", "jpeg"]:
        loaded_image = Image.open(uploaded_file)
        st.image(loaded_image, caption="Uploaded Image Preview", use_container_width=True)

elif text_input:
    extracted_text = text_input

# 4. Bloom's Taxonomy Question Distribution
st.subheader("2. Select Questions Count for Bloom's Taxonomy Levels")
col1, col2, col3 = st.columns(3)

with col1:
    remember_count = st.number_input("Remember (Level 1)", min_value=0, value=2)
    understand_count = st.number_input("Understand (Level 2)", min_value=0, value=2)

with col2:
    apply_count = st.number_input("Apply (Level 3)", min_value=0, value=1)
    analyze_count = st.number_input("Analyze (Level 4)", min_value=0, value=1)

with col3:
    evaluate_count = st.number_input("Evaluate (Level 5)", min_value=0, value=1)
    create_count = st.number_input("Create (Level 6)", min_value=0, value=1)

# 5. Generate Button Action
if st.button("🚀 Generate Question Paper"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar!")
    elif not extracted_text and loaded_image is None:
        st.warning("Please upload a PDF/Image or enter some text content.")
    else:
        with st.spinner("Generating Question Paper based on Bloom's Taxonomy..."):
            prompt = f"""
            You are an expert educator. Create a Question Paper based strictly on the provided content using Bloom's Taxonomy.

            Generate questions in the following exact breakdown:
            - {remember_count} Remembering Questions (e.g., Define, List, Recall)
            - {understand_count} Understanding Questions (e.g., Explain, Describe, Summarize)
            - {apply_count} Applying Questions (e.g., Solve, Use, Demonstrate)
            - {analyze_count} Analyzing Questions (e.g., Compare, Categorize, Differentiate)
            - {evaluate_count} Evaluating Questions (e.g., Justify, Critique, Judge)
            - {create_count} Creating Questions (e.g., Design, Formulate, Construct)

            Formatting Requirements:
            1. Group questions by Bloom's Taxonomy level with clear headings.
            2. Mention marks for each question (e.g., [2 Marks], [5 Marks]).
            3. Provide a brief Answer Key / Marking Scheme at the end.
            """

            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # If Image is uploaded
                if loaded_image is not None:
                    response = model.generate_content([prompt, loaded_image])
                else:
                    full_prompt = f"{prompt}\n\nText Content:\n{extracted_text[:4000]}"
                    response = model.generate_content(full_prompt)
                
                st.success("Question Paper Generated Successfully!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error generating question paper: {e}")
