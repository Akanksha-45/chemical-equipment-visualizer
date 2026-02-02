import pandas as pd
from django.db.models import Avg, Count

def analyze_equipment_csv(csv_file):
    """Analyze uploaded CSV file and return summary statistics"""
    try:
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Clean data
        df = df.dropna()

        summary = {
            "total_equipment": int(len(df)),
            "avg_flowrate": round(float(df["Flowrate"].mean()), 2),
            "avg_pressure": round(float(df["Pressure"].mean()), 2),
            "avg_temperature": round(float(df["Temperature"].mean()), 2),
            "equipment_type_distribution": df["Type"].value_counts().to_dict(),
        }

        # Calculate detailed statistics
        summary["statistics"] = {
            "flowrate": {
                "min": round(float(df["Flowrate"].min()), 2),
                "max": round(float(df["Flowrate"].max()), 2),
                "median": round(float(df["Flowrate"].median()), 2),
                "std": round(float(df["Flowrate"].std()), 2) if len(df) > 1 else 0,
            },
            "pressure": {
                "min": round(float(df["Pressure"].min()), 2),
                "max": round(float(df["Pressure"].max()), 2),
                "median": round(float(df["Pressure"].median()), 2),
                "std": round(float(df["Pressure"].std()), 2) if len(df) > 1 else 0,
            },
            "temperature": {
                "min": round(float(df["Temperature"].min()), 2),
                "max": round(float(df["Temperature"].max()), 2),
                "median": round(float(df["Temperature"].median()), 2),
                "std": round(float(df["Temperature"].std()), 2) if len(df) > 1 else 0,
            }
        }

        risk_distribution = {"Normal": 0, "Warning": 0, "Critical": 0}

        for _, row in df.iterrows():
            issues = 0
            if row["Pressure"] > 10:
                issues += 1
            if row["Temperature"] > 120:
                issues += 1
            if row["Flowrate"] > 100:
                issues += 1

            if issues == 0:
                risk_distribution["Normal"] += 1
            elif issues == 1:
                risk_distribution["Warning"] += 1
            else:
                risk_distribution["Critical"] += 1

        summary["risk_distribution"] = risk_distribution
        return summary, None
    
    except Exception as e:
        return None, f"Error analyzing CSV: {str(e)}"

def parse_csv_to_equipment_list(df):
    """Convert DataFrame to list of equipment dictionaries for database storage"""
    equipment_list = []
    for _, row in df.iterrows():
        equipment_list.append({
            'equipment_name': str(row['Equipment Name']),
            'equipment_type': str(row['Type']),
            'flowrate': float(row['Flowrate']),
            'pressure': float(row['Pressure']),
            'temperature': float(row['Temperature']),
        })
    return equipment_list
