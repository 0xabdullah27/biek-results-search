"""
Check for duplicates and missing rolls
"""

# Read all roll numbers from sg_rolls.txt
print("Reading sg_rolls.txt...")
with open('sg_rolls.txt', 'r') as f:
    rolls_to_check = set(line.strip() for line in f if line.strip())

print(f"Total unique rolls in sg_rolls.txt: {len(rolls_to_check):,}")

# Read all roll numbers from sg_results.csv
print("Reading sg_results.csv...")
import csv
found_rolls = set()
all_found_rolls = []
duplicate_counts = {}

with open('results/sg_results.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('roll_no'):
            roll = row['roll_no'].strip()
            all_found_rolls.append(roll)
            found_rolls.add(roll)
            duplicate_counts[roll] = duplicate_counts.get(roll, 0) + 1

print(f"Total lines in sg_results.csv: {len(all_found_rolls):,}")
print(f"Total unique rolls in sg_results.csv: {len(found_rolls):,}")

# Check for duplicates
duplicates = {roll: count for roll, count in duplicate_counts.items() if count > 1}
if duplicates:
    print(f"\nFound {len(duplicates)} duplicate roll numbers:")
    for roll, count in sorted(duplicates.items(), key=lambda x: int(x[0]))[:20]:
        print(f"  {roll}: appears {count} times")
    if len(duplicates) > 20:
        print(f"  ... and {len(duplicates) - 20} more")

# Find missing rolls
missing = sorted(rolls_to_check - found_rolls, key=int)

print(f"\nMissing roll numbers: {len(missing):,}")
print("=" * 60)

if missing:
    print("\nMissing rolls:")
    for i, roll in enumerate(missing, 1):
        print(f"  {i:5}. {roll}")

    # Save missing rolls to a file
    with open('missing_sg_rolls.txt', 'w') as f:
        for roll in missing:
            f.write(f"{roll}\n")
    print(f"\nSaved {len(missing):,} missing rolls to missing_sg_rolls.txt")
