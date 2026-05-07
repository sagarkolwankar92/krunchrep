import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pdfplumber
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="KrunchRep", layout="wide")
st.title("🔬 KrunchRep")
st.markdown("**Smart Number & Impact Dashboard for Academic Papers & Reports**")

# Input
url = st.text_input("Enter Paper / Report URL (PDF or webpage):", 
                    placeholder="https://arxiv.org/pdf/xxxx.xxxxx.pdf")

if st.button("Generate KrunchRep Dashboard", type="primary"):
    if not url:
        st.error("Please enter a URL")
    else:
        with st.spinner("Fetching and analyzing document..."):
            try:
                # Fetch content
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                text = ""
                if url.endswith('.pdf') or 'pdf' in url:
                    with pdfplumber.open(BytesIO(response.content)) as pdf:
                        for page in pdf.pages:
                            text += page.extract_text() or ""
                else:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                
                # Extract key numbers with context
                number_pattern = r'(?<!\w)([-+]?\d*\.?\d+|\d+[%])'
                matches = re.finditer(number_pattern, text)
                
                metrics = []
                for match in matches:
                    num = match.group(0)
                    start = max(0, match.start() - 80)
                    end = min(len(text), match.end() + 80)
                    context = text[start:end].strip().replace('\n', ' ')
                    page_approx = "N/A"  # Can be improved later
                    
                    # Simple impact coloring
                    impact = "neutral"
                    if any(x in context.lower() for x in ["significant", "increase", "higher", "improved", "positive"]):
                        impact = "green"
                    elif any(x in context.lower() for x in ["decrease", "lower", "reduced", "negative", "risk"]):
                        impact = "red"
                    
                    metrics.append({
                        "number": num,
                        "label": "Key Metric",
                        "context": context[:150] + "...",
                        "page": page_approx,
                        "impact": impact
                    })
                
                # Limit to top 12
                metrics = metrics[:12]
                
                # Dashboard
                st.success("✅ Dashboard Generated!")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    title = st.text_input("Dashboard Title", value="Key Impact Metrics from Study")
                with col2:
                    st.write("### Generated on")
                    st.write(datetime.now().strftime("%d %b %Y"))
                
                summary = st.text_area("TL;DR / Summary", value="Auto-generated summary would go here...", height=100)
                
                st.markdown("### Key Numbers & Impact")
                cols = st.columns(3)
                for i, m in enumerate(metrics):
                    with cols[i % 3]:
                        color = "#4CAF50" if m["impact"] == "green" else "#f44336" if m["impact"] == "red" else "#2196F3"
                        st.markdown(f"""
                        <div style="background: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 10px;">
                            <h3 style="margin:0;color:{color}">{m['number']}</h3>
                            <strong>{m['label']}</strong><br>
                            <small>{m['context']}</small><br>
                            <small style="color:#888">Page: {m['page']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("### Credits")
                st.info("**KrunchRep v1** • Built for Swati • Powered by Grok + Streamlit")
                
                # Download buttons
                st.markdown("### Download Dashboard")
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    st.download_button("📥 Download as PNG", "placeholder", file_name="krunchrep_dashboard.png")
                with col_d2:
                    st.download_button("📥 Download as JPEG", "placeholder", file_name="krunchrep_dashboard.jpg")
                with col_d3:
                    st.download_button("📥 Download as SVG", "placeholder", file_name="krunchrep_dashboard.svg")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
