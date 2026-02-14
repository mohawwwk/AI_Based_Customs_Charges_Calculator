import pickle
import re
import numpy as np
import os

class ProductClassifier:
    """
    ML-based product classifier using TF-IDF and Naive Bayes
    """
    
    def __init__(self, model_path='models/product_classifier.pkl'):
        """Load trained model"""
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please train the model first by running: python train_model.py"
            )
        
        print(f"📦 Loading ML model from {model_path}...")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        self.hs_code_mapping = model_data['hs_code_mapping']
        
        print(f"✅ Model loaded successfully!")
        print(f"   Categories: {list(self.classifier.classes_)}")
        print(f"   Vocabulary size: {len(self.vectorizer.get_feature_names_out())}")
    
    def preprocess_text(self, text):
        """Clean and normalize text"""
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def classify(self, description: str) -> dict:
        """
        Classify product and return results
        
        Args:
            description: Product description text
            
        Returns:
            Dictionary with category, hs_code, confidence, keywords
        """
        
        # Preprocess
        clean_text = self.preprocess_text(description)
        
        # Vectorize
        text_vectorized = self.vectorizer.transform([clean_text])
        
        # Get probabilities
        probabilities = self.classifier.predict_proba(text_vectorized)[0]
        
        # Get prediction
        predicted_idx = np.argmax(probabilities)
        predicted_category = self.classifier.classes_[predicted_idx]
        confidence = probabilities[predicted_idx]
        
        # Get top keywords from input
        feature_names = self.vectorizer.get_feature_names_out()
        text_vector_array = text_vectorized.toarray()[0]
        top_indices = text_vector_array.argsort()[-5:][::-1]
        keywords = [feature_names[i] for i in top_indices if text_vector_array[i] > 0]
        
        # Convert NumPy types to Python native types (IMPORTANT!)
        return {
            'category': str(predicted_category),  # Ensure string
            'hs_code': str(self.hs_code_mapping[predicted_category]),  # Ensure string
            'confidence': float(confidence),  # Convert numpy.float64 to Python float
            'keywords': [str(k) for k in keywords[:5]],  # Convert numpy strings to Python strings
            'requires_manual_review': bool(confidence < 0.75)  # Convert numpy.bool_ to Python bool
        }