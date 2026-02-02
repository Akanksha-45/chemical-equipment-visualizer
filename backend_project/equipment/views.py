from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Equipment, Dataset
from .data_analysis import analyze_equipment_csv, parse_csv_to_equipment_list
import json
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

@csrf_exempt
def upload_csv(request):
    """Upload CSV file and store equipment data"""
    if request.method == "POST":
        try:
            if 'file' not in request.FILES:
                return JsonResponse({"error": "No file uploaded"}, status=400)
            
            csv_file = request.FILES['file']
            
            # Validate file extension
            if not csv_file.name.endswith('.csv'):
                return JsonResponse({"error": "File must be a CSV"}, status=400)
            
            # Analyze the CSV
            summary, error = analyze_equipment_csv(csv_file)
            if error:
                return JsonResponse({"error": error}, status=400)

            # Normalize summary keys to match frontend expectations
            normalized_summary = {
                "total_count": summary.get("total_equipment", 0),
                "averages": {
                    "avg_flowrate": summary.get("avg_flowrate", 0),
                    "avg_pressure": summary.get("avg_pressure", 0),
                    "avg_temperature": summary.get("avg_temperature", 0),
                },
                "type_distribution": summary.get("equipment_type_distribution", {}),
                "statistics": summary.get("statistics", {}),
                "risk_distribution": summary.get("risk_distribution", {}),
            }
            
            # Read CSV again for database storage
            csv_file.seek(0)  # Reset file pointer
            df = pd.read_csv(csv_file)
            
            # Create dataset record
            dataset = Dataset.objects.create(
                filename=csv_file.name,
                total_records=len(df)
            )
            
            # Parse and save equipment data
            equipment_list = parse_csv_to_equipment_list(df)
            equipment_objects = [
                Equipment(dataset=dataset, **eq) for eq in equipment_list
            ]
            Equipment.objects.bulk_create(equipment_objects)
            
            # Clean up old datasets (keep only last 5)
            old_datasets = Dataset.objects.all()[5:]
            for ds in old_datasets:
                ds.delete()
            
            return JsonResponse({
                "message": "CSV uploaded successfully",
                "dataset_id": dataset.id,
                "summary": normalized_summary
            }, status=201)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only POST allowed"}, status=405)


@csrf_exempt
def get_summary(request):
    """Get summary statistics of all equipment or specific dataset"""
    if request.method == "GET":
        dataset_id = request.GET.get('dataset_id')
        
        if dataset_id:
            equipment = Equipment.objects.filter(dataset_id=dataset_id)
        else:
            equipment = Equipment.objects.all()
        
        if not equipment.exists():
            return JsonResponse({
                "total_count": 0,
                "averages": {},
                "type_distribution": {},
                "message": "No equipment data found"
            })
        
        # Calculate statistics
        data = list(equipment.values('equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature'))
        df = pd.DataFrame(data)
        
        summary = {
            "total_count": len(df),
            "averages": {
                "avg_flowrate": round(df['flowrate'].mean(), 2),
                "avg_pressure": round(df['pressure'].mean(), 2),
                "avg_temperature": round(df['temperature'].mean(), 2),
            },
            "type_distribution": df['equipment_type'].value_counts().to_dict(),
            "statistics": {
                "flowrate": {
                    "min": round(df['flowrate'].min(), 2),
                    "max": round(df['flowrate'].max(), 2),
                    "median": round(df['flowrate'].median(), 2),
                    "std": round(df['flowrate'].std(), 2) if len(df) > 1 else 0,
                },
                "pressure": {
                    "min": round(df['pressure'].min(), 2),
                    "max": round(df['pressure'].max(), 2),
                    "median": round(df['pressure'].median(), 2),
                    "std": round(df['pressure'].std(), 2) if len(df) > 1 else 0,
                },
                "temperature": {
                    "min": round(df['temperature'].min(), 2),
                    "max": round(df['temperature'].max(), 2),
                    "median": round(df['temperature'].median(), 2),
                    "std": round(df['temperature'].std(), 2) if len(df) > 1 else 0,
                }
            }
        }
        
        return JsonResponse(summary)
    
    return JsonResponse({"error": "Only GET allowed"}, status=405)


@csrf_exempt
def get_equipment_list(request):
    """Get list of all equipment or from specific dataset"""
    if request.method == "GET":
        dataset_id = request.GET.get('dataset_id')
        
        if dataset_id:
            equipment = Equipment.objects.filter(dataset_id=dataset_id)
        else:
            equipment = Equipment.objects.all()[:100]  # Limit to 100 for performance
        
        data = list(equipment.values(
            'id', 'equipment_name', 'equipment_type', 
            'flowrate', 'pressure', 'temperature', 'uploaded_at'
        ))
        
        return JsonResponse({"data": data}, safe=False)
    
    return JsonResponse({"error": "Only GET allowed"}, status=405)


@csrf_exempt
def get_dataset_history(request):
    """Get list of last 5 uploaded datasets"""
    if request.method == "GET":
        datasets = Dataset.objects.all()[:5]
        
        data = []
        for ds in datasets:
            data.append({
                "id": ds.id,
                "filename": ds.filename,
                "uploaded_at": ds.uploaded_at.isoformat(),
                "total_records": ds.total_records
            })
        
        return JsonResponse({"datasets": data})
    
    return JsonResponse({"error": "Only GET allowed"}, status=405)


@csrf_exempt
def generate_pdf_report(request):
    """Generate PDF report with equipment summary and statistics"""
    if request.method == "GET":
        try:
            dataset_id = request.GET.get('dataset_id')
            
            # Get equipment data
            if dataset_id:
                equipment = Equipment.objects.filter(dataset_id=dataset_id)
                dataset = Dataset.objects.get(id=dataset_id)
                report_title = f"Equipment Report - {dataset.filename}"
            else:
                equipment = Equipment.objects.all()
                report_title = "Complete Equipment Report"
            
            if not equipment.exists():
                return JsonResponse({"error": "No equipment data found"}, status=404)
            
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            # Container for PDF elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Add custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            elements.append(Paragraph(report_title, title_style))
            elements.append(Spacer(1, 12))
            
            # Report metadata
            report_date = datetime.now().strftime("%B %d, %Y %H:%M:%S")
            elements.append(Paragraph(f"<b>Generated:</b> {report_date}", styles['Normal']))
            elements.append(Paragraph(f"<b>Total Equipment:</b> {equipment.count()}", styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Calculate statistics
            data = list(equipment.values('equipment_name', 'equipment_type', 
                                        'flowrate', 'pressure', 'temperature'))
            df = pd.DataFrame(data)
            
            # Summary Statistics Section
            elements.append(Paragraph("Summary Statistics", heading_style))
            
            summary_data = [
                ['Metric', 'Flowrate', 'Pressure', 'Temperature'],
                ['Average', f"{df['flowrate'].mean():.2f}", 
                 f"{df['pressure'].mean():.2f}", 
                 f"{df['temperature'].mean():.2f}"],
                ['Minimum', f"{df['flowrate'].min():.2f}", 
                 f"{df['pressure'].min():.2f}", 
                 f"{df['temperature'].min():.2f}"],
                ['Maximum', f"{df['flowrate'].max():.2f}", 
                 f"{df['pressure'].max():.2f}", 
                 f"{df['temperature'].max():.2f}"],
                ['Std Dev', f"{df['flowrate'].std():.2f}" if len(df) > 1 else "0.00", 
                 f"{df['pressure'].std():.2f}" if len(df) > 1 else "0.00", 
                 f"{df['temperature'].std():.2f}" if len(df) > 1 else "0.00"],
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 20))
            
            # Equipment Type Distribution
            elements.append(Paragraph("Equipment Type Distribution", heading_style))
            
            type_dist = df['equipment_type'].value_counts()
            type_data = [['Equipment Type', 'Count', 'Percentage']]
            for eq_type, count in type_dist.items():
                percentage = (count / len(df)) * 100
                type_data.append([eq_type, str(count), f"{percentage:.1f}%"])
            
            type_table = Table(type_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(type_table)
            elements.append(Spacer(1, 20))
            
            # Equipment List (First 20 records)
            elements.append(Paragraph("Equipment List (Top 20)", heading_style))
            
            equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
            for index, row in df.head(20).iterrows():
                equipment_data.append([
                    row['equipment_name'][:20],  # Truncate long names
                    row['equipment_type'][:15],
                    f"{row['flowrate']:.2f}",
                    f"{row['pressure']:.2f}",
                    f"{row['temperature']:.2f}"
                ])
            
            equipment_table = Table(equipment_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
            equipment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(equipment_table)
            
            # Add footer
            elements.append(Spacer(1, 30))
            footer_text = "Chemical Equipment Visualizer - Automated Report Generation"
            elements.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Return PDF response
            response = HttpResponse(pdf_data, content_type='application/pdf')
            filename = f"equipment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only GET allowed"}, status=405)

