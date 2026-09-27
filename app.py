import streamlit as st
import google.generativeai as genai
import pypdf
from PIL import Image
from fpdf import FPDF

# Page Setup
st.set_page_config(page_title="Bloom's Taxonomy Question Generator", layout="wide")
st.title("📚 LLM-based Bloom's Taxonomy Question Paper Generator")

# Streamlit Secrets ਤੋਂ API Key ਪ੍ਰਾਪਤ ਕਰਨਾ (ਇੱਥੇ Variable ਦਾ ਨਾਮ ਲਿਖਣਾ ਹੈ)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key ਨਹੀ ਮਿਲੀ! ਕਿਰਪਾ ਕਰਕੇ Streamlit Secrets ਵਿੱਚ GEMINI_API_KEY ਸੈੱਟ ਕਰੋ।")

# Function to create PDF
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    
    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 8, txt=line)
    
    return pdf.output(dest='S').encode('latin-1')

# Main UI
st.subheader("1. Upload Study Material (PDF / Image / Text)")

# PDF, PNG, JPG ਅਪਲੋਡ ਕਰਨ ਦੀ ਆਪਸ਼ਨ
uploaded_file = st.file_uploader("Upload PDF or Image File (JPG/PNG)", type=["pdf", "png", "jpg", "jpeg"])
text_input = st.text_area("Or Paste Content/Syllabus Here", height=150)

extracted_text = ""
uploaded_image = None

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() or ""
    else:
        # ਫੋਟੋ (Image) ਪ੍ਰੋਸੈਸ ਕਰਨ ਲਈ
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="Uploaded Image Preview", use_container_width=True)

elif text_input:
    extracted_text = text_input

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

if st.button("🚀 Generate Question Paper"):
    if not extracted_text and uploaded_image is None:
        st.warning("Please upload a PDF/Image or enter some text content.")
    else:
        with st.spinner("Generating Question Paper based on Bloom's Taxonomy..."):
            prompt = f"""
            You are an expert educator. Create a Question Paper based strictly on the provided content using Bloom's Taxonomy.

            Generate questions in the following exact breakdown:
            - {remember_count} Remembering Questions
            - {understand_count} Understanding Questions
            - {apply_count} Applying Questions
            - {analyze_count} Analyzing Questions
            - {evaluate_count} Evaluating Questions
            - {create_count} Creating Questions

            Formatting Requirements:
            1. Group questions by Bloom's Taxonomy level with clear headings.
            2. Mention marks for each question.
            3. Provide a brief Answer Key / Marking Scheme at the end.
            """

            try:
                model = genai.GenerativeModel("gemini-3.8-flash")
                
                # ਜੇ ਫੋਟੋ ਅਪਲੋਡ ਕੀਤੀ ਹੈ ਤਾਂ Gemini Multi-modal ਵਰਤਿਆ ਜਾਵੇਗਾ
                if uploaded_image is not None:
                    response = model.generate_content([prompt, uploaded_image])
                else:
                    full_prompt = f"{prompt}\n\nText Content:\n{extracted_text[:4000]}"
                    response = model.generate_content(full_prompt)
                
                st.session_state['generated_paper'] = response.text
                st.success("Question Paper Generated Successfully!")
                
            except Exception as e:
                st.error(f"Error generating question paper: {e}")

# Display Generated Paper and Download Option
if 'generated_paper' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['generated_paper'])
    
    pdf_data = create_pdf(st.session_state['generated_paper'])
    st.download_button(
        label="📥 Download Question Paper as PDF",
        data=pdf_data,
        file_name="Question_Paper.pdf",
        mime="application/pdf"
    )
