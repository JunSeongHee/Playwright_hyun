from playwright.sync_api import Page, expect, TimeoutError, Locator
from utils.customLogger import LogGen

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = LogGen.loggen()

    def get_element_by_text(self, text: str):
        return self.page.get_by_text(text)

    def get_element_by_id(self, element_id: str):
        return self.page.locator(f"#{element_id}")

    def get_element_by_xpath(self, xpath: str):
        return self.page.locator(f"xpath={xpath}")

    def get_element_by_css(self, selector: str):
        return self.page.locator(selector)

    def get_element_by_class(self, class_name: str):
        return self.page.locator(f".{class_name}")

    def get_element_by_role(self, role: str, name: str = None):
        return self.page.get_by_role(role, name=name) if name else self.page.get_by_role(role)

    def get_element_by_css_hasText(self, selector: str, hastext: str):
        return self.page.locator(selector, has_text=hastext)

    def get_element_by_svg_path(self, svg_path_d: str):
        return self.page.locator(f"svg path[d=\'{svg_path_d}\']")

    def is_element_visible(self, locator, timeout=2000):
        try:
            expect(locator).to_be_visible(timeout=timeout)
            return True
        except Exception:
            return False

     # --- AG-Grid 공통 ---
    def row_by_cell_text(self, text: str) -> Locator:
        # 셀 텍스트 → 가장 가까운 row
        row = self.page.locator(
            f'xpath=//span[normalize-space(.)="{text}"]/ancestor::div[@role="row"][1]'
        ).first
        row.scroll_into_view_if_needed()
        return row

    def row_index_of(self, row: Locator) -> str:
        idx = row.get_attribute("row-index") or row.get_attribute("aria-rowindex")
        assert idx, "row-index 를 찾지 못했습니다."
        return idx.strip()

    def checkbox_in_row(self, row: Locator) -> Locator:
        cb = row.get_by_role("checkbox").first
        if cb.count() == 0:
            cb = row.locator('input[type="checkbox"]').first
        return cb

    def check_checkbox_of_row_index(self, idx: str):
        target_row = self.page.locator(
            f'div[role="row"][row-index="{idx}"]'
        ).first
        self.checkbox_in_row(target_row).check()

    # --- Dialog/Confirm 공통 ---
    def confirm_or_duplicate(self, ok_text: str) -> bool:
        # 성공 다이얼로그
        ok = self.page.locator('.dialog_desc', has_text=ok_text)
        dup = self.page.locator('.dialog_desc', has_text='중복')
        try:
            ok.wait_for(state="visible", timeout=2000)
            self.click_by_role("button", name="확인")
            return True
        except Exception:
            pass
        try:
            dup.wait_for(state="visible", timeout=1000)
            self.click_by_role("button", name="확인")
            return False
        except Exception:
            # 진짜로 아무 다이얼로그도 없다면 실패로 간주
            return False

    # --- Visible Method ---
    def is_element_visible(self, locator: Locator, timeout=1500) -> bool:
        try:
            expect(locator).to_be_visible(timeout=timeout)
            return True
        except Exception:
            return False

    # --- Click Method ---
    def click_by_text(self, text: str, index: int = None, mode: str = "visible"):
        if index is not None:
            locator = self.get_element_by_text(text).nth(index)

        else:
            locator = self.get_element_by_text(text)

        self._click(locator, f"{text} : click", mode=mode)

    def click_by_exact_text(self, text: str, mode: str = "visible"):
        locator = self.page.get_by_text(text, exact=True)
        self._click(locator, f"{text} 정확히 일치하는 text : click", mode=mode)

    def click_by_id(self, element_id: str, mode: str = "visible"):
        locator = self.page_element_by_id(element_id)
        self._click(locator, f"{element_id} : click", mode=mode)

    def click_by_xpath(self, xpath: str, mode: str = "visible"):
        locator = self.get_element_by_xpath(xpath)
        self._click(locator, f"{xpath} (XPath) : click", mode=mode)

    def click_by_css(self, selector: str, mode: str = "visible"):
        self._click(self.page.locator(selector), f"{selector} (CSS) : click", mode=mode)

    def click_by_class(self, class_name: str, mode: str = "visible"):
        locator = self.get_element_by_class(class_name)
        self._click(locator, f".{class_name} (class) : click", mode=mode)

    def click_by_role(self, role: str, name: str = None, index: int = None, mode: str = "visible"):
        locator = self.get_element_by_role(role, name)
        if index is not None:
            locator = locator.nth(index)
            desc = f"role={role}, name={name}, index={index} : click"

        else:
            desc = f"role={role}, name={name} : click"

        self._click(locator, desc, mode=mode)

    def click_by_css_hasText(self, selector: str, hastext: str, mode: str = "visible"):
        locator = self.get_element_by_css_hasText(selector, hastext)
        self._click(locator, f".{selector} with text {hastext} : click", mode=mode)

    def click_button_next_to_label(self, label_selector: str, mode: str = "visible"):
        locator = self.page.locator(label_selector).locator("..").locator("button")
        self._click(locator, f"[{label_selector}] 옆 버튼 : click", mode=mode)

    def click_button_next_to_label_by_index(self, base_selector: str, nth: int = 1, mode: str = "visible"):
        locator = self.page.locator(base_selector).locator("..").nth(nth).locator("button")
        self._click(locator, f"[{base_selector}] 옆 nth={nth} 버튼 : click", mode=mode)

    def click_first_option_item(self, container_selector: str, mode: str = "visible"):
        locator = self.page.locator(container_selector).first
        self._click(locator, f"[{container_selector}] 내 첫 번쨰 항목 : click", mode=mode)

    def click_element_by_index(self, container_selector: str, index: int = 0, mode: str = "visible"):
        locator = self.page.locator(container_selector).nth(index)
        self._click(locator, f"[{container_selector}] 내 {index} 항목 : click", mode=mode)

    def click_element_inside(self, outer_selector: str, inner_selector: str, mode: str = "visible"):
        locator = self.page.locator(outer_selector).locator(inner_selector)
        self._click(locator, f"{outer_selector}, {inner_selector} : click", mode=mode)

    def click_element_within_by_index(self, outer_selector: str, inner_selector: str, index: int = 0, mode: str = "visible"):
        locator = self.page.locator(outer_selector).locator(inner_selector).nth(index)
        self._click(locator, f"{outer_selector}, {inner_selector}, {index}번째 click", mode=mode)

    # --- Fill ---
    def fill_input_by_selector(self, selector: str, value: str):
        locator = self.page.locator(selector)
        self._fill_with_locator(locator, value)

    def fill_input_by_index(self, selector: str, value: str, index: int=0):
        locator = self.page.locator(selector).nth(index)
        self._fill_with_locator(locator, value)

    def fill_input_next_to_label(self, lable_selector: str, value: str):
        locator = self.page.locator(lable_selector).locator("..").locator("input")
        self._fill_with_locator(locator, value)

    def fill_by_label(self, label_text: str, value: str):
        inp = self.page.locator(f'xpath=//label[normalize-space()="{label_text}"]/following::input[@type="text"][1]').first

        if inp.count() > 0:
            inp.fill(value)
            return True

        raise AssertionError(f'"{label_text}" 필드의 입력 요소를 찾지 못했습니다.')

    # ---------- 공통 Click & Fill 핸들러 -----------
    def _click(self, locator, description: str, mode: str = "visible"):
        try:
            if mode == "visible":
                expect(locator).to_be_visible(timeout=3000)
            elif mode == "enabled":
                expect(locator).to_be_enabled(timeout=3000)
            else:
                raise ValueError(f"Invalid click mode: {mode}")

            locator.click()
            self.logger.info(f"{description} OK")
        except TimeoutError:
            self.logger.error(f"{description} 실패 - 요소가 {mode} 상태가 아님")
            raise
        except Exception as e:
            self.logger.error(f"{description} 실패 - 예외 발생: {e}")
            raise

    def _fill_with_locator(self, locator: Locator, value:str):
        try:
            expect(locator).to_be_visible(timeout=3000)
            locator.fill(value)
            self.page.wait_for_timeout(1000)
            expect(locator).to_have_value(value)
            self.logger.info(f"값 {value} 입력 성공")
        except TimeoutError:
            self.logger.error(f"요소가 나타나지 않음")
            raise
        except Exception as e:
            self.logger.error(f"값 입력 실패 - 예외 발생: {e}")
            raise

    # ---------- 기타 유틸 -----------
    def get_title(self) -> str:
        return self.page.title()