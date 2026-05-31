from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@patch("cli.helpers.get_bridge")
def test_catalog_select(mock_get_bridge, runner):
    """lr catalog select がphotoIdでの写真選択を実行する"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "1",
        "success": True,
        "result": {"selected": 2},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "select", "123", "456"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.setSelectedPhotos", {"photoIds": ["123", "456"]}, timeout=30.0
    )


@patch("cli.helpers.get_bridge")
def test_catalog_find_by_path(mock_get_bridge, runner):
    """lr catalog find-by-path がパスで写真を検索する"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "2",
        "success": True,
        "result": {"id": 123, "filename": "IMG_001.jpg"},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "find-by-path", "/photos/IMG_001.jpg"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.findPhotoByPath", {"path": "/photos/IMG_001.jpg"}, timeout=30.0
    )


@patch("cli.helpers.get_bridge")
def test_catalog_collections(mock_get_bridge, runner):
    """lr catalog collections がコレクション一覧を返す"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "3",
        "success": True,
        "result": {"collections": [], "count": 0},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "collections"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with("catalog.getCollections", {}, timeout=30.0)


@patch("cli.helpers.get_bridge")
def test_catalog_keywords(mock_get_bridge, runner):
    """lr catalog keywords がキーワード一覧を返す"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "4",
        "success": True,
        "result": {"keywords": [], "count": 0},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "keywords"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with("catalog.getKeywords", {}, timeout=30.0)


@patch("cli.helpers.get_bridge")
def test_catalog_folders(mock_get_bridge, runner):
    """lr catalog folders がフォルダ一覧を返す"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "5",
        "success": True,
        "result": {"folders": [], "count": 0},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "folders"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with("catalog.getFolders", {"includeSubfolders": False}, timeout=30.0)


@patch("cli.helpers.get_bridge")
def test_catalog_folders_recursive(mock_get_bridge, runner):
    """lr catalog folders --recursive がサブフォルダ付きで返す"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "6",
        "success": True,
        "result": {"folders": [], "count": 0, "includeSubfolders": True},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "folders", "--recursive"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with("catalog.getFolders", {"includeSubfolders": True}, timeout=30.0)


@patch("cli.helpers.get_bridge")
def test_catalog_set_title(mock_get_bridge, runner):
    """lr catalog set-title 123 'Sunset' がcatalog.setTitleに正しいパラメータを送信する"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "7",
        "success": True,
        "result": {
            "photoId": "123",
            "title": "Sunset",
            "message": "Title set successfully",
        },
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "set-title", "123", "Sunset"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.setTitle", {"photoId": "123", "title": "Sunset"}, timeout=30.0
    )


@patch("cli.helpers.get_bridge")
def test_catalog_set_caption(mock_get_bridge, runner):
    """lr catalog set-caption 123 'A beautiful sunset' がcatalog.setCaptionに正しいパラメータを送信する"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "8",
        "success": True,
        "result": {
            "photoId": "123",
            "caption": "A beautiful sunset",
            "message": "Caption set successfully",
        },
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "set-caption", "123", "A beautiful sunset"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.setCaption",
        {"photoId": "123", "caption": "A beautiful sunset"},
        timeout=30.0,
    )


@patch("cli.helpers.get_bridge")
def test_catalog_set_color_label(mock_get_bridge, runner):
    """lr catalog set-color-label 123 red がcatalog.setColorLabelに正しいパラメータを送信する"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "9",
        "success": True,
        "result": {
            "photoId": "123",
            "label": "red",
            "message": "Color label set successfully",
        },
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "set-color-label", "123", "red"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.setColorLabel", {"photoId": "123", "label": "red"}, timeout=30.0
    )


@patch("cli.helpers.get_bridge")
def test_catalog_batch_metadata(mock_get_bridge, runner):
    """lr catalog batch-metadata がバッチメタデータを返す"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "10",
        "success": True,
        "result": {"photos": [{"id": "1", "fileName": "test.jpg"}]},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "batch-metadata", "1", "2"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.batchGetFormattedMetadata",
        {"photoIds": ["1", "2"], "keys": ["fileName", "dateTimeOriginal", "rating"]},
        timeout=30.0,
    )


@patch("cli.helpers.get_bridge")
def test_catalog_batch_metadata_custom_keys(mock_get_bridge, runner):
    """lr catalog batch-metadata --keys でカスタムキーを指定できる"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "11",
        "success": True,
        "result": {"photos": []},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "batch-metadata", "1", "--keys", "fileName,rating"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.batchGetFormattedMetadata",
        {"photoIds": ["1"], "keys": ["fileName", "rating"]},
        timeout=30.0,
    )


@patch("cli.helpers.get_bridge")
def test_catalog_find_brackets_defaults_to_selection(mock_get_bridge, runner):
    """lr catalog find-brackets searches the current selection by default"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "12",
        "success": True,
        "result": {"groups": [], "count": 0},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "find-brackets"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.findExposureBrackets",
        {
            "maxSecondsBetween": 2.0,
            "minPhotos": 3,
            "maxPhotos": 9,
            "source": "selected",
        },
        timeout=60.0,
    )


