
# **Bank Statement Fraud Detection System**

## **Overview**
A full-stack web application that analyzes bank statements for potential fraudulent transactions using machine learning. The system processes PDF bank statements, extracts transaction data, and provides detailed fraud analysis metrics.

## **Features**
* PDF bank statement upload and processing
* Transaction data extraction
* Machine learning-based fraud detection
* Real-time analysis results
* Interactive dashboard
* Detailed transaction metrics
* Fraud probability scoring

## **Tech Stack**

### **Frontend**
* React.js
* CSS3
* Axios for API calls

### **Backend**
* Django
* Python 3.11
* scikit-learn for ML
* pdfplumber for PDF processing

## **Installation**

### **Prerequisites**
* Python 3.11
* Node.js and npm
* Git

### **Backend Setup**

1. **Clone the repository**
```bash
git clone https://github.com/yaojiejia/loan.git
cd loan
```

2. **Create and activate virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Set up the database**
```bash
python3 manage.py migrate
```

5. **Run the development server**
```bash
python3 manage.py runserver
```

**For production deployment:**
```bash
nohup python3.11 manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
```

### **Frontend Setup**

1. **Navigate to frontend directory**
```bash
cd loan
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm start
```

**For production deployment:**
```bash
npm run build
nohup serve -s build -l 3000 > react.log 2>&1 &
```

## **API Endpoints**

### **File Upload**
* `POST /api/upload/`
  * Accepts PDF bank statements
  * Returns analysis results

## **Machine Learning Model**
The fraud detection model is built using Random Forest Classifier and trained on transaction patterns. Model files needed:
* `random_forest_fraud_model.pkl`
* `column_names.pkl`

Place these files in `backend/backend/loan_analyzer/utils/`

## **Development**

### **Backend (Django on EC2)**
```bash
# Install required system packages
sudo apt update
sudo apt install python3.11 python3.11-venv

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with nohup
nohup python3.11 manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
```

### **Frontend (React on EC2)**
```bash
# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Install dependencies and build
npm install
npm run build

# Install serve
npm install -g serve

# Run with nohup
nohup serve -s build -l 3000 > react.log 2>&1 &
```

## **Monitoring**

Check application logs:
```bash
# Backend logs
tail -f django.log

# Frontend logs
tail -f react.log
```

## **Common Issues**

1. **CORS Issues**
   * Ensure CORS settings are properly configured in Django
   * Check allowed origins in settings.py

2. **PDF Processing**
   * Verify PDF file format compatibility
   * Check file permissions

3. **Model Loading**
   * Ensure model files are in correct location
   * Verify scikit-learn versions match

## **Contributing**

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## **License**
This project is licensed under the MIT License - see the LICENSE file for details.
