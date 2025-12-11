import pytest
import pytest_check as check

from pages.lnb.lnb_menu_page import LnbMenuPage
from pages.master_sales_price_manage.master_sale_price_management import MasterSalePriceManage
from pages.tree_composition.tree_composition_management_page import TreeCompositionManagement
from utils.customLogger import LogGen

# 전역 로거 설정
logger = LogGen.loggen()

def goto_sale_price_create(page, base_url):
    """ 국내판매시스템 진입 및 LNB 메뉴 통한 화면 진입 """
    """ 기준정보 > 가격관리 > 판매가격관리 """
    print(f"test_basePage: test_open_base_url {base_url}")

    page.wait_for_load_state("networkidle")
    page.wait_for_tiemout(1000)

    lnb = LnbMenuPage(page)
    lnb.go_to_salge_code_management()

    return MasterSalePriceManage(page)

def goto_newsale_Code_create(page, base_url):
    """ 국내판매시스템 진입 및 LNB 메뉴 통한 화면 진입 """
    """ 기준정보 > 판매코드관리 > 신판매코드 생성 """
    print(f"test_basePage: test_open_base_url {base_url}")
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    lnb = LnbMenuPage(page)
    lnb.go_to_newsale_code_create()

    return TreeCompositionManagement(page)

@pytest.mark.order(5)
def test_master_sale_code_workflow(page, base_url):
    """ 판매가격관리 시나리오 전체 흐름 """
    # 판매가격 관리 화면 진입
    sale_code = goto_sale_price_create(page, base_url)
    logger.info("판매가격관리 페이지 진입 완료")

    # 판매가격 관리 화면에서 가격 설정
    sale_code.basic_perform()
    # 신판매코드 화면 진입
    newcsale_code = goto_newsale_Code_create(page, base_url)
    logger.info("신판매코드 페이지 진입 완료")
    count = newcsale_code.search_conf_tree()

    logger.info(f"[조회 건수] : {count}")
    if count > 0:
        newcsale_code.search_result_table_select()