@patch("cli.helpers.get_bridge")
def test_catalog_find_brackets_with_photo_ids(mock_get_bridge, runner):
    """lr catalog find-brackets can inspect explicit IDs"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "13",
        "success": True,
        "result": {"groups": [], "count": 0},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(
        cli,
        [
            "catalog",
            "find-brackets",
            "--photo-ids",
            "1,2,3",
            "--max-seconds-between",
            "1.5",
            "--min-photos",
            "3",
            "--max-photos",
            "5",
        ],
    )
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.findExposureBrackets",
        {
            "maxSecondsBetween": 1.5,
            "minPhotos": 3,
            "maxPhotos": 5,
            "photoIds": ["1", "2", "3"],
        },
        timeout=60.0,
    )


@patch("cli.helpers.get_bridge")
def test_catalog_find_brackets_all(mock_get_bridge, runner):
    """lr catalog find-brackets --all scans the catalog"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "14",
        "success": True,
        "result": {"groups": [], "count": 0},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "find-brackets", "--all"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.findExposureBrackets",
        {
            "maxSecondsBetween": 2.0,
            "minPhotos": 3,
            "maxPhotos": 9,
            "source": "all",
        },
        timeout=60.0,
    )


@patch("cli.helpers.get_bridge")
def test_catalog_find_brackets_all_with_filters(mock_get_bridge, runner):
    """lr catalog find-brackets forwards restrictive filters for intentional scans"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "15",
        "success": True,
        "result": {"groups": [], "count": 0},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(
        cli,
        [
            "catalog",
            "find-brackets",
            "--all",
            "--folder-path",
            "/Shoot/Day1",
            "--capture-date-from",
            "2026-05-01",
            "--capture-date-to",
            "2026-05-02",
            "--file-format",
            "RAW",
        ],
    )
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.findExposureBrackets",
        {
            "maxSecondsBetween": 2.0,
            "minPhotos": 3,
            "maxPhotos": 9,
            "source": "all",
            "folderPath": "/Shoot/Day1",
            "captureDateFrom": "2026-05-01",
            "captureDateTo": "2026-05-02",
            "fileFormat": "RAW",
        },
        timeout=60.0,
    )


@patch("cli.helpers.get_bridge")
def test_catalog_find_brackets_rejects_empty_photo_ids_before_connect(mock_get_bridge, runner):
    result = runner.invoke(cli, ["catalog", "find-brackets", "--photo-ids", ",,,"])
    assert result.exit_code == 2
    mock_get_bridge.assert_not_called()


@patch("cli.helpers.get_bridge")
def test_catalog_find_brackets_rejects_max_below_min_before_connect(mock_get_bridge, runner):
    result = runner.invoke(cli, ["catalog", "find-brackets", "--min-photos", "5", "--max-photos", "3"])
    assert result.exit_code == 2
    mock_get_bridge.assert_not_called()


@patch("cli.helpers.get_bridge")
def test_catalog_rotate_left(mock_get_bridge, runner):
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "20",
        "success": True,
        "result": {"message": "Rotated left"},
    }
    mock_get_bridge.return_value = mock_bridge
    result = runner.invoke(cli, ["catalog", "rotate-left"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with("catalog.rotateLeft", {}, timeout=30.0)


@patch("cli.helpers.get_bridge")
def test_catalog_rotate_right(mock_get_bridge, runner):
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "21",
        "success": True,
        "result": {"message": "Rotated right"},
    }
    mock_get_bridge.return_value = mock_bridge
    result = runner.invoke(cli, ["catalog", "rotate-right"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with("catalog.rotateRight", {}, timeout=30.0)


@patch("cli.helpers.get_bridge")
def test_catalog_create_virtual_copy(mock_get_bridge, runner):
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "22",
        "success": True,
        "result": {"message": "Virtual copy created"},
    }
    mock_get_bridge.return_value = mock_bridge
    result = runner.invoke(cli, ["catalog", "create-virtual-copy"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with("catalog.createVirtualCopy", {}, timeout=30.0)


@patch("cli.helpers.get_bridge")
def test_catalog_set_metadata(mock_get_bridge, runner):
    """lr catalog set-metadata が汎用メタデータを設定する"""
    mock_bridge = AsyncMock()
    mock_bridge.send_command.return_value = {
        "id": "30",
        "success": True,
        "result": {"photoId": "123", "key": "copyright", "value": "2026 Photographer"},
    }
    mock_get_bridge.return_value = mock_bridge

    result = runner.invoke(cli, ["catalog", "set-metadata", "123", "copyright", "2026 Photographer"])
    assert result.exit_code == 0
    mock_bridge.send_command.assert_called_once_with(
        "catalog.setMetadata",
        {"photoId": "123", "key": "copyright", "value": "2026 Photographer"},
        timeout=30.0,
    )
