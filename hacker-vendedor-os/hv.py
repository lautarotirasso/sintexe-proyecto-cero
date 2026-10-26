"""Hacker Vendedor OS: CRM local, sin envíos externos."""
import argparse
import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "hv.sqlite3"
FIELDS = ["nombre","empresa","cargo","pais","canal","fuente","fecha","oportunidad","prioridad","estado","email","telefono","url"]

def connect(path=DB):
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE IF NOT EXISTS leads (
      id INTEGER PRIMARY KEY, nombre TEXT, empresa TEXT, cargo TEXT, pais TEXT,
      canal TEXT NOT NULL, fuente TEXT NOT NULL, fecha TEXT, oportunidad TEXT,
      prioridad TEXT, estado TEXT, email TEXT, telefono TEXT, url TEXT,
      dedup_key TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)""")
    return con

def key_for(row):
    email = row.get("email","").strip().casefold()
    phone = "".join(c for c in row.get("telefono","") if c.isdigit())
    url = row.get("url","").strip().lower().rstrip("/")
    company = row.get("empresa","").strip().casefold()
    name = row.get("nombre","").strip().casefold()
    if email: return "email:"+email
    if phone: return "phone:"+phone
    if url: return "url:"+url
    if company and name: return "entity:"+company+"|"+name
    return None

def import_csv(con, path):
    stats = {"investigados":0,"verificados":0,"duplicados":0,"descartados":0}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            stats["investigados"] += 1
            row = {k:(raw.get(k) or "").strip() for k in FIELDS}
            key = key_for(row)
            if not row["fuente"].startswith(("https://","http://")) or not row["canal"] or not key:
                stats["descartados"] += 1
                continue
            vals = [row[k] for k in FIELDS] + [key,datetime.now(timezone.utc).isoformat()]
            try:
                con.execute("INSERT INTO leads ("+",".join(FIELDS)+",dedup_key,created_at) VALUES ("+",".join("?" for _ in vals)+")",vals)
                stats["verificados"] += 1
            except sqlite3.IntegrityError:
                stats["duplicados"] += 1
    con.commit()
    return stats

def export(con, folder=ROOT/"exports"):
    folder.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    rows = con.execute("SELECT "+",".join(FIELDS)+" FROM leads ORDER BY id").fetchall()
    csv_path = folder / ("HV_"+stamp+".csv")
    vcf_path = folder / ("HV_"+stamp+".vcf")
    with csv_path.open("w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f);writer.writerow(FIELDS);writer.writerows(rows)
    def safe(s): return str(s or "").replace("\\","\\\\").replace("\n"," ").replace(";","\\;").replace(",","\\,")
    with vcf_path.open("w",encoding="utf-8") as f:
        for r in rows:
            d=dict(zip(FIELDS,r))
            lines=["BEGIN:VCARD","VERSION:3.0","FN:"+safe(d["nombre"] or d["empresa"]),"ORG:"+safe(d["empresa"])]
            if d["cargo"]:lines.append("TITLE:"+safe(d["cargo"]))
            if d["email"]:lines.append("EMAIL;TYPE=WORK:"+safe(d["email"]))
            if d["telefono"]:lines.append("TEL;TYPE=WORK:"+safe(d["telefono"]))
            if d["url"]:lines.append("URL:"+safe(d["url"]))
            lines += ["NOTE:"+safe(d["fuente"]),"END:VCARD"]
            f.write("\n".join(lines)+"\n")
    return {"csv":str(csv_path),"vcf":str(vcf_path),"registros":len(rows)}

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init");sub.add_parser("report");sub.add_parser("export")
    sub.add_parser("import-csv").add_argument("file")
    args=p.parse_args();con=connect()
    if args.cmd=="init": out={"status":"inicializado","database":str(DB)}
    elif args.cmd=="import-csv":out=import_csv(con,args.file)
    elif args.cmd=="report":out={"registros":con.execute("SELECT count(*) FROM leads").fetchone()[0]}
    else:out=export(con)
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
