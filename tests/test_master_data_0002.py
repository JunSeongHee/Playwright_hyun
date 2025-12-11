import pytest
from pages.lnb.lnb_menu_page import LnbMenuPage
from pages.master_data_0002.master_data_0002_page import MasterData0002
from utils.customLogger import LogGen

# 전역 로거 설정
logger = LogGen.loggen()

def open_master_data_0002(page, base_url):
    page.goto(base_url)
    page.screenshot(path="screenshot.png", full_page=True)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    lnb = LnbMenuPage(page)
    lnb.go_to_master_data_0002()

    return MasterData0002(page)

@pytest.mark.order(2)
def test_master1_code_workflow(page, base_url):
    master_page = open_master_data_0002(page, base_url)
    logger.info("차량속성마스터 관리 페이지 진입 완료")

    try:
        page.wait_for_timeout(timeout=1000)
        assert master_page.model_add() is True

        page.wait_for_timeout(timeout=1000)
        assert master_page.option_add() is True
    except Exception as e:
        logger.error(f"#차량속성마스터 관리 - 처리 중 에러 발생: {e}")
        return False, f"처리 중 에러 발생: {e}"
