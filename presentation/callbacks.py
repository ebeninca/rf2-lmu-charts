from presentation.callbacks_cache import server_file_cache, server_metadata_cache, CACHE_FILE
from presentation.callbacks_desktop import register_desktop_callbacks
from presentation.callbacks_upload import register_upload_callbacks
from presentation.callbacks_filters import register_filter_callbacks
from presentation.callbacks_tabs import register_tab_callbacks


def register_callbacks(app, initial_df, initial_race_info, initial_incidents):
    register_desktop_callbacks(app, initial_df, initial_race_info, initial_incidents)
    register_upload_callbacks(app, initial_df, initial_race_info, initial_incidents)
    register_filter_callbacks(app)
    register_tab_callbacks(app)
