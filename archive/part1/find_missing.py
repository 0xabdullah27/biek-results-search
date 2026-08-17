"""
Find missing roll numbers from sg_rolls.txt that are not in sg_results.csv
"""

# Read all roll numbers from sg_rolls.txt
print("Reading sg_rolls.txt...")
with open('sg_rolls.txt', 'r') as f:
    rolls_to_check = set(line.strip() for line in f if line.strip())

print(f"Total rolls in sg_rolls.txt: {len(rolls_to_check):,}")

# Read all roll numbers from sg_results.csv
print("Reading sg_results.csv...")
found_rolls = set()
with open('results/sg_results.csv', 'r', encoding='utf-8') as f:
    import csv
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('roll_no'):
            found_rolls.add(row['roll_no'].strip())

print(f"Total rolls in sg_results.csv: {len(found_rolls):,}")

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
else:
    print("All rolls found!")
