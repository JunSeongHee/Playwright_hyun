from playwright.sync_api import Page, TimeoutError
from pages.base_page import BasePage

class LnbMenuPage(BseePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def go_to_vehicle_info_management(self):
        self.logger.info('LNB 통한 차량정보관리 진입')

        try:
            self.click_by_css('button.btn_menu:has-text("기준정보")')
            self.click_by_text('판매코드 관리', 0)
            self.click_by_text('차량정보 관리')

        except TimeoutError:
            self.page.screenshot(path="lnb_fail_차량정보관리.png")
            raise AssertionError("기준정보 메뉴를 10초 내에 찾지 못했습니다. 네트워크, 서버, UI 상태를 확인하세요.")
        except Exception as e:
            self.page.screenshot(path="lnb_unexpected_fail_차량정보관리.png")
            self.logger.error(f"예기치 않은 LNB 진입 에러: {e}")
            raise

    def go_to_master_data_0002(self):
        self.logger.info('LNB 통한 차량속성 마스터 관리 진입')
        try:
            self.click_by_css('button.btn_menu:has-text("기준정보")')
            self.click_by_text('판매코드 관리', 0)
            self.click_by_text('차량속성마스터 관리', 0)
        except TimeoutError:
            self.page.screenshot(path="lnb_fail_차량속성마스터.png")
            raise AssertionError("기준정보 메뉴를 10초 내에 찾지 못했습니다. 네트워크, 서버, UI 상태를 확인하세요.")
        except Exception as e:
            self.page.screenshot(path="lnb_unexpected_fail_차량속성마스터.png")
            self.logger.error(f"예기치 않은 LNB 진입 에러: {e}")
            raise

    def go_to_nsc_management(self):
        self.logger.info('LNB 통한 신판매코드(NSC) 구성 관리 진입')
        try:
            self.click_by_css('button.btn.menu:has-text("기준정보")')
            self.click_by_text('판매코드 관리', 0)
            self.click_by_text('신판매코드(NSC) 구성 관리')
        except TimeoutError:
            self.page.screenshot(path="lnb_fail_신판매코드(NSC).png")
            raise AssertionError("기준정보 메뉴를 10초 내에 찾지 못했습니다. 네트워크, 서버, UI 상태를 확인하세요.")
        except Exception as e:
            self.page.screenshot(path="lnb_unexpected_fail_신판매코드(NSC).png")
            self.logger.error(f"예기치 않은 LNB 진입 에러: {e}")
            raise

    def go_to_newsale_code_create(self):
        self.logger.info('LNB 통한 신판매코드 생성 진입')
        try:
            self.click_by_css('button.btn.menu:has-text("기준정보")')
            self.click_by_text('판매코드 관리', 0)
            self.page.get_by_text('신판매코드 생성').nth(0).click()
        except TimeoutError:
            self.page.screenshot(path="lnb_fail_신판매코드.png")
            raise AssertionError("기준정보 메뉴를 10초 내에 찾지 못했습니다. 네트워크, 서버, UI 상태를 확인하세요.")
        except Exception as e:
            self.page.screenshot(path="lnb_unexpected_fail_신판매코드.png")
            self.logger.error(f"예기치 않은 LNB 진입 에러: {e}")
            raise

    def go_to_salge_code_management(self):
        self.logger.info('LNB 통한 판매가격관리 진입')
        try:
            self.click_by_css('button.btn.menu:has-text("기준정보")')
            self.click_by_text('가격관리', 0)
            self.page.locator('span[title="판매가격관리"]').click()
        except TimeoutError:
            self.page.screenshot(path="lnb_fail_판매가격관리.png")
            raise AssertionError("기준정보 메뉴를 10초 내에 찾지 못했습니다. 네트워크, 서버, UI 상태를 확인하세요.")
        except Exception as e:
            self.page.screenshot(path="lnb_unexpected_fail_판매가격관리.png")
            self.logger.error(f"예기치 않은 LNB 진입 에러: {e}")
            raise

    def go_to_vehicle_selection(self):
        self.logger.info('LNB 통한 차량 선택 진입')
        try:
            self.click_by_css('button.btn.menu:has-text("기준정보")')
            self.click_by_text('판매코드 관리', 0)
            self.click_by_text('차량 선택', 0)
        except TimeoutError:
            self.page.screenshot(path="lnb_fail_판매가격관리.png")
            raise AssertionError("기준정보 메뉴를 10초 내에 찾지 못했습니다. 네트워크, 서버, UI 상태를 확인하세요.")
        except Exception as e:
            self.page.screenshot(path="lnb_unexpected_fail_차량선택.png")
            self.logger.error(f"예기치 않은 LNB 진입 에러: {e}")
            raise