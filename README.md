#  CreativeAI Studio: The Automated Creative Engine

**Tagline:** An AI-powered creative engine that transforms a single logo and product image into 10+ high-quality ad variations with compelling captions in under 60 seconds.

---

## 1. The Problem (Real World Scenario)
**Context:** Small businesses waste **15-20 hours/week** manually designing ad variations.
**Pain Point:** Manual design is slow, expensive (-150/variation), and delays campaigns.
**Solution:** **CreativeAI Studio** automates this. Upload assets -> Get 10+ professional ads + captions in 60s.

---

## 2. Expected End Result
**Input:** Brand Logo + Product Image.
**Action:** Click 'Generate' -> Wait 60s.
**Output:** ZIP file containing:
- 10+ High-Res Ad Variations (1024x1024px)
- AI-Generated Captions (captions.json)
- PDF Creative Report

---

## 3. Technical Approach
**Architecture:**
1.  **Intelligent Analysis:** **Gemini 1.5 Pro** analyzes the product (e.g., 'yellow headphones') to understand context.
2.  **Smart Composition:**
    -   **Background Removal:** rembg isolates the product.
    -   **Shadow Generation:** Custom algorithm adds realistic shadows for depth.
    -   **Scene Generation:** **FLUX.1-schnell** creates photorealistic backgrounds.
3.  **Generative AI:**
    -   **Image:** FLUX.1-schnell (Free, High Quality).
    -   **Text:** Gemini 1.5 Pro (Free, Advanced Reasoning).
4.  **Orchestration:** Gradio UI + ReportLab for PDF generation.

---

## 4. Tech Stack
-   **Language:** Python 3.11
-   **UI:** Gradio
-   **AI Models:** FLUX.1-schnell (Hugging Face), Gemini 1.5 Pro (Google)
-   **Processing:** OpenCV, PIL, Rembg

---

## 5. Challenges & Learnings
1.  **The 'Sticker Effect':** Product looked fake on backgrounds.
    -   *Solution:* Implemented a custom **Shadow Generation Algorithm** to ground the product.
2.  **Background Relevance:** Random backgrounds clashed.
    -   *Solution:* Used **Gemini Vision** to analyze the product first and generate matching scenes (e.g., 'tech studio' for headphones).

---

## 6. Visual Proof
*(Add Screenshots Here)*
-   **Input:** Raw Product Image.
-   **Output:** Professional Ad Creative with Shadow & Context.

---

## 7. How to Run
\\\ash
# 1. Clone Repo
git clone https://github.com/Abhiram678/GT_AI_Hackathon.git
cd GT_AI_Hackathon

# 2. Install Deps
pip install -r requirements.txt

# 3. Add Keys (.env)
# HUGGINGFACE_TOKEN=hf_...
# GEMINI_API_KEY=AIza_...

# 4. Run
python app.py
\\\
*Open http://127.0.0.1:7860*

---
**Note:** Uses **Free Tier** models for accessibility. Enterprise-ready architecture allows swapping for DALL-E 3 / GPT-4.
