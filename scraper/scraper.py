import time
from typing import Dict, List, Any
from seleniumbase.common.exceptions import NoSuchElementException, NotConnectedException
from lxml import html
from seleniumbase import Driver


class Scraper():
    def check_address(self, address: str) -> Dict[str, List[Any]]:
        max_attempts = 5
        wallets_list = []
        driver = Driver(uc = True, headless = True)


        print("Opening chrome driver...")


        for attempt in range(max_attempts):
            try:
                # Open Dexscreener.com with token address
                driver.uc_open_with_reconnect("https://dexscreener.com/solana/" + address, 3)
                time.sleep(5)
                print("opened site")


                # Check CloudFlare pass. Raise NotConnectedException if not passed
                if driver.get_title() == "Just a moment...":
                    raise NotConnectedException
                print("Passed CloudFlare")
                

                # Check token symbol. Raise IndexError from "tree.xpath()" if there is no token symbol
                try:
                    tree_xml = html.fromstring(driver.get_page_source())
                    token_symbol = tree_xml.xpath("//*[@id='root']/div/main/div/div/div[1]/div/div[1]/div[1]/div/div[1]/h2/span[1]/span")[0].text_content().strip()
                except:
                    raise IndexError
                
                if not token_symbol.startswith("$"):
                    token_symbol = "$" + token_symbol


                # Open "Top traders" tab
                driver.click("//*[@id='root']/div/main/div/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/button[2]")
                time.sleep(2)
                tree_xml = html.fromstring(driver.get_page_source())


                # Obtain an array of wallet elements
                elements = tree_xml.xpath("//*[@id='root']/div/main/div/div/div[2]/div[1]/div[2]/div/div[1]/div[2]/div[2]")[0]

                for child in elements:
                    # Get wallet with purchase less than $3000
                    price = child[2]
                    price_element = price.find(".//span")

                    if price_element is None:
                        continue

                    price_value = price_element.text_content()

                    if price_value[-1] == 'K' or price_value[-1] == 'M':
                        continue

                    price_value = price_value.replace("$", "")

                    try:
                        if int(price_value.replace(",", "")) > 3000:
                            continue
                    except:
                        print("Unexpected error")
                        continue

                    # Get wallet address
                    last_child = child[-1]
                    link_element = last_child.find(".//a")

                    if link_element is None:
                        continue

                    href_value = link_element.attrib.get("href")
                    wallet = href_value.rsplit('/', 1)[-1]


                    # Open wallet address on Gmgn.ai
                    driver.uc_open_with_reconnect("https://gmgn.ai/sol/address/" + wallet, 20)
                    time.sleep(1)
                    

                    # Pass "It could take up to..." modal
                    try:
                        tree_xml = html.fromstring(driver.get_page_source())
                        if len(tree_xml.xpath("//*[@id='chakra-modal--body-:r13:']/div/button")) > 0:
                            driver.click("//*[@id='chakra-modal--body-:r13:']/div/button")
                    except:
                        pass


                    # Pass "First time on site" modal
                    try:
                        tree_xml = html.fromstring(driver.get_page_source())
                        if len(tree_xml.xpath("//*[@id='chakra-modal-:ri:']/button")) > 0:
                            driver.click("//*[@id='chakra-modal-:ri:']/button")
                    except:
                        pass

                    
                    # Select 30-day stats time interval
                    driver.click("//*[@id='__next']/div/div/main/div[2]/div[1]/div[2]/div[1]/div/div[2]")
                    time.sleep(1)


                    # Check wallet PnL and winrate
                    pnl = driver.get_text("//*[@id='__next']/div/div/main/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]")
                    winrate = driver.get_text("//*[@id='__next']/div/div/main/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]")
                    print(f"Address: {wallet};\t PnL: {pnl};\t WinRate: {winrate};")
                    
                    wallet_address = str(wallet)
                    wallet_pnl = float(pnl.rstrip("%"))
                    if winrate != "--%":
                        wallet_winrate = float(winrate.rstrip("%"))
                    else:
                        wallet_winrate = winrate.rstrip("%")
                    
                    if wallet_pnl > 100 or wallet_winrate != "--" and wallet_winrate == 100:
                        wallets_list.append({"address": wallet_address, "pnl": wallet_pnl, "winrate": wallet_winrate})
                
                driver.quit()
                print("Driver closed")

                return {"token_symbol": token_symbol, "wallets_list": wallets_list}

            except NotConnectedException:
                print(f"Attempt: {attempt + 1} | Error: Antibot not passed")

                if attempt < max_attempts - 1:
                    print("Starting next attempt...")
                else:
                    driver.quit()
                    print("Driver closed")
                    raise NotConnectedException("Antibot not passed\nContact the admin to resolve this")

            except IndexError:
                print(f"Attempt: {attempt + 1} | Error: No such address: {address}")
                driver.quit()
                print("Driver closed")
                raise IndexError(f"No such address: {address}")
                    

            except NoSuchElementException:
                print(f"Attempt: {attempt + 1} | Error: No such element")

                if attempt < max_attempts - 1:
                    print("Starting next attempt...")
                else:
                    driver.quit()
                    print("Driver closed")
                    raise NoSuchElementException("No such element\nContact the admin to resolve this")
