import os, sys

ROOT = r"D:\RazarPay\Ai Risk Manager"
targets = [
    "backend/app/api/__init__.py",
    "backend/app/__init__.py",
    "backend/app/services/__init__.py",
    "backend/app/services/audit_service.py",
    "backend/app/services/transaction_service.py",
    "backend/app/api/routes/transactions.py",
    "backend/app/db/seed_transactions.py",
]

for rel in targets:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print("MISSING", rel)
        continue
    with open(p, "rb") as f:
        data = f.read()
    if b"\x00" not in data:
        print("OK", rel)
        continue
    # Decode as UTF-16 (2 bytes per char, BOM optional) then re-encode UTF-8
    text = data.decode("utf-16-le", errors="ignore")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("CONVERTED", rel)