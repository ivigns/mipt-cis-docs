from client.web.models.update_doc_request import UpdateDocRequest
import json

doc_req = UpdateDocRequest(0, 0, 1, [["patch", 0], ["patch2", 2]])
jj = json.dumps(doc_req.to_dict())
print(jj)
dic_from_jj = json.loads(jj)

doc_resp = UpdateDocRequest(**dic_from_jj)
