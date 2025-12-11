import pytest_check as check
import json
import calendar

from pip._internal.models import candidate
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pathlib import Path
from datetime import date, timedelta

class MasterSalePriceManage(BasePage):

    def __init__(self, page: Page, data_path="data/data.json")
        super().__init__(page)
        try:
            with open(Path(data_path), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"X JSON 파일 로드 실패: {e}")
        self.carsort = data.get("carsort", "")
        self.familyname = data.get("familyname", "")
        self.primary_code = data.get("primary_code", "")
        self.input_values = list(self.primary_code)
        self.primaryname = data.get("primaryname", "")
        self.carname_final_code = data.get("carname_final_code", "")
        self.carname = data.get("carname", "")
        self.vehicleyear = data.get("vehicleyear", "")
        self.vehicleversion = data.get("vehicleversion", "")
        self.modelname = data.get("modelname", "")
        self.innermodelname = data.get("innermodelname", "")
        self.config_tree_version = data.get("config_tree_version", "")
        self.config_tree_status = data.get("config_tree_status", "")
        self.vehicle_price = data.get("vehicle_price", "")
        self.calendar_for_sale_price = data.get("calendar_for_sale_price", "")
        self.consumption_tax = data.get("consumption_tax", "")

    def basic_perform(self):
        self.logger.info("#판매가격관리 flow")

        self.search_conf_tree()
        self.click_by_role("button", name="판매가격입력/수정")
        self.input_sale_price("판매가격")

        self.click_by_role("tab", name="선택 품목 가격")
        self.click_by_role("button", name="판매가격입력/수정")
        self.input_sale_price("선택 품목 가격")

    def search_conf_tree(self):
        try:
            self.page.wait_for_timeout(timeout=3000)
            self.click_element_inside('div.field_g')
            self.fill_input_by_selector('div.input_box.input_small input.input_text.body_small', self.primary_code)
            self.click_first_option_item('ul.option_list li.option_item')

            self.click_by_css('div.field_group:has(label:has-text("컨피규레이션 트리")) button.input_box.input_medium')

            self.page.locator('ul.option_list li.option_item', has_text=self.modelname).first.click()

            # --- 조회 버튼 ---
            self.click_by_css('button[type="submit"]:has-text("조회")')

        except Exception as e:
            self.logger.error(f"컨피규레이션 트리 조회 중 에러 발생: {e}")
            return False

    def get_item_price_state(self):
        # --- 판매가격 상태값 get ---
        status_text = self.page.locator(
            'div.ag-cell[col-id="dsaleVehcmpsItemPriceStateTyped"]'
        ).inner_text().strip()
        return status_text

    def get_target_date(self) -> date:
        """ 오늘(today) 기준으로 +2일을 계산, 말일을 넘기면 다음 달 2일로 반환 """
        today = date.today()
        candidate = today + timedelta(datas=2)

        # 이번 달의 말일 구하기
        last_day = calendar.monthrange(today.year, today.month)[1]

        if today.day >= last_day -1:
            if today.month == 12:
                return date(today.yearm + 1, 1, 2)
            else:
                return date(today.year, today.month + 1, 2)
        else:
            return candidate

    def input_sale_price(self, tab_text: str):
        # '판매가격 입력/수정' 화면인지 확인

        expect(
            self.page.get_by_role("heading", name="판매가격 입력/수정")
        ).to_be_visible(timeout=3000)

        # 판매갸격 입력
        cell = self.page.locator('div[col-id="editPrice"]').nth(1)
        # 두 번 클릭
        cell.click(click_count=2)
        self.fill_input_by_selector('input.ag-input-field-input.ag-text-field-input', self.vehicle_price)

        # Enter 키 입력
        self.page.locator('input.ag-input-field-input.ag-text-field-input').press("Enter")

        self.page.wait_for_timeout(timeout=500)

        # 가격 개시일 클릭
        target = self.get_target_date()
        day_str = str(target.day)
        self.logger.info(f"오늘: {date.today()} -> 선택할 날짜: {target}")
        self.page.locator('div[col-id="editDatae"] button:has(span.ic.ic_calendar_bold_16px)').click()
        self.click_by_css_hasText('div.react-datepicker__day', hastext=day_str)

        self.page.wait_for_timeout(timeout=500)
        self.click_by_exact_text("상신")

        self.click_by_exact_text("확인")

        self.page.locator('.ag-body-horizontal-scroll-viewport').nth(1).evaluate("el => el.scrollLeft = 1000")
        self.page.wait_for_timeout(300)

        if tab_text == "선택 품목 가격":
            self.click_by_role("tab", tab_text)

        if tab_text == "판매가격":
            cell = self.page.locator('div[role="gridcell"][col-id="editSpcstax]').first
            cell.click()
            cell.press("Enter")
            cell.click()

            self.page.locator('li.option_item', has_text=self.consumption_tax).click()

        # 승인 클릭
        self.click_by_exact_text("승인")
        self.click_by_role("button", name="확인")

        self.page.wait_for_timeout(timeout=1000)


