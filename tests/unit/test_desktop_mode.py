import pytest
import os
import base64
from unittest.mock import patch, MagicMock
from dash import html
import pandas as pd


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
        assert 'Select Folder' in str(upload_component.children)
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
        """Test handling folder upload with valid XML files"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Simulate folder upload with XML files
        contents_list = [f'data:text/xml;base64,{mock_xml_content}', f'data:text/xml;base64,{mock_xml_content}']
        filenames_list = ['file1.xml', 'file2.xml']
        app_mode = 'desktop'
        
        # Get the callback function
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children..last-folder-store.data']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status, last_folder = result
        
        assert len(xml_files) == 2
        assert xml_files[0]['filename'] == 'file1.xml'
        assert xml_files[1]['filename'] == 'file2.xml'
        assert style == {'display': 'block'}
        assert file_list is not None
        assert last_folder == xml_files
    
    def test_handle_folder_upload_no_xml_files(self):
        """Test handling folder upload with no XML files"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        contents_list = ['data:text/plain;base64,dGVzdA==']
        filenames_list = ['file.txt']
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children..last-folder-store.data']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status, last_folder = result
        
        assert xml_files is None
        assert file_list is None
        assert style == {'display': 'none'}
        assert 'No XML files found' in str(status)
        assert last_folder is None
    
    def test_handle_folder_upload_web_mode_ignored(self):
        """Test that folder upload is ignored in web mode"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        contents_list = ['data:text/xml;base64,test']
        filenames_list = ['file.xml']
        app_mode = 'web'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children..last-folder-store.data']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status, last_folder = result
        
        assert xml_files is None
        assert file_list is None
        assert style == {'display': 'none'}
        assert status == ''
        assert last_folder is None
    
    def test_handle_folder_upload_empty_contents(self):
        """Test handling folder upload with empty contents"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        contents_list = None
        filenames_list = None
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children..last-folder-store.data']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status, last_folder = result
        
        assert xml_files is None
        assert file_list is None
        assert style == {'display': 'none'}
        assert status == ''
        assert last_folder is None
    
    @patch('presentation.callbacks.parse_xml_scores')
    @patch('presentation.callbacks.validate_upload')
    def test_load_selected_file_success(self, mock_validate, mock_parse, mock_xml_content):
        """Test loading a selected file successfully"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        # Mock validation and parsing
        mock_validate.return_value = ('file.xml', '<xml>test</xml>')
        mock_parse.return_value = (
            pd.DataFrame({'Driver': ['Test'], 'Lap': [1]}),
            {'track': 'Test Track'},
            {'chat': [], 'incident': [], 'penalty': []}
        )
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        xml_files = [{'filename': 'file1.xml', 'content': f'data:text/xml;base64,{mock_xml_content}'}]
        n_clicks_list = [1]
        button_ids = [{'type': 'file-button', 'index': 0}]
        app_mode = 'desktop'
        
        callback = app.callback_map['stored-data.data..stored-race-info.data..stored-incidents.data..upload-status.children..standings-lap-store.data']['callback']
        
        result = callback(n_clicks_list, app_mode, xml_files, button_ids)
        data, race_info, incidents, status, lap = result
        
        assert len(data) > 0
        assert 'loaded successfully' in str(status)
    
    def test_load_selected_file_web_mode_ignored(self):
        """Test that file loading is ignored in web mode"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        import dash.exceptions
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        xml_files = [{'filename': 'file1.xml', 'content': 'data:text/xml;base64,test'}]
        n_clicks_list = [1]
        button_ids = [{'type': 'file-button', 'index': 0}]
        app_mode = 'web'
        
        callback = app.callback_map['stored-data.data..stored-race-info.data..stored-incidents.data..upload-status.children..standings-lap-store.data']['callback']
        
        with pytest.raises(dash.exceptions.PreventUpdate):
            callback(n_clicks_list, app_mode, xml_files, button_ids)
    
    def test_load_selected_file_no_clicks(self):
        """Test that no file is loaded when no button is clicked"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        import dash.exceptions
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        xml_files = [{'filename': 'file1.xml', 'content': 'data:text/xml;base64,test'}]
        n_clicks_list = [0]
        button_ids = [{'type': 'file-button', 'index': 0}]
        app_mode = 'desktop'
        
        callback = app.callback_map['stored-data.data..stored-race-info.data..stored-incidents.data..upload-status.children..standings-lap-store.data']['callback']
        
        with pytest.raises(dash.exceptions.PreventUpdate):
            callback(n_clicks_list, app_mode, xml_files, button_ids)
    
    @patch('presentation.callbacks.validate_upload')
    def test_load_selected_file_invalid_file(self, mock_validate, mock_xml_content):
        """Test loading an invalid file"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        # Mock validation to raise error
        mock_validate.side_effect = ValueError('Invalid XML')
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        xml_files = [{'filename': 'file1.xml', 'content': f'data:text/xml;base64,{mock_xml_content}'}]
        n_clicks_list = [1]
        button_ids = [{'type': 'file-button', 'index': 0}]
        app_mode = 'desktop'
        
        callback = app.callback_map['stored-data.data..stored-race-info.data..stored-incidents.data..upload-status.children..standings-lap-store.data']['callback']
        
        result = callback(n_clicks_list, app_mode, xml_files, button_ids)
        data, race_info, incidents, status, lap = result
        
        assert 'Error loading' in str(status)
    
    def test_update_data_desktop_mode_ignored(self):
        """Test that update_data callback is ignored in desktop mode"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        import dash.exceptions
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        contents = 'data:text/xml;base64,test'
        app_mode = 'desktop'
        filename = 'test.xml'
        
        # Find the update_data callback
        for key in app.callback_map.keys():
            if 'stored-data.data' in key and 'upload-data.contents' in str(app.callback_map[key].get('inputs', [])):
                callback = app.callback_map[key]['callback']
                
                with pytest.raises(dash.exceptions.PreventUpdate):
                    callback(contents, app_mode, filename)
                break


class TestDesktopModeEdgeCases:
    """Tests for edge cases in Desktop mode"""
    
    def test_mixed_file_types_in_folder(self, mock_xml_content):
        """Test folder with mixed file types"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        contents_list = [
            f'data:text/xml;base64,{mock_xml_content}',
            'data:text/plain;base64,dGVzdA==',
            f'data:text/xml;base64,{mock_xml_content}'
        ]
        filenames_list = ['file1.xml', 'file.txt', 'file2.xmlx']
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children..last-folder-store.data']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status, last_folder = result
        
        assert len(xml_files) == 2
        assert xml_files[0]['filename'] == 'file1.xml'
        assert xml_files[1]['filename'] == 'file2.xmlx'
        assert last_folder == xml_files
    
    def test_large_file_in_desktop_mode(self):
        """Test handling large file in desktop mode"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Create large content (>20MB)
        large_content = base64.b64encode(b'x' * (21 * 1024 * 1024)).decode()
        xml_files = [{'filename': 'large.xml', 'content': f'data:text/xml;base64,{large_content}'}]
        n_clicks_list = [1]
        button_ids = [{'type': 'file-button', 'index': 0}]
        app_mode = 'desktop'
        
        callback = app.callback_map['stored-data.data..stored-race-info.data..stored-incidents.data..upload-status.children..standings-lap-store.data']['callback']
        
        result = callback(n_clicks_list, app_mode, xml_files, button_ids)
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
        """Test that last folder is stored in local storage"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        contents_list = [f'data:text/xml;base64,{mock_xml_content}']
        filenames_list = ['test.xml']
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children..last-folder-store.data']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status, last_folder = result
        
        assert last_folder is not None
        assert len(last_folder) == 1
        assert last_folder[0]['filename'] == 'test.xml'
    
    def test_restore_last_folder_on_load(self, mock_xml_content):
        """Test that last folder is restored when app loads"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Simulate stored folder data
        stored_data = [{'filename': 'stored.xml', 'content': f'data:text/xml;base64,{mock_xml_content}'}]
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style']['callback']
        
        result = callback(stored_data, app_mode)
        xml_files, file_list, style = result
        
        assert xml_files == stored_data
        assert style == {'display': 'block'}
    
    def test_file_list_has_scrollbar(self, mock_xml_content):
        """Test that file list has scrollbar when many files"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Create 10 files
        contents_list = [f'data:text/xml;base64,{mock_xml_content}' for _ in range(10)]
        filenames_list = [f'file{i}.xml' for i in range(10)]
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children..last-folder-store.data']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status, last_folder = result
        
        # Check that the inner div has maxHeight and overflowY
        inner_div = file_list.children[1]
        assert 'maxHeight' in inner_div.style
        assert inner_div.style['maxHeight'] == '200px'
        assert inner_div.style['overflowY'] == 'auto'
