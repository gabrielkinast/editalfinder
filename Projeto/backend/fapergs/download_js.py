import requests
url="https://fapergs.rs.gov.br/matriz_common/versions/2.1.5/js/procergs/jquery.matrizPagedList.js?2.1.5.156.5+7"
r=requests.get(url)
print('status', r.status_code)
print(r.text[:3000])
