import pandas as pd
import pickle


with open("/home/alex/Documents/loan/backend/backend/loan_analyzer/utils/random_forest_fraud_model.pkl", 'rb') as file:
    loaded_model = pickle.load(file)

with open("/home/alex/Documents/loan/backend/backend/loan_analyzer/utils/column_names.pkl", 'rb') as file:
    column_names = pickle.load(file)

test_data_point = {
    'amount': 5000,
    'oldbalanceOrg': 10000,
    'newbalanceOrig': 5000,
    'oldbalanceDest': 2000,
    'newbalanceDest': 7000,
    'type_CASH_IN': 0,
    'type_CASH_OUT': 1,
    'type_DEBIT': 0,
    'type_PAYMENT': 0,
    'type_TRANSFER': 0,
    'is_large_transaction': True,
    'balance_difference': -5000
}
test_data_point_df = pd.DataFrame([test_data_point])

test_data_point_df = test_data_point_df.reindex(columns=column_names, fill_value=0)

prediction = loaded_model.predict(test_data_point_df)
print(f"Predicted class: {prediction[0]}")

prediction_proba = loaded_model.predict_proba(test_data_point_df)
print(f"Prediction probabilities: {prediction_proba}")
