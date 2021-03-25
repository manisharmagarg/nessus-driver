from driverapp import app, MEDIA_FOLDER
from flask import send_from_directory
from driverapp.views import HomeView, CreateScan, GetScan, NessusJobs, NessusEventJobs, DownloadFile


app.add_url_rule('/', view_func=HomeView.as_view('home'))

app.add_url_rule('/create-scan/', view_func=CreateScan.as_view('createScan'))

app.add_url_rule('/get-scan/<string:scan_id>/', view_func=GetScan.as_view('getScan'))

app.add_url_rule('/api/jobs/nessus/', view_func=NessusJobs.as_view('nessusJobs'))

app.add_url_rule('/api/jobs/nessus/<string:scan_id>', view_func=NessusJobs.as_view('nessusJobsById'))

app.add_url_rule('/api/event-jobs/', view_func=NessusEventJobs.as_view('nessusEventJobs'))

app.add_url_rule('/media/<path:filename>', view_func=DownloadFile.as_view('downloadFile'))
