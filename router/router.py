"""
A library which allows for the creation and modification of
ngnix configuration files related to datacats sites.
"""

# {{ and }} because of 
REDIRECT_TEMPLATE = """server {{
    listen 80;
    server_name {site_name};

    location / {{
        proxy_pass http://localhost:{site_port};
    }}
}}
"""

class DatacatsNgnixConfig(object):
    def __init__(self, environment):
        """
        Reads configuration files for the given environment and
        initializes this object with it.
        """
        pass
