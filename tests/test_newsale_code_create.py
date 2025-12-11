import json, pytest
import pytest_check as check

from pages.lnb.lnb_menu_page import LnbMenuPage
from pages.vehicle_info.vehicle_info_management_page import VehicleInfoManagement
from pages.tree_composition.tree_composition_management import TreeCompositionManagement
from utils.customLogger import LogGen

logger = LogGen.loggen()

def load_test_data():
    with open('data/data.json', encoding='utf-8') as f:
        data = json.load(f)
    return data

def goto_vehicle_info_management(page, base_url):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    lnb = LnbMenuPage(page)
    lnb.go_to_vehicle_info_management()

    return VehicleInfoManagement(page)

def goto_newsale_code_create(page, base_url):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    lnb = LnbMenuPage(page)
    lnb.go_to_newsale_code_create()

    return TreeCompositionManagement(page)

@pytest.mark.order(3)
def test_vehicle_info_Register(page, base_url):
    vehicle_info = goto_vehicle_info_management(page, base_url)
    assert vehicle_info is not None, "VehicleInfoManagement page 객체 생성 실패"

    # 대표차명 등록
    vehicle_info.register_primary_car()
    check.is_true(True, "대표차명 등록 Pass")

    # 차명 등록
    vehicle_info.register_car_name()
    check.is_true(True, "차명 등록 Pass")

    # 모델명 등록
    vehicle_info.register_model_name()
    check.is_true(True, "모델명 등록 Pass")

@pytest.mark.order(4)
def test_configuration_tree_create(page, base_url):
    logger.info("컨피규레이션 트리 신규 등록")
    tree_conf = goto_newsale_code_create(page, base_url)

    test_data = load_test_data()
    modelname = test_data["modelname"]
    config_tree_version = test_data["config_tree_versions"]
    config_tree_status = test_data["config_tree_statuses"]

    # 조회 시, 갯수가 0(조회가 안되면)이면 컨피규레이션 트리 신규 등록
    logger.info("컨피규레이션 트리 조회")
    count = tree_conf.search_conf_tree()

    if count == 0:
        # 컨피규레이션 트리 신규 등록
        assert tree_conf.register_conf_tree() is True
        # 신규 등록 후 1단계 구성 수행
        assert tree_conf.configuration_tree_one_composition() is True
        # 이후 2단계, 3단계 등 계속 진행
        assert run_tree_composition_flow(tree_conf, modelname, config_tree_version, config_tree_status) is True
    else:
        logger.info(f"조회 갯수 : {count}, 버전 : {modelname}_{config_tree_version[0]}")
        page.get_by_text(f"{modelname}_{config_tree_version[0]}").click()
        assert run_tree_composition_flow(tree_conf, modelname, config_tree_version, config_tree_status) is True

def run_tree_composition_flow(tree_conf, modelname, config_tree_version, config_tree_status) -> bool:
    if not tree_conf.configuration_tree_two_composition():
        return False
    if not tree_conf.configuration_tree_three_composition():
        return False
    if not tree_conf.stage_link_connection("[기본모델] 1"):
        return False
    if not tree_conf.stage_link_connection("[트림] 2"):
        return False

    result = tree_conf.create_sales_code
    logger.info(f"판매코드 생성 result : {result}")
    return bool(result)



