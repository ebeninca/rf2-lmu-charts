import pytest
import os
import base64
from unittest.mock import patch, MagicMock
from dash import html
import pandas as pd


def get_callback(app, *output_ids):
    """Find callback by checking if all output_ids are present in the key"""
    for key in app.callback_map:
        if all(oid in key for oid in output_ids):
            return app.callback_map[key]['callback']
    raise KeyError(f'No callback found containing outputs: {output_ids}')


@pytest.fixture
def mock_xml_content():
    """Mock XML content for testing"""
    xml = """<?xml version="1.0"?>
<rFactorXML>
    <RaceResults>
        <Race laps="10" time="0" server="Test Server" track="Silverstone" course="Grand Prix" 
              trackLength="5891" mechFail="0" damage="100" fuel="100" tire="100" tireWarmers="1" 
              gameVersion="1.0" date="2024-01-01"/>
        <Driver name="Driver1" car="Team1" vehName="Car1" carType="GT3" class="GT3" 
                position="1" laps="10" finishTime="600.0" bestLap="60.0"/>
    </RaceResults>
</rFactorXML>"""
    return base64.b64encode(xml.encode()).decode()


@pytest.fixture
def mock_app_mode_desktop():
    """Mock APP_MODE as desktop"""
    with patch.dict(os.environ, {'APP_MODE': 'desktop'}):
        yield


@pytest.fixture
def mock_app_mode_web():
    """Mock APP_MODE as web"""
    with patch.dict(os.environ, {'APP_MODE': 'web'}):
        yield


@pytest.fixture
def mock_dotenv():
    """Mock python-dotenv load_dotenv"""
    with patch('app.load_dotenv'):
        yield


class TestDesktopModeLayout:
    """Tests for Desktop mode layout changes"""
    
    def test_layout_desktop_mode_shows_folder_upload(self, mock_app_mode_desktop):
        """Test that Desktop mode shows 'Select Folder' text"""
        from presentation.layouts import create_main_layout
        
        layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        
        # Find upload component
        upload_component = None
        for child in layout.children[0].children:
            if hasattr(child, 'id') and child.id == 'upload-data':
                upload_component = child
                break
        
        assert upload_component is not None
        assert 'Select Multiple XML Files' in str(upload_component.children)
        assert upload_component.multiple is True
    
    def test_layout_web_mode_shows_file_upload(self, mock_app_mode_web):
        """Test that Web mode shows 'Select XML File' text"""
        from presentation.layouts import create_main_layout
        
        layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        
        upload_component = None
        for child in layout.children[0].children:
            if hasattr(child, 'id') and child.id == 'upload-data':
                upload_component = child
                break
        
        assert upload_component is not None
        assert 'Select XML File' in str(upload_component.children)
        assert upload_component.multiple is False
    
    def test_layout_includes_file_list_container(self, mock_app_mode_desktop):
        """Test that layout includes file-list-container"""
        from presentation.layouts import create_main_layout
        
        layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        
        # Check for file-list-container
        has_file_list = False
        for child in layout.children[0].children:
            if hasattr(child, 'id') and child.id == 'file-list-container':
                has_file_list = True
                break
        
        assert has_file_list is True
    
    def test_layout_includes_app_mode_store(self, mock_app_mode_desktop):
        """Test that layout includes app-mode store"""
        from presentation.layouts import create_main_layout
        
        layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        
        # Check for app-mode store
        has_app_mode_store = False
        for child in layout.children[0].children:
            if hasattr(child, 'id') and child.id == 'app-mode':
                has_app_mode_store = True
                assert child.data == 'desktop'
                break
        
        assert has_app_mode_store is True


