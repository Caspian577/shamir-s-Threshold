# Shamir's Threshold Scheme 🔐

A practical implementation of Shamir's Secret Sharing Threshold Algorithm, demonstrating how the mathematics behind secret sharing function to securely distribute and recover sensitive data.

## 🎯 Objective
The goal of this project is to explore the inner workings and core functionality of Shamir's Threshold Scheme. This implementation serves as a foundational exploration to integrate this powerful cryptographic framework into future encryption and data security projects.

## 🧠 How it Works (The Math behind the Code)
This project visualizes how algebraic polynomials interact with text data to split secrets securely:
1. **Data Translation (UTF-8):** The original secret (a word or string) is encoded using UTF-8 to translate the text characters into numeric values that the algorithm can process mathematically.
2. **Polynomial Generation:** A random polynomial of degree $K-1$ (where $K$ is the threshold) is generated, where the constant term (f(0)) is the secret itself.
3. **Share Distribution:** Unique points $(x, y)$ on this polynomial are calculated and distributed as "shares."
4. **Lagrange Interpolation:** To recover the secret, the algorithm uses Lagrange polynomial interpolation. If the minimum threshold of shares is met, the polynomial is reconstructed, revealing the constant term which is then decoded back from UTF-8 into the original text.

## 🛠️ Key Features
* **Threshold Flexibility:** Dynamically splits a secret into $N$ total shares, requiring a minimum of $K$ shares to reconstruct.
* **Text-to-Math Pipeline:** Seamless integration of UTF-8 encoding to handle real text secrets instead of just raw numbers.
* **Mathematical Security:** Demonstrates perfect secrecy—having $K-1$ shares provides zero information about the secret.

## 🧰 Tech Stack
* **Language:** Python 🐍
* **Concepts:** Cryptography, Polynomial Interpolation, Finite Fields, UTF-8 Data Encoding. 
