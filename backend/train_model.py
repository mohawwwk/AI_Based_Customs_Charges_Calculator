import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import numpy as np
import re

class ProductClassifierTrainer:
    """Train and evaluate product classification model"""
    
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.hs_code_mapping = {
            'Electronics': '8518.30.00',
            'Clothing': '6109.10.00',
            'Books': '4901.99.00',
            'Toys': '9503.00.00'
        }
    
    def preprocess_text(self, text):
        """Clean and normalize text"""
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def load_data(self, filepath='data/training_data.csv'):
        """Load training data from CSV"""
        print(f"📂 Loading training data from {filepath}...")
        
        df = pd.read_csv(filepath)
        
        print(f"✅ Loaded {len(df)} training examples")
        print(f"📊 Class distribution:")
        print(df['category'].value_counts())
        print()
        
        return df
    
    def train(self, df):
        """Train the model"""
        print("🔄 Preprocessing text...")
        
        # Preprocess descriptions
        X = df['product_description'].apply(self.preprocess_text)
        y = df['category']
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"📊 Training set: {len(X_train)} examples")
        print(f"📊 Test set: {len(X_test)} examples")
        print()
        
        # Create TF-IDF vectorizer
        print("🔄 Creating TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=500,  # Top 500 most important words
            ngram_range=(1, 2),  # Use single words and word pairs
            min_df=2,  # Word must appear in at least 2 documents
            max_df=0.8,  # Ignore words in more than 80% of documents
            sublinear_tf=True  # Use logarithmic term frequency
        )
        
        X_train_vectorized = self.vectorizer.fit_transform(X_train)
        X_test_vectorized = self.vectorizer.transform(X_test)
        
        print(f"✅ Vocabulary size: {len(self.vectorizer.get_feature_names_out())}")
        print()
        
        # Train classifier
        print("🔄 Training Naive Bayes classifier...")
        self.classifier = MultinomialNB(alpha=0.1)
        self.classifier.fit(X_train_vectorized, y_train)
        
        print("✅ Model trained!")
        print()
        
        # Evaluate
        print("📊 EVALUATION RESULTS:")
        print("="*60)
        
        # Training accuracy
        train_pred = self.classifier.predict(X_train_vectorized)
        train_accuracy = accuracy_score(y_train, train_pred)
        print(f"Training Accuracy: {train_accuracy*100:.2f}%")
        
        # Test accuracy
        test_pred = self.classifier.predict(X_test_vectorized)
        test_accuracy = accuracy_score(y_test, test_pred)
        print(f"Test Accuracy: {test_accuracy*100:.2f}%")
        print()
        
        # Detailed classification report
        print("Classification Report:")
        print(classification_report(y_test, test_pred))
        
        # Confusion matrix
        print("Confusion Matrix:")
        cm = confusion_matrix(y_test, test_pred)
        categories = sorted(df['category'].unique())
        
        # Print confusion matrix nicely
        print("\n        Predicted →")
        print("Actual ↓ ", end="")
        for cat in categories:
            print(f"{cat[:4]:>8}", end="")
        print()
        
        for i, cat in enumerate(categories):
            print(f"{cat[:8]:<9}", end="")
            for j in range(len(categories)):
                print(f"{cm[i][j]:>8}", end="")
            print()
        print()
        
        return test_accuracy
    
    def show_top_features(self, n=10):
        """Show top features for each category"""
        print("🔍 TOP FEATURES PER CATEGORY:")
        print("="*60)
        
        feature_names = self.vectorizer.get_feature_names_out()
        
        for i, category in enumerate(self.classifier.classes_):
            # Get feature log probabilities for this class
            log_probs = self.classifier.feature_log_prob_[i]
            
            # Get top N features
            top_indices = log_probs.argsort()[-n:][::-1]
            top_features = [feature_names[idx] for idx in top_indices]
            
            print(f"\n{category}:")
            print(f"  {', '.join(top_features)}")
        
        print()
    
    def test_predictions(self):
        """Test model on example inputs"""
        print("🧪 TESTING MODEL ON EXAMPLES:")
        print("="*60)
        
        test_examples = [
            "Apple iPhone 15 Pro smartphone with 256GB storage",
            "Nike Air Max running shoes for men",
            "The Great Gatsby novel by F. Scott Fitzgerald",
            "LEGO Star Wars Millennium Falcon building set",
            "Sony WH-1000XM5 wireless noise cancelling headphones",
            "Levi's 501 original fit blue jeans",
            "Harry Potter complete book collection",
            "Barbie dreamhouse playset with furniture"
        ]
        
        for example in test_examples:
            prediction = self.predict(example)
            print(f"\nInput: {example}")
            print(f"  Category: {prediction['category']}")
            print(f"  HS Code: {prediction['hs_code']}")
            print(f"  Confidence: {prediction['confidence']*100:.1f}%")
            print(f"  Top keywords: {', '.join(prediction['keywords'][:3])}")
    
    def predict(self, text):
        """Make a prediction on new text"""
        # Preprocess
        clean_text = self.preprocess_text(text)
        
        # Vectorize
        text_vectorized = self.vectorizer.transform([clean_text])
        
        # Get probabilities
        probabilities = self.classifier.predict_proba(text_vectorized)[0]
        
        # Get prediction
        predicted_idx = np.argmax(probabilities)
        predicted_category = self.classifier.classes_[predicted_idx]
        confidence = probabilities[predicted_idx]
        
        # Get top keywords
        feature_names = self.vectorizer.get_feature_names_out()
        text_vector_array = text_vectorized.toarray()[0]
        top_indices = text_vector_array.argsort()[-5:][::-1]
        keywords = [feature_names[i] for i in top_indices if text_vector_array[i] > 0]
        
        return {
            'category': predicted_category,
            'hs_code': self.hs_code_mapping[predicted_category],
            'confidence': float(confidence),
            'keywords': keywords,
            'requires_manual_review': confidence < 0.75
        }
    
    def save_model(self, filepath='models/product_classifier.pkl'):
        """Save trained model"""
        print(f"💾 Saving model to {filepath}...")
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'hs_code_mapping': self.hs_code_mapping
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved successfully!")
        print(f"📦 File size: {os.path.getsize(filepath) / 1024:.1f} KB")

def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("PRODUCT CLASSIFICATION MODEL TRAINER")
    print("="*60 + "\n")
    
    # Initialize trainer
    trainer = ProductClassifierTrainer()
    
    # Load data
    df = trainer.load_data('data/training_data.csv')
    
    # Train model
    accuracy = trainer.train(df)
    
    # Show top features
    trainer.show_top_features(n=10)
    
    # Test predictions
    trainer.test_predictions()
    
    # Save model
    trainer.save_model('models/product_classifier.pkl')
    
    print("\n" + "="*60)
    print(f"✅ TRAINING COMPLETE! Test Accuracy: {accuracy*100:.2f}%")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()