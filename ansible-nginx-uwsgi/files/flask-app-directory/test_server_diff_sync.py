from mock_stack import MockStack
from mock_connector import MockConnector

from server_diff_sync import ServerDiffSync

server_text = ""

server_shadow = ""

edits = [["@@ -1,8 +1,11 @@\n+hee\n %0A%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82 \n", 8], ["@@ -1,11 +1,13 @@\n he\n-e\n+llo\n %0A%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82 \n", 9]]
edits_to_send = MockStack(edits)

server_backup = server_shadow
server_connector = MockConnector(server_text, server_shadow, server_backup)
server_diff_sync = ServerDiffSync(server_connector, MockStack())

server_diff_sync.patch_edits(edits_to_send, 0)

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
