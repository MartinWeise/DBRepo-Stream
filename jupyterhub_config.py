import os

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
# notebook_dir = '/notebooks'
# c.DockerSpawner.notebook_dir = notebook_dir
# c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
c.DockerSpawner.remove_containers = True
c.DockerSpawner.debug = True

c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080

# TLS config
# c.JupyterHub.port = 443
# c.JupyterHub.ssl_key = os.environ['SSL_KEY']
# c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Persist hub data on volume mounted inside container
# data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')
# c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
#     'jupyterhub_cookie_secret')

# c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
#     host=os.environ['POSTGRES_HOST'],
#     password=os.environ['POSTGRES_PASSWORD'],
#     db=os.environ['POSTGRES_DB'],
# )

# Whitlelist users and admins
c.Authenticator.whitelist = {'retropotato','MartinWeise'}
c.Authenticator.admin_users = {'retropotato','MartinWeise'}
c.JupyterHub.admin_access = True