from playwright.sync_api import sync_playwright
import json
import time


def clean(t):
    return " ".join(t.split())

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()


        print("The page is opening...")
        page.goto("https://www3.inegi.org.mx/sistemas/ci/relps/", wait_until="load")
        page.wait_for_timeout(2000)

        # find iframe
        relps = None
        for f in page.frames:
            if "relps" in f.url.lower():
                relps = f
                break

        if not relps:
            raise Exception("RELPS iframe not found!")

        print("iframe found:", relps.url)

        # open full table
        relps.locator("text=Ver total de proveedores sancionados").click()
        relps.wait_for_selector("(//tbody)[5]")

        # get the lines
        rows = relps.locator("(//tbody)[5]//tr")
        total = rows.count()
        print("Total rows:", total)

        # 🔥 MERGE STRUCTURE (KEY FIX)
        merged = {}

        for i in range(total):
            rows = relps.locator("(//tbody)[5]//tr")
            row = rows.nth(i)
            cols = row.locator("td")

            if cols.count() < 2:
                print(f"Row {i}: no column, skipping")
                continue

            proveedor = clean(cols.nth(0).text_content())

            # link element (no popup)
            link = row.locator("xpath=.//a[contains(@id,'gvProveedores')]")

            if link.count() == 0:
                print(f"Row {i}: link not found, skipping")
                continue

            print(f"Row {i}: link found, clicking…")
            link.first.click()

            # wait for the detail page to load
            relps.wait_for_selector("//*[@id='cphContenido_gvHistorial']/tbody/tr[2]/td[2]")

            numeros = []

            rows_hist = relps.locator("//*[@id='cphContenido_gvHistorial']/tbody/tr")
            count_hist = rows_hist.count()

            for h in range(1, count_hist):  
                try:
                    num = clean(rows_hist.nth(h).locator("td").nth(1).text_content())
                    if num:
                        numeros.append(num)
                except:
                    pass

            numeros = list(set(numeros))
            
            if not numeros:
                print(f"Row {i}: empty numero, skipping")
                relps.locator("//*[contains(@id,'btnRegresar')]").click()
                relps.locator("text=Ver total de proveedores sancionados").click()
                continue

            # ---------------------------
            # 🔥 MERGE LOGIC (FIX)
            # ---------------------------
            if proveedor not in merged:
                merged[proveedor] = set(numeros)
            else:
                merged[proveedor].update(numeros)

            # go back
            relps.locator("//*[contains(@id,'btnRegresar')]").click()
            relps.locator("text=Ver total de proveedores sancionados").click()
            relps.wait_for_selector("(//tbody)[5]")


            # ---------------------------
            # FINAL CLEAN DATA
            # ---------------------------
        data = []


        for proveedor, numeros in merged.items():
            data.append({
                "proveedor": proveedor,
                "numero": sorted(list(numeros)),
                "source": "inegi_playwright.json"
            })

        print(f"\nFinal unique records: {len(data)}")



        # ---------------------------
        # SAVE
        # ---------------------------
    output_path = "/app/data/inegi_playwright.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Saved → {output_path}")

    browser.close()

except Exception as e:
    print("ERROR:", e)
