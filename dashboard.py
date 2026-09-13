"""Streamlit launcher for the same reviewed HTML artifact; no second scoring engine."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="FIRELINE · Peta Prioritas",page_icon="🌿",layout="wide")
root=Path(__file__).resolve().parent
artifact=root/"review_outputs"/"FIRELINE_Priority_Map.html"
if not artifact.exists():
    st.info("Data dashboard belum dibangun. Jalankan python -m fireline.pipeline atau notebook 06 terlebih dahulu.")
    st.stop()
st.markdown('<style>.block-container{padding:0.5rem 1rem;max-width:none}footer{display:none}</style>',unsafe_allow_html=True)
# Trusted local template and JSON escaping in render.py; no HTML from user input.
components.html(artifact.read_text(encoding="utf-8"),height=1900,scrolling=True)
