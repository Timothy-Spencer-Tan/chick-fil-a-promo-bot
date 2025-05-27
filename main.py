from teams.lafc import run_lafc_promo

def run_all_promos():
    print("🍗 Chick-fil-A Promo Tracker")
    try:
        run_lafc_promo()
    except Exception as e:
        print(f"⚠️ LAFC check failed: {e}")

if __name__ == "__main__":
    run_all_promos()
