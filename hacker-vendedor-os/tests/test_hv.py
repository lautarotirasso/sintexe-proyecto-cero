import csv
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hv import connect, import_csv, key_for, export

class CRMTests(unittest.TestCase):
    def test_dedup(self):
        self.assertEqual(key_for({"email":"A@EXAMPLE.COM"}),"email:a@example.com")
    def test_import_and_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            db=connect(root/"test.db")
            source=root/"input.csv"
            with source.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=["nombre","empresa","canal","fuente","email"])
                w.writeheader()
                for _ in range(2):
                    w.writerow({"nombre":"Ejemplo","empresa":"Organizacion ficticia","canal":"email corporativo","fuente":"https://example.org","email":"test@example.org"})
            result=import_csv(db,source)
            self.assertEqual(result,{"investigados":2,"verificados":1,"duplicados":1,"descartados":0})
            out=export(db,root/"exports")
            self.assertEqual(out["registros"],1)
            self.assertEqual((root/"exports").exists(),True)
if __name__=="__main__":unittest.main()
