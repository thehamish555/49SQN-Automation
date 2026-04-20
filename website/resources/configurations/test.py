import json
import csv
import random

SYLLABUS_FILE = "syllabus.json"
OUTPUT_CSV = "test.csv"

NCO_POOL = [
    "CPL Ward",
    "CPL Johnson",
    "SGT Holtzhausen",
    "A/F/S Douglas",
    "A/F/S Hann",
    "F/S Gibbs",
    "W/O Griffiths",
]

OFFICER_POOL = [
    "OFFCDT Hargreaves",
    "OFFCDT Lester",
    "SQNLDR Douglas",
]

def hyperlink(code, url):
    return f'=HYPERLINK("{url}", "{code}")'

def allocate_instructors_for_week():
    """Get a shuffled pool of all available instructors"""
    all_instructors = NCO_POOL.copy() + OFFICER_POOL.copy()
    random.shuffle(all_instructors)
    return all_instructors

def smart_sort_key(lesson_num_str):
    """
    Sort lesson numbers properly: 1.1, 1.2, 1.3, ..., 1.9, 1.10, 1.11, 1.12
    NOT: 1.1, 1.10, 1.11, 1.12, 1.2
    """
    parts = str(lesson_num_str).split('.')
    if len(parts) == 2:
        return (int(parts[0]), int(parts[1]))
    elif len(parts) == 1:
        return (int(parts[0]), 0)
    else:
        return (0, 0)

def ordered_lessons(year_data):
    lessons = []
    for subject, items in year_data.items():
        if subject in ("SEA", "FLD"):
            continue
        sorted_keys = sorted(items.keys(), key=smart_sort_key)
        for num in sorted_keys:
            data = items[num]
            lessons.append({
                "code": f"{subject} {num}",
                "title": data["title"],
                "url": data["url"],
                "periods": data["periods"],
                "subject": subject,
            })
    return lessons

with open(SYLLABUS_FILE, "r", encoding="utf-8") as f:
    syllabus = json.load(f)

# Week structure: 10 weeks, empty, 11 weeks, empty, 10 weeks, empty, 9 weeks
week_counts = [10, 11, 10, 9]

# Get all lessons for all years
all_year_lessons = {}
for year_num in [1, 2, 3, 4]:
    year = f"Year {year_num}"
    if year in syllabus:
        all_year_lessons[year] = ordered_lessons(syllabus[year])

# Build rows structure
rows = []

# Header row
header = [""]
for i, count in enumerate(week_counts):
    for week in range(1, count + 1):
        header.append(f"Week {week}")
    if i < len(week_counts) - 1:
        header.append("")  # Empty column
rows.append(header)

total_cols = len(header)

# Initialize row structure for all years
year_row_map = {}
for year_num in [1, 2, 3, 4]:
    year = f"Year {year_num}"
    if year not in all_year_lessons:
        continue
    
    start_row = len(rows)
    year_row_map[year] = start_row
    
    rows.append([f"{year} Period 1"] + [""] * (total_cols - 1))
    rows.append([""] * total_cols)  # lesson codes
    rows.append([""] * total_cols)  # titles
    rows.append([""] * total_cols)  # teachers
    
    rows.append([f"{year} Period 2"] + [""] * (total_cols - 1))
    rows.append([""] * total_cols)  # lesson codes
    rows.append([""] * total_cols)  # titles
    rows.append([""] * total_cols)  # teachers
    
    rows.append([""] * total_cols)  # blank row

# Now fill year by year, handling multi-period lessons
for year_num in [1, 2, 3, 4]:
    year = f"Year {year_num}"
    if year not in all_year_lessons:
        continue
    
    lessons = all_year_lessons[year]
    base_row = year_row_map[year]
    
    col_idx = 1  # Start at column 1 (after label column)
    lesson_idx = 0  # Current lesson we're on
    current_lesson = None
    remaining_periods = 0
    instructor = None
    
    for block_idx, week_count in enumerate(week_counts):
        # Check if this is winter (blocks 1 or 2, which are terms 2-3)
        is_winter = block_idx in [1, 2]
        
        for week in range(week_count):
            if col_idx >= total_cols:
                break
            
            # Get unique instructors for this week
            week_instructors = allocate_instructors_for_week()
            instructor_idx = 0
            
            # PERIOD 1
            if remaining_periods == 0:
                # Need to start a new lesson
                if lesson_idx < len(lessons):
                    current_lesson = lessons[lesson_idx]
                    remaining_periods = current_lesson["periods"]
                    instructor = week_instructors[instructor_idx % len(week_instructors)]
                    instructor_idx += 1
                    lesson_idx += 1
            
            if current_lesson and remaining_periods > 0:
                rows[base_row + 1][col_idx] = hyperlink(current_lesson["code"], current_lesson["url"])
                rows[base_row + 2][col_idx] = current_lesson["title"]
                rows[base_row + 3][col_idx] = instructor
                remaining_periods -= 1
            
            # PERIOD 2
            if remaining_periods == 0:
                # Need to start a new lesson
                if lesson_idx < len(lessons):
                    current_lesson = lessons[lesson_idx]
                    remaining_periods = current_lesson["periods"]
                    
                    # Skip drill in winter for Period 2
                    if is_winter and current_lesson["subject"] == "DRL":
                        # Find next non-drill lesson
                        temp_idx = lesson_idx
                        while temp_idx < len(lessons) and lessons[temp_idx]["subject"] == "DRL":
                            temp_idx += 1
                        
                        if temp_idx < len(lessons):
                            current_lesson = lessons[temp_idx]
                            remaining_periods = current_lesson["periods"]
                            lesson_idx = temp_idx + 1
                        else:
                            # No non-drill available, use current
                            lesson_idx += 1
                    else:
                        lesson_idx += 1
                    
                    instructor = week_instructors[instructor_idx % len(week_instructors)]
                    instructor_idx += 1
            
            if current_lesson and remaining_periods > 0:
                rows[base_row + 5][col_idx] = hyperlink(current_lesson["code"], current_lesson["url"])
                rows[base_row + 6][col_idx] = current_lesson["title"]
                rows[base_row + 7][col_idx] = instructor
                remaining_periods -= 1
            
            col_idx += 1
        
        # Skip empty column between blocks
        if block_idx < len(week_counts) - 1:
            col_idx += 1

# Write as TSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    csv.writer(f, delimiter='\t').writerows(rows)

print(f"Output written to {OUTPUT_CSV}")
OUTPUT_CSV