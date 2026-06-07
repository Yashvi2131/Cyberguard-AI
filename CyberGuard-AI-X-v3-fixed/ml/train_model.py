"""
CyberGuard AI X - Model Training Script
Trains TF-IDF + Logistic Regression classifier for cybercrime categories
Run: python ml/train_model.py
"""

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from preprocessor import TextPreprocessor

# Training data - cybercrime complaint samples
TRAINING_DATA = [
    # Phishing
    ("I received an email from my bank asking me to click a link and enter my password", "Phishing"),
    ("Got a fake email claiming to be from SBI bank with suspicious link", "Phishing"),
    ("Someone sent me a phishing email pretending to be PayPal asking for card details", "Phishing"),
    ("I received a fake OTP request from an unknown number", "Phishing"),
    ("Got an email from a fake government site asking for Aadhaar details", "Phishing"),
    ("Received suspicious message asking to click link to update bank KYC", "Phishing"),
    ("Fake email claiming I won lottery asking me to provide bank account", "Phishing"),
    ("My email account was targeted with fake Microsoft login page", "Phishing"),
    ("Got SMS asking to verify account by entering password on fake website", "Phishing"),
    ("Fake IRCTC login page was used to steal my credentials", "Phishing"),
    ("Received WhatsApp message with link claiming to be from Amazon with prize", "Phishing"),
    ("Bank impersonation fraud via fake email to steal login credentials", "Phishing"),

    # Hacking
    ("My social media account was hacked and someone is posting from it", "Hacking"),
    ("Unknown person accessed my email account without my permission", "Hacking"),
    ("My website was defaced and all data was deleted by hackers", "Hacking"),
    ("Someone hacked into my computer and stole all my files", "Hacking"),
    ("My Facebook account was taken over by hackers", "Hacking"),
    ("Unauthorized access to my company server detected", "Hacking"),
    ("My Instagram account was compromised and password was changed", "Hacking"),
    ("Got notification of login from unknown device in different country", "Hacking"),
    ("Someone broke into my gmail account and deleted emails", "Hacking"),
    ("My YouTube channel was hacked and videos were deleted", "Hacking"),
    ("Someone gained root access to my system without authorization", "Hacking"),
    ("My phone was remotely accessed and all data was wiped", "Hacking"),

    # Malware
    ("My computer got infected with a virus that encrypted all my files", "Malware"),
    ("Ransomware attacked my laptop and demanded bitcoin payment", "Malware"),
    ("Downloaded file contained trojan horse that stole my passwords", "Malware"),
    ("My system is behaving strangely after clicking an unknown link", "Malware"),
    ("Found spyware on my device that was tracking my activities", "Malware"),
    ("Keylogger installed on my computer without my knowledge", "Malware"),
    ("My antivirus detected a dangerous worm in the system", "Malware"),
    ("Adware keeps showing pop-ups and redirecting my browser", "Malware"),
    ("Received malicious attachment in email that infected my PC", "Malware"),
    ("USB drive infected my computer with ransomware virus", "Malware"),
    ("Rootkit was installed on my system by unknown attacker", "Malware"),
    ("Malicious software encrypted all my business documents", "Malware"),

    # Online Fraud
    ("I was cheated online while shopping on a fake e-commerce website", "Online Fraud"),
    ("Paid for product on Instagram but never received it", "Online Fraud"),
    ("Online seller took money and disappeared without delivering goods", "Online Fraud"),
    ("Fake job offer website collected registration fees and vanished", "Online Fraud"),
    ("Cheated in online lottery claiming I won a car", "Online Fraud"),
    ("Fake matrimonial profile stole money after building trust", "Online Fraud"),
    ("Online rental fraud - paid advance for apartment that does not exist", "Online Fraud"),
    ("Fake investment website promised high returns and disappeared with money", "Online Fraud"),
    ("OLX seller fraud - paid for second hand phone but never received", "Online Fraud"),
    ("Fake NGO collected donations online and it was a scam", "Online Fraud"),
    ("Online gaming fraud - paid for virtual currency that was never credited", "Online Fraud"),
    ("Cheated by fake travel booking website took money no tickets", "Online Fraud"),

    # Financial Fraud
    ("Money was deducted from my bank account without my authorization", "Financial Fraud"),
    ("Fraudulent transactions on my credit card I did not make", "Financial Fraud"),
    ("Someone used my debit card details to make unauthorized purchases", "Financial Fraud"),
    ("UPI fraud - money transferred from my account using fake OTP", "Financial Fraud"),
    ("Bank fraud - someone opened account in my name and took loans", "Financial Fraud"),
    ("Credit card cloned and used for purchases in another city", "Financial Fraud"),
    ("Fake bank employee convinced me to share OTP and stole money", "Financial Fraud"),
    ("Received call claiming to be from RBI asking for card details", "Financial Fraud"),
    ("Net banking account hacked and all savings transferred out", "Financial Fraud"),
    ("ATM skimming device used to steal my card data and money", "Financial Fraud"),
    ("Investment fraud promised 30% monthly returns took 5 lakhs", "Financial Fraud"),
    ("Ponzi scheme took all my retirement savings of 10 lakhs", "Financial Fraud"),

    # Identity Theft
    ("Someone is using my personal information to open bank accounts", "Identity Theft"),
    ("My Aadhaar card details were misused by a fraudster", "Identity Theft"),
    ("Someone took a loan in my name using my stolen documents", "Identity Theft"),
    ("My PAN card was used to file fraudulent income tax returns", "Identity Theft"),
    ("Found out someone opened credit cards in my name", "Identity Theft"),
    ("My digital identity was stolen and used for illegal activities", "Identity Theft"),
    ("Fake profile created using my photos and personal information", "Identity Theft"),
    ("Someone used my driving license to commit fraud", "Identity Theft"),
    ("My passport details were stolen and used for fake bookings", "Identity Theft"),
    ("Identity theft - someone registered company using my documents without consent", "Identity Theft"),
    ("My voter ID was misused for voter fraud in elections", "Identity Theft"),
    ("Personal data sold online without consent by data breach", "Identity Theft"),

    # Cyberbullying
    ("I am being harassed online with abusive messages every day", "Cyberbullying"),
    ("Someone is sending me threatening messages on WhatsApp", "Cyberbullying"),
    ("Fake profile created to defame me and spread lies", "Cyberbullying"),
    ("My private photos shared online without my consent", "Cyberbullying"),
    ("Being trolled and harassed on Twitter by anonymous accounts", "Cyberbullying"),
    ("Receiving death threats on social media from unknown persons", "Cyberbullying"),
    ("Blackmailed using personal photos to pay money", "Cyberbullying"),
    ("Online stalking by someone who knows my daily routine", "Cyberbullying"),
    ("Abusive comments and body shaming on my social media posts", "Cyberbullying"),
    ("Someone created a hate group targeting me online", "Cyberbullying"),
    ("Doxxing attack - personal address and phone shared publicly online", "Cyberbullying"),
    ("Revenge porn - intimate photos shared without consent for harassment", "Cyberbullying"),
]


def train_model():
    preprocessor = TextPreprocessor()

    # Prepare data
    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    # Preprocess texts
    processed_texts = [preprocessor.preprocess(t) for t in texts]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        processed_texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # Create pipeline — tuned for higher confidence predictions
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=8000,
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
            analyzer='word',
        )),
        ('clf', LogisticRegression(
            max_iter=2000,
            C=5.0,           # Higher C = less regularization = stronger predictions
            class_weight='balanced',
            random_state=42,
            multi_class='multinomial',
            solver='lbfgs'
        ))
    ])

    # Train
    print("Training CyberGuard AI X Model...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Cross-validation
    cv_scores = cross_val_score(pipeline, processed_texts, labels, cv=5)
    print(f"\nCross-Validation Scores: {cv_scores}")
    print(f"Mean CV Score: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"\nModel saved to: {model_path}")

    return pipeline


if __name__ == '__main__':
    train_model()
