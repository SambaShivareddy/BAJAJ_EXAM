import json
from datetime import datetime
from collections import Counter
from scipy.stats import pearsonr

with open('DataEngineeringQ2.json', 'r') as file:
    dataset = json.load(file)

def calculate_age_from_birth_date(birth_date):
    if not birth_date:
        return None
    birth_date = datetime.strptime(birth_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    today = datetime.now()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def is_valid_mobile(phone_number):
    if phone_number.startswith("+91"):
        phone_number = phone_number[3:]
    elif phone_number.startswith("91"):
        phone_number = phone_number[2:]

    if len(phone_number) == 10 and phone_number.isdigit():
        num = int(phone_number)
        if 6000000000 <= num <= 9999999999:
            return True
    return False

valid_mobile_count = 0

for record in dataset:
    phone_number = record.get("phoneNumber", "")
    if is_valid_mobile(phone_number):
        valid_mobile_count += 1
        
ages = []
num_medicines = []
missing_data = {"firstName": 0, "lastName": 0, "birthDate": 0}
age_groups = {"Child": 0, "Teen": 0, "Adult": 0, "Senior": 0}
medicine_count = 0
medicine_counter = Counter()
active_medicines = 0
inactive_medicines = 0

for record in dataset:
    patient_details = record.get("patientDetails", {})
    phone_number = patient_details.get("phoneNumber", "")
    gender = patient_details.get("gender", "")
    birth_date = patient_details.get("birthDate")
    consultation_data = record.get("consultationData", {})

    for field in missing_data:
        if not patient_details.get(field):
            missing_data[field] += 1

    if is_valid_mobile(phone_number):
        valid_mobile_count += 1

    age = calculate_age_from_birth_date(birth_date)
    if age is not None:
        ages.append(age)
        if age <= 12:
            age_groups["Child"] += 1
        elif age <= 19:
            age_groups["Teen"] += 1
        elif age <= 59:
            age_groups["Adult"] += 1
        else:
            age_groups["Senior"] += 1

    medicines = consultation_data.get("medicines", [])
    num_medicines.append(len(medicines))
    for medicine in medicines:
        medicine_count += 1
        medicine_counter[medicine["medicineName"]] += 1
        if medicine.get("isActive"):
            active_medicines += 1
        else:
            inactive_medicines += 1

filtered_ages = []
filtered_num_medicines = []

for i in range(min(len(ages), len(num_medicines))):
    filtered_ages.append(ages[i])
    filtered_num_medicines.append(num_medicines[i])

correlation = "Insufficient data"
if len(filtered_ages) > 1 and len(filtered_num_medicines) > 1:
    correlation, _ = pearsonr(filtered_ages, filtered_num_medicines)
    correlation = round(correlation, 2)

total_records = len(dataset)
average_medicines = round(medicine_count / total_records, 2)

third_most_common_medicine = medicine_counter.most_common(3)[-1][0] if len(medicine_counter) >= 3 else None

active_percentage = round((active_medicines / medicine_count) * 100, 2) if medicine_count else 0
inactive_percentage = round((inactive_medicines / medicine_count) * 100, 2) if medicine_count else 0

missing_percentages = {k: round((v / total_records) * 100, 2) for k, v in missing_data.items()}

ages = []
num_medicines = []

for record in dataset:
    birth_date = record.get("patientDetails", {}).get("birthDate")
    age = calculate_age_from_birth_date(birth_date)
    if age is not None:
        ages.append(age)
        medicines = record.get("consultationData", {}).get("medicines", [])
        num_medicines.append(len(medicines))

if len(ages) > 1 and len(num_medicines) > 1:
    correlation, _ = pearsonr(ages, num_medicines)
    print(round(correlation, 2))
else:
    print("Insufficient data for correlation calculation.")



female_count_imputed = sum(1 for record in dataset if record.get("patientDetails", {}).get("gender", "") == "F")
female_percentage = round((female_count_imputed / total_records) * 100, 2)

results = {
    "missing_percentages": missing_percentages,
    "female_percentage": female_percentage,
    "adult_count": age_groups["Adult"],
    "average_medicines": average_medicines,
    "third_most_frequent_medicine": third_most_common_medicine,
    "medicine_distribution": (active_percentage, inactive_percentage),
    "valid_mobile_count": valid_mobile_count,
    "pearson_correlation": correlation
}

for key, value in results.items():
    print(f"{key}: {value}")
