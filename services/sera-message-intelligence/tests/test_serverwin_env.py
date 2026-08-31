import importlib.util
import os
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_serverwin_wechat_collector.py"
SPEC = importlib.util.spec_from_file_location("serverwin_collector", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_load_env_file_strips_utf8_bom(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / "serverwin.env"
    env_file.write_bytes(b"\xef\xbb\xbfSMI_WECHAT_ACCOUNT_ID=wechat-main\n")

    MODULE.load_env_file(env_file)

    assert os.environ["SMI_WECHAT_ACCOUNT_ID"] == "wechat-main"
