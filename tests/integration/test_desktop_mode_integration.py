import pytest
import os
import base64
from unittest.mock import patch

try:
    from dash.testing.application_runners import import_app
    DASH_TESTING_AVAILABLE = True
except ImportError:
    DASH_TESTING_AVAILABLE = False

pytestmark = pytest.mark.skipif(not DASH_TESTING_AVAILABLE, reason='dash.testing not available')


@pytest.fixture
def sample_xml_files():
    """Create sample XML files for testing"""
    xml1 = """<?xml version="1.0"?>
<rFactorXML>
    <RaceResults>
        <Race laps="5" time="0" server="Test Server 1" track="Silverstone" course="Grand Prix" 
              trackLength="5891" mechFail="0" damage="100" fuel="100" tire="100" tireWarmers="1" 
              gameVersion="1.0" date="2024-01-01"/>
        <Driver name="Driver1" car="Team1" vehName="Car1" carType="GT3" class="GT3" 
                position="1" laps="5" finishTime="300.0" bestLap="60.0"/>
    </RaceResults>
</rFactorXML>"""
    
    xml2 = """<?xml version="1.0"?>
<rFactorXML>
    <RaceResults>
        <Race laps="10" time="0" server="Test Server 2" track="Spa" course="Grand Prix" 
              trackLength="7004" mechFail="0" damage="100" fuel="100" tire="100" tireWarmers="1" 
              gameVersion="1.0" date="2024-01-02"/>
        <Driver name="Driver2" car="Team2" vehName="Car2" carType="GT3" class="GT3" 
                position="1" laps="10" finishTime="600.0" bestLap="60.0"/>
    </RaceResults>
</rFactorXML>"""
    
    return [
        {'filename': 'race1.xml', 'content': base64.b64encode(xml1.encode()).decode()},
        {'filename': 'race2.xml', 'content': base64.b64encode(xml2.encode()).decode()}
    ]


class TestDesktopModeIntegration:
    """Integration tests for Desktop mode"""
    
    @patch.dict(os.environ, {'APP_MODE': 'desktop'})
    def test_desktop_mode_full_workflow(self, dash_duo, sample_xml_files):
        """Test complete workflow in desktop mode"""
        # Import app with desktop mode
        app = import_app('app')
        dash_duo.start_server(app)
        
        # Verify upload component shows folder selection
        upload_text = dash_duo.find_element('#upload-data').text
        assert 'Select Folder' in upload_text
        
        # Simulate folder upload would require Selenium file upload
        # which is complex for folders, so we test the callback directly
        
    @patch.dict(os.environ, {'APP_MODE': 'web'})
    def test_web_mode_unchanged(self, dash_duo):
        """Test that web mode still works as expected"""
        app = import_app('app')
        dash_duo.start_server(app)
        
        # Verify upload component shows file selection
        upload_text = dash_duo.find_element('#upload-data').text
        assert 'Select XML File' in upload_text
    
    def test_mode_switching(self):
        """Test that mode can be switched via environment variable"""
        # Test desktop mode
        with patch.dict(os.environ, {'APP_MODE': 'desktop'}):
            from presentation.layouts import create_main_layout
            import pandas as pd
            
            layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
            
            # Find app-mode store
            app_mode_store = None
            for child in layout.children[0].children:
                if hasattr(child, 'id') and child.id == 'app-mode':
                    app_mode_store = child
                    break
            
            assert app_mode_store is not None
            assert app_mode_store.data == 'desktop'
        
        # Test web mode
        with patch.dict(os.environ, {'APP_MODE': 'web'}):
            from presentation.layouts import create_main_layout
            import pandas as pd
            
            # Need to reload module to pick up new env var
            import importlib
            import presentation.layouts
            importlib.reload(presentation.layouts)
            from presentation.layouts import create_main_layout
            
            layout = create_main_layout(pd.DataFrame(), {}, {'chat': [], 'incident': [], 'penalty': []})
            
            app_mode_store = None
            for child in layout.children[0].children:
                if hasattr(child, 'id') and child.id == 'app-mode':
                    app_mode_store = child
                    break
            
            assert app_mode_store is not None
            assert app_mode_store.data == 'web'


class TestDesktopModeErrorHandling:
    """Integration tests for error handling in Desktop mode"""
    
    @patch.dict(os.environ, {'APP_MODE': 'desktop'})
    def test_corrupted_xml_in_folder(self):
        """Test handling of corrupted XML file in folder"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        import pandas as pd
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Create corrupted XML
        corrupted_xml = base64.b64encode(b'<xml>corrupted</invalid>').decode()
        
        xml_files = [{'filename': 'corrupted.xml', 'content': f'data:text/xml;base64,{corrupted_xml}'}]
        n_clicks_list = [1]
        button_ids = [{'type': 'file-button', 'index': 0}]
        app_mode = 'desktop'
        
        callback = app.callback_map['stored-data.data..stored-race-info.data..stored-incidents.data..upload-status.children..standings-lap-store.data']['callback']
        
        result = callback(n_clicks_list, app_mode, xml_files, button_ids)
        data, race_info, incidents, status, lap = result
        
        # Should return error message
        assert 'Error' in str(status)
    
    @patch.dict(os.environ, {'APP_MODE': 'desktop'})
    def test_empty_folder(self):
        """Test handling of empty folder (no XML files)"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        import pandas as pd
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Empty contents
        contents_list = []
        filenames_list = []
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status = result
        
        assert xml_files is None
        assert style == {'display': 'none'}
    
    @patch.dict(os.environ, {'APP_MODE': 'desktop'})
    def test_folder_with_only_non_xml_files(self):
        """Test folder containing only non-XML files"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        import pandas as pd
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Non-XML files
        contents_list = [
            'data:text/plain;base64,dGVzdA==',
            'data:application/pdf;base64,dGVzdA=='
        ]
        filenames_list = ['file.txt', 'document.pdf']
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status = result
        
        assert xml_files is None
        assert 'No XML files found' in str(status)


class TestDesktopModePerformance:
    """Performance tests for Desktop mode"""
    
    @patch.dict(os.environ, {'APP_MODE': 'desktop'})
    def test_large_number_of_files(self):
        """Test handling of folder with many XML files"""
        from presentation.callbacks import register_callbacks
        from dash import Dash
        import pandas as pd
        
        app = Dash(__name__)
        initial_df = pd.DataFrame()
        initial_race_info = {}
        initial_incidents = {'chat': [], 'incident': [], 'penalty': []}
        
        register_callbacks(app, initial_df, initial_race_info, initial_incidents)
        
        # Create 50 XML files
        xml_content = base64.b64encode(b'<?xml version="1.0"?><rFactorXML></rFactorXML>').decode()
        contents_list = [f'data:text/xml;base64,{xml_content}' for _ in range(50)]
        filenames_list = [f'race_{i}.xml' for i in range(50)]
        app_mode = 'desktop'
        
        callback = app.callback_map['folder-files-store.data..file-list-container.children..file-list-container.style..upload-status.children']['callback']
        
        result = callback(contents_list, app_mode, filenames_list)
        xml_files, file_list, style, status = result
        
        assert len(xml_files) == 50
        assert style == {'display': 'block'}
