from pathlib import Path
import pandas as pd

ROOT=Path(__file__).parent / "sample_data"; ROOT.mkdir(parents=True,exist_ok=True)
inventory=[
 ["P001","Laptop Pro 14","Electronics",15,20,100,50000,"Hyderabad"],
 ["P002","Mechanical Keyboard","Electronics",40,50,200,2000,"Hyderabad"],
 ["P003","Wireless Mouse","Electronics",500,100,1000,500,"Hyderabad"],
 ["P004","27-inch Monitor","Electronics",25,30,150,15000,"Hyderabad"],
 ["P005","USB-C Dock","Accessories",8,25,120,7500,"Bengaluru"],
 ["P006","Noise-Cancel Headset","Accessories",90,40,180,6000,"Bengaluru"],
 ["P007","Webcam HD","Accessories",12,20,100,3500,"Mumbai"],
 ["P008","External SSD 1TB","Storage",220,50,200,8000,"Mumbai"],
]
pd.DataFrame(inventory,columns=["product_id","product_name","category","current_stock","reorder_level","maximum_stock","unit_cost","warehouse"]).to_excel(ROOT/"inventory.xlsx",index=False)

orders=[]
spec=[("P001","Laptop Pro 14",[10,8,6,4]),("P002","Mechanical Keyboard",[30,22,18,15]),("P003","Wireless Mouse",[100,80,75,60]),("P004","27-inch Monitor",[15,12,10]),("P005","USB-C Dock",[8,10,6,9]),("P006","Noise-Cancel Headset",[12,15,10]),("P007","Webcam HD",[9,7,8]),("P008","External SSD 1TB",[25,30,20])]
oid=1
for pidx,(pid,name,quantities) in enumerate(spec):
    for idx,qty in enumerate(quantities):
        date=pd.Timestamp("2026-08-07")+pd.Timedelta(days=idx*3+pidx%3)
        priority="HIGH" if pid in {"P001","P005","P007"} and idx<2 else ("MEDIUM" if idx%2==0 else "LOW")
        orders.append([f"ORD{oid:03d}",pid,name,qty,date,f"Customer {chr(65+(oid%12))}",priority,"PENDING"]); oid+=1
pd.DataFrame(orders,columns=["order_id","product_id","product_name","quantity","order_date","customer","priority","status"]).to_excel(ROOT/"orders.xlsx",index=False)

suppliers=[]; sid=1
for pid,name,base in [("P001","Laptop Pro 14",50000),("P002","Mechanical Keyboard",2000),("P003","Wireless Mouse",500),("P004","27-inch Monitor",15000),("P005","USB-C Dock",7500),("P006","Noise-Cancel Headset",6000),("P007","Webcam HD",3500),("P008","External SSD 1TB",8000)]:
    suppliers.append([f"S{sid:03d}","ReliableSource India",pid,name,base,20 if base>10000 else 50,7,.95,"REGULAR"]); sid+=1
    suppliers.append([f"S{sid:03d}","RapidRelief Supply",pid,name,round(base*1.30,2),5 if base>10000 else 10,2,.86,"EMERGENCY"]); sid+=1
pd.DataFrame(suppliers,columns=["supplier_id","supplier_name","product_id","product_name","unit_price","minimum_order_quantity","lead_time_days","reliability_score","supplier_type"]).to_excel(ROOT/"suppliers.xlsx",index=False)
print(f"Generated curated workbooks in {ROOT}")
