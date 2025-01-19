import { useState } from 'react';
import './App.css';

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
    setIsLoading(true);
    setAnalysisResults(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        body: formData,
      }); 

      const data = await response.json();

      if (response.ok) {
        setUploadStatus('Files uploaded successfully!');
        setAnalysisResults(data.analysis_results);
      } else {
        setUploadStatus(`Upload failed: ${data.message}`);
      }
    } catch (error) {
      console.error('Error uploading files:', error);
      setUploadStatus(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const renderAnalysisResults = () => {
    if (!analysisResults || analysisResults.length === 0) return null;

    const result = analysisResults[0];
    const { fraud_analysis, transaction_analysis } = result;

    return (
      <>
        <div className="analysis-grid">
          {/* Fraud Analysis Card */}
          <div className="analysis-card">
            <h3>Fraud Analysis Metrics</h3>
            <div className="metrics">
              <div className="metric-item">
                <label>Total Fraudulent Transactions:</label>
                <span>{fraud_analysis.total_fraudulent}</span>
              </div>
              <div className="metric-item">
                <label>Fraud Percentage:</label>
                <span>{fraud_analysis.fraud_percentage.toFixed(2)}%</span>
              </div>
              <div className="metric-item">
                <label>Average Fraud Probability:</label>
                <span>{fraud_analysis.average_fraud_probability.toFixed(2)}%</span>
              </div>
            </div>
          </div>

          {/* Transaction Summary Card */}
          <div className="analysis-card">
            <h3>Transaction Summary</h3>
            <div className="metrics">
              <div className="metric-item">
                <label>Total Transactions:</label>
                <span>{transaction_analysis.total_transactions}</span>
              </div>
              <div className="metric-item">
                <label>Total Amount:</label>
                <span>{formatCurrency(transaction_analysis.total_amount)}</span>
              </div>
              <div className="metric-item">
                <label>Average Transaction:</label>
                <span>{formatCurrency(transaction_analysis.average_transaction)}</span>
              </div>
            </div>
          </div>

          {/* Risk Assessment Card */}
          <div className="analysis-card">
            <h3>Risk Assessment</h3>
            <div className={`decision-status ${fraud_analysis.fraud_percentage > 5 ? 'rejected' : 'approved'}`}>
              <span>{fraud_analysis.fraud_percentage > 5 ? 'HIGH RISK' : 'LOW RISK'}</span>
              <p>Based on fraud analysis</p>
            </div>
          </div>

          {/* Largest Transactions Card */}
          <div className="analysis-card">
            <h3>Largest Transactions</h3>
            <div className="transactions-list">
              {transaction_analysis.largest_transactions.map((transaction, index) => (
                <div key={index} className="transaction-item">
                  <div className="transaction-amount">
                    {formatCurrency(Math.abs(transaction.amount))}
                  </div>
                  <div className="transaction-details">
                    <span className="transaction-date">{transaction.date}</span>
                    <span className={`transaction-type ${transaction.amount < 0 ? 'debit' : 'credit'}`}>
                      {transaction.amount < 0 ? 'Debit' : 'Credit'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="App">
      <div className="container">
        <h1>Bank Statement Analysis</h1>
        
        <div className="upload-section">
          <h2>Upload Bank Statements</h2>
          <button className="upload-btn" disabled={isLoading}>
            {isLoading ? 'Analyzing...' : selectedFiles.length > 0 ? `${selectedFiles.length} files selected` : 'Choose Files'}
            <input 
              type="file" 
              multiple 
              accept=".pdf,.csv,.xlsx"
              onChange={handleFileUpload}
              disabled={isLoading}
            />
          </button>
          {uploadStatus && (
            <p className={`upload-status ${uploadStatus.includes('success') ? 'success' : 'error'}`}>
              {uploadStatus}
            </p>
          )}
        </div>

        {isLoading ? (
          <div className="loading">Analyzing your documents...</div>
        ) : (
          renderAnalysisResults()
        )}
      </div>
    </div>
  );
}

export default App;