import json, re

from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pathlib import Path

class TreeCompositionManagement(BasePage):
    # 공통 상수 선언
    TRASH_SVG_PATH = 'svg path[d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6zM19 4h-3.51-1-1h-5l-1 1H5v2h14z"]'
    PLUS_SVG_PATH = 'svg path[d="M13 11h"]'
    PLUS_ITEM_SVG_PATH = 'svg path[d="M19 13h"]'
    STEP_PLUS_SVG_PATH = 'svg path[d="M12 2C6.48"]'

    def __init__(self, page: Page, data_path="data/data.json"):
        super().__init__(page)

        try:
            with open(Path(data_path), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"X JSON 파일 로드 실패: {e}")

        self.carsort = data.get["carsort"]
        self.familyname = data.get["familyname"]
        self.primary_code = data.get["primary_code"]
        self.input_values = list(self.primary_code)
        self.primaryname = data.get["primaryname"]
        self.carname_final_code = data["carname_final_code"]
        self.carname = data.get["carname"]
        self.vehicleyear = data.get["vehicleyear"]
        self.vehicleversion = data.get["vehicleversion"]
        self.modelname = data.get["modelname"]
        self.innermodelname = data["innermodelname"]
        self.config_tree_version = data.get("config_tree_versions", [])
        self.config_tree_status = data.get("config_tree_statuses", [])

    def register_conf_tree(self) -> bool:
        self.logger.info("#신판매코드 생성 : 컨피규레이션 트리 신규 등록")

        try:
            # 1. 신규 등록 버튼 클릭
            self.click_by_role("button", name="컨피규레이션 트리 신규 등록")

            # 2. 모델명 입력 및 선택
            self.click_button_next_to_label_by_index(f"label:has-text('모델명')", nth=1)
            self.click_first_option_item('div.option_group li.option_item')

            # 3. 등록 및 확인
            self.click_by_role("button", name="등록")
            self.click_by_role("button", name="확인")

            self.logger.info("#신판매코드 생성 : [성공] 컨피규레이션 트리 신규 등록 완료")
            return True
        except Exception as e:
            self.logger.error(f"#신판매코드 생성 : [실패] 컨피규레이션 트리 등록 예외 발생: {e}")
            return False

    def search_conf_tree(self) -> int:
        self.logger.info("#신판매코드 생성 : 컨피규레이션 트리 성공")

        try:
            # 대표자명 우측의 dropdown 선택
            self.page.wait_for_timeout(timeout=3000)
            self.click_element_inside('div.field_group:has(label:has-text("대표 차명"))', 'button')

            #대표차명 우측의 dropdown : 전체 클릭
            self.click_by_css('span.label_text.body_small:has-text("전체")')

            self.fill_input_by_selelctor('input[aria-describedby="uio-text-desc01"][class="input_text body_small"]', self.primary_code)
            self.click_first_option_item(f'label.label_checkbox:has-text("{self.primary_code}")')

            self.click_by_role("button", name="적용")

            self.click_by_css('button[type="submit"]:has-text("조회")')

            self.page.wait_for_timeout(500)

            total_text = self.page.locator("string.title_small span.text_info").inner_text()
            print("총 건수 : ", total_text)

            # 조회 갯수 반환
            if total_text == "0":
                return 0
            else:
                number = re.findall(r'\d+', total_text)
                count = int(number[0])
                print(f"건수 : {count}")
                return count
        except Exception as e:
            self.logger.error(f"컨피규레이션 트리 조회 중 에러 발생: {e}")
            return None

    def configuration_tree_one_composition(self) -> bool:
        self.logger.info(f"#신판매코드 생성 : 컨피규레이션 1단계 composition 구성 시작 - '{self.modelname}'_'{self.config_tree_version[0]}', '{self.config_tree_status[0]}'")

        if self.get_config_tree_status_exist(f"{self.modelname}_{self.config_tree_version[0]}", self.config_tree_status[0]):
            self.logger.infot("컨피규레이션 composition 구성 : 1단계 추가 시작")
            expect(self.page.get_by_text("1단계")).to_be_visible()

            if self.get_element_by_role("button", name="수정").is_visible():
                self.click_by_role("button", name="수정")

            self.page.wait_for_timeout(500)

            try:
                # ∇ 버튼 클릭
                self.click_element_inside("svg path[d='m7 10 5 5 5-5z']", "xpath=ancestor::button")

                # 기본모델 클릭
                self.click_by_css('li[role="menuitem"]:has-text("기본모델")')

                # 1단계의 아이템 추가(+ 버튼 - 기본모델 추가)
                self.click_by_css(f"button:has({self.PLUS_SVG_PATH})")

                #기본모델 클릭하여 포커싱
                self.click_by_exact_text("[기본모델] 1")
                self.page.wait_for_timeout(500)

                #차량속성마스터(CAM) 속성 추가 아이콘 버튼 클릭
                self.click_element_within_by_index(f"{self.STEP_PLUS_SVG_PATH}", "xpath=ancestor::button", 1)

                #차량속성마스터(CAM) 속성 추가 팝업 : input box 클릭
                self.click_element_by_index('input[placeholder="속성명 또는 속성분류명 검색"]')

                self.fill_input_by_index('input[placeholder="속성명 또는 속성분류명 검색"]', '엔진')

                self.page.wait_for_timeout(1000)

                self.click_by_text("스마트스트림 가솔린 3.5")

                self.click_by_css(f"button:has({self.PLUS_ITEM_SVG_PATH})")

                self.click_by_role("button", name="저장")

                self.logger.info("#신판매코드 생성 : 컨피규레이션 1단계 composition 구성 추가 완료")

            except Exception as e:
                self.logger.error(f"컨피규레이션 1단계 composition 구성 실패: {e}")

                self.page.wait_for_timeout(3000)

                self.click_element_within_by_index(f"{self.TRASH_SVG_PATH}", 'xpath=ancestor::button', 2)

                assert False, "컨피규레이션 1단계 comoposition 구성 실패"

        else:
            assert False, f"컨피규레이션 1단계 composition 구성 실패 : '{self.modelname}' 상태가 아님"

        return True


    def configuration_tree_two_composition(self) -> bool:
        self.logger.info("#신판매코드 생성 : 컨피규레이션 2단계 composition 구성 시작")

        if self.get_config_tree_status_exist(f"{self.modelname}_{self.config_tree_version[0]}", self.config_tree_status[0]):
            self.logger.info("컨피규레이션 composition 구성 : 2단계 추가 시작")
            expect(self.page.get_by_text("1 단계")).to_be_visible()

            if self.get_element_by_role("button", name="수정").is_visible():
                self.click_by_role("button", name="수정")

            self.page.wait_for_timeout(500)

        try:
            # 1단계에서 2단계 추가 버튼 클릭(단계 추가)
            self.click_element_by_index(f"button.MuiButtonBase-root:has({self.STEP_PLUS_SVG_PATH})", "enabled")
            self.page.wait_for_timeout(500)

            # 2단계의 아이템 추가 버튼 클릭(+ 버튼 - 트림 추가)
            self.click_element_by_index(f"button:has({self.PLUS_ITEM_SVG_PATH})", 1)

            # 트림 아이템의 클릭하여 포커싱
            self.click_first_option_item("li:has_text('Main 속성') button")

            self.page.wait_for_timeout(500)

            # 트림의 Main 속성을 Stadard (스탠다드) 로 설정
            self.click_by_css('div[role="gridcell"][col-id="vehicleAttributeName"] >> text=Stadard (스탠다드)')

            # "저장" 버튼 클릭
            self.click_by_role("button", name="저장")

            self.page.wait_for_timeout(500)

            # "Standard (스탠다드)" 가 추가되어 있는지 체크
            expect(self.page.locator('div.css-1to0bjd span:has-text("Standard (스탠다드)")')).to_be_visible(timeout=3000)

            # "Sub 속성 (0)" 항목 내의 + 버튼 클릭
            self.click_by_css(f"li:has(div:has-text('Sub 속성 (0)')) button:has({self.STEP_PLUS_SVG_PATH})")

            self.page.wait_for_timeout(500)
            # [트림] 2 의 sub 속성 추가 팝업 visible 확인
            sub_dialog = self.page.locator(
                'strong.dialog_title:has(div:has-text("[트림] 2")):has(div:has-text("차량속성마스터(CAM) 속성 추가-Sub 속성"))'
            )
            expect(sub_dialog).to_be_visible(timeout=3000)
            # 미션 입력 후 선택 후 추가
            self.add_attribute("미션", "스마트스트림 6단 자동변속기")
            # [트림] 2의 Sub 속성 추가  팝업 : 추가 아이콘 버튼 클릭
            self.click_by_css(f"button:has({self.PLUS_ITEM_SVG_PATH})")

            # 구동 입력 선택 후 추가
            self.clear_input_field("미션")
            self.add_attribute("구동", "4WD")
            self.click_by_css(f"button:has({self.PLUS_ITEM_SVG_PATH})")

            # 인승
            self.clear_input_field("구동")
            self.add_attribute("인승", "4인승")
            self.click_by_css(f"button:has({self.PLUS_ITEM_SVG_PATH})")

            self.click_by_role("button", name="저장")

            self.logger.error(f"신판매코드 생성 : 컨피규레이션 2단계 composition 구성 추가 완료")

        except Exception as e:
            self.logger.error(f"컨피규레이션 2단계 composition 구성 실패: {e}")

            self.click_element_within_by_index(f"{self.TRASH_SVG_PATH}", 'xpath=ancestor::button', 3)

            assert False, "컨피규레이션 2단계 composition 구성 실패"

        return True

    def configuration_tree_three_composition(self) -> bool:
        self.logger.info("#신판매코드 생성 : 컨피규레이션 3단계 composition 구성 시작")

        if self.get_config_tree_status_exist(f"{self.modelname}_{self.config_tree_version[0]}", self.config_tree_status[0]):
            self.logger.info("컨피규레이션 composition 구성 : 2단계 추가 시작")
            expect(self.page.get_by_text("1 단계")).to_be_visible()
            # 수정 버튼 클릭
            if self.get_element_by_role("button", name="수정").is_visible():
                self.click_by_role("button", name="수정")

            self.page.wait_for_timeout(500)

        try:
            # 2단계에서 3단계 추가 버튼 클릭 (단계 추가)
            self.click_element_by_index(f"button.MuiButtonBase-root:has({self.STEP_PLUS_SVG_PATH})", 1)
            self.page.wait_for_timeout(500)

            # ∇ 버튼 클릭
            self.click_element_within_by_index("svg path[d='m7 10 5 5 5-5z]", "xpath=ancestor::button", 2)

            # 선택품목 - 일반 옵션 클릭
            self.click_by_css('li[role="menuitem]:has-text("선택품목 - 일반 옵션")')

            # 3단계의 아이템 추가(+ 버튼 - 일반 옵션 추가)
            self.click_element_by_index(f"button:has({self.PLUS_ITEM_SVG_PATH})", 2)
            self.page.wait_for_timeout(500)

            # 일반옵션의 Main 속성을 추가
            self.click_first_option_item("li:has-text('Main 속성') button")
            self.page.wait_for_timeout(500)

            # 트림 Main 속성을 추가할 수 있는 팝업 visible 확인
            main_dialog = self.page.locator{
                'strong.dialog_title:has(div:has-text("선택품목 - 일반옵션")):has(div:has-text("차량속성마스터(CAM) 속성 추가-Main 속성"))'
            }
            expect(main_dialog).to_be_visible(timeout=3000)

            self.page.wait_for_timeout(500)

            # 차량속성마스터(CAM) 속성 추가 팝업 : input box 클릭
            self.add_attribute("선루프", "파노라마 선루프 + 루프랙 + LED 실내등")

            # "저장" 버튼 클릭
            self.click_by_role("button", name="저장")

            # "파노라마 선루프 + 루프랙..." 가 추가되어 있는지 체크
            expect(self.page.locator('div.css-1odsljb span:has-text("파노라마 선루프 + 루프랙 + LED 실내등")')).to_be_visible(timeout=3000)

            # "Sub 속성 (0)" 항목 내의 + 버튼 클릭
            self.click_by_css(f"li:has(div:has-text('Sub 속성 (0)')) button:has({self.STEP_PLUS_SVG_PATH})")
            self.page.wait_for_timeout(500)

            # [트림] 2의 sub 속성 추가 팝업 visible 확인
            sub_dialog = self.page.locator{
                'strong.dialog_title:has(div:has-text("선택품목 - 일반옵선")):has(div:has-text("차량속성마스터(CAM) 속성 추가-Sub 속성"))'
            }
            expect(sub_dialog).to_be_visible(timeout=3000)

            self.add_attribute("시트", "인조가죽 시트(블랙)")

            self.click_by_css(f"button:has({self.PLUS_ITEM_SVG_PATH})")

            self.click_by_role("button", name="저장")

            self.logger.info("#신판매코드 생성 : 컨피규레이션 3단계 composition 구성 추가 완료")

        except Exception as e:
            self.logger.error(f"컨피규레이션 3단계 composition 구성 실패: {e}")

            # 삭제 아이콘 버튼 선택
            self.click_element_within_by_index(f"{self.TRASH_SVG_PATH}", 'xpath=ancestor::button', 5)

            assert False, "컨피규레이션 3단계 composition 구성 실패"
        return True

    def get_config_tree_status_exist(self, version: str, status: str) -> bool:
        self.logger.info(f"#컨피규레이션 트리 : {version} + {status} 상태 존재 여부 확인")

        expect(self.page.get_by_text(f"{version}")).to_be_visible(timeout=3000)

        try:
            if status == "생성 완료":
                # 생성 완료 또는 생성 둘 중 하나라도 존재하면 True 반환
                model_locator_done = self.page.get_by_text("생성 완료")
                model_locator_processiong = self.page.get_by_text("생성 중")

                if model_locator_done.is_visible(timeout=3000):
                    self.logger.info(f"#컨피규레이션 트리 : 모델명_{version} + 생성 완료 상태 확인 완료")
                    return True
                elif model_locator_processiong.is_visible(timeout=3000)
                    self.logger.info(f"컨피규레이션 트리 : 모델명_{version} + 생성 중 상태 확인 완료")
                    return True
                else:
                    raise Exception("생성 완료/생성 중 상태가 모두 존재하지 않음")
            elif status == "사용 중":
                # 생성 완료 또는 생성 중 둘 중 하나라도 존재하면 True 반환
                model_locator_using = self.page.get_by_text("사용 중")

                if model_locator_using.is_visible(timeout=3000)
                    self.logger.info(f"컨피규레이션 트리 : 모델명_{version} + 사용 중 상태 확인 완료")
                    return True
                else:
                    raise Exception("사용 중 상태가 존재하지 않음")
            else:
                model_loc_temp_save = self.page.get_by_text("임시 저장")

                if model_loc_temp_save.is_visible(timeout=3000):
                    self.logger.info(f"#컨피규레이션 트리 : 모델명_{version} + 임시 저장 중 상태 확인 완료")
                    return True
                else:
                    raise Exception("임시 저장 중 상태가 존재하지 않음")

        except Exception as e:
            self.logger.warning(f"컨피규레이션 트리 : 해당 요소를 찾지 못했습니다. 예외: {e}")
            return False

    def stage_link_composition(self, text):
        self.logger.info("#신판매코드 생성 : 단계와 단계의 관계 설정")

        try:
            self.click_by_exact_text(text)

            # '관계 설정' 탭 클릭
            self.click_by_role("tab", name="관계 설정")

            self.click_by_role("button", name="링크 추가")

            self.page.wait_for_timeout(500)

            # 관계 설정 - 선택 클릭
            dropdown = self.page.get_by_placeholder("선택").locator('xpath=ancestor::button')
            dropdown.click()

            self.click_first_option_item("div.option_group li.option_item")

            # 저장 클릭
            self.click_by_role("button", name="저장")
        except Exception as e:
            self.logger.error(f"#신판매코드 생성 :  단계와 단계 관계 설정 실패: {e}")
            assert False, "#신판매코드 생성 :  단계와 단계 관계 설정 실패"
        return True

    def add_attribute(self, search_text: str, item_text: str):
        locator = 'input[placeholder="속성명 또는 속성분류명 검색"]'
        self.click_element_by_index(locator)
        self.fill_input_by_index(locator, search_text)
        self.page.wait_for_timeout(500)

        self.click_by_exact_text(item_text)

    def clear_input_field(self, value: str):
        """
        팝업 내 특정 placeholder와 같이 일치하는 input 필드를 찾아 클릭 후 값을 초기화한다.
        """
        popup = self.page.locator('div[role="dialog"]')
        input_locator = popup.locator(f'input[value="{value}"]')

        expect(input_locator).to_be_visible(timeout=3000)
        input_locator.click()
        input_locator.fill("")
        self.logger.info(f"팝업 내 입력값 삭제")

    @property
    def create_sales_code(self) -> bool:
        """
        오류 갯수 0을 확인 후 판매코드 생성한다. -> 생성 완료 상태값으로 만듦
        """
        self.page.wait_for_timeout(500)
        self.logger.info(f"#신판매코드 생성 : 판매코드 생성 버튼 - '{self.modelname}'_'{self.config_tree_version[0]}', '{self.config_tree_status[0]}'")

        model = f"{self.modelname}_{self.config_tree_version[0]}"
        status = self.config_tree_status[0]

        if not self.get_config_tree_status_exist(model, status):
            self.logger.warning("#신판매코드 생성 : 해당 모델명 + 상태값 조합이 존재하지 않음")
            return False

        loc = self.get_element_by_role("button", name="판매코드 생성").nth(1)

        if self.get_element_by_role("button", name="수정").is_visible():
            self.click_by_role("button", name="수정")

        if loc.is_visible(timeout=3000):
            loc.click()

        self.page.wait_for_timeout(timeout=500)
        # 오류 탭으로 전환
        self.click_by_role("tab", name="오류", index = 0)

        # 오류 갯스 텍스트 완전 피싱
        err_val_loc = self.page.locator("//div[text()='오류 종류 갯수']/following-sibling::div//div").inner_text()
        self.logger.info(f"오류 종류 갯수1 : {err_val_loc}")
        raw_err = err_val_loc.strip()
        self.logger.info(f"오류 종류 갯수2 : {raw_err}")

        # 숫자만 추출(콤마/공백/한글 섞임 대비)
        m = re.search(r"\d+", raw_err.replace(",", ""))
        self.logger.info(f"실제 오류 종류 갯수 : {m}")
        if not m:
            self.logger.error(f"오류 갯수 파싱 실패: '{raw_err}'")
            self.click_by_text("취소")

            return False
        error_count = int(m.group())
        self.logger.info(f"오류 종류 갯수: {error_count}")

        if error_count >= 1:
            self.logger.warning(f"오류 {error_count}건 존재 -> 생성 취소")
            self.click_by_text("취소")
            return False

        # 오류가 0이면 '생성 예쌍 판매코드' 탭으로
        tab_preview = self.page.get_by_role("tab", name="생성 예상 판매코드")
        expect(tab_preview).to_be_visible()
        tab_preview.click()

        # 예상 개수 읽기 (셀렉터 안정화 권장)
        label_loc = self.page.get_by_text("예상 판매코드 개수")
        if not label_loc.count() == 1:
            self.logger.error(f"예상 판매코드 개수가 {label_loc.count()} 이므로 nth를 사용하세요")
            return False

        value = label_loc.locator("xpath=following-sibling::div//div").first.inner_text()
        self.logger.info(f"예상 판매코드 개수1 : {value}")

        if not value:
            self.logger.error(f"예상 판매코드 개수 파싱 실패: '{value}'")
            self.click_by_text("취소")
            return False

        count_value = int(value)
        self.logger.info(f"예상 판매코드 개수 파싱 실패: '{value}'")

        if count_value != 1:
            self.logger.warning(f"예상 개수 {count_value}건 -> 생성 조건 불충족")
            self.click_by_text("취소")
            return False

        # 최종 "판매코드 생성" 버튼 (모달/화면 내 유일 버튼을 가정)
        final_btn = self.page.get_by_role("button", name="판매코드 생성").last
        expect(final_btn).to_be_visible()
        final_btn.click()

        # 확인(모달)
        confirm_btn = self.page.get_by_role("button", name="확인")
        expect(confirm_btn).to_be_visible()
        confirm_btn.click()

        self.logger.info("판매코드 생성 완료")
        return True

    def search_result_table_select(self):
        # 조회 결과 첫번째 행 선택
        cell = self.page.locator('div[role="gridcell"][col-id="vehicleCompositionName"] button').first
        cell.click()

        self.page.wait_for_timeout(timeout=1000)
        self.set_deployment()

    def set_deployment(self) -> bool:
        # 배포 클릭
        self.logger.info("배포")
        self.click_by_exact_text("배포")
        self.page.wait_for_timeout(timeout=1000)
        self.click_by_role("button", name="확인")
        return True










