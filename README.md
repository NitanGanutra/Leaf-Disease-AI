# 🌱 Agri-AI: The 99.3% Accurate Crop Doctor

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)](https://fastapi.tiangolo.com/)

**Agri-AI** is a high-performance deep learning system designed to help farmers identify crop diseases instantly. Built with a fine-tuned **MobileNetV2** architecture, this model achieved a staggering **99.3% validation accuracy** in distinguishing between 8 common Potato and Tomato diseases.

---

## 🚀 The Mission
In regions like Bihar, agriculture is the backbone of the economy. Agri-AI aims to bridge the gap between complex data science and the farmer's field by providing a simple, fast, and highly accurate diagnostic tool.
## 📱 App Preview
![AgriVision Dashboard](./assets/sample_output.png)
## ✨ Key Features
- **99.3% Precision:** High-confidence detection using state-of-the-art Transfer Learning.
- **Lightning Fast:** Powered by MobileNetV2, designed to run efficiently even on mobile devices.
- **Farmer-Centric UI:** A clean, modern dashboard for uploading and analyzing leaf health.
- **Actionable Insights:** Doesn't just name the disease—it provides symptoms and treatment steps.

---

## 🛠️ Tech Stack
- **Brain:** PyTorch, MobileNetV2 (Transfer Learning)
- **Engine:** FastAPI (Python Backend)
- **Face:** HTML5, CSS3, JavaScript (Vanilla JS)
- **Data:** PlantVillage Dataset (8 optimized classes)

---

## 📂 Project Structure
```text
agri-ai-project/
├── dataset/             # Training/Validation data (8 classes)
├── model/               
│   ├── disease_model.pth # The 99.3% accurate weights
│   ├── inference.py      # Logic for loading & prediction
│   └── disease_info.json # Disease library & treatments
├── static/              # Frontend UI components
├── train.py             # Optimization & training pipeline
└── main.py              # FastAPI server entry point