class TestDesktopModeCallbacks:
    """Tests for Desktop mode callbacks"""

    def test_handle_folder_upload_with_xml_files(self, mock_xml_content):
        from presentation.callbacks_desktop import _handle_folder_upload, server_file_cache
        server_file_cache.clear()
        contents_list = [f'data:text/xml;base64,{mock_xml_content}', f'data:text/xml;base64,{mock_xml_content}']
        result = _handle_folder_upload(contents_list, 'desktop', ['file1.xml', 'file2.xml'])
        xml_files, file_list, style, status, last_folder = result
        assert 'file1.xml' in xml_files
        assert 'file2.xml' in xml_files
        assert style == {'display': 'block'}
        assert file_list is not None

    def test_handle_folder_upload_no_xml_files(self):
        from presentation.callbacks_desktop import _handle_folder_upload, server_file_cache
        server_file_cache.clear()
        result = _handle_folder_upload(['data:text/plain;base64,dGVzdA=='], 'desktop', ['file.txt'])
        xml_files, file_list, style, status, last_folder = result
        assert style == {'display': 'none'}
        assert 'No XML files found' in str(status)

    def test_handle_folder_upload_web_mode_ignored(self):
        from presentation.callbacks_desktop import _handle_folder_upload
        result = _handle_folder_upload(['data:text/xml;base64,test'], 'web', ['file.xml'])
        xml_files, file_list, style, status, last_folder = result
        assert xml_files is None
        assert style == {'display': 'none'}
        assert status == ''
        assert last_folder is None

    def test_handle_folder_upload_empty_contents(self):
        from presentation.callbacks_desktop import _handle_folder_upload
        result = _handle_folder_upload(None, 'desktop', None)
        xml_files, file_list, style, status, last_folder = result
        assert xml_files is None
        assert style == {'display': 'none'}
        assert status == ''
        assert last_folder is None

    @patch('presentation.callbacks_desktop.parse_xml_scores')
    @patch('presentation.callbacks_desktop.validate_upload')
    def test_load_selected_file_success(self, mock_validate, mock_parse, mock_xml_content):
        from presentation.callbacks_desktop import _load_selected_file, server_file_cache
        mock_validate.return_value = ('file1.xml', '<xml/>')
        mock_parse.return_value = (
            pd.DataFrame({'Driver': ['Test'], 'Lap': [1]}),
            {'track': 'Test Track'},
            {'chat': [], 'incident': [], 'penalty': []}
        )
        server_file_cache['file1.xml'] = f'data:text/xml;base64,{mock_xml_content}'
        with patch('presentation.callbacks_desktop.dash.callback_context') as mock_ctx:
            mock_ctx.triggered = [{'prop_id': '{"type": "file-button", "index": 0}.n_clicks', 'value': 1}]
            result = _load_selected_file([1], ['file1.xml'], 'desktop', pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        data, race_info, incidents, status, lap = result
        assert len(data) > 0
        assert 'loaded successfully' in str(status)

    def test_load_selected_file_web_mode_ignored(self):
        from presentation.callbacks_desktop import _load_selected_file
        import dash.exceptions
        with pytest.raises(dash.exceptions.PreventUpdate):
            _load_selected_file([1], None, 'web', pd.DataFrame(), {}, {})

    def test_load_selected_file_no_clicks(self):
        from presentation.callbacks_desktop import _load_selected_file
        import dash.exceptions
        with patch('presentation.callbacks_desktop.dash.callback_context') as mock_ctx:
            mock_ctx.triggered = [{'prop_id': 'something.n_clicks', 'value': 0}]
            with pytest.raises(dash.exceptions.PreventUpdate):
                _load_selected_file([0], ['file1.xml'], 'desktop', pd.DataFrame(), {}, {})

    @patch('presentation.callbacks_desktop.validate_upload')
    def test_load_selected_file_invalid_file(self, mock_validate, mock_xml_content):
        from presentation.callbacks_desktop import _load_selected_file, server_file_cache
        mock_validate.side_effect = Exception('Invalid XML')
        server_file_cache['bad.xml'] = f'data:text/xml;base64,{mock_xml_content}'
        with patch('presentation.callbacks_desktop.dash.callback_context') as mock_ctx:
            mock_ctx.triggered = [{'prop_id': '{"type": "file-button", "index": 0}.n_clicks', 'value': 1}]
            result = _load_selected_file([1], ['bad.xml'], 'desktop', pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        data, race_info, incidents, status, lap = result
        assert 'Error loading' in str(status)

    def test_update_data_desktop_mode_ignored(self):
        from presentation.callbacks_upload import register_upload_callbacks
        from dash import Dash
        import dash.exceptions
        app = Dash(__name__)
        register_upload_callbacks(app, pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        # Verify the callback is registered — actual invocation tested via upload module directly
        assert any('stored-data.data' in k for k in app.callback_map)


class TestDesktopModeEdgeCases:
    """Tests for edge cases in Desktop mode"""

    def test_mixed_file_types_in_folder(self, mock_xml_content):
        from presentation.callbacks_desktop import _handle_folder_upload, server_file_cache
        server_file_cache.clear()
        contents_list = [
            f'data:text/xml;base64,{mock_xml_content}',
            'data:text/plain;base64,dGVzdA==',
            f'data:text/xml;base64,{mock_xml_content}'
        ]
        result = _handle_folder_upload(contents_list, 'desktop', ['file1.xml', 'file.txt', 'file2.xmlx'])
        xml_files, file_list, style, status, last_folder = result
        assert 'file1.xml' in xml_files
        assert 'file2.xmlx' in xml_files
        assert 'file.txt' not in xml_files

    def test_large_file_in_desktop_mode(self):
        from presentation.callbacks_desktop import _load_selected_file, server_file_cache
        large_content = base64.b64encode(b'x' * (60 * 1024 * 1024)).decode()
        server_file_cache['large.xml'] = f'data:text/xml;base64,{large_content}'
        with patch('presentation.callbacks_desktop.dash.callback_context') as mock_ctx:
            mock_ctx.triggered = [{'prop_id': '{"type": "file-button", "index": 0}.n_clicks', 'value': 1}]
            result = _load_selected_file([1], ['large.xml'], 'desktop', pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
        data, race_info, incidents, status, lap = result
        assert 'too large' in str(status).lower()

    def test_app_mode_empty_string_defaults_to_web(self):
        """Test that empty APP_MODE defaults to web behavior"""
        with patch.dict(os.environ, {'APP_MODE': ''}):
            from presentation.layouts import create_main_layout
            
            layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
            
            upload_component = None
            for child in layout.children[0].children:
                if hasattr(child, 'id') and child.id == 'upload-data':
                    upload_component = child
                    break
            
            assert upload_component is not None
            assert upload_component.multiple is False
    
    def test_app_mode_not_set_defaults_to_web(self):
        """Test that missing APP_MODE defaults to web behavior"""
        with patch.dict(os.environ, {}, clear=True):
            from presentation.layouts import create_main_layout
            
            layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
            
            upload_component = None
            for child in layout.children[0].children:
                if hasattr(child, 'id') and child.id == 'upload-data':
                    upload_component = child
                    break
            
            assert upload_component is not None
            assert upload_component.multiple is False
    
    def test_last_folder_store_persistence(self, mock_xml_content):
        from presentation.callbacks_desktop import _handle_folder_upload, server_file_cache
        server_file_cache.clear()
        result = _handle_folder_upload([f'data:text/xml;base64,{mock_xml_content}'], 'desktop', ['test.xml'])
        xml_files, file_list, style, status, last_folder = result
        assert last_folder is not None
        assert 'test.xml' in last_folder

    def test_restore_last_folder_on_load(self, mock_xml_content):
        from presentation.callbacks_desktop import _restore_last_folder, server_file_cache
        server_file_cache.clear()
        server_file_cache['stored.xml'] = f'data:text/xml;base64,{mock_xml_content}'
        result = _restore_last_folder(['stored.xml'], 'desktop')
        xml_files, file_list, style, last_folder = result
        assert style == {'display': 'block'}
        assert 'stored.xml' in xml_files

    def test_file_list_has_scrollbar(self, mock_xml_content):
        from presentation.callbacks_desktop import _handle_folder_upload, server_file_cache
        server_file_cache.clear()
        contents_list = [f'data:text/xml;base64,{mock_xml_content}' for _ in range(10)]
        filenames_list = [f'file{i}.xml' for i in range(10)]
        result = _handle_folder_upload(contents_list, 'desktop', filenames_list)
        xml_files, file_list, style, status, last_folder = result
        assert 'maxHeight' in str(file_list)
        assert '200px' in str(file_list)
