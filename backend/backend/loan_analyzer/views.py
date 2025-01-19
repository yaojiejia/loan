from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from datetime import datetime
import hashlib
from .utils.extract import analyze_bank_statement

@csrf_exempt
def upload_files(request):
    if request.method == 'POST':
        try:
            files = request.FILES.getlist('files')
            uploaded_files = []
            analysis_results = []

            upload_dir = os.path.join(settings.BASE_DIR.parent, 'data')
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                allowed_extensions = ['.pdf', '.csv', '.xlsx']
                file_ext = os.path.splitext(file.name)[1].lower()
                
                if file_ext not in allowed_extensions:
                    return JsonResponse({
                        'message': f'Invalid file type for {file.name}. Only PDF, CSV, and XLSX files are allowed.'
                    }, status=400)

                # Generate hashed filename
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                original_name = os.path.splitext(file.name)[0]
                hash_input = f"{original_name}{timestamp}".encode('utf-8')
                hashed_name = hashlib.sha256(hash_input).hexdigest()[:16]
                unique_filename = f"{hashed_name}{file_ext}"
                file_path = os.path.join(upload_dir, unique_filename)

                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                uploaded_files.append(unique_filename)

                if file_ext.lower() == '.pdf':
                    try:
                        result = analyze_bank_statement(file_path)
                        fraud_analysis = result.get('summary', {}).get('fraud_analysis', {})
                        transactions = result.get('transactions', [])
                        
                        largest_transactions = sorted(
                            transactions, 
                            key=lambda x: abs(float(x.get('amount', 0))), 
                            reverse=True
                        )[:5]

                        total_transactions = len(transactions)
                        total_amount = sum(abs(float(t.get('amount', 0))) for t in transactions)
                        average_transaction = total_amount / total_transactions if total_transactions > 0 else 0

                        analysis_results.append({
                            'filename': unique_filename,
                            'fraud_analysis': {
                                'total_fraudulent': fraud_analysis.get('total_fraudulent', 0),
                                'fraud_percentage': float(fraud_analysis.get('fraud_percentage', 0)),
                                'average_fraud_probability': float(fraud_analysis.get('average_fraud_probability', 0))
                            },
                            'transaction_analysis': {
                                'total_transactions': total_transactions,
                                'total_amount': round(total_amount, 2),
                                'average_transaction': round(average_transaction, 2),
                                'largest_transactions': largest_transactions
                            }
                        })
                    except Exception as analysis_error:
                        analysis_results.append({
                            'filename': unique_filename,
                            'error': str(analysis_error)
                        })

            return JsonResponse({
                'message': 'Files uploaded successfully',
                'files': uploaded_files,
                'analysis_results': analysis_results
            })

        except Exception as e:
            return JsonResponse({
                'message': f'Error uploading files: {str(e)}'
            }, status=500)

    return JsonResponse({
        'message': 'Method not allowed'
    }, status=405)