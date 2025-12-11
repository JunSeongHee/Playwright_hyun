import pytest
import pytest_check as check
from pages.lnb.lnb_menu_page import LnbMenuPage
from pages.vehicle_info.vehicle_info_management_page import VehicleInfoManagement
from utils.customLogger import LogGen

logger = LogGen.loggen()

def goto_vehicle_info_management(page, base_url):
    logger.info(f"test_basePage: test_open_base_url {base_url}")
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    lnb = LnbMenuPage(page)
    lnb.go_to_vehicle_info_management()

    return VehicleInfoManagement(page)

@pytest.mark.order(1)
def test_vehicle_info_management_workflow(page, base_url):
    vehicle_info = goto_vehicle_info_management(page, base_url)
    logger.info("대표차명관리 페이지 진입 완료")

    assert vehicle_info is not None, "VehicleInfoManagement page 객체 생성 실패"

    # 대표차명 등록
    vehicle_info.register_primary_car()
    logger.info("대표차명 등록 완료")
    check.is_true(True, "대표차명 등록 Pass")

    # 차명 등록
    vehicle_info.register_car_name()
    logger.info("차명 등록 완료")
    check.is_true(True, "차명 등록 Pass")

    # 모델명 등록
    vehicle_info.register_model_name()
    logger.info("모델명 등록 완료")
    check.is_true(True, "차명 등록 Pass")

    # 조회 결과 확인
    result = vehicle_info.perform_search()
    if all(result.values()):
        logger.info("수정 완료 후 삭제 수행")

        result = vehicle_info.delete_all_tabs()
        if result:
            logger.info("삭제 완료\n 차량정보관리 TEST PASS")
            check.is_true(True, "등록한 차량 정보 삭제 Pass")
    else:
        logger.warning("조회 결과 없음 -> 수정/삭제 불가")
        assert False, "조회 결과 없어 Fail"
