# Tinta ✍️  
*An Automated System for Generating and Simulating Human-Like Filipino Grammar Errors with Artificial Rules for Data Augmentation*

## 📌 Overview
**Tinta** is a Python-based rule-driven system designed to simulate **Filipino grammar errors** in otherwise correct sentences. By modeling common mistakes found in actual student writings, Tinta generates realistic erroneous data for tasks like:

- Data augmentation for machine learning
- Grammar checking tool training
- Language education and research

This system is based on grammatical patterns identified in [#], particularly from student-written Filipino translation activities.

---
## ⚙️ How It Works

1. **Input**: Clean sentences are read from `sentences.txt`.
2. **Operations Applied**:
   - **Insert**: Adds random Filipino function words
   - **Delete**: Removes random tokens
   - **Substitute**: Introduces realistic grammar errors based on defined rules
   - **Swap**: Reorders nearby tokens
3. **Error Types Simulated**:
   - Use of ligatures 
   - Use of enclitics 
   - Hyphenation removal 
   - “Ng” vs “Nang” confusion
   - Morphophonemic changes
   - Word repetition

4. **Output**:
   - A set of grammatically incorrect sentences
   - Summary tables of error and operation distributions
  ## 👥 Authors

This is a collaborated project in **Introduction to Artificial Intelligence**.

- **Jomar J. Ronquillo**
- **Niñalene G. Paguio**
- **Kenneth Claire M. Tulang**
- **Reynalyn R. Bawag**

---

## 📚 References

- Dataset: BALARILA Project  
- Error Taxonomy: **Octaviano, M., Go, M. P., Borra, A., & Oco, N. (2016)**. *A corpus-based analysis of Filipino writing errors.* In *International Conference on Asian Language Processing (IALP)*.


