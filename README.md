# ⚛️ Individual Project: Integral Graphs

Integral Graphs is a fascinating and complex problem residing in the fields of **Graph Theory** and **Combinatorics**. This project focuses on identifying and generating these specific types of graphs.

---

## 📜 Problem Definition

A simple graph $G$ with an adjacency matrix $A(G)$ is called an **integral graph** if and only if **all eigenvalues** of its adjacency matrix $A(G)$ are **integers**.

The core challenge is the **identification, generation, and verification** of integral graphs for a specific set of parameters.

### ⚙️ Target Parameters

| Parameter | Symbol | Value | Notes |
| :--- | :--- | :--- | :--- |
| **Graph Order** | $n$ | $15$ | Number of vertices |
| **Number of Edges** | $k$ | $16$ | Total connections |

**Goal:** Find all unique integral graphs of order $n=15$ and $k=16$ edges.

Given the vast search space, the project emphasizes **computational efficiency** in the search process.

---

## 🎯 Project Objectives

The main objective is to develop and compare different methodologies for searching, generating, and rigorously verifying integral graphs.

### Key Tasks:

1.  **Graph Generation:** Generating candidate graphs using tools like **geng** or the **G(n,k) random model**.
2.  **Integrality Verification:** Efficiently calculating and checking if all eigenvalues of the adjacency matrix are integers.
3.  **Canonical Transformation:** Normalizing found graphs using **labelg** to ensure only unique (non-isomorphic) graphs are counted. 

[Image of canonical labeling of a graph]

4.  **Complementary Search:** Investigating the complementary problem: a graph $G$ is integral if its complement $G'$ (with $k'=105-16=89$ edges) is also integral.

---

## 🔬 Methodology and Algorithms

The search strategy is divided into three parallel paths to address the large search space.

### 1. Exact Algorithm

This approach aims for **completeness**—finding *every* integral graph for the given parameters.

* **Generator (geng):** Utilizes the powerful `geng` tool (part of the **nauty** package) to systematically generate **all non-isomorphic graphs** that satisfy the $n=15$ and $k=16$ constraints.

### 2. Metaheuristic Algorithms

These algorithms prioritize **efficiency and speed** to find a large subset of integral graphs without exhaustive enumeration.

* **Randomized Greedy Algorithm (RGA):** Combines local search (greedy choices) with randomness to escape local minima and explore a wider solution space.
* **Pure Greedy Algorithm:** A faster method that builds graphs by making the locally optimal edge choice at each step.
* **Random Algorithm:** Generates candidate graphs according to the **G(n,k) random graph model** for probabilistic exploration.

### 3. Verification Pipeline

All generated candidate graphs undergo a two-stage verification process:

| Stage | Tool/Method | Purpose |
| :--- | :--- | :--- |
| **Pre-Screening** | **Integral Graph Sieve (e.g., *sito5*)** | Uses fast algebraic tests (like checking traces of matrix powers) to quickly **reject** graphs that cannot possibly be integral, drastically reducing the dataset size. |
| **Normalization** | **Canonical Transformation (labelg)** | Transforms every verified integral graph into its **canonical form**. This is crucial for eliminating duplicate, isomorphic copies and generating a final, correct count of unique integral graphs. |