import csv
import random
import os
import time

students_data = []

all_possible_weeks = [f"Week {i}" for i in range(1, 14)]
valid_score_weeks = [week for week in all_possible_weeks if week != "Week 6"]


def read_csv_data(filename):
    global students_data
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            students_data = list(reader)
            time.sleep(1)
        print(f"Successfully read data from '{filename}'.")
        time.sleep(1.5)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found. Please ensure the path is correct.")
        exit(1)


def adding_missing_scores():
    print("Generating missing scores for later weeks...")
    time.sleep(1.5)
    weeks_to_preserve = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
    for row in students_data:
        for week in valid_score_weeks:
            if week in weeks_to_preserve:
                continue
            current_score = row.get(week)
            if not current_score or not str(current_score).strip().isdigit():
                random_score = random.randint(0, 3)
                row[week] = str(random_score)
    print("Missing scores for later weeks populated.")
    time.sleep(1.5)


def calculate_all_student_metrics():
    print("Calculating total and average points...")
    time.sleep(1)
    for row in students_data:
        scores = []
        for week in valid_score_weeks:
            score_value = row.get(week)
            if score_value is not None and str(score_value).strip().isdigit():
                scores.append(int(str(score_value).strip()))
        row["Total Points"] = calculate_total_points(scores)
        row["Average Points"] = calculate_average_points(scores)
    print("Calculations complete.")


def calculate_total_points(scores):
    if len(scores) >= 10:
        top_scores = sorted(scores, reverse=True)[:10]
        return sum(top_scores)
    else:
        return "###"


def calculate_average_points(scores):
    if len(scores) >= 10:
        top_scores = sorted(scores, reverse=True)[:10]
        return round(sum(top_scores) / 10, 2)
    else:
        return "###"


def write_updated_csv(filename):
    output_fieldnames = ["Name"] + valid_score_weeks + ["Total Points", "Average Points"]

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=output_fieldnames)
            writer.writeheader()
            for row in students_data:
                clean_row = {key: row.get(key, "") for key in output_fieldnames}
                writer.writerow(clean_row)
        print(f"Updated data successfully written to:")
        time.sleep(1.5)
        print(f"  {os.path.abspath(filename)}")
    except Exception as e:
        print(f"An error occurred while writing the CSV file: {e}")


if __name__ == "__main__":
    # <<<<<<<<<<<< Customize These >>>>>>>>>>>>>
    input_directory_path = r"C:\Users\schmi\OneDrive\Dokumente\!Uni\2 Semester\TechBasics 1"
    input_csv_base_filename = "Technical Basics I_2025 - Sheet1.csv"
    user_identifier = "MyAnalysis"

    input_csv_filename = os.path.join(input_directory_path, input_csv_base_filename)

    print(f"\nStarting processing for file: '{input_csv_filename}'")

    # Step 1: Read the CSV file
    read_csv_data(input_csv_filename)

    # Step 2: Add missing scores (excluding Week 1–5)
    adding_missing_scores()

    # Step 3: Calculate totals and averages based on best 10 scores
    calculate_all_student_metrics()

    # Step 4: Save results to a new file in the same folder
    output_csv_filename = input_directory_path + "\\results_calculated.csv"

    write_updated_csv(output_csv_filename)

    print("\nScript execution finished.")