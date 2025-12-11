import pytest, allure
import os, re, shutil, subprocess, glob, warnings

from shutil import which
from _pytest.warning_types import PytestWarning
from datetime import datetime
from playwright.sync_api import Page, sync_playwright
from lib2to3.fixes.fix_metaclass import remove_trailing_newline

def _slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", s)

def _allure_path() -> str | None:
    return which("allure")  # e.g. C:\ProgramData\chocolatey\bin\allure.bat

def _has_allure_json(results_dir: str) -> bool:
    return bool(glob.glob(os.path.join(results_dir, "*.json")))

def pytest_addoption(parser):
    print("conftest : pytest_addoption")
    parser.addini("base_url", "Base url for the application under test")
    parser.addini("env", "Execution environment for allure (DEV/STG/PRD)", default="DEV")
    parser.addini("browser", "Browser name for playwright (chromium/chrome/msedge)", default="chromium")
    parser.addini("headless","Run browser headless mode (true/false)", default="false")
    parser.addini("allure_auto", "auto open allure: none|open|serve")

    parser.addoption("--headless", action="store_true", help="Run browser in headless mode")
    parser.addoption(
        "--allure-auto",
        dest="allure_auto",
        action="store",
        default=os.environ.get("ALLURE_AUTO", "none"),
        choices=("none", "serve", "open"),
        help="Auto open Allure after tests: serve|open|none (default: none)",
    )
    parser.addoption(
        "--slowmo",
        action="store",
        default="0",
        help="Playwright slow motion delay (ms)"
    )

@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getini("base_url")

@pytest.fixture(scope="session")
def exec_env(pytestconfig) -> str:
    return pytestconfig.getini("env") or "DEV"

@pytest.fixture(scope="session")
def browser_name(pytestconfig) -> str:
    return pytestconfig.getini("browser").strip().lower()

@pytest.fixture(scope="session")
def headless(pytestconfig):
    ini_value = pytestconfig.getini("headless").strip().lower()
    cli_flag = pytestconfig.getoption("--headless")
    # cli 가 우선, 없으면 ini 값 사용
    return cli_flag or ini_value in ("true", "1", "yes")

@pytest.fixture(scope="session")
def pw():
    with sync_playwright() as p:
        yield p

# ------------------------------------------
# Playwright Page fixture
# ------------------------------------------
@pytest.fixture(scope="function")
def page(pw, browser_name, headless, base_url, pytestconfig):
    """
    각 테스트에서 사용할 Playwright Page fixture.
    - 브라우저 띄우고
    - 새 context / page 만들고
    - base_url 로 진입까지 수행
    """
    name = browser_name or "chromium"

    # slowmo 옵션 (pytest --slowmo=500 이런 식으로)
    try:
        slow_mo = int(pytestconfig.getoption("--slowmo") or "0")
    except ValueError:
        slow_mo = 0

    # browser 타입 선택
    if name in ("chromium", "firefox", "webkit"):
        browser_type = getattr(pw, name)
    else:
        # 이상한 이름 들어오면 기본 chromium
        browser_type = pw.chromium

    browser = browser_type.launch(headless=headless, slow_mo=slow_mo)

    context = browser.new_context(
        viewport={"width": 1920, "height": 1080}
    )
    context.set_default_timeout(30_000)  # 30초

    page = context.new_page()
    if base_url:
        page.goto(base_url)

    # 테스트에서 여기까지 쓴 다음에
    yield page

    # 테스트 끝나면 정리
    context.close()
    browser.close()


def pytest_configure(config):
    os.makedirs("allure-results", exist_ok=True)
    env_info = {
        "BASE_URL": config.getini("base_url"),
        "ENV": config.getini("env") or "STG",
        "BROWSER": config.getini("browser") or "chromium",
        "RUN_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Allure는 environment.properties 파일을 자동 인식
    with open("allure-results/environment.properties", "w", encoding="utf-8") as f:
        for k, v in env_info.items():
            if v:
                f.write(f"{k}={v}\n")

# ------------------------------------------
# 테스트 결과 정보 (setup/call/teardown) 저장
# ------------------------------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # 각 단계 결과를 보관 (setup/call/teardown)
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# ------------------------------------------
# 세션 종료 후 Allure Report 자동 실행
# ------------------------------------------
def pytest_sessionfinish(session, exitstatus: int):
    """ 테스트 세션 종료 후 Allure Report 자동 생성 및 열기 """
    config = session.config

    # xdist 워커에서는 한 번만 실행되도록
    if hasattr(config, "workerinput"):
        return

    # 우선순위: CLI --allure-auto > 환경변수 ALLURE_AUTO > pytest.ini allure_auto
    try:
        cli_mode = config.getoption("allure_auto") or "none"
    except ValueError:
        cli_mode = "none"

    env_mode = (os.environ.get("ALLURE_AUTO") or "none").strip().lower()
    ini_mode = (config.getini("allure_auto") or "none").strip().lower()
    mode = cli_mode if cli_mode != "none" else (env_mode if env_mode != "none" else ini_mode)

    # CI 환경에서는 자동 오픈 스킵
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        print("[Allure] CI 환경 감지 -> 자동 오픈 스킵")
        return

    if mode == "none":
        print(f"[Allure] 자동 오픈 비활성화(mode={mode})")
        return

    results_dir = "allure-results"
    report_dir = "allure-report"

    if not os.path.isdir(results_dir):
        warnings.warn(
            f"[Allure] 결과 폴더가 없습니다: {results_dir}"
            f" (pytest 실행 시 '--alluredir={results_dir}' 지정 필요)",
            PytestWarning,
        )
        return

    if not _has_allure_json(results_dir):
        details = [
            "1) 'alluredir' 미지정 또는 다른 경로에 생성됨",
            "2) 'allure-pytest' 플러그인 미설치/미활성 (pip install allure-pytest)",
            "3) 모든 테스트가 수집/실행되지 않아 결과가 비어있음",
        ]
        warnings.warn(
            "[Allure] 결과 JSON이 없습니다. 자동 오픈을 건너뜁니다.\n - "
            + "\n - ".join(details),
            PytestWarning,
        )
        return

    allure_cmd = _allure_path()
    if not allure_cmd:
        warnings.warn(
            "[Allure] Allure Commandline이 PATH에 없습니다. (allure --version / Java 확인)",
            PytestWarning,
        )
        return

    # history 복사 (트렌드 유지)
    hist_src = os.path.join(report_dir, "history")
    hist_dst = os.path.join(results_dir, "history")

    if os.path.isdir(hist_src):
        try:
            shutil.copytree(hist_src, hist_dst, dirs_exist_ok=True)
        except Exception:
            pass

    try:
        if mode == "serve":
            print(f"[Allure] serve 시작 -> {results_dir}")
            subprocess.Popen([allure_cmd, "serve", results_dir])
        elif mode == "open":
            if os.path.isdir(report_dir):
                shutil.rmtree(report_dir, ignore_errors=True)
            print(f"[Allure] generate -> {report_dir}")
            subprocess.check_call([allure_cmd, "generate", results_dir, "-o", report_dir, "--clean"])
            print(f"[Allure] open")

            try:
                subprocess.Popen([allure_cmd, "open", report_dir])
            except Exception:
                index_html = os.path.join(report_dir, "index.html")
                if os.name == "nt" and os.path.exists(index_html):
                    os.startfile(index_html)

    except Exception as e:
        warnings.warn(f"[Allure] 자동 실행 중 오류: {e}", PytestWarning)

@pytest.fixture(autouse=True)
def _allure_attach_on_fail(request):
    """
    각 테스트가 실패하면:
    - 스크린샷
    - DOM HTML
    - trace.zip
    - (가능하면) video를 Allure에 첨부
    """
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        # page / context / artifacts_dir 가져오기
        page = request.node.funcargs.get("page", None)
        # artifacts_dir은 page 생성 시점에 계산했으므로 다시 계산
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = _slug(request.node.nodeid)
        artifacts_dir = os.path.join("artifacts", f"{ts}__{safe_name}")

        # 스크린샷 + DOM
        if page:
            try:
                png_bytes = page.screenshot(full_page=True)
                allure.attach(png_bytes, name="screenshot", attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                allure.attach(str(e), name="screenshot_error.txt", attachment_type=allure.attachment_type.TEXT)

            try:
                html = page.content()
                allure.attach(html, name="dom.html", attachment_type=allure.attachment_type.HTML)
            except Exception as e:
                allure.attach(str(e), name="dom_error.txt", attachment_type=allure.attachment_type.TEXT)

    # trace.zip (테스트 종료 훅에서 저장)
    trace_zip_candidates = []
    for root, _, files in os.walk("artifacts"):
        for fn in files:
            if fn == "trace.zip":
                trace_zip_candidates.append(os.path.join(root, fn))
    for tz in trace_zip_candidates[-1:] or []: # 가장 최근 것 하나
        try:
            with open(tz, "rb") as f:
                allure.attach(f.read(), name="trace.zip", attachment_type=allure.attachment_type.ZIP)
        except Exception:
            pass

    # HAR
    har_candidates = []
    for root, _, files in os.walk("artifacts"):
        for fn in files:
            if fn.endswith(".har"):
                har_candidates.append(os.path.join(root, fn))

    for har in har_candidates[-1:] or []:
        try:
            with open(har, "rb") as f:
                allure.attach(f.read(), name="network.har", attachment_type=allure.attachment_type.MP4)
        except Exception:
            pass

    # VIDEO (최신 mp4 하나 첨부)
        # VIDEO (최신 mp4/webm 하나 첨부)
    video_candidates = []
    for root, _, files in os.walk("artifacts"):
        for fn in files:
            if fn.endswith(".webm") or fn.endswith(".mp4"):
                video_candidates.append(os.path.join(root, fn))

    for v in video_candidates[-1:] or []:
        try:
            with open(v, "rb") as f:
                allure.attach(f.read(), name=os.path.basename(v), attachment_type=allure.attachment_type.MP4)
        except Exception:
            pass