import pytest


def test_bake_with_defaults(cookies, bake_in_temp_dir, text_in_file):
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path.is_dir()
        assert result.exit_code == 0
        assert result.exception is None

        print(result.project_path.iterdir())
        found_toplevel_files = [f.name for f in result.project_path.iterdir()]
        assert 'infra' in found_toplevel_files
        assert 'extract' in found_toplevel_files
        assert 'transform' in found_toplevel_files
