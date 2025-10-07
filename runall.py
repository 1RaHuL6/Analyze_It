import os

fixtures_dir = "attendance_portal/fixtures/split_fixtures"

for file in sorted(os.listdir(fixtures_dir)):
    if file.endswith(".json"):
        path = os.path.join(fixtures_dir, file)
        print(f"📥 Loading {path} ...")
        os.system(f"python manage.py loaddata {path}")

print("✅ All fixtures loaded into Postgres!")