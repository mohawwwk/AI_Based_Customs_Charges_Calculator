# AI-Assisted Customs Charge Calculator

An intelligent system for automating customs duty calculations using AI classification and database-driven rules.

## 🎯 Project Overview

This system eliminates manual customs processing by using:
- **AI Classification**: Machine learning model (TF-IDF + Naive Bayes) to classify products
- **Database-Driven Rules**: All tariff rates stored in MySQL - update without code deployment
- **Transparent Calculations**: Every charge traceable to specific regulations
- **Audit Trail**: Complete logging of all calculations

## 🏗️ Architecture
```
User Interface (Streamlit)
        ↓
FastAPI REST API
        ↓
ML Model (scikit-learn) + MySQL Database
        ↓
PDF Report Generator
```

## 📊 Features

### Core Features
- ✅ AI-powered product classification (95% accuracy)
- ✅ Real-time customs duty calculation
- ✅ Support for 2 routes: USA→India, China→India
- ✅ 4 product categories: Electronics, Clothing, Books, Toys
- ✅ Professional PDF report generation
- ✅ Complete audit trail

### Admin Features
- ✅ View all customs rules
- ✅ Update duty rates without code deployment
- ✅ Add new routes and categories
- ✅ System statistics dashboard
- ✅ Audit log viewer

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <your-repo>
cd PBLII
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start MySQL**
```bash
net start MySQL80
```

4. **Create database**
```bash
mysql -u root -p < database/schema.sql
```

5. **Train ML model**
```bash
cd backend
python train_model.py
```

6. **Start FastAPI backend**
```bash
cd backend
python main.py
```

7. **Start Streamlit frontend** (new terminal)
```bash
cd frontend
streamlit run app.py
```

8. **Access the application**
- Main App: http://localhost:8501
- Admin Panel: http://localhost:8502 (run: `streamlit run admin.py --server.port 8502`)
- API Docs: http://localhost:8000/docs

## 📁 Project Structure
```
PBLII/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # MySQL connection
│   ├── train_model.py          # ML model trainer
│   ├── test_api.py             # API tests
│   ├── data/
│   │   └── training_data.csv   # Training data (200 examples)
│   ├── models/
│   │   └── product_classifier.pkl  # Trained ML model
│   ├── routes/
│   │   └── admin.py            # Admin endpoints
│   └── services/
│       ├── classifier.py       # ML classifier
│       ├── calculator.py       # Calculation engine
│       └── pdf_generator.py    # PDF generation
├── frontend/
│   ├── app.py                  # Main user interface
│   └── admin.py                # Admin dashboard
├── database/
│   └── schema.sql              # MySQL schema
├── outputs/                    # Generated PDFs
└── README.md
```

## 🧪 Testing

Run automated tests:
```bash
cd backend
python test_api.py
```

## 📊 ML Model Performance

- **Algorithm**: TF-IDF + Multinomial Naive Bayes
- **Training Data**: 200 product descriptions (50 per category)
- **Test Accuracy**: 95%
- **Inference Time**: < 0.1 seconds

### Confusion Matrix
```
              Predicted →
Actual ↓   Books  Clothing  Electronics  Toys
Books        10      0          0         0
Clothing      0     10          0         0
Electronics   0      1          9         0
Toys          0      0          1         9
```

## 💡 Key Innovation

**Database-Driven Rate Updates (No Code Deployment)**

Traditional systems hardcode rates in source code:
- ❌ Requires developers for every change
- ❌ Takes days/weeks to update
- ❌ Costs $5,000-$50,000 per update

Our system stores rates in database:
- ✅ Business users update via web dashboard
- ✅ Takes 2 minutes to update
- ✅ Zero downtime
- ✅ Complete audit trail

## 📈 Business Impact

**For a company processing 10,000 orders/day:**
- **Time Savings**: 2-4 hours → 2 seconds per calculation
- **Cost Savings**: ~$500,000/year in manual processing
- **Error Reduction**: 15-20% error rate → <5%
- **Scalability**: Manual max 200/day → 100,000+/day

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend API | FastAPI | REST API server |
| Database | MySQL | Store rules & audit logs |
| ML Model | scikit-learn | Product classification |
| Frontend | Streamlit | User interface |
| PDF Generation | ReportLab | Professional reports |
| Validation | Pydantic | Data validation |

## 👥 Team

- **Mohak Sareen** (23070122139)
- **Mohnish Kundnani** (23070122142)
- **Nigel Francy** (23070122148)
- **Nitesh Ghimire** (23070122150)

**Guided by:** Dr. Shewtambhari Chiwhane  
**Industry Mentor:** Sanya Sareen (SDE - Amazon)

## 📝 License

This project is for educational purposes as part of PBL Project 2024.

## 🙏 Acknowledgments

- Dr. Shewtambhari Chiwhane for guidance
- Sanya Sareen for industry insights
- Amazon for the problem statement