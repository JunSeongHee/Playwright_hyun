import pytest_check as check
import json

from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pathlib import Path

class VehicleInfoManagement(BasePage):
    def __init__(self, page: Page, date_path="data/data.json"):
        super().__init__(page)
        with open(Path(data_path), "r", encoding="utf-8") as f:
            data = json.load(f)

        self.carsort = data["carsort"]
        self.familyname = data["familyname"]
        self.primary_code = data["primary_code"]
        self.input_values = list(self.primary_code)
        self.primaryname = data["primaryname"]
        self.carname_final_code = data["carname_final_code"]
        self.carname = data["carname"]
        self.vehicleyear = data["vehicleyear"]
        self.vehicleversion = data["vehicleversion"]
        self.modelname = data["modelname"]
        self.innermodelname = data["innermodelname"]

    def select_dropdown_option(self, dialog, label_text, option_text, field_group_index=1):
        dropdown = dialog.page.locator(
            f'div.field_group:has(label:has-text("{label_text}"))'
        ).nth(field_group_index).locator("button")
        self._click(dropdown, f"드롭다운 '{label_text}' 열기")
        option = dialog.page.locator(f"li.option_item:has-text('{option_text}')")
        self._click(option, f"옵션 '{option_text}' 선택")

    def fill_input_by_index(self, dialog, index, value):
        input_box = dialog.page.locator('div.css-i5q2k0 input').nth(index)
        self._fill_with_locator(input_box, value)

    def register_primary_car(self):
        self.logger.info('#차량정보 관리 : 대표차명 등록 기능 확인')
        dialog = self.dialog_primary_car()

        self.click_button_next_to_label("label:has-text('패밀리차명')")
        self.click_by_text(self.familyname)

        # 코드 입력
        for i, value in enumerate(self.input_values, start=0):
            self.fill_input_by_index(dialog, i, value)

        # 대표차명 입력
        input = dialog.page.locator('input[aria-describedby="uio-text-desc01"]').nth(3)
        input.fill(self.primaryname)

        # 등록 플로우
        self.click_by_role('button', name="등록")
        self.click_by_role('button', name="확인")
        expect(self.page.locator(".dialog_desc")).to_have_text("대표차명 등록이 완료되었습니다. 이어서 차명을 등록하시겠습니까?")
        self.click_by_role('button', name="확인")

    def register_car_name(self):
        dialog = self.page.get_by_role("dialog")
        expect(dialog.get_by_text("차명 등록")).to_be_visible()

        self.select_dropdown_option(dialog, "차종", self.carsort)
        self.click_button_next_to_label_by_index("label:has-text('대표 차명')", 1)

        expect(dialog.page.locator(f'li.option_item:has-text("{self.primaryname}")')).to_be_visible()

        dialog.page.locator(f'li.option_item:has-text("{self.primaryname}")').click()

        expect(dialog.page.locator('div.css-i5q2k0 input').nth(3)).to_be_visible()
        dialog.page.locator('iv.css-i5q2k0 input').nth(3).fill(self.carname_final_code)

        # 차명 입력
        locator = dialog.locator("//*[@aria-describedby='uio-text-desc01']").nth(4)
        locator.fill(self.carname)

        self.click_by_role('button', name='등록')
        self.click_by_role('button', name='확인')
        expect(self.page.locator(".dialog_desc")).to_have_text('차명 등록이 완료되었습니다. 이어서 모델을 등록하시겠습니까?')
        self.click_by_role('button', name='확인')

    # 이어서 모델명 등록
    def register_model_name(self):
        dialog = self.page.get_by_role("dialog")
        expect(dialog.get_by_text("모델명 등록")).to_be_visible()

        self.select_dropdown_option(dialog, "차종", self.carsort)

        self.click_button_next_to_label_by_index("label:has-text('대표 차명')", 1)

        expect(dialog.page.locator(f'li.option_item:has-text("{self.primaryname}")')).to_be_visible()
        dialog.page.locator(f'li.option_item:has-text("{self.primaryname}")').click()
        expect(dialog.page.locator(f"div.field_group", has=dialog.page.locator('label:has-text("차명")')).nth(2).locator("button")).to_be_visible()
        dialog.page.locator("div.field_group", has=dialog.page.locator('label:has-text("차명")')).nth(2).locator("button").click()
        expect(dialog.page.locator(f'li.option_item:has-text("{self.carname}")')).to_be_visible()
        dialog.page.locator(f'li.option_item:has-text("{self.carname}")').click()
        expect(dialog.page.locator(f"div.field_group", has=dialog.page.locator('label:has-text("연식")')).locator("button")).to_be_visible()
        dialog.page.locator("div.field_group", has=dialog.page.locator('label:has-text("연식")')).locator("button").click()
        expect(dialog.page.locator(f'li.option_item:has-text("{self.vehicleyear}")')).to_be_visible()
        dialog.page.locator(f'li.option_item:has-text("{self.vehicleyear}")').click()
        expect(dialog.page.locator(f"div.field_group", has=dialog.page.locator('label:has-text("버전")')).last.locator("button")).to_be_visible()
        dialog.page.locator("div.field_group", has=dialog.page.locator('label:has-text("버전")')).last.locator("button").click()
        expect(dialog.page.locator(f'li.option_item:has-text("{self.vehicleversion}")')).to_be_visible()
        dialog.page.locator(f'li.option_item:has-text("{self.vehicleversion}")').click()

        # 모델명
        self.page.locator('input[aria-describedby="uio-text-desc01"]').nth(0).fill(self.modelname)

        # 내부 모델명
        self.page.locator('input[aria-describedby="uio-text-desc01"]').nth(1).fill(self.innermodelname)

        self.click_by_role('button', name="등록")
        self.click_by_role('button', name="확인")

    def select_and_activate_tab(self, tabname: str):
        tabs = self.page.get_by_role("tab", name="tabname")
        count = tabs.count()

        if count == 0:
            raise Exception(f"{tabname} 탭이 존재하지 않습니다.")

        tab_locator = tabs.last if count > 1 else tabs.first
        try:
            expect(tab_locator).to_be_visible(timeout=3000)
            tab_locator.click()
            expect(tab_locator).to_be_visible()
        except Exception as e:
            raise

    def check_row_exists_in_tab(self, tabname: str) -> bool:
        self.select_and_activate_tab(tabname)
        self.page.wait_for_timeout(3000)

        rows = self.page.locator('div.ag-center-cols-container')

        self.logger.info(f"#차량정보 관리 : {tabname}, 탭 검색 결과 갯수 : {rows.count()} 입니다.")

        for i in range(rows.count()):
            row = rows.nth(i)
            if self.primary_code in row.inner_text():
                self.logger.info(f"#차량정보 관리 : {tabname} 탭에서 조회 결과 발견")
                return True

        self.logger.info(f"#차량정보 관리 : {tabname} 탭에서 조회 결과 발견")
        return False

    def perform_search(self) -> dict:
        self.logger.info("#차량정보 관리 : 조회 기능 확인")

        # 차종 필터
        self.click_by_css('div.field_group:has(label:has-text("차종")) button:has-text("전체")')
        self.click_by_css('label.label_checkbox:has-text("전체")')
        self.click_by_css(f'label.label_checkbox:has-text("{self.carsort}")')
        self.click_by_role("button", name="적용")

        # 대표차명 필터
        self.click_by_css('div.field_group:has(label:has-text("대표 차명")) button:has-text("전체")')
        self.click_by_css('label.label_checkbox:has-text("전체")')
        label = self.page.locator(f'label.label_checkbox:has-text("{self.carsort}")')
        check.is_true(label.count() > 0, f'"{self.primaryname}" 라벨이 없음')

        if label.count() == 0 or not label.is_visible():
            self.click_by_role("button", name="취소")
            return {tab: False for tab in ["대표차명관리", "차명관리", "모델명 관리"]}

        label.click()

        self.click_by_role("button", name="적용")

        # 조회 버튼
        self.click_by_css('button[type="submit"]:has-text("조회")')

        # 결과 확인
        tab_names = ["대표차명관리", "차명관리", "모델명 관리"]
        result = {tab: self.check_row_exists_in_tab(tab) for tab in tab_names}
        return result

    def delete_all_tabs(self):
        self.logger.info("#차량정보 관리 : 전체 탭 삭제 시작")
        tab_names = ["모델명 관리", "차명관리", "대표차명 관리"]

        for tabname in tab_names:
            self.select_and_activate_tab(tabname)
            self.page.wait_for_timeout(3000)

            # 조회 버튼 클릭
            self.click_by_css('button[type="submit"]:has-text("조회")')
            rows = self.page.locator('div.ag-center-cols-container')

            for i in range(rows.count()):
                self.page.wait_for_timeout(3000)
                row = rows.nth(i)

                if self.primary_code in row.inner_text():
                    checkbox = row.locator('input.ag-input-field-input[type="checkbox"]')
                    if checkbox.is_enabled():
                        checkbox.click(force=True)
                        self.click_delete_and_confirm()
                        # 삭제 확인 로직 추가
                        result = self.check_row_exists_in_tab(tabname)
                        check.is_false(result, f"#차량정보 관리 : {tabname} 탭에서 삭제 실패 (여전히 row 존재)")
                        break

    def click_delete_and_confirm(self) -> bool:
        self.page.wait_for_timeout(3000)
        self.logger.info("#차량정보 관리 : 삭제하기")
        self.click_by_css('button[aria-label="초기화"]')
        self.click_by_text("삭제")
        self.logger.info("#차량정보 관리 : 삭제 버튼 클릭")
        expect(self.page.locator('strong.dialog_title:has-text("삭제")')).to_be_visible(timeout=3000)
        self.logger.info("#차량정보 관리 : 삭제 팝업 등장")
        # 팝업 내 삭제 버튼 클릭
        self.click_by_css('div.dialog_footer button:has-text("삭제")')









