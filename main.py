import flormar
import urls

data = flormar.retrive_all(urls.urls)
print(urls.urls)

wks = flormar.select_sheet("T Test",0)
flormar.insert_into_sheet(data,wks)
