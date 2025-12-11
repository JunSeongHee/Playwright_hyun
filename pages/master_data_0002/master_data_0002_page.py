# pages/master_data_0002/master_data_0002_page.py
import json
from pathlib import Path
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

class MasterData0002(BasePage):
    def __init__(self, page: Page, data_path="data/data.json"):
        super().__init__(page)
        try:
            with open(Path(data_path), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"X JSON 파일 로드 실패: {e}")

        self.model_property_category = data.get("model_property_category", "")
        self.model_property_long_desc = data.get("model_property_long_desc", "")
        self.model_property_short_desc = data.get("model_property_short_desc", "")

        self.option_property_category = data.get("option_property_category", "")
        self.option_property_long_desc = data.get("option_property_long_desc", "")
        self.option_property_short_desc = data.get("option_property_short_desc", "")

    # -------- 공통 흐름(추가 → 조회 → 속성추가 → 수정 → 삭제) ----------
    def _flow_property_crud(self, top_tab: str, sub_tab: str,
                            category: str, long_desc: str, short_desc: str) -> bool:
        try:
            # 탭 선택
            self.select_tab(top_tab, sub_tab)

            # 1) 속성분류 추가
            self.register_property("속성분류 추가", category=category)
            if not self.confirm_or_duplicate("추가 되었습니다."):
                self.logger.error("속성분류 추가 실패(중복/에러)")
                return False

            # 2) 검색 → 결과 선택
            self.search_property(category)

            # 3) 속성 추가
            self.register_property("속성 추가", long_desc=long_desc, short_desc=short_desc)
            if not self.confirm_or_duplicate("추가 되었습니다."):
                self.logger.error("속성 추가 실패(중복/에러)")
                return False

            # 4) 새로고침 후 탭 복귀
            self.page.reload()
            self.select_tab(top_tab, sub_tab)

            # 5) 수정
            self.update_property(category, long_desc, short_desc)
            if not self.confirm_or_duplicate("수정하시겠습니까?"):
                self.logger.error("수정 확인 실패")
                return False

            # 6) 삭제 (속성 → 속성분류)
            return self._delete_property_flow(top_tab, sub_tab, category)
        except Exception as e:
            self.logger.error(f"공통 흐름 실패: {e}")
            return False

    def model_add(self) -> bool:
        return self._flow_property_crud(
            top_tab="승소상", sub_tab="모델",
            category=self.model_property_category,
            long_desc=self.model_property_long_desc,
            short_desc=self.model_property_short_desc
        )

    def option_add(self) -> bool:
        return self._flow_property_crud(
            top_tab="트럭", sub_tab="옵션",
            category=self.option_property_category,
            long_desc=self.option_property_long_desc,
            short_desc=self.option_property_short_desc
        )

    # -------- 개별 동작들 ----------
    def select_tab(self, top_category: str, sub_category: str):
        self.click_by_role("tab", top_category)
        self.click_by_exact_text(sub_category)

    def search_property(self, search_query: str):
        input_box = self.page.get_by_placeholder("폴더명 또는 속성분류명 입력", exact=True)
        input_box.fill(search_query)
        self.click_by_css_hasText('span.css-9x4jlj mark', search_query)  # BasePage에 있다면 거기로

    def register_property(self, text: str, category: str = None, long_desc: str = None, short_desc: str = None):
        self.click_by_exact_text(text)
        self.popup_handle(text, category=category, long_desc=long_desc, short_desc=short_desc)

    def popup_handle(self, text: str, category: str = None, long_desc: str = None, short_desc: str = None):
        popup = self.page.locator('div[role="dialog"]')
        title = popup.locator('.dialog_title')

        if text == "속성분류 추가":
            if self.is_element_visible(title.filter(has_text="속성분류 추가")):
                popup.get_by_placeholder("속성분류명").fill(category)
                popup.get_by_text("추가", exact=True).click()
            else:
                assert False, "속성 분류 추가 팝업 미표시"
        elif text == "속성 추가":
            if self.is_element_visible(title.filter(has_text="속성 추가")):
                self.fill_by_label("Long Description", long_desc)
                self.fill_by_label("Short Description", short_desc)
                popup.get_by_text("추가", exact=True).click()
            else:
                assert False, "속성 추가 팝업 미표시"
        elif text == "속성 정보":
            if self.is_element_visible(title.filter(has_text="속성 정보")):
                self.fill_by_label("Long Description", f"{long_desc}_Update")
                self.fill_by_label("Short Description", f"{short_desc}_Update")
                popup.get_by_text("저장", exact=True).click()
            else:
                assert False, "속성 정보 팝업 미표시"
        elif text == "삭제":
            popup.locator('button.btn.btn_primary', has_text="삭제").click()
        else:
            assert False, "알 수 없는 팝업 타입"

    def update_property(self, query, long_desc, short_desc):
        self.search_property(query)
        self.click_by_exact_text(long_desc)  # 수정 대상 선택 기준
        self.click_by_role("button", "수정")
        self.popup_handle("속성 정보", long_desc=long_desc, short_desc=short_desc)

    # 삭제 동작 (속성 → 속성분류)
    def _delete_property_flow(self, top_tab: str, sub_tab: str, query: str) -> bool:
        try:
            # 1) 속성 삭제
            self.page.reload()
            self.select_tab(top_tab, sub_tab)
            self.search_property(query)

            # BUGFIX: 따옴표 누락 수정
            self.page.locator('input[data-ref="eInput"][type="checkbox"]').first.click()
            self.click_by_role("button", "삭제")
            self.click_by_role("button", "확인")

            # 2) 속성분류 삭제
            self.page.reload()
            self.select_tab(top_tab, sub_tab)

            row = self.row_by_cell_text(query)
            idx = self.row_index_of(row)
            self.check_checkbox_of_row_index(idx)

            self.click_by_role("button", "삭제")
            self.click_by_role("button", "확인")
            return True
        except Exception as e:
            self.logger.error(f"삭제 실패: {e}")
            return False
