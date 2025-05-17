import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# Inject custom CSS
# -------------------------------


# CSS สำหรับปุ่มแต่ละแบบ
st.markdown("""
<style>
div.stButton > button {
    background-color: #002f6c;      /* สีส้ม */
    color: white;                   /* ตัวอักษรสีขาว */
    font-size: 12px;                /* ขนาดตัวอักษร */
    border-radius: 12px;            /* มุมโค้ง */
    border: none;
    padding: 10px 24px;
     width: 100%;
     height: 100%;
}
div.stButton > button:hover {
    background-color: #e67300;      /* สีตอน hover */
/* เส้นใต้กล่องปุ่ม */
.button-wrapper {
    border-bottom: 2px solid #002f6c;
    padding-bottom: 16px;
    margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)




# -------------------------------
# เตรียม state
# -------------------------------
if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = None
if "input_topic" not in st.session_state:
    st.session_state["input_topic"] = ""

for i in range(1, 4):
    st.session_state.setdefault(f"messages_bot{i}", [])
    st.session_state.setdefault(f"prefill_input_{i}", "")

# -------------------------------
# โหลด system prompt
# -------------------------------
with open("genai-mf-prompt-for-first-draft.txt", "r", encoding="utf-8") as f:
    prompt_mf = f.read()
with open("gen-ai-motor-first-draft.txt", "r", encoding="utf-8") as f:
    prompt_motor = f.read()
with open("genai-cc-prompt-for-first-draft.txt", "r", encoding="utf-8") as f:
    prompt_cc = f.read()
    
import pandas as pd
df=pd.read_csv('df.csv')
df2=pd.read_csv('df2.csv') 
df3=pd.read_csv('df3.csv') 
df4=pd.read_csv('df4.csv')
df5=pd.read_csv('df5.csv') 
df6=pd.read_csv('df6.csv')  
df7=pd.read_csv('df7.csv')  
card_info ="""[
  {
    "prod_credit_card": "so fast",
    "card_expired_date": "30/05/2025",
    "last_usage_date": "-",
    "card_status": "active",
    "point_bal_present": 0,
    "card_no_masking":"211549XXXXXX3382"
  },
  {
    "prod_credit_card": "reserve infinite",
    "card_expired_date": "31/05/2027",
    "last_usage_date": "13/05/2025",
    "card_status": "active",
    "point_bal_present": 1231569,
    "card_no_masking":"431569XXXXXX3542"
  }
]"""
cust="""[{
  "age": 62,
  "life_stage_by_age": "Young Wealth",
  "gender_cd": "M",
  "tmba_occ_group": "Salary",
  "pri_city": "กรุงเทพ",
  "med_income": 300000,
  "occupation_bu" : "Professional"
}]"""
df=df[['preference','subcategory','merchant','total_amount','total_txn','as_of_date']]
df2=df2[['preference','datamonth','total_amount','total_txn']]
df3=df3[['country_name','total_spending_last6m','total_txn_last6m']]
for index, row in df5.iterrows():
    df5.at[index, 'rag'] = (
        'ลูกค้าควร redemption point  :' + row['recommended_redemption_name'] +
        'ซึ่งอยู่ในหมวดหมู่' + row['subcategory'] +
        'เป็น redemption point ประเภท' + row['redemption_type'] +
        'เนื่องด้วย' + row['reason'] +
        'ดูรายละเอียดได้ที่' + row['recommended_redemption_url']   )

df4.columns = df4.columns.str.strip()
df4['points_required'] = df4['points_required'].astype(float).fillna(0).astype(str)
df4['privilege_name'] = df4['privilege_name'].fillna('')
df4['privilege_subcat'] = df4['privilege_subcat'].fillna('')
df4['privilege_type'] = df4['privilege_type'].fillna('')
df4['reason'] = df4['reason'].fillna('')
df4['privilege_url'] = df4['privilege_url'].fillna('')
for index, row in df4.iterrows():
    df4.at[index, 'rag'] = (
        'ลูกค้าควรได้สิทธิประโยชน์หรือ privillage :' + row['privilege_name'] +
        'ซึ่งอยู่ในหมวดหมู่' + row['privilege_subcat'] +
        'เป็นสิทธิประโยชน์ประเภท' + row['privilege_type'] +
        'เนื่องด้วย' + row['reason'] + 'ต้องใช้คะแนนทั้งหมด' + row['points_required'] +
        'ดูรายละเอียดได้ที่' + row['privilege_url'])
for index, row in df7.iterrows():
    df7.at[index, 'rag'] = (
        'ลูกค้าควรได้สิทธิประโยชน์หรือ promotion :' + row['recommended_promotion_name'] +
        'ซึ่งอยู่ในหมวดหมู่' + row['subcategory'] +
        'เป็นสิทธิประโยชน์ประเภท' + row['benefit_type'] +
        'เนื่องด้วย' + row['reason'] + 'ต้องใช้คะแนนทั้งหมด'
        'ดูรายละเอียดได้ที่' + row['recommended_promotion_url']    )
pro=''
for i in (list(df4['rag'])):
    pro=pro+str(i)+',/n'
rd=''
for i in (list(df5['rag'])):
    rd=rd+str(i)+',/n'
o=''
for i in (list(df7['rag'])):
    o=o+str(i)+',/n'

from datetime import datetime
now = datetime.now()
now_string = now.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD HH:MM:SS
# Create the query string
prompt_cc_raw =  f"""ในฐานที่คุณเป็นผู้เชี่ยวชาญด้านการใช้บัตรเคดิตของ ttb และเป็นพนักงานทีม creditcard ของ ttb ดั่งนี้
1 ข้อมูล Persona ของลูกค้า ให้ใช้ข้อมูลจากข้อมูล  JSON {cust} ซึ่งลูกค้าอายุ 62 เป็น Young Wealth และอยู่ที่กรุงเทพ เป็นผู้ชาย    
  ทำอาชีพพนักงานเงินเดือน(Professional) ประมาณ 300,000 บาท
2 ถ้าโดนถามเรื่อง ข้อมูลบัตรเคดิต ให้ใช้ข้อมูลจากข้อมูล  JSON {card_info}  โดย prod_credit_card คือ ประเภททีบัตรที่ลูกค้าถือ และ  
   จำนวนบัตร คือ นับส่วนประกอบใน json เช่น จากตัวอย่างนี้ลูกค้าถือบัตร 2 ใบ คือ reserve infinite  และ so fast
   card_expired_date คือ วันหมดอายุของบัตร  และ card_no_masking คือ หมายเลขบัตร  เช่น ถ้าวันนี้คือ วันที่ {now_string} บัตรที่ใกล้หมดอายุภายใน 1 เดือนคือ  211549XXXXXX3382  จะหมดอายุในวันที่ 30/05/2025
   point_bal_present คือ point ในบัตรที่เหลือในปัจจุบัน เช่น บัตร 431569XXXXXX3542 เหลือ point 1231569 ซึ่งสามารถนำยไปใช้ในสิทธิประโยชน์ต่างๆได้
   last_usage_date คือ วันที่ใช้บัตรล่าสุด เช่น บัตร  431569XXXXXX3542 เป็นบัตรที่ใช้ล่าสุดซึ่งคือวันที่ 13/05/2025
   card_status คือ สถานะของบัตร โดย active คือ ลูกค้ายังแอคทีฟบัตรนั้นอยู่ ส่วน inactive คือ ลูกค้าไม่ได้ใช้งานบัตร
3 ข้อมูลด้านล่างคือพฤติกรรมการใช้บัตรเครดิตของลูกค้า A ที่อ้างอิงจากตาราง `df` ซึ่งมี transaction การใช้จ่ายในช่วง 6  
  เดือนที่ผ่านมา: {df.groupby('subcategory').agg({'total_amount': 'sum','total_txn': 'sum'}).reset_index()}
  และ ถ้าแบบหมวดหมู่ร้านค้า perference  {df.groupby(['subcategory', 'preference']).agg({'total_amount': 'sum','total_txn': 'sum'
}).reset_index()} ถ้าดูในระดับร้านค้า {df.groupby(['merchant','subcategory','preference']).agg({'total_amount': 'sum','total_txn': 'sum'}).reset_index()} ข้อมูล trend การใช้งาน {(df2.groupby(['datamonth','preference']).agg({'total_amount': 'sum','total_txn': 'sum'
}).reset_index())}  ข้อมูลการรูทบัตรเคดิตในแต่ละประเทศ {(df3.groupby(['country_name']).agg({'total_spending_last6m': 'sum','total_txn_last6m': 'sum'}).reset_index())}  
  3.1 พฤติกรรมการใช้จ่ายของลูกค้าในมุมของยอดเงินที่ใช้จ่ายทั้งหมดใน 6 เดือน ในมุมของร้านค้าและ category/subcategory หรือหมวดหมู่ของร้านค้า
  ซึ่งพฤติกรรมการใช้จ่ายของลูกค้า A ใน 6 เดือนมียอดรวม 2848347.18 ส่วนใหญ่ใช้จ่ายด้าน LIFE INSURANCE ,OTHER SHOPPING,RESTAURANT PHYSICAL ซึ่ง คือจ่ายด้านประกัน ช๊อปปิ้ง และ ร้านอาหารที่กินแบบไม่ใช่ online (physical) แต่ใช้จ่ายน้อสุดในหมวด KID
  ถ้าดูในระดับร้านค้าจะพบว่า KRUNGTHAI AXA เป็น merchant ที่ใช้จ่ายเยอะที่สุดใน 6 เดือนและ เยอะที่สุดในหมวดหมู่ LIFE INSURANCE  โดยมียอด 1263890.5  ในแง่มุมของความถี่ในการใช้บริการ หรือ transaction ที่ทำจะพบว่าลูกค้าใช้หมวด online  เยอะที่สุด  ทั้งหมด 72 ครั้ง แต่ ร้านค้าที่มีความถี่เยอะที่สุด 34 ครั้ง คือ SHOPEE  ใน 6 เดือนลูกค้ามี ticket size ทั้งหมดโดยเฉลี่ย 6781
  ขออธิบายเพิ่มเติมในแต่ละ subcategory ร้านค้า หรือหมวดหมู่ร้านค้า
subcategory :ATTRACTIONคือสถานที่ท่องเที่ยว เช่น สวนสนุก พิพิธภัณฑ์
subcategory :RESTAURANT DELIVERYคือร้านอาหารแบบเดลิเวอรี่ เช่น GrabFood, foodpanda
subcategory :ONLINEคือการใช้จ่ายออนไลน์ทั่วไป เช่น ช้อปปิ้งบนแอปหรือเว็บไซต์
subcategory :RESTAURANT PHYSICAL - TH MASSคือร้านอาหารทั่วไปในไทยแบบออฟไลน์ เช่น ร้านในห้าง ร้านข้างทาง
subcategory :DIGITALคือบริการดิจิทัล เช่น สตรีมมิ่ง เพลง แอปสมาชิกต่าง ๆ
subcategory :OTHERคืออื่น ๆ 
subcategory :SHOPPING GROCERYคือร้านซูเปอร์มาร์เก็ต หรือ ร้านขายของชำ
subcategory :EXPRESSWAYคือค่าทางด่วน
subcategory :DESSERT AND DRINKคือของหวานและเครื่องดื่ม เช่น ชานม กาแฟ
subcategory :FASHION - INTERNATIONALคือเสื้อผ้าแฟชั่นแบรนด์ต่างประเทศ
subcategory :GADGET AND TELECOMคืออุปกรณ์ไอที มือถือ อินเทอร์เน็ต
subcategory :OTHER SHOPPINGคือหมวดการช้อปปิ้งอื่น ๆ ที่ไม่อยู่ในหมวดหลัก
subcategory :TRAVEL BOOKING PLATFORM & TRAVEL AGENTคือจองทัวร์/ตั๋วผ่านแอปหรือเอเจนซี่ท่องเที่ยว
subcategory :LIFE INSURANCEคือประกันชีวิต
subcategory :GASคือปั๋มน้ำมันรถหรือแก๊ส
subcategory :SPORTS STOREคือร้านขายอุปกรณ์กีฬา
subcategory :FASHION - TH MASSคือเสื้อผ้าแบรนด์ไทยทั่วไป เช่น AIIZ, G2000
subcategory :RESTAURANT PHYSICAL - INTERNATIONALคือร้านอาหารต่างประเทศแบบออฟไลน์
subcategory :NON-LIFE INSURANCEคือประกันที่ไม่ใช่ชีวิต เช่น ประกันรถ บ้าน สุขภาพ
subcategory :CAR RENTALคือค่าเช่ารถยนต์
subcategory :BOOK AND STATIONERYคือร้านหนังสือและเครื่องเขียน
subcategory :HOMEคือร้านที่เกี่ยวกับบ้าน เช่น อุปกรณ์สร้างบ้าน
subcategory :RESTAURANT PHYSICAL - TH LUXURYคือร้านอาหารหรูในไทย แบบออฟไลน์ เช่น Fine Dining
subcategory :MALL - TH LUXURYคือห้างหรูในไทย เช่น Siam Paragon
subcategory :HOTEL - TH LUXURYคือโรงแรมหรูในไทย 
subcategory :HOTEL - TH MASSคือโรงแรมทั่วไปในไทย
subcategory :HEALTH FITNESSคือร้านค้าที่เกี่ยวกับสุขภาพ เช่น  ฟิตเนส โยคะ คลาสสุขภาพ คลินิก
subcategory :HOME FURNITUREคือเฟอร์นิเจอร์ในบ้าน เช่น โต๊ะ เตียง โซฟา
subcategory :MALL - INTERNATIONALคือห้างแบรนด์ต่างประเทศ 
subcategory :KIDคือของใช้เด็ก ของเล่นเด็ก
subcategory :EDUCATIONคือค่าเล่าเรียน คอร์สเรียน หนังสือเรียน
subcategory :TRANSPORTATIONคือการเดินทาง เช่น รถไฟฟ้า รถสาธารณะ
subcategory :LEASING AND DEALERคือค่าผ่อนรถ หรือจากดีลเลอร์รถยนต์



***ชื่อร้านค้าต้องใช้ merchant  จากตาราง {df} เท่านั้น  ห้ามแต่งชื่อใหม่ เช่น ถ้าถามว่าลูกค้าใช้จ่ายในหมวดการศึกษา(education) คำตอบคือร้าน BISB LIMITED จำนวนเงิน 80000 บาท
   หรือถ้าถูกถามว่าใน 6 เดือนลูกค้าเคยใช้ร้านค้าใดบ้างในหมวดหมู่ร้านหนังสือ ต้องตอบว่า ร้านที่ลูกค้่เคยไปคิอ YOSHIYA HANABISHI,SUZUKANO SUZUKAPASHUYAK,B2S ตอบจากข้อมูลตาราง {df}
   หากถูกถามว่าใน 6 เดือนที่ผ่านมาไปใช้ร้านบริการ B2S ด้วยจำนวนเงินที่เท่าไร และ กี่ครั้ง ต้องงตอบว่า 64 บาท ใช้ทั้งหมด 1 ครั้ง
   
  3.2 พฤติกรรมการใช้ร้านค้าในมุมของหมวดหมู่ร้านค้า preference หรือลักษณะของร้านค้าซึ่งจะแบ่งออกเป็น 3 ลักษณ์ คือ Financial preference(ร้านที่เกี่ยวกับด้านการเงิน),Luxury preference(ร้านอาหารที่ค่อนข้างหรู มีราคาแพง) และ General preference(ร้านค้าทั่วไป)
  จากข้อมูลลูกค้า A ถ้าดูจากหมวดหมู่ร้านค้า หมวดหมู่ด้านการเงิน(Financial preference) ลูกค้าใช้จ่าย ใน LIFE INSURANCE มากที่สุด ใน 6 เดือนเป็นยอด 1562879.73 โดย merchant ที่จ่ายสูงสุดคือ KRUNGTHAI AXA ยอด 1263890.5 ในหมด Financial preference ลูกค้าใช้จ่ายถี่ หรือ transaction มากในmerchant  FWD LIFE ทั้งหมด 4 ครั้ง
  ถ้าในหมวดหมู่ร้านค้า Luxury (Luxury preference  ) จะพบว่าใช้จ่ายในหมวด HOTEL  เยอะที่สุดซึ่งคือร้าน  KIRIMAYA RESORT & SPA
  ถ้าในหมวดหมู่ร้านค้าทั่วไป จะพบว่าลูกค้าใช้จ่ายในหมวด OTHER SHOPPING มากที่สุด โดย merchant ที่จ่ายสูงสุดคือ ร้าน  KALA KRITI ยอด 202248.32  
  3.3 ข้อมูล trend ของลูกค้าจะพบว่า มียอดเงินใช้จ่ายที่สูงขึ้นในช่วง 3 เดือนล่าสุดโดยเพิ่มขึ้นจากเดิม 56% โดยคำนวนจากผลต่างของค่าเฉลี่ยยอดเงินใน 3 เดือนก่อนหน้าและหลังว่า เปอร์เซ็นผลต่างเป็นอย่างไร และช่วงที่ยอดสูงสุดคือ 2025-03-31 ยอดเงิน 1326529.51 บาท แต่ Luxury preference มีทิศทางลดลง 99% จากผลเฉลี่ย 3 เดือนแรก 19426.2 เหลือ ผลเฉลี่ยเงิน 199 บาทใน 3
  เดือนหลัง และ Financial preference มี trend ที่เพิ่มขึ้น ซึ่งในเดือนล่าสุดลูกค้ามีการใช้ยอดในหมวด Financial preference มากที่สุด  
  3.4 ลักษณะการใช้จ่ายของลูกค้าเป็นแบบ online หรือ ชอบใช้จ่ายในประเทศใด
   จากข้อมูลจะพบว่าลูกค้ามีการใช้จ่ายออนไลน์มากที่สุดซึ่ง ออนไลน์คือการจ่ายผ่านระบบออนไลน์ รองลงมาประเทศไทย ยอดการใช้จ่ายที่น้อยที่สุดใน 6 เดือนคือ ประเทศ ญีปุ่น
  3.5 พฤติกรรมการแลก point ของลูกค้าเพื่อวิเคราะห์ความชอบและการใช้งานของลูกค้า
  จากประวัติการแลก point ของลูกค้า {(df6)} จะพบว่าลูกค้าแลกใน benefit ลีมูซีน Camry1 เที่ยว  มากที่สุด และเป็นประเภท AIRLINE point ที่ ใช้ 24000 point และมีการแลกซื้อกองทุน จากข้อมูลจะสามารถวิเคราะห์พฤติกรรมการใช้จ่ายของลูกได้
4 สิทธิประโยชน์ที่ ttb เสนอให้ลูกค้า หรือ ลูกค้าควรได้
  4.1 Privilege สิทธิประโยชน์ของผู้ถือบัตร reserve
  ถ้าถามเกี่ยวกับ Privilege สิทธิประโยชน์ของผู้ถือบัตร reserve หรือสิทธิประโยชน์ให้ดู {(df4)} คือสิ่งที่ ttb offer สิทธิประโยชน์ให้ลูกค้า โดย privilege_name คือชื่อของสิทธิประโยชน์ และ privilege_url  คือลิ้งที่ลูกค้าสามารถเข้าไปใช้สิทธิประโยชน์ได้ และ reason คือ เหตุผลที่ลูกค้าได้ offer ส่วน privilege_rank คืออันดับที่ลูกค้าควรได้ offer ยิ่งเลขน้อยยิ่งดี โดยการ rank จะแบ่งตาประเภทสิทธิประโยชน์ตามช่อง privilege_subcat
  จากการที่ ttb offer privilage  ต้องดูจาก สิทธิประโยชน์ ของ ttb เท่านั้นตัวอย่างการเสนอ privilage
  โดยชนิดของ privilege มี 2 ประเภทจาก  privilege_type ได้แก่ เอกสิทธิ์สำหรับผู้ถือบัตรเครดิต คือ สิทธิพิเศษสำหรับผู้ถือบัตร reserve โดยไม่ต้องใช้ point ในการแลกสิทธิประโยชน์, เอกสิทธิ์ใช้คะแนนแลกของกำนัลพิเศษ  คือ สิทธิพิเศษสำหรับผู้ถือบัตร reserve ที่ต้องใช้ point ในการแลกสิทธิประโยชน์ ข้อมูลสิทธิประโยชน์ที่ offer จากพฤติกรรมให้ลูกค้าคนนี้มีดั่งนี้""" + pro + """
  4.2 ttb reward ที่ต้องใช้ point แลก
   ในการแนะนำให้ลูกค้าแลก point หรือ การ redemption แนะนำให้ลูกค้าเข้าร่วมโปรโมชั่น """+rd+"""
  4.3 ttb Promotion บัตรเคดิต
   ในการแนะนำ promotion บัตรเคดิต จากพฤติกรรมการใช้จ่ายของลูกค้า ต้อง offer ดั่งนี้"""+o+"""
***จากข้อมูลทั้งหมดพยายามตอบแบบคิดวิเคราะห์เชื่อมโยงอย่างเป็นเหตุเป็นผลจากข้อมูลทั้งหมดทั้งข้อมูลการใช้บัตร การแลก point ข้อมูล persona ลูกค้า ข้อมูลการ offer สิทธิประโยชน์ ข้อมูลบัตร ข้อมูลการแลก point ในอดีต และต้องสะกดคำให้ถูกต้อง ไม่ต้องบอกว่ามากจาก json หรือ dataframe
***ห้ามโชว์การคำนวณเด็ดขาดในคำตอบ
***พยายามตอบโดยให้เหตุผลจากข้อมูล และเชื่อมโยงข้อมูล รวมถึงอ้างอิงจากข้อมูลที่ให้ไปเท่านั้น
****ห้ามสะกดคำผิด หรือ ห้ามตอบภาษาแปลกๆ เช่น จีน หรือ ญีปุ่น สัญญาลักษณ์แปลกๆ
****อย่าสะกดภาษาไทยทับซับภาษอังกฤษ
****ตอบในโทนของผู้เชี่ยวชาญด้านการแนะนำ ดูน่าเชื่อถือ
***ชื่อร้านค้าต้องใช้ merchant  จากตาราง {df} เท่านั้น ห้ามแต่งชื่อร้านหรือ promotion ขึ้นเอง
****ข้อมูลนี้คือลูกค้าไปใช้บริการไม่ใช่ให้บริการ"""



 

# -------------------------------
# ฟังก์ชันเรียก OpenAI
# -------------------------------
def ask_openai(messages, system_prompt, max_history=10):
    full_messages = [{"role": "system", "content": system_prompt}] + messages[-max_history:]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=full_messages
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

# -------------------------------
# STEP 1: เลือกหัวข้อหลัก
# -------------------------------

st.markdown(
    """
    <div style='text-align: center; margin-top: -20px;'>
    <br>
        <img src="https://www.ttbbank.com/global/assets/img/media-img/ttb_primary-logo-RGB-01.png" width="120">
        <div style='margin-top: -5px;'>
        </div>
        <h4 style='margin: 8px 0 4px 0;'>Segment of One</h4>
        <hr style='width: 85%; margin: 6px auto; border: 1px solid #aaa;' />
        <p style='font-size: 16px; margin: 0;'>Personalized Financial Solution for Wealth Customer</p>
    </div>
    """,
    unsafe_allow_html=True
)



if st.session_state["selected_topic"] is None:
    st.chat_message("assistant").markdown(
        "สวัสดีค่ะคุณอยากสอบถามเรื่องอะไร?\n\n"
        "กรุณาพิมพ์หัวข้อที่คุณสนใจ ได้แก่: `Asset Allocation`, `Motor Insurance`, หรือ `Credit card` หากต้องการเปลี่ยนหัวข้อให้พิมพ์ว่า `เปลี่ยนหัวข้อ` ค่ะ"
      
    )
    # เส้นแบ่งด้านล่าง
    st.markdown(
    "<hr style='border: 1.5px solid #002f6c; margin-top: 30px; margin-bottom: 30px;' />",
    unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
      if st.button("   Asset Allocation   "):
        st.session_state["input_topic"] = "Asset Allocation"
        st.rerun()

    with col2: 
        if st.button("   Motor Insurance    "):
            st.session_state["input_topic"] = "Motor Insurance"
            st.rerun()

    with col3:
        if st.button("   Credit card    "):
            st.session_state["input_topic"] = "Credit Card"
            st.rerun()

    with st.form(key="topic_form"):
        input_topic = st.text_input("หัวข้อที่คุณต้องการพูดคุย...", value=st.session_state["input_topic"])
        submitted = st.form_submit_button("ส่ง")
        if submitted:
            topic = input_topic.strip().lower()
            topic_map = {
                "asset allocation": "asset",
                "asset": "asset",
                "motor insurance": "motor",
                "motor": "motor",
                "credit card": "credit",
                "credit": "credit"
            }
            if topic in topic_map:
                st.session_state["selected_topic"] = topic_map[topic]
                st.rerun()
            else:
                st.warning("กรุณาพิมพ์เฉพาะ asset allocation, motor insurance, หรือ credit card เท่านั้นนะคะ")

# -------------------------------
# STEP 2: แสดงแชทตามหัวข้อ
# -------------------------------
def chat_tab(title, bot_index, system_prompt, preset_buttons):
    tabs = st.tabs([title])
    with tabs[0]:
        st.subheader(title)

        # แสดงข้อความสนทนาก่อนหน้า
        for msg in st.session_state[f"messages_bot{bot_index}"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ปุ่ม preset → prefill
        cols = st.columns(len(preset_buttons))  # สร้าง columns ตามจำนวน preset
        for i, (col, text) in enumerate(zip(cols, preset_buttons)):
            if col.button(f" {text}", key=f"btn{bot_index}_{i}"):
                st.session_state[f"prefill_input_{bot_index}"] = text
                st.rerun()

        # กล่องแชท
        cols = st.columns([10, 1])
        with cols[0]:
            user_input = st.text_input(
                "ถามคำถาม...",
                value=st.session_state[f"prefill_input_{bot_index}"],
                key=f"text_input_{bot_index}",
                label_visibility="collapsed",
                placeholder="ถามคำถาม..."
            )
        with cols[1]:
            send = st.button("➤", key=f"send_btn_{bot_index}")

        if send and user_input.strip():
            prompt = user_input.strip()
            st.session_state[f"prefill_input_{bot_index}"] = ""

            if prompt == "เปลี่ยนหัวข้อ":
                st.session_state[f"messages_bot{bot_index}"] = []
                st.session_state["selected_topic"] = None
                st.rerun()
            else:
                st.session_state[f"messages_bot{bot_index}"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                reply = ask_openai(st.session_state[f"messages_bot{bot_index}"], system_prompt)
                st.chat_message("assistant").markdown(reply)
                st.session_state[f"messages_bot{bot_index}"].append({"role": "assistant", "content": reply})
                st.rerun()

# -------------------------------
# STEP 3: เปิดแชทตามหัวข้อ
# -------------------------------
if st.session_state["selected_topic"] == "asset":
    chat_tab("Asset Allocation", 1, prompt_mf, [
        "ลูกค้ามี AUM เท่าไหร่ และ Trend AUM ของลูกค้าเป็นอย่างไรใน 1 ปี  ",
        "ลูกค้าจัดสรรเงินส่วนใหญ่ไว้ในผลิตภัณฑ์เงินฝากและกองทุนอย่างไร  ",
        "กองทุนของลูกค้ามี Exposure อย่างไร ทั้งในอดีต ปัจจุบัน และอนาคต  ",
        "ลูกค้ามีเงินเย็นอยู่กี่บาท และวางได้เป็นระยะเวลาเท่าไหร่ นำไปจัดสรรอย่างไร",
        "ผลิตภัณฑ์ Portfolio และ MF ที่แนะนำคืออะไร Potential Gain เป็นเท่าไหร่",
    ])
elif st.session_state["selected_topic"] == "motor":
    chat_tab("Motor Insurance", 2, prompt_motor, [
        "ข้อมูลรถของลูกค้า เช่น ยี่ห้อรถ",
        "ประกันที่ลูกค้าถือก่อนหน้าคือ",
        "VMI ที่เหมาะกับลูกค้าคืออะไร",
        "VMI ที่เสนอประหยัดไปได้เท่าไหร่",
        "ช่องทางที่ลูกค้าจ่ายได้"
    ])
elif st.session_state["selected_topic"] == "credit":
    chat_tab("Credit Card", 3, prompt_cc, [
        "ลูกค้าถือบัตรประเภทไหน status เป็นอย่างไร",
        "พฤติกรรมการใช้จ่ายของลูกค้าเป็นอย่างไร",
        "ลูกค้ามี  Lifestyle การใช้จ่ายเป็นอย่างไร",
        "Promotion/Privilage ที่เหมาะกับลูกค้า",
        "Benefit ที่ลูกค้าควรจะได้รับคืออะไร"
    ])





