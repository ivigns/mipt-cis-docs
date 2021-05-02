from diff_sync.mocks.mock_stack import MockStack
from diff_sync.mocks.mock_connector import MockConnector

from diff_sync.client_diff_sync import ClientDiffSync
from diff_sync.server_diff_sync import ServerDiffSync

# Client

client_text = """
My best document!

1. cat;
2. god;
"""
client_shadow = """
My first document

1. cat
2. god
"""

client_connect = MockConnector(client_text, client_shadow)
client_diff_sync = ClientDiffSync(client_connect, MockStack())

client_diff_sync.update()

edits_to_send = client_diff_sync.get_edits()
server_version_to_send = client_diff_sync.get_received_version()
# Server

server_text = """
My first document

1. dog
2. cat
3. rabbit
"""

server_shadow =  """
My first document

1. cat
2. god
"""

server_backup = server_shadow
server_connector = MockConnector(server_text, server_shadow, server_backup)
server_diff_sync = ServerDiffSync(server_connector, MockStack())

server_diff_sync.patch_edits(edits_to_send, server_version_to_send)

print("HERE IS THE SERVER SHADOW AFTER PATCH")
print("-------------------------------",end='')
print(server_connector.get_shadow())
print("-------------------------------")

print("HERE IS THE SERVER AFTER PATCH")
print("-------------------------------",end='')
print(server_connector.get_text())
print("-------------------------------")


server_diff_sync.update()

edits_to_send = server_diff_sync.get_edits()
client_version_to_send = server_diff_sync.get_received_version()

## client

client_diff_sync.patch_edits(edits_to_send, client_version_to_send)

print("HERE IS THE CLIENT SHADOW AFTER PATCH")
print("-------------------------------",end='')
print(client_connect.get_shadow())
print("-------------------------------")

print("HERE IS THE CLIENT AFTER PATCH")
print("-------------------------------",end='')
print(client_connect.get_text())
print("-------------------------------")